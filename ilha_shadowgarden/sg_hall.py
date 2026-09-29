# sg_hall - INTERIOR do Mining Hall da Ilha 3 (Shadow Garden): a mineracao principal, dentro da nave do castelo.
# Substitui sg_blockout.hall(). A CASCA (paredes, porta, janelas por fora, teto colidivel em HALL_CEIL, telhado) e do
# sg_castle; aqui so o que fica DENTRO do retangulo HALL_X0..X1 x HALL_Y0..Y1 (84 x 88, piso HALL 52,2).
# REFINAMENTO 2026-09-28 (salao de uma ORDEM): sistema de identidade (sg_emblem) e paleta com funcao (sg_lib.SMATS).
# OVERHAUL 04/05 (2026-09-29, "zero tolerancia", setores 04 castelo interior e 05 bordas do Mining Hall). No Roblox nao
# ha textura: a leitura vem da GEOMETRIA em camadas PAREDE -> RECUO -> PILAR/TRIM -> JANELA -> MOLDURA -> VIDRO.
#   - PAREDES: paramento ESPESSO (0,8) na frente da casca com SILHAR em fiadas (kit de cantaria do sg_castle) ate +8,
#     cordao com pingadeira, rodape em talude; os nichos sao RECUOS de verdade (fundo liso escuro, sem ruido) com
#     moldura varrida (toro + cavete), peitoril e fecho de obsidiana. Alternancia DIRIGIDA: A = misula de pedra com
#     candeia de 3 velas, B = prateleira de pedra com vaso de ferro; os nichos do eixo dos vitrais ganham moldura dupla;
#   - PILASTRAS: soco em talude, nucleo chanfrado, colunelos com base (toro/escocia) e o capitel (anel + cavete + abaco);
#   - GALERIA: laje com focinho boleado, cornija em cavete, misulas em perfil S, grade de barras redondas com roseta a
#     cada 3, corrimao boleado de prata, montantes com remate em bola (nada de piramide);
#   - VITRAIS: vidro RECUADO no vao da casca (1 stud para dentro), chumbo e rendilhado atras da moldura interna;
#   - ABOBADA: panos lisos (sem ruido) com LINHAS DE FIADA, nervuras em PERA (toro), chaves em FLORAO de 8 petalas;
#     o emblema da ordem so na chave central (y 88);
#   - PORTA (lado de dentro): ombreiras com colunelo violeta (base e capitel de torno), verga moldurada e arquivolta
#     varrida; as folhas (dobradas no vao) e o intradorso em caixotoes sao do sg_castle;
#   - FOCO: trono refeito (bracos com voluta, pes em pata, espaldar de moldura escalonada com crista ogival vazada,
#     almofadas com volume, estrado com espelhos moldurados), retabulo com pilares compostos e pinaculos do kit;
#   - LUSTRES e CANDEIAS: kit de vela (prato de ferro, vela CREME nao emissiva, chama em gota Neon pequena);
#   - estandartes: so os 2 do altar (os 4 das pilastras sairam: emblema demais no quadro).
#   - LUZ (6): 4 lustres quentes, 1 luar pelo vitral NO, 1 violeta no trono/emblema.
# NAO modela minerio nem pedra/cristal flutuante (sao do jogo). Dentro da MINE_RECT nada colidivel e nada solto no chao;
# nada no eixo do salao abaixo de piso+24; o corredor da porta fica livre. Tudo o que e novo fica nas BORDAS (d <= 3,5).
# Colisao propria: bases das pilastras, pilares do altar, ombreiras da porta, estrado (3 degraus) e trono (fora da zona).
import math, random
import bmesh
import sg_lib as SL
from sg_lib import MB, col_box2, light
import fm_lib
import sg_layout as L
import sg_emblem as EM
import sg_castle as CA

S = fm_lib.S
# ------------------------------------------------------------------ materiais novos da zona
# (fundo dos nichos e panos da abobada SEM o prefixo Stone_: pedra lisa, sem a textura de ruido do Stone_ - 05.05/14.02;
#  no Roblox continuam SmoothPlastic, como toda pedra)
NEW_MATS = {
    "Slate_SGHallVault": (S(26, 30, 60), 0.85, 0.0, 0, None, 0.0),        # panos da abobada: azul-noite liso
    "Slate_SGHallVaultJoint": (S(50, 56, 94), 0.85, 0.0, 0, None, 0.0),   # linhas de fiada da abobada
    "Slate_SGHallNiche": (S(58, 50, 76), 0.8, 0.0, 0, None, 0.0),         # fundo dos nichos / galeria: pedra lisa escura
    "Wax_SGHallCandle": (S(226, 194, 146), 0.7, 0.0, 0, None, 0.0),     # cera CREME QUENTE (Emblem_Cream lia branco)
    "Glass_SGHallMoon": (S(96, 124, 186), 0.4, 0.0, 0.4, S(110, 145, 220), 0.0),   # vitral de luar (= sg_castle)
    "Glass_SGHallViolet": (S(112, 56, 196), 0.3, 0.0, 0.9, S(130, 70, 230), 0.0),   # medalhoes / vitral do trono
}
for _k, _v in NEW_MATS.items():
    fm_lib.MATS.setdefault(_k, _v)

MARBLE, OBS, SILVER, IRON = "Stone_SG_MarbleBlack", "Stone_SG_Obsidian", "Metal_SG_Silver", "Metal_SG_BlackIron"
CLOTH, VIOST, RUNE, VGLOW = "Cloth_SG_Purple", "Stone_SG_Violet", "SG_Rune_Glow", "SG_VioletDeep_Glow"
VSOFT = "SG_VioletSoft_Glow"
CS, TR, VA, NI = "Stone_SG_Castle", "Stone_SG_Trim", "Slate_SGHallVault", "Slate_SGHallNiche"
VJ = "Slate_SGHallVaultJoint"
CAPL = CA.CAPL                      # remate perto do jogador (um valor abaixo do Stone_SG_Trim: 14.01)
ASH = CA.ASH                        # silhar
MOON, VGLASS = "Glass_SGHallMoon", "Glass_SGHallViolet"
IRONL = "Metal_SG_Iron"             # ferro um valor acima do negro (vasos, candeias: le volume)
WAX, FLAME = "Wax_SGHallCandle", "Lantern_Glow"

Z = L.HALL
X0, X1, Y0, Y1 = L.HALL_X0, L.HALL_X1, L.HALL_Y0, L.HALL_Y1
HALF_W = (X1 - X0) / 2.0                 # 42
CEIL_H = L.HALL_CEIL - Z                 # 28
MX0, MY0, MX1, MY1 = L.MINE_RECT

# ritmo da nave: vitrais no eixo das janelas da casca (4 por lado) e pilastras entre eles
WIN_Y = [Y0 + 16.0 + k * (Y1 - Y0 - 32.0) / 3.0 for k in range(4)]            # 60, 78.67, 97.33, 116
PIER_Y = [WIN_Y[0] - (WIN_Y[1] - WIN_Y[0]) / 2.0] + [(a + b) / 2.0 for a, b in zip(WIN_Y, WIN_Y[1:])] + \
         [WIN_Y[-1] + (WIN_Y[1] - WIN_Y[0]) / 2.0]                             # 50.67 ... 125.33
VAULT_Y = [Y0] + PIER_Y + [Y1]                                                   # linhas de apoio da abobada

SPRING = 20.0          # arranque das nervuras (topo dos capiteis)
ZC = CEIL_H - 0.1      # fecho da abobada (logo abaixo do teto colidivel da casca)
PIER_D = 3.0           # saliencia maxima das pilastras (x fica >= 38,8: fora da MINE_RECT, que vai ate 38)
PIER_HW = 2.0
GAL_H = 14.4           # piso da galeria alta (acima de piso+14: fora do alcance)
PF = 0.8               # face do paramento espesso (a casca fica em d = 0)
EMB_C = (0.0, PIER_Y[2])                         # centro do medalhao do piso (na faixa transversal do meio)
EMB_R = 6.4
MED = 9.4                                        # meia-aresta do quadrado do medalhao
RUN_HW = 2.0                                     # tapete (miolo roxo) - meia largura
RUN_EDGE = 2.2                                   # + filete de prata
RUN_OUT = 2.5                                    # + margem de obsidiana
DAIS_D = 3.1                                     # profundidade do estrado (y >= 128,9: fora da zona)

CAMS = {
    "CAM_SGHall_Door": ((0.0, Y0 + 2.0, Z + 7.0), (0.0, Y1, Z + 12.0), 18),
    "CAM_SGHall_FromThrone": ((0.0, Y1 - 5.5, Z + 8.0), (0.0, Y0, Z + 10.0), 18),
    "CAM_SGHall_Diag": ((X0 + 8.0, Y0 + 6.0, Z + 15.0), (22.0, 120.0, Z + 12.0), 18),
    "CAM_SGHall_Ceiling": ((0.0, 66.0, Z + 5.0), (0.0, 104.0, Z + 27.0), 16),
    "CAM_SGHall_Throne": ((6.0, 104.0, Z + 5.2), (0.0, Y1, Z + 11.0), 22),
    "CAM_SGHall_West": ((34.0, 90.0, Z + 8.0), (X0, 90.0, Z + 15.0), 18),
    "CAM_SGHall_East": ((-34.0, 82.0, Z + 8.0), (X1, 94.0, Z + 15.0), 18),
    "CAM_SGHall_PlayerMid": ((6.0, 72.0, Z + 5.2), (-4.0, Y1, Z + 9.0), 22),
    # OVERHAUL 04/05 (2026-09-29): closes na ALTURA DO JOGADOR (olho a 5,2), angulos de quem anda pelo salao
    "CAM_SGHall_OV_DoorIn": ((7.0, 60.0, Z + 5.2), (-1.0, Y0, Z + 9.0), 22),
    "CAM_SGHall_OV_DoorOut": ((2.5, 33.5, Z + 5.2), (-7.0, 42.5, Z + 7.5), 22),
    "CAM_SGHall_OV_Reveal": ((-3.0, 38.5, Z + 5.2), (8.0, 42.5, Z + 7.0), 20),
    "CAM_SGHall_OV_Pier": ((-31.0, 62.0, Z + 5.2), (-40.5, 69.3, Z + 9.0), 22),
    "CAM_SGHall_OV_Niche": ((-31.5, 84.0, Z + 5.2), (-42.0, 78.7, Z + 6.5), 22),
    "CAM_SGHall_OV_Gallery": ((27.0, 83.0, Z + 5.2), (41.0, 90.0, Z + 15.5), 22),
    "CAM_SGHall_OV_Window": ((18.0, 92.0, Z + 5.2), (42.0, 97.3, Z + 22.0), 22),
    "CAM_SGHall_OV_Chandelier": ((-6.0, 60.0, Z + 5.2), (-15.0, 69.3, Z + 19.5), 22),
    "CAM_SGHall_OV_Throne": ((5.0, 115.0, Z + 5.2), (0.0, Y1, Z + 6.5), 22),
    "CAM_SGHall_OV_Altar": ((-8.0, 117.0, Z + 5.2), (-16.4, 129.5, Z + 13.0), 22),
    "CAM_SGHall_OV_FloorEdge": ((35.0, 101.0, Z + 5.2), (41.8, 108.0, Z + 0.6), 22),
}

# rota extra: volta pela margem do salao (entre as pilastras e o miolo) - prova que as bases nao fecham a passagem
EXTRA_ROUTES = {
    "SALAO_VOLTA": ([(0.0, Y0 + 3.0), (-36.5, 56.0), (-36.5, 124.0), (36.5, 124.0), (36.5, 56.0), (0.0, Y0 + 3.0)], Z),
}
EXTRA_PROBES = []


# ------------------------------------------------------------------ referencial das paredes internas
# s = coordenada ao longo da parede (y nas laterais, x no norte/sul), d = distancia da face interna para dentro,
# h = altura acima do piso
def wp(side, s, d, h):
    if side == "W":
        return (X0 + d, s, Z + h)
    if side == "E":
        return (X1 - d, s, Z + h)
    if side == "S":
        return (s, Y0 + d, Z + h)
    return (s, Y1 - d, Z + h)


# o mesmo referencial no formato do kit de cantaria do sg_castle: W = (origem, u, normal); t = d (para DENTRO do salao)
WFR = {"W": ((X0, 0.0), (0.0, 1.0), (1.0, 0.0)), "E": ((X1, 0.0), (0.0, 1.0), (-1.0, 0.0)),
       "S": ((0.0, Y0), (1.0, 0.0), (0.0, 1.0)), "N": ((0.0, Y1), (1.0, 0.0), (0.0, -1.0))}
INW = {"W": (1.0, 0.0, 0.0), "E": (-1.0, 0.0, 0.0), "S": (0.0, 1.0, 0.0), "N": (0.0, -1.0, 0.0)}


def WT(side, t):
    """referencial da parede deslocado para o plano d = t"""
    W = WFR[side]
    return (CA._P(W, 0.0, t, 0.0)[:2], W[1], W[2])


def wbox(mb, side, s0, s1, d0, d1, h0, h1, m, bevel=0.0):
    mb.box2(wp(side, s0, d0, h0), wp(side, s1, d1, h1), m, bevel)


def wcol(area, side, s0, s1, d0, d1, h0, h1):
    a, b = wp(side, s0, d0, h0), wp(side, s1, d1, h1)
    col_box2(area, tuple(min(p, q) for p, q in zip(a, b)), tuple(max(p, q) for p, q in zip(a, b)))


def wcyl(mb, side, s, d, h0, h1, r, m, n=8, bevel=0.0):
    mb.cyl(r, h1 - h0, wp(side, s, d, (h0 + h1) / 2.0), m=m, n=n, bevel=bevel)


def wpoly(side, pts_sd):
    """poligono (s, d) da planta junto a parede -> (x, y) do mundo, anti-horario"""
    P = [wp(side, s, d, 0.0)[:2] for s, d in pts_sd]
    a = sum(P[i][0] * P[(i + 1) % len(P)][1] - P[(i + 1) % len(P)][0] * P[i][1] for i in range(len(P)))
    return P if a > 0 else list(reversed(P))


def rect_sd(s0, s1, d0, d1, ch=0.0):
    """retangulo (s, d) com as 2 quinas da FRENTE (d1) chanfradas em ch (as de tras ficam dentro da parede)"""
    if ch <= 0.0:
        return [(s0, d0), (s1, d0), (s1, d1), (s0, d1)]
    return [(s0, d0), (s1, d0), (s1, d1 - ch), (s1 - ch, d1), (s0 + ch, d1), (s0, d1 - ch)]


def wprism(mb, side, pts_sd, h0, h1, m, bevel=0.0):
    mb.prism(wpoly(side, pts_sd), Z + h0, Z + h1, m, bevel)


def wloft(mb, side, A, B, h0, h1, m):
    """solido entre o poligono A (s, d) em h0 e B em h1 (mesmo numero de pontos): talude, cavete, sino"""
    PA, PB = wpoly(side, A), wpoly(side, B)
    bm = mb.bm
    a = [bm.verts.new((x, y, Z + h0)) for x, y in PA]
    b = [bm.verts.new((x, y, Z + h1)) for x, y in PB]
    n = len(a)
    bm.faces.new(list(reversed(a)))
    bm.faces.new(b)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[i], a[j], b[j], b[i]))
    mb._post(a + b, m, None, 0, 1)


def mold(mb, side, pts_sh, t, prof, m):
    """MOLDURA varrida: perfil (a, b) ao longo da linha (s, h) no plano d = t; a > 0 aponta para o VAO (lado de dentro
    da linha), b sai da parede para o salao"""
    path = [wp(side, s, t, h) for s, h in pts_sh]
    up = INW[side]
    cs_ = sum(s for s, _ in pts_sh) / len(pts_sh)
    ch_ = sum(h for _, h in pts_sh) / len(pts_sh)
    c = wp(side, cs_, t, ch_)
    p0, p1 = path[0], path[1]
    tv = (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
    sv = (tv[1] * up[2] - tv[2] * up[1], tv[2] * up[0] - tv[0] * up[2], tv[0] * up[1] - tv[1] * up[0])
    if sum(a * (b - q) for a, b, q in zip(sv, c, p0)) < 0:
        path.reverse()
    mb.sweep(path, prof, m, True, None, up=up)


def arch_path(cs, hw, zs, zr, rise, d=0.0, n=6):
    """contorno de vao ogival (kit do castelo) em (s, h): perna esquerda de zs, arco, perna direita ate zs"""
    arc = CA.ogive(cs, hw, zr, rise, d=d, n=n)
    return [(cs - hw - d, zs)] + arc + [(cs + hw + d, zs)]


def _ogive_center(hw, rise):
    """centro (c, zc) e raio do arco DIREITO de um arco quebrado (ogiva) de meio vao hw e flecha rise. O centro fica
    sempre do lado oposto do eixo (c <= -0,25 hw): com flecha baixa ele desce abaixo do arranque (ogiva abatida),
    assim o fecho e sempre em ponta (nunca 'afunda' no meio)."""
    xc = (hw * hw - rise * rise) / (2.0 * hw)
    c = min(xc, -0.25 * hw)
    zc = (rise * rise - hw * hw + 2.0 * hw * c) / (2.0 * rise)
    R = math.hypot(hw - c, zc)
    return c, zc, R


def ogive_right(hw, rise, n):
    """meio arco ogival (lado direito) de (hw, 0) ate o fecho (0, rise)"""
    c, zc, R = _ogive_center(hw, rise)
    t0 = math.atan2(-zc, hw - c)
    ta = math.atan2(rise - zc, -c)
    pts = [(c + R * math.cos(t0 + (ta - t0) * k / n), zc + R * math.sin(t0 + (ta - t0) * k / n)) for k in range(n + 1)]
    pts[0] = (hw, 0.0)
    pts[-1] = (0.0, rise)
    return pts


def ogive(cs, hw, rise, spring, n=6):
    """arco ogival completo (arranque esquerdo -> fecho -> arranque direito) no plano da parede"""
    r = ogive_right(hw, rise, n)
    left = [(cs - u, spring + v) for u, v in r]
    right = [(cs + u, spring + v) for u, v in reversed(r)][1:]
    return left + right


def ogive_z(hw, rise, u):
    """altura do arco ogival (meio vao hw, flecha rise) a distancia |u| do eixo"""
    c, zc, R = _ogive_center(hw, rise)
    return max(0.0, zc + math.sqrt(max(0.0, R * R - (abs(u) - c) ** 2)))


def band(mb, side, inner, outer, d0, d1, m, closed=False):
    """faixa solida no plano da parede entre duas polilinhas (s, h) de mesmo tamanho (arquivolta, moldura, anel)"""
    bm = mb.bm
    n = len(inner)
    iF = [bm.verts.new(wp(side, s, d1, h)) for s, h in inner]
    iB = [bm.verts.new(wp(side, s, d0, h)) for s, h in inner]
    oF = [bm.verts.new(wp(side, s, d1, h)) for s, h in outer]
    oB = [bm.verts.new(wp(side, s, d0, h)) for s, h in outer]
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        j = (i + 1) % n
        bm.faces.new((oF[i], oF[j], iF[j], iF[i]))
        bm.faces.new((iB[i], iB[j], oB[j], oB[i]))
        bm.faces.new((iF[i], iF[j], iB[j], iB[i]))
        bm.faces.new((oB[i], oB[j], oF[j], oF[i]))
    if not closed:
        for k in (0, n - 1):
            bm.faces.new((iF[k], oF[k], oB[k], iB[k]))
    mb._post(iF + iB + oF + oB, m, None, 0, 1)


def slab(mb, side, pts, d0, d1, m):
    """placa no plano da parede a partir de um poligono (s, h) simples"""
    bm = mb.bm
    F = [bm.verts.new(wp(side, s, d1, h)) for s, h in pts]
    B = [bm.verts.new(wp(side, s, d0, h)) for s, h in pts]
    n = len(pts)
    bm.faces.new(F)
    bm.faces.new(list(reversed(B)))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((F[j], F[i], B[i], B[j]))
    mb._post(F + B, m, None, 0, 1)


def arch_band(mb, side, cs, hw, rise, spring, foot, t, d0, d1, m, n=6):
    """arquivolta ogival com as pernas ate 'foot' (vao interno hw, espessura t)"""
    inner = [(cs - hw, foot)] + ogive(cs, hw, rise, spring, n) + [(cs + hw, foot)]
    outer = [(cs - hw - t, foot)] + ogive(cs, hw + t, rise + t, spring, n) + [(cs + hw + t, foot)]
    band(mb, side, inner, outer, d0, d1, m)


def arch_panel(mb, side, cs, hw, rise, spring, foot, d0, d1, m, n=6):
    """miolo cheio de um arco ogival (vitral ou fundo de nicho)"""
    slab(mb, side, [(cs - hw, foot)] + ogive(cs, hw, rise, spring, n) + [(cs + hw, foot)], d0, d1, m)


def ring(mb, side, cs, ch, r0, r1, d0, d1, m, n=12):
    inner = [(cs + r0 * math.cos(2 * math.pi * k / n), ch + r0 * math.sin(2 * math.pi * k / n)) for k in range(n)]
    outer = [(cs + r1 * math.cos(2 * math.pi * k / n), ch + r1 * math.sin(2 * math.pi * k / n)) for k in range(n)]
    band(mb, side, inner, outer, d0, d1, m, closed=True)


def disk(mb, side, cs, ch, r, d0, d1, m, n=12):
    slab(mb, side, [(cs + r * math.cos(2 * math.pi * k / n), ch + r * math.sin(2 * math.pi * k / n)) for k in range(n)],
         d0, d1, m)


def s_curve(t0, t1, z0, z1, k=6):
    """perfil em S (gola) de (t0, z0) ate (t1, z1): misula, console"""
    out = []
    for i in range(k + 1):
        f = i / k
        g = f * f * (3.0 - 2.0 * f)
        out.append((t0 + (t1 - t0) * g, z0 + (z1 - z0) * f))
    return out


# ------------------------------------------------------------------ emblema DEITADO (piso e chave central)
def _ann(mb, cx, cy, r0, r1, z0, z1, m, n=32):
    """coroa circular horizontal (anel chato) entre r0 e r1"""
    bm = mb.bm
    ang = [2 * math.pi * k / n for k in range(n)]
    oT = [bm.verts.new((cx + r1 * math.cos(a), cy + r1 * math.sin(a), z1)) for a in ang]
    iT = [bm.verts.new((cx + r0 * math.cos(a), cy + r0 * math.sin(a), z1)) for a in ang]
    oB = [bm.verts.new((cx + r1 * math.cos(a), cy + r1 * math.sin(a), z0)) for a in ang]
    iB = [bm.verts.new((cx + r0 * math.cos(a), cy + r0 * math.sin(a), z0)) for a in ang]
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((oT[i], oT[j], iT[j], iT[i]))
        bm.faces.new((iB[i], iB[j], oB[j], oB[i]))
        bm.faces.new((oB[i], oB[j], oT[j], oT[i]))
        bm.faces.new((iT[i], iT[j], iB[j], iB[i]))
    mb._post(oT + iT + oB + iB, m, None, 0, 1)


def flat_emblem(mb, cx, cy, zf, r, sgn=1, rays=False, v=(0.0, 1.0), seg=None, glow=RUNE):
    """o emblema da ordem DEITADO e rente: piso (sgn=+1, face para cima em zf) ou chave do teto (sgn=-1, face para
    baixo). Geometria unica do sg_emblem (emblem_flat): sobe no maximo ~0,056 da superficie, fundos embutidos."""
    EM.emblem_flat(mb, mb, mb, (cx, cy, zf), math.atan2(v[1], v[0]), r, monumental=rays, up=sgn, glow=glow,
                   field=False, seg=seg)


def finish(mb, recalc=True):
    """mb.finish() + remove faces de area nula (o tubo do anel do sg_emblem, congelado, deixa quads de area zero)"""
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


# ------------------------------------------------------------------ KIT DE VELA (12.09) e remates de torno
def candle(mb, x, y, z, hc=0.6, s=1.0, dish=True, cup=False):
    """vela da ordem: prato de ferro (opcional) ou COPINHO de prata (bobeche), vela CREME QUENTE nao emissiva de
    altura hc, PAVIO de ferro e chama em GOTA (so ela e Neon; ~0,44 s de altura: le a 15 studs no Roblox).
    z = apoio. Devolve o topo da chama."""
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
    EM._lathe(mb, (x, y, zf), [(0.0, 0.0), (0.11 * s, 0.14 * s), (0.06 * s, 0.3 * s), (0.0, 0.44 * s)], FLAME, 6)
    return zf + 0.44 * s


def ball_finial(mb, x, y, z, r=0.2, m=SILVER, n=6):
    """remate em BOLA COM COLAR (torno): o remate baixo do kit (12.12), no lugar da piramide de 4 lados"""
    EM._lathe(mb, (x, y, z), [(r * 0.7, 0.0), (r * 0.42, r * 0.38), (r * 0.95, r * 0.95), (0.0, r * 1.9)], m, n,
              caps=(False, True))


# ------------------------------------------------------------------ piso
def _sub(rects, hole):
    """subtrai o retangulo 'hole' de cada retangulo (x0, y0, x1, y1) da lista"""
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


def floor():
    """marmore negro com topo EXATO em HALL (so visual: a colisao e do sg_col). Particao SEM sobreposicao coplanar:
    borda de obsidiana, filete de prata no contorno da zona, faixas de obsidiana com filete de prata no ritmo das
    pilastras, medalhao (quadrado de obsidiana -> aro de prata -> campo do emblema) e o tapete roxo (rente, +0,04)."""
    mb = MB("SG_Hall_Floor", "03_MINING_HALL", random.Random(301), detail="near")
    zt, zb = Z, Z - 0.4
    ecx, ecy = EMB_C
    FW = 0.25                                           # filete do contorno
    outer = (MX0 - FW, MY0 - FW, MX1 + FW, MY1 + FW)
    holes = [(-RUN_OUT, Y0, RUN_OUT, ecy - MED), (-RUN_OUT, ecy + MED, RUN_OUT, Y1 - DAIS_D),
             (ecx - MED, ecy - MED, ecx + MED, ecy + MED)]
    groups = {MARBLE: [], OBS: [], SILVER: []}
    groups[OBS] += [(X0, Y0, X1, outer[1]), (X0, outer[3], X1, Y1), (X0, outer[1], outer[0], outer[3]),
                    (outer[2], outer[1], X1, outer[3])]
    groups[SILVER] += [(outer[0], outer[1], outer[2], MY0), (outer[0], MY1, outer[2], outer[3]),
                       (outer[0], MY0, MX0, MY1), (MX1, MY0, outer[2], MY1)]
    BH, BS = 0.5, 0.1                                   # meia largura da faixa / do filete de prata central
    TY = PIER_Y[1:-1]
    LX = [-25.5, -12.5, 12.5, 25.5]
    for y in TY:
        groups[OBS] += [(MX0, y - BH, MX1, y - BS), (MX0, y + BS, MX1, y + BH)]
        groups[SILVER].append((MX0, y - BS, MX1, y + BS))
    ybr = [MY0] + [v for y in TY for v in (y - BH, y + BH)] + [MY1]
    for x in LX:
        for k in range(0, len(ybr), 2):
            ya, yb = ybr[k], ybr[k + 1]
            groups[OBS] += [(x - BH, ya, x - BS, yb), (x + BS, ya, x + BH, yb)]
            groups[SILVER].append((x - BS, ya, x + BS, yb))
    xbr = [MX0] + [v for x in LX for v in (x - BH, x + BH)] + [MX1]
    for i in range(0, len(xbr), 2):
        for k in range(0, len(ybr), 2):
            groups[MARBLE].append((xbr[i], ybr[k], xbr[i + 1], ybr[k + 1]))
    for m, rects in groups.items():
        for h in holes:
            rects = _sub(rects, h)
        for x0, y0, x1, y1 in rects:
            if x1 - x0 > 0.01 and y1 - y0 > 0.01:
                mb.box2((x0, y0, zb), (x1, y1, zt), m, 0.0)
    for ya, yb in ((Y0, ecy - MED), (ecy + MED, Y1 - DAIS_D)):
        for s in (-1, 1):
            mb.box2((s * RUN_EDGE, ya, zb), (s * RUN_OUT, yb, zt), OBS, 0.0)
            mb.box2((s * RUN_HW, ya, zb), (s * RUN_EDGE, yb, zt + 0.035), SILVER, 0.0)
        mb.box2((-RUN_HW, ya, zb), (RUN_HW, yb, zt + 0.04), CLOTH, 0.0)
    for y in TY:
        for x in LX:
            q = 0.75
            mb.prism([(x, y - q), (x + q, y), (x, y + q), (x - q, y)], zt - 0.05, zt + 0.03, SILVER)
    n = 32
    ang = [2 * math.pi * k / n for k in range(n)]
    R0, R1 = 8.6, 8.3
    sq = [(ecx + MED * math.cos(a) / max(abs(math.cos(a)), abs(math.sin(a))),
           ecy + MED * math.sin(a) / max(abs(math.cos(a)), abs(math.sin(a)))) for a in ang]
    circ = lambda r: [(ecx + r * math.cos(a), ecy + r * math.sin(a)) for a in ang]
    bm = mb.bm
    for outer_p, inner_p, m in ((sq, circ(R0), OBS), (circ(R0), circ(R1), SILVER)):
        oT = [bm.verts.new((x, y, zt)) for x, y in outer_p]
        iT = [bm.verts.new((x, y, zt)) for x, y in inner_p]
        oB = [bm.verts.new((x, y, zb)) for x, y in outer_p]
        iB = [bm.verts.new((x, y, zb)) for x, y in inner_p]
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((oT[i], oT[j], iT[j], iT[i]))
            bm.faces.new((iB[i], iB[j], oB[j], oB[i]))
            bm.faces.new((oB[i], oB[j], oT[j], oT[i]))
            bm.faces.new((iT[i], iT[j], iB[j], iB[i]))
        mb._post(oT + iT + oB + iB, m, None, 0, 1)
    mb.prism(circ(R1), zb, zt, OBS)
    flat_emblem(mb, ecx, ecy, zt, EMB_R * 0.97, 1, rays=True, glow=VSOFT)
    finish(mb)


# ------------------------------------------------------------------ pilastras compostas (salao e retabulo)
def pier_stack(mb, side, s, core_hw, core_d, plinth_hw, plinth_d, top, shafts, collar=False, impost=True,
               shaft_m=MARBLE):
    """pilastra composta (05.03): soco de obsidiana em TALUDE, faixa de remate, nucleo de quinas CHANFRADAS, colunelos
    com BASE de torno (plinto, toro, escocia), colar da galeria, CAPITEL = anel de pedra violeta + cavete + abaco
    chanfrado, e o impost onde nascem as nervuras. shafts = [(ds, d, r)] (ds ao longo da parede)."""
    hb = 1.05
    wprism(mb, side, rect_sd(s - plinth_hw, s + plinth_hw, -0.4, plinth_d, 0.3), 0.0, hb, OBS, 0.06)
    wloft(mb, side, rect_sd(s - plinth_hw, s + plinth_hw, -0.4, plinth_d, 0.3),
          rect_sd(s - plinth_hw + 0.25, s + plinth_hw - 0.25, -0.4, plinth_d - 0.25, 0.3), hb, hb + 0.3, OBS)
    wprism(mb, side, rect_sd(s - plinth_hw + 0.2, s + plinth_hw - 0.2, -0.4, plinth_d - 0.2, 0.25), hb + 0.3,
           hb + 0.55, CAPL, 0.05)
    z0 = hb + 0.55
    zc = top - 1.3
    wprism(mb, side, rect_sd(s - core_hw, s + core_hw, -0.4, core_d, 0.3), z0, zc, CS)
    env_s = max(abs(ds) + r for ds, d, r in shafts) + 0.08
    env_d = max(d + r for ds, d, r in shafts) + 0.08
    for ds, d, r in shafts:
        c = wp(side, s + ds, d, z0)
        nn = 8 if r > 0.82 else 6
        EM._lathe(mb, c, [(r + 0.16, 0.0), (r + 0.16, 0.12), (r + 0.06, 0.24), (r + 0.11, 0.36), (r, 0.5)], CAPL, nn,
                  math.pi / nn, caps=(False, True))
        mb.cyl(r, zc - z0 - 0.5, wp(side, s + ds, d, (z0 + 0.5 + zc) / 2.0), m=shaft_m, n=nn, bevel=0.0, caps=False,
               rot=(0, 0, math.pi / nn))
    if collar:
        wprism(mb, side, rect_sd(s - env_s - 0.05, s + env_s + 0.05, -0.4, env_d + 0.1, 0.35), GAL_H - 0.6,
               GAL_H + 0.4, OBS, 0.06)
    # capitel: anel (astragalo) de pedra violeta SEM brilho, cavete (sino) e abaco chanfrado
    A0 = rect_sd(s - env_s, s + env_s, -0.4, env_d, 0.35)
    wprism(mb, side, rect_sd(s - env_s - 0.06, s + env_s + 0.06, -0.4, env_d + 0.06, 0.38), zc, zc + 0.25, VIOST)
    wloft(mb, side, A0, rect_sd(s - env_s - 0.42, s + env_s + 0.42, -0.4, env_d + 0.42, 0.45), zc + 0.25, zc + 0.95, TR)
    wprism(mb, side, rect_sd(s - env_s - 0.5, s + env_s + 0.5, -0.4, env_d + 0.5, 0.3), zc + 0.95, top, TR, 0.06)
    if impost:
        wprism(mb, side, rect_sd(s - PIER_HW - 0.2, s + PIER_HW + 0.2, -0.4, PIER_D + 0.3, 0.3), top, top + 1.1, TR,
               0.1)


HALL_SHAFTS = [(0.0, 2.1, 0.85), (-1.75, 0.55, 0.45), (1.75, 0.55, 0.45)]


def corner_pier(mb, side, s, corner):
    """pilar de canto (ocupa o canto das duas paredes): corner = sinal da parede transversal (+1 = sul)"""
    a = s + corner * 2.4
    s0, s1 = min(s, a), max(s, a)
    wprism(mb, side, rect_sd(s0, s1, -0.4, 2.8, 0.25), 0.0, 1.05, OBS, 0.06)
    wloft(mb, side, rect_sd(s0, s1, -0.4, 2.8, 0.25), rect_sd(s0, s1, -0.4, 2.55, 0.25), 1.05, 1.35, OBS)
    wprism(mb, side, rect_sd(s0, s1, -0.4, 2.2, 0.25), 1.35, SPRING - 1.3, CS)
    wprism(mb, side, rect_sd(s0, s1, -0.4, 2.3, 0.3), SPRING - 1.3, SPRING - 1.05, VIOST)
    wloft(mb, side, rect_sd(s0, s1, -0.4, 2.25, 0.3), rect_sd(s0, s1, -0.4, 2.6, 0.35), SPRING - 1.05, SPRING - 0.35, TR)
    wprism(mb, side, rect_sd(s0, s1, -0.4, 2.7, 0.3), SPRING - 0.35, SPRING + 1.1, TR, 0.1)
    wcol("SG_HallPier", side, s0, s1, 0.0, 2.8, -0.5, SPRING)


# ------------------------------------------------------------------ paredes: paramento, nichos, galeria
def _block_open(mb, W, u0, u1, z0, z1, t0, t1, ch, m):
    """bloco de cantaria do kit (face da frente recuada 'ch' nas 4 arestas) SEM a face de tras: ela encosta no
    paramento e nunca aparece (orcamento)"""
    bm = mb.bm
    ch = min(ch, (u1 - u0) * 0.3, (z1 - z0) * 0.3)
    back = [bm.verts.new(CA._P(W, u, t0, z)) for u, z in ((u0, z0), (u1, z0), (u1, z1), (u0, z1))]
    fr = [bm.verts.new(CA._P(W, u, t1, z)) for u, z in ((u0 + ch, z0 + ch), (u1 - ch, z0 + ch), (u1 - ch, z1 - ch),
                                                        (u0 + ch, z1 - ch))]
    fs = [bm.faces.new(list(reversed(fr)))]
    for i in range(4):
        j = (i + 1) % 4
        fs.append(bm.faces.new((back[i], fr[i], fr[j], back[j])))
    for f in fs:
        f.normal_update()
    # a face da frente aponta para o salao (+t)
    n = CA._P(W, 0.0, 1.0, 0.0)
    o = CA._P(W, 0.0, 0.0, 0.0)
    if fs[0].normal.x * (n[0] - o[0]) + fs[0].normal.y * (n[1] - o[1]) < 0:
        for f in fs:
            f.normal_flip()
    mb._post(back + fr, m, None, 0, 1)


def ashlar(mb, W, u0, u1, z0, z1, excl=(), m=ASH, PL=3.3, dep=0.12, ch=0.07, phase=0.0, gap=0.08, hs=CA.COURSES):
    """o SILHAR do kit do castelo (CA.ashlar: fiadas de 2 alturas, juntas desencontradas, recorte nos vaos) com o
    bloco aberto atras"""
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
            rects = CA._cut(rects, *e)
        off = phase + (k % 2) * PL * 0.5
        for a, b, ra, rb in rects:
            cuts = [a] + [u0 + off + PL * j for j in range(-1, int((u1 - u0) / PL) + 3)
                          if a + 0.7 < u0 + off + PL * j < b - 0.7] + [b]
            for c0, c1 in zip(cuts, cuts[1:]):
                p0 = c0 + (gap / 2 if c0 > a else 0.0)
                p1 = c1 - (gap / 2 if c1 < b else 0.0)
                if p1 - p0 > 0.2 and rb - ra > 0.2:
                    _block_open(mb, W, p0, p1, ra, rb, -0.03, dep, ch, m)
        zz += h
        k += 1

NICHE_HW, NICHE_ZS, NICHE_ZR, NICHE_RISE = 3.4, 1.6, 7.0, 4.2
M1_W, M2_W = 0.56, 0.4                   # largura da moldura interna / da externa (moldura dupla)
PROF_M1 = [(0.06, -0.02), (0.06, 0.24), (-0.1, 0.46), (-0.34, 0.3), (-0.5, 0.34), (-0.56, -0.02)]                                       # toro no vao, cavete, filete
PROF_M2 = [(0.0, -0.02), (0.0, 0.16), (-0.1, 0.26), (-0.4, 0.26), (-0.4, -0.02)]
CORD_Z = NICHE_ZR                        # cordao com pingadeira no ARRANQUE dos arcos dos nichos (topo do silhar)
S_NICHES, N_NICHES = (18.5, 30.5), (24.6, 34.0)


def niche_ext(double):
    return NICHE_HW + M1_W + (M2_W if double else 0.0)


def niche(mb, side, cs, kind, double, iw):
    """NICHO (05.01): recuo real no paramento espesso (fundo liso escuro em d 0,15), peitoril de remate, moldura varrida
    (dupla no eixo dos vitrais) e fecho de obsidiana. kind 'A' = misula + candeia de 3 velas; 'B' = prateleira de pedra
    com vaso de ferro."""
    W = WFR[side]
    hw, zs, zr, rise = NICHE_HW, NICHE_ZS, NICHE_ZR, NICHE_RISE
    arc = CA.ogive(cs, hw + 0.03, Z + zr, rise)
    CA.panel(mb, W, [(cs - hw - 0.03, Z + zs - 0.02), (cs + hw + 0.03, Z + zs - 0.02)] + list(reversed(arc)), 0.02,
             0.15, NI)
    # peitoril (o piso do nicho) com chanfro por baixo; as pontas entram no paramento
    CA.ledge(mb, W, cs - hw - 0.35, cs + hw + 0.35, [(0.1, Z + zs - 0.42), (PF + 0.22, Z + zs - 0.42),
                                                     (PF + 0.45, Z + zs - 0.2), (PF + 0.45, Z + zs), (0.1, Z + zs)],
             CAPL)
    mold(mb, side, [(u, z - Z) for u, z in arch_path(cs, hw, Z + zs, Z + zr, rise, n=4)], PF, PROF_M1, CAPL)
    apex = Z + zr + rise
    if double:
        mold(mb, side, [(u, z - Z) for u, z in arch_path(cs, hw, Z + zs, Z + zr, rise, d=M1_W, n=4)], PF, PROF_M2,
             VIOST)
    ka = 0.36 if not double else 0.42
    CA.block(mb, W, cs - ka, cs + ka, apex - 0.2, apex + M1_W + (M2_W if double else 0.0) + 0.35, PF - 0.1, PF + 0.62,
             0.08, OBS)
    if kind == "A":
        # MISULA de pedra em perfil S + abaco, com a CANDEIA de ferro de 3 velas (alturas dirigidas: alta no meio)
        zt = Z + 3.9
        prof = [(0.1, zt - 1.0)] + s_curve(0.34, 1.02, zt - 1.0, zt - 0.02, 4) + [(1.02, zt), (0.1, zt)]
        CA.ledge(mb, W, cs - 0.5, cs + 0.5, prof, CAPL)
        CA.ledge(mb, W, cs - 0.64, cs + 0.64, [(0.1, zt), (1.14, zt), (1.14, zt + 0.16), (0.1, zt + 0.16)], CAPL)
        c = CA._P(W, cs, 0.64, zt + 0.16)
        EM._lathe(iw, c, [(0.14, 0.0), (0.46, 0.06), (0.47, 0.12), (0.4, 0.12), (0.0, 0.08)], IRONL, 6,
                  caps=(True, False))
        for du, hc in ((-0.26, 0.5), (0.0, 0.78), (0.26, 0.5)):
            p = CA._P(W, cs + du, 0.64, zt + 0.24)
            candle(iw, p[0], p[1], p[2], hc, 1.15, dish=False)
    else:
        # PRATELEIRA de pedra engastada nos lados do recuo, sobre 2 misulas pequenas, e o VASO de ferro
        zt = Z + 3.2
        CA.ledge(mb, W, cs - hw - 0.02, cs + hw + 0.02, [(0.1, zt - 0.24), (0.9, zt - 0.24), (1.02, zt - 0.14),
                                                         (1.02, zt), (0.1, zt)], CAPL)
        c = CA._P(W, cs, 0.56, zt)
        vs = 1.3                                        # vaso na escala do nicho (1,9 de altura)
        EM._lathe(iw, c, [(r * vs, h * vs) for r, h in ((0.26, 0.0), (0.16, 0.2), (0.36, 0.5), (0.41, 0.8),
                                                         (0.18, 1.25), (0.29, 1.44), (0.0, 1.4))], IRONL, 7,
                  caps=(True, False))
        EM._lathe(iw, c, [(r * vs, h * vs) for r, h in ((0.37, 0.5), (0.42, 0.6), (0.37, 0.7))], SILVER, 7, closed=True)
        for k in (-1, 1):
            pts = [CA._P(W, cs + k * u * vs, 0.56, zt + zz * vs) for u, zz in ((0.26, 1.14), (0.52, 1.18), (0.56, 0.94),
                                                                                (0.4, 0.74))]
            iw.tube(pts, 0.055, IRONL, 4)
        # ARANDELA quente no fundo do nicho, acima do vaso (o nicho B tambem tem luz): espelho de ferro, braco curvo,
        # copinho de prata e vela do kit
        za = zt + 2.75
        a0, a1 = CA._P(W, cs, 0.13, za - 0.2), CA._P(W, cs, 0.24, za - 0.2)
        iw.rod(a0, a1, 0.34, IRONL, 6)
        iw.rod(CA._P(W, cs, 0.24, za - 0.2), CA._P(W, cs, 0.27, za - 0.2), 0.2, SILVER, 6)
        iw.tube([CA._P(W, cs, 0.26, za - 0.35), CA._P(W, cs, 0.55, za - 0.5), CA._P(W, cs, 0.78, za - 0.3),
                 CA._P(W, cs, 0.82, za - 0.02)], 0.06, IRONL, 4)
        c = CA._P(W, cs, 0.82, za)
        candle(iw, c[0], c[1], c[2], 0.55, 1.15, dish=False, cup=True)


def bay_wall(mb, side, sa, sb, niches, top, iw):
    """paramento ESPESSO de sa a sb (d 0..PF) com os recuos dos nichos, silhar em fiadas ate o cordao, cordao com
    pingadeira, rodape em talude. niches = [(cs, kind, double)]"""
    W = WFR[side]
    opens = [(cs, NICHE_HW, Z + NICHE_ZS, Z + NICHE_ZR, NICHE_RISE) for cs, _, _ in niches]
    CA.wall_run(mb, W, sa, sb, Z + 0.9, Z + top, 0.0, PF, opens, CS)
    excl = [(cs - niche_ext(dbl) - 0.02, cs + niche_ext(dbl) + 0.02, Z, Z + 30.0) for cs, _, dbl in niches]
    ashlar(mb, WT(side, PF), sa, sb, Z + 1.0, Z + CORD_Z - 0.34, excl, PL=4.0, phase=(sa * 0.37) % 1.3)
    # cordao: corre entre as molduras (morre nelas)
    cuts = [sa] + [v for cs, _, dbl in sorted(niches) for v in (cs - niche_ext(dbl), cs + niche_ext(dbl))] + [sb]
    for a, b in zip(cuts[0::2], cuts[1::2]):
        if b - a > 0.3:
            CA.ledge(mb, WT(side, PF), a, b, CA.drip(Z + CORD_Z, 0.36, 0.5), OBS)
    CA.ledge(mb, W, sa, sb, CA.plinth(Z - 0.05, Z + 0.95, PF + 0.3, PF + 0.12), OBS)
    for cs, kind, dbl in niches:
        niche(mb, side, cs, kind, dbl, iw)


def gallery(mb, side, sa, sb, corbels, rail="iron"):
    """GALERIA ALTA (05.04): laje de obsidiana com FOCINHO boleado, cornija em cavete, misulas em perfil S, fundo liso
    escuro. rail='iron' (lados dos vitrais): grade de barras redondas com roseta a cada 3, corrimao boleado de prata,
    montantes com remate em bola; rail='stone' (paredes de fundo): PARAPEITO de pedra com paineis cegos e capa
    moldurada (hierarquia: a grade leve fica com os vitrais)"""
    W = WFR[side]
    g = Z + GAL_H
    CA.ledge(mb, W, sa, sb, [(-0.3, g), (2.3, g), (2.52, g + 0.12), (2.6, g + 0.38), (2.52, g + 0.64),
                             (2.35, g + 0.8), (-0.3, g + 0.8)], OBS)
    CA.ledge(mb, W, sa, sb, [(PF - 0.1, g - 0.62), (PF + 0.12, g - 0.62)] + s_curve(PF + 0.12, 1.6, g - 0.62, g, 4)[1:] +
             [(PF - 0.1, g)], OBS)
    wbox(mb, side, sa, sb, 0.0, 0.1, GAL_H + 0.8, GAL_H + 3.0, NI, 0.0)
    for c in corbels:
        prof = [(PF - 0.1, g - 2.5)] + s_curve(PF + 0.1, 2.2, g - 2.5, g - 0.3, 4) + [(2.2, g - 0.02),
                                                                                      (PF - 0.1, g - 0.02)]
        CA.ledge(mb, W, c - 0.42, c + 0.42, prof, OBS)
    if rail == "stone":
        CA.ledge(mb, W, sa, sb, [(2.05, g + 0.78), (2.45, g + 0.78), (2.45, g + 1.9), (2.05, g + 1.9)], CS)
        CA.ledge(mb, W, sa - 0.02, sb + 0.02, [(1.95, g + 1.88), (2.52, g + 1.88), (2.62, g + 1.98), (2.58, g + 2.12),
                                               (1.95, g + 2.12)], TR)
        npn = max(2, int(round((sb - sa) / 3.2)))
        pw = (sb - sa) / npn
        for i in range(npn):
            CA.block(mb, W, sa + i * pw + 0.35, sa + (i + 1) * pw - 0.35, g + 1.0, g + 1.7, 2.43, 2.53, 0.05, CS)
        return
    # grade: travessa de baixo, barras redondas, rosetas a cada 3, corrimao boleado
    CA.ledge(mb, W, sa, sb, [(2.22, g + 0.8), (2.48, g + 0.8), (2.48, g + 1.02), (2.22, g + 1.02)], IRON)
    hr = g + 2.7
    CA.ledge(mb, W, sa - 0.08, sb + 0.08, [(2.12, hr - 0.02), (2.58, hr - 0.02), (2.63, hr + 0.1), (2.52, hr + 0.24),
                                           (2.35, hr + 0.28), (2.18, hr + 0.24), (2.07, hr + 0.1)], SILVER)
    L_ = sb - sa - 0.9
    nb = max(4, int(round(L_ / 1.4)))
    posts = {0, nb, nb // 2}
    for q in range(nb + 1):
        s = sa + 0.45 + q * L_ / nb
        if q in posts:
            wprism(mb, side, rect_sd(s - 0.17, s + 0.17, 2.18, 2.52), GAL_H + 0.8, GAL_H + 2.7, IRON)
            c = wp(side, s, 2.35, GAL_H + 2.98)
            ball_finial(mb, c[0], c[1], c[2], 0.2, SILVER)
            continue
        mb.rod(wp(side, s, 2.35, GAL_H + 1.0), wp(side, s, 2.35, GAL_H + 2.7), 0.085, IRON, 6, caps=False)
        if q % 3 == 0:
            a, b = wp(side, s, 2.27, GAL_H + 1.85), wp(side, s, 2.43, GAL_H + 1.85)
            mb.rod(a, b, 0.2, SILVER, 6)


def walls(iw):
    wl = MB("SG_Hall_Walls", "03_MINING_HALL", random.Random(313), detail="near")
    mb = wl                                   # pilastras e paramento no MESMO objeto (MeshParts)
    for side in ("W", "E"):
        for y in PIER_Y:
            pier_stack(mb, side, y, 1.5, 2.0, PIER_HW + 0.35, PIER_D + 0.25, SPRING, HALL_SHAFTS, collar=True)
            wcol("SG_HallPier", side, y - PIER_HW - 0.35, y + PIER_HW + 0.35, 0.0, PIER_D + 0.25, -0.5, SPRING)
        corner_pier(mb, side, Y0, 1)
        corner_pier(mb, side, Y1, -1)
        bays = [(Y0 + 2.4, PIER_Y[0] - PIER_HW - 0.35)] + \
               [(a + PIER_HW + 0.35, b - PIER_HW - 0.35) for a, b in zip(PIER_Y, PIER_Y[1:])] + \
               [(PIER_Y[-1] + PIER_HW + 0.35, Y1 - 2.4)]
        kinds = ["A", "B", "B", "A"]            # ritmo dirigido: honra nas pontas (porta / altar), vaso no miolo
        for bi, (sa, sb) in enumerate(bays):
            cs = (sa + sb) / 2.0
            if sb - sa > 8.0:
                bay_wall(wl, side, sa, sb, [(cs, kinds[bi - 1], True)], GAL_H, iw)
                gallery(wl, side, sa, sb, (cs - 4.6, cs + 4.6))
                # acima da galeria: paramento dos dois lados do vitral ate o formeiro
                wc = WIN_Y[min(range(4), key=lambda i: abs(WIN_Y[i] - cs))]
                for a, b in ((sa, wc - 3.6), (wc + 3.6, sb)):
                    slab(wl, side, _curve_top(side, a, b, lambda s: zf(s) - 0.05, GAL_H + 3.0), 0.0, 0.1, CS)
            else:
                # tramo estreito das pontas: paramento espesso + silhar ate o cordao, pano liso ate o formeiro
                bay_wall(wl, side, sa, sb, [], CORD_Z + 0.4, iw)
                slab(wl, side, _curve_top(side, sa, sb, lambda s: zf(s) - 0.05, CORD_Z + 0.4, 3), 0.0, 0.1, CS)
    # parede sul: paramento espesso com os nichos, galeria (a moldura interna da porta e do portal())
    dw = L.HALL_DOOR_W / 2.0
    endwall = lambda s: SPRING + (ZC - SPRING) * math.sqrt(max(0.0, 1.0 - (s / HALF_W) ** 2)) - 0.05
    for k in (-1, 1):
        a, b = sorted((k * (dw + 1.6), k * (HALF_W - 2.4)))
        bay_wall(wl, "S", a, b, [(k * S_NICHES[0], "A", False), (k * S_NICHES[1], "B", False)], GAL_H, iw)
        slab(wl, "S", _curve_top("S", a, b, endwall, GAL_H + 3.0, 6), 0.0, 0.1, CS)
        gallery(wl, "S", a, b, [k * c for c in (13.0, 24.5, 36.0)], rail="stone")
    slab(wl, "S", _curve_top("S", -dw - 1.6, dw + 1.6, endwall, L.HALL_DOOR_H + 1.4, 4), 0.0, 0.1, CS)
    # parede norte: paramento espesso fora do altar
    for k in (-1, 1):
        a, b = sorted((k * 18.8, k * (HALF_W - 2.4)))
        bay_wall(wl, "N", a, b, [(k * N_NICHES[0], "A", False), (k * N_NICHES[1], "B", False)], GAL_H, iw)
        gallery(wl, "N", a + (0.4 if k > 0 else 0.0), b - (0.4 if k < 0 else 0.0), [k * c for c in (19.9, 29.3, 38.6)],
                rail="stone")
        slab(wl, "N", _curve_top("N", a, b, endwall, GAL_H + 3.0, 6), 0.0, 0.1, CS)
    slab(wl, "N", _curve_top("N", -18.8, 18.8, endwall, 0.9, 6), 0.0, 0.1, CS)
    finish(wl)


def _curve_top(side, s0, s1, top_fn, h0, k=5):
    """poligono convexo (s, h): base reta em h0 e topo seguindo a curva top_fn(s) de s0 a s1"""
    pts = [(s0, h0), (s1, h0)]
    for i in range(k + 1):
        s = s1 + (s0 - s1) * i / k
        pts.append((s, top_fn(s)))
    return pts


# ------------------------------------------------------------------ portal (lado de dentro da porta principal)
PROF_DOOR = [(0.1, -0.02), (0.1, 0.34), (0.0, 0.56), (-0.2, 0.66), (-0.42, 0.56), (-0.52, 0.4), (-0.72, 0.46),
             (-0.78, -0.02)]


def portal(mb):
    """a porta vista de DENTRO (04.01): ombreiras de remate com soco em talude e COLUNELO violeta de torno (base atica
    e capitel em cesto, os mesmos perfis do porche), verga moldurada, arquivolta VARRIDA (toro + cavete) e faixa
    violeta. As folhas dobradas no vao, as dobradicas e o intradorso em caixotoes sao do sg_castle."""
    dw = L.HALL_DOOR_W / 2.0
    dh = L.HALL_DOOR_H
    base_prof = [(0.62, 0.0), (0.62, 0.1), (0.54, 0.2), (0.58, 0.3), (0.46, 0.42), (0.42, 0.5), (0.46, 0.56),
                 (0.5, 0.62), (0.4, 0.74)]
    cap_prof = [(0.4, 0.0), (0.47, 0.07), (0.4, 0.15), (0.44, 0.35), (0.56, 0.6), (0.66, 0.74)]
    for k in (-1, 1):
        a, b = sorted((k * dw, k * (dw + 1.6)))
        wbox(mb, "S", a, b, -0.1, 1.35, 0.0, 1.2, OBS, 0.08)
        wloft(mb, "S", rect_sd(a, b, -0.1, 1.35), rect_sd(a + (0.0 if k > 0 else 0.0), b, -0.1, 1.2), 1.2, 1.45, OBS)
        wbox(mb, "S", a, b, 0.0, 1.2, 1.45, dh, CAPL, 0.08)
        wcol("SG_HallDoor", "S", a, b, 0.0, 1.35, -0.5, dh)
        # colunelo violeta na quina do vao (casa com os do porche)
        cx = k * (dw + 0.32)
        c0 = wp("S", cx, 1.2, 1.45)
        sc = 0.62
        EM._lathe(mb, c0, [(r * sc, h * sc) for r, h in base_prof], CAPL, 8, 0.0)
        z1 = dh - 1.1
        mb.cyl(0.4 * sc, z1 - (1.45 + 0.74 * sc), wp("S", cx, 1.2, (1.45 + 0.74 * sc + z1) / 2.0), m=VIOST, n=8,
               bevel=0.0, caps=False)
        EM._lathe(mb, wp("S", cx, 1.2, z1), [(r * sc, h * sc) for r, h in cap_prof], CAPL, 8, 0.0)
        wbox(mb, "S", cx - 0.45, cx + 0.45, 0.75, 1.65, z1 + 0.46, z1 + 0.62, CAPL, 0.04)
    # verga moldurada (abaco, filete, gola) e o timpano liso acima (paramento do walls)
    CA.ledge(mb, WFR["S"], -dw - 1.75, dw + 1.75, [(-0.1, Z + dh), (1.45, Z + dh), (1.45, Z + dh + 0.22),
                                                    (1.25, Z + dh + 0.36), (1.25, Z + dh + 0.95), (1.5, Z + dh + 1.15),
                                                    (1.5, Z + dh + 1.4), (-0.1, Z + dh + 1.4)], OBS)
    pts = [(-(dw + 1.0), dh + 1.4)] + ogive(0.0, dw + 1.0, 5.2, dh + 1.4, 8) + [(dw + 1.0, dh + 1.4)]
    mold(mb, "S", pts, 0.1, PROF_DOOR, TR)
    arch_band(mb, "S", 0.0, dw + 1.85, 6.05, dh + 1.4, dh + 1.4, 0.45, 0.0, 0.5, VIOST)


# ------------------------------------------------------------------ vitrais (lado de dentro das janelas altas)
WIN_A, WIN_SILL, WIN_SPRING, WIN_RISE = 3.0, GAL_H + 3.2, 21.8, 3.9      # = sg_castle (vao 6 x 12 na casca)
G_T = -1.05                                                              # vidro RECUADO no vao da casca


def lancet(mb, side, cs, a=WIN_A, zs=WIN_SILL, zr=WIN_SPRING, rise=WIN_RISE, med=(2.3, 0.8)):
    """vitral (janela = moldura + recuo + vidro + luz): o vidro de luar fica 1 stud DENTRO do vao da casca, chumbo e
    rendilhado de remate na frente dele, moldura ogival de cantaria na face e peitoril em talude."""
    W = WFR[side]
    arc = CA.ogive(cs, a - 0.01, Z + zr, rise)
    CA.panel(mb, W, [(cs - a + 0.01, Z + zs), (cs + a - 0.01, Z + zs)] + list(reversed(arc)), G_T - 0.12, G_T, MOON)
    tf = G_T
    # chumbo: travessas finas + rendilhado (mainel, 2 subarcos e oculo com medalhao violeta)
    h = zs + 1.7
    while h < zr - 0.5:
        CA.panel(mb, W, CA.rect(cs - a, cs + a, Z + h - 0.06, Z + h + 0.06), tf, tf + 0.08, IRON)
        h += 1.7
    CA.panel(mb, W, CA.rect(cs - 0.17, cs + 0.17, Z + zs, Z + zr + 0.6), tf, tf + 0.42, TR)
    sub = (a - 0.17) / 2.0
    for k in (-1, 1):
        uc = cs + k * (0.17 + sub)
        i0 = CA.ogive(uc, sub - 0.24, Z + zr - 0.3, 1.9, n=4)
        i1 = CA.ogive(uc, sub - 0.24, Z + zr - 0.3, 1.9, d=0.24, n=4)
        CA.panel(mb, W, i0 + list(reversed(i1)), tf, tf + 0.4, TR)
        for s in (-1, 1):
            u0, u1 = sorted((uc + s * (sub - 0.24), uc + s * sub))
            CA.panel(mb, W, CA.rect(u0, u1, Z + zs, Z + zr - 0.3), tf, tf + 0.4, TR)
    if med:
        dh, r = med
        disk(mb, side, cs, zr + dh, r, tf - 0.04, tf + 0.06, VGLASS, n=12)
        ring(mb, side, cs, zr + dh, r, r + 0.28, tf, tf + 0.42, TR, n=8)
    # moldura na face (fora do vao) + peitoril em talude que entra no vao
    inner = [(cs - a, zs)] + [(u, z - Z) for u, z in CA.ogive(cs, a, Z + zr, rise, n=5)] + [(cs + a, zs)]
    outer = [(cs - a - 0.6, zs)] + [(u, z - Z) for u, z in CA.ogive(cs, a, Z + zr, rise, d=0.6, n=5)] + \
        [(cs + a + 0.6, zs)]
    band(mb, side, inner, outer, 0.0, 0.5, TR)
    CA.ledge(mb, W, cs - a - 0.85, cs + a + 0.85, [(G_T - 0.2, Z + zs - 0.4), (0.95, Z + zs - 0.4), (0.95, Z + zs - 0.18),
                                                    (0.4, Z + zs + 0.02), (G_T - 0.2, Z + zs + 0.02)], TR)


def vitrais():
    mb = MB("SG_Hall_Windows", "03_MINING_HALL", random.Random(321), detail="near")
    for side in ("W", "E"):
        for y in WIN_Y:
            lancet(mb, side, y)
    finish(mb)


# ------------------------------------------------------------------ abobada de nervuras
def zf(y):
    """altura do arco formeiro na parede lateral (ogival entre as linhas de apoio da abobada)"""
    for ya, yb in zip(VAULT_Y, VAULT_Y[1:]):
        if ya - 1e-6 <= y <= yb + 1e-6:
            half = (yb - ya) / 2.0
            rise = min(7.4, 0.8 * (yb - ya))
            return SPRING + ogive_z(half, rise, y - (ya + yb) / 2.0)
    return SPRING


def zv(x, y):
    """altura (acima do piso) do intradorso da abobada em (x, y)"""
    d = min(abs(x), HALF_W) / HALF_W
    g = math.sqrt(max(0.0, 1.0 - d * d))
    f = zf(y)
    return f + (ZC - f) * g


def pear(w, dep, top=0.12, fine=False):
    """perfil de nervura em PERA/toro (04.04): lados retos no alto, bojo e quilha arredondada embaixo"""
    h = w / 2.0
    if fine:
        return [(-h, top), (h, top), (h, -dep * 0.3), (h * 0.55, -dep * 0.78), (0.0, -dep), (-h * 0.55, -dep * 0.78),
                (-h, -dep * 0.3)]
    return [(-h, top), (h, top), (h, -dep * 0.25), (h * 0.62, -dep * 0.66), (0.0, -dep), (-h * 0.62, -dep * 0.66),
            (-h, -dep * 0.25)]


def _formeret_ys():
    """amostras do formeiro: 4 por tramo largo (a curva ogival) e as linhas de apoio"""
    ys = []
    for ya, yb in zip(VAULT_Y, VAULT_Y[1:]):
        k = 2 if yb - ya < 10.0 else 5
        ys += [ya + (yb - ya) * i / k for i in range(k)]
    ys.append(VAULT_Y[-1])
    return [min(max(y, Y0 + 0.5), Y1 - 0.5) for y in ys]


def rosette(mb, cx, cy, zt, R, dep, m, petals=8, n=24, flat=0.0):
    """FLORAO pendente (chave): rosa de 'petals' petalas (raio modulado pelo angulo), do teto (zt) descendo 'dep'.
    flat > 0: termina num disco LISO de raio flat (a face do emblema da chave central)"""
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


def vault():
    # panos: superficie UNICA do intradorso (normais para baixo, sem extradorso escondido), lisa, com as LINHAS DE FIADA
    # (faixas de junta) ao longo da nave nas linhas da propria grade -> assentam exatas no pano
    pv = MB("SG_Hall_Vault", "03_MINING_HALL", random.Random(331), detail="near")
    bm = pv.bm
    K = 10
    half = [HALF_W * math.sin(0.5 * math.pi * k / K) for k in range(K + 1)]
    xs = sorted(set([-v for v in half] + half))
    ys = []
    for ya, yb in zip(VAULT_Y, VAULT_Y[1:]):
        ny = max(3, int(round((yb - ya) / 3.0)))
        ys += [ya + (yb - ya) * k / ny for k in range(ny)]
    ys.append(VAULT_Y[-1])
    nx, ny = len(xs), len(ys)
    lo = [[bm.verts.new((x, y, Z + zv(x, y))) for x in xs] for y in ys]
    for j in range(ny - 1):
        for i in range(nx - 1):
            bm.faces.new((lo[j][i], lo[j + 1][i], lo[j + 1][i + 1], lo[j][i + 1]))
    pv._post([v for r in lo for v in r], VA, None, 0, 1)
    jv = []
    for i, x in enumerate(xs):
        if abs(x) < 1.0 or abs(x) > HALF_W - 2.5:
            continue
        # a faixa acompanha a grade: meia largura 0,07 para cada lado, 0,02 abaixo do pano
        xa, xb = x - 0.07, x + 0.07
        A = [bm.verts.new((xa, y, Z + zv(xa, y) - 0.025)) for y in ys]
        B = [bm.verts.new((xb, y, Z + zv(xb, y) - 0.025)) for y in ys]
        for j in range(ny - 1):
            bm.faces.new((A[j], A[j + 1], B[j + 1], B[j]))
        jv += A + B
    pv._post(jv, VJ, None, 0, 1)
    for f in bm.faces:
        f.normal_update()
        if f.normal.z > 0:
            f.normal_flip()
    finish(pv, recalc=False)

    mb = MB("SG_Hall_Ribs", "03_MINING_HALL", random.Random(333), detail="near")
    prof = pear(1.0, 0.9)
    prof_w = pear(0.7, 0.7, fine=True)
    prof_s = [(-0.26, 0.12), (0.26, 0.12), (0.26, -0.18), (0.0, -0.5), (-0.26, -0.18)]
    prof_f = [(-0.35, 0.12), (0.35, 0.12), (0.35, -0.7), (-0.35, -0.7)]     # formeiro colado a parede (so a quina le)
    x_end = HALF_W - 1.3
    tx = sorted(set([x_end * math.sin(0.5 * math.pi * k / 7) for k in range(8)] +
                    [-x_end * math.sin(0.5 * math.pi * k / 7) for k in range(8)]))

    def rib(pts2, pr, m):
        mb.sweep([(x, y, Z + zv(x, y) - 0.02) for x, y in pts2], pr, m)

    for y in VAULT_Y:
        yy = min(max(y, Y0 + 0.5), Y1 - 0.5)
        rib([(x, yy) for x in tx], prof if Y0 < y < Y1 else prof_w, OBS)
    for ya, yb in zip(VAULT_Y, VAULT_Y[1:]):
        if yb - ya < 10.0:
            continue                      # tramos estreitos das pontas: so o arco transversal
        ya2, yb2 = max(ya, Y0 + 0.5), min(yb, Y1 - 0.5)
        n = 10
        for s in (1, -1):
            pts = []
            for k in range(n + 1):
                t = k / n
                x = -x_end + 2 * x_end * t
                pts.append((x * s, ya2 + (yb2 - ya2) * t))
            rib(pts, prof_s, SILVER)
    rib([(0.0, Y0 + 0.5 + (Y1 - Y0 - 1.0) * k / 16.0) for k in range(17)], prof_s, SILVER)
    for s in (-1, 1):
        rib([(s * (HALF_W - 0.45), y) for y in _formeret_ys()], prof_f, OBS)
    # chaves (04.04): FLORAO de 8 petalas nas linhas das pilastras; o emblema SO na chave central (y 88, sobre o
    # medalhao do piso); nos meios dos tramos, florao pequeno com botao de prata
    for y in PIER_Y:
        zt = Z + zv(0.0, y) + 0.05
        if abs(y - EMB_C[1]) < 0.1:
            rosette(mb, 0.0, y, zt, 2.6, 1.45, OBS, n=16, flat=1.62)
            _ann(mb, 0.0, y, 1.62, 1.8, zt - 1.47, zt - 1.4, SILVER, 24)
            flat_emblem(mb, 0.0, y, zt - 1.45, 1.4, -1, rays=False, seg=16, glow=VSOFT)
        else:
            rosette(mb, 0.0, y, zt, 2.0, 1.3, OBS, n=16)
            EM._lathe(mb, (0.0, y, zt - 1.62), [(0.0, 0.0), (0.2, 0.08), (0.24, 0.22), (0.14, 0.36)], SILVER, 8,
                      caps=(False, True))
    for ya, yb in zip(VAULT_Y, VAULT_Y[1:]):
        y = (ya + yb) / 2.0
        if yb - ya < 10.0:
            continue
        zt = Z + zv(0.0, y) + 0.05
        rosette(mb, 0.0, y, zt, 1.25, 0.95, OBS, n=12)
        EM._lathe(mb, (0.0, y, zt - 1.2), [(0.0, 0.0), (0.14, 0.06), (0.17, 0.16), (0.1, 0.27)], SILVER, 8,
                  caps=(False, True))
    finish(mb)


# ------------------------------------------------------------------ FOCO: altar do fundo norte (trono + emblema)
SP = 12.5              # arranque das arquivoltas
PS = 16.4              # eixo dos pilares compostos
AR = [(13.4, 0.9, 2.4, 10.4, OBS), (14.3, 0.8, 1.7, 11.3, VIOST), (15.1, 0.8, 1.0, 12.1, TR)]
STEPS = [(10.0, DAIS_D, 0.45), (8.4, 2.4, 0.9), (6.8, 1.75, 1.35)]     # (meia largura, profundidade, topo)
EMB_H = 16.4           # centro do emblema monumental (acima do trono)


def altar():
    # altar, trono e portal num objeto so (hero: chanfro completo; menos MeshParts)
    mb = MB("SG_Hall_Altar", "03_MINING_HALL", random.Random(341), detail="hero")
    portal(mb)
    side = "N"
    # pilares compostos que sustentam a moldura (04.03): mesma pilastra do salao (soco em talude, colunelos com base,
    # capitel em anel + cavete + abaco) e o PINACULO do kit do castelo (corpo chanfrado com gabletes, agulha octogonal
    # com colar, anel, crochés e florao) no lugar da caixa + piramide de 4 lados + bola
    for k in (-1, 1):
        s = k * PS
        pier_stack(mb, side, s, 1.7, 2.2, 2.4, 3.0, SP, [(0.0, 2.2, 0.8), (-1.9, 0.9, 0.5), (1.9, 0.9, 0.5)],
                   impost=False)
        c = wp(side, s, 1.55, SP)
        CA.pinnacle(mb, c[0], c[1], c[2], s=1.1, hb=4.0, hn=5.6, body_m=CS, spire_m=CS, cap_m=OBS)
        wcol("SG_HallAltar", side, s - 2.4, s + 2.4, 0.0, 3.0, -0.5, SP)
    # retabulo de fundo liso escuro + 3 arquivoltas escalonadas (obsidiana / pedra violeta / cantaria) e o fio violeta
    # SUAVE no intradorso
    arch_panel(mb, side, 0.0, AR[0][0], AR[0][3], SP, 0.9, 0.0, 0.2, NI, n=8)
    CA.ledge(mb, WFR[side], -14.0, 14.0, CA.plinth(Z - 0.05, Z + 0.95, 0.55, 0.35), OBS)
    for hw, t, dep, rise, m in AR:
        arch_band(mb, side, 0.0, hw, rise, SP, SP, t, 0.0, dep, m, n=8)
    arch_band(mb, side, 0.0, AR[0][0] - 0.25, AR[0][3] - 0.25, SP, SP, 0.25, 1.9, 2.25, VSOFT, n=8)
    # vitral violeta central (o fundo do emblema) + 2 lancetas de luar com medalhao violeta
    _altar_lancet(mb, 0.0, 4.4, 11.0, EMB_H, 5.0, VGLASS, None)
    for k in (-1, 1):
        _altar_lancet(mb, k * 7.9, 1.8, 11.2, 16.0, 3.2, MOON, (1.2, 0.45))
    # EMBLEMA MONUMENTAL da ordem diante do vitral violeta
    EM.emblem(mb, mb, mb, wp(side, 0.0, 0.45, EMB_H), -math.pi / 2, 3.8, depth=0.8, monumental=True)
    # estandartes da ordem ladeando o trono (os UNICOS do salao; verga presa no pilar e numa misula no retabulo)
    for k in (-1, 1):
        s = k * 12.05
        EM.banner(mb, mb, mb, mb, wp(side, s, 1.0, 15.0), -math.pi / 2, 2.8, 10.5)
        wbox(mb, side, s - k * 1.75 - 0.15, s - k * 1.75 + 0.15, 0.2, 1.0, 14.8, 15.2, IRON, 0.0)
    throne(mb)
    finish(mb)


def _altar_lancet(mb, cs, hw, sill, spring, rise, m_gl, med):
    """lanceta do retabulo (rente ao fundo: e parede cega com vidro de cor, nao vao na casca): vidro, moldura de
    cantaria, peitoril e chumbo"""
    side = "N"
    arch_panel(mb, side, cs, hw, rise, spring, sill, 0.05, 0.3, m_gl)
    arch_band(mb, side, cs, hw, rise, spring, sill, 0.55, 0.0, 0.6, TR)
    wbox(mb, side, cs - hw - 0.8, cs + hw + 0.8, 0.0, 0.9, sill - 0.45, sill, TR, 0.06)
    h = sill + 2.1
    while h < spring - 0.6:
        wbox(mb, side, cs - hw, cs + hw, 0.3, 0.4, h - 0.1, h + 0.1, IRON, 0.0)
        h += 2.1
    wbox(mb, side, cs - 0.1, cs + 0.1, 0.3, 0.4, sill, spring + rise * 0.3, IRON, 0.0)
    if med:
        dh, r = med
        disk(mb, side, cs, spring + dh, r, 0.05, 0.36, VGLASS, n=12)
        ring(mb, side, cs, spring + dh, r, r + 0.3, 0.05, 0.5, TR, n=12)


def throne(mb):
    """TRONO DE SHADOW (04.02) sobre estrado de 3 degraus (fora da zona de minerio: y >= 128,9). Estrado com ESPELHOS
    moldurados (focinho boleado, campo recuado, filete de prata, rodape); trono de obsidiana com soco moldurado, avental
    com painel emoldurado, almofada com VOLUME, BRACOS em perfil com VOLUTA (botao de prata no olho), PES EM PATA de
    prata, espaldar com moldura ESCALONADA em 2 camadas (prata + obsidiana) e almofada em 2 niveis, montantes com
    pinaculos do kit e CRISTA em ogiva VAZADA com florao."""
    side = "N"
    W = WFR[side]
    prev = 0.0
    for i, (hw, dd, top) in enumerate(STEPS):
        z0 = prev - 0.1 if i == 0 else prev
        # campo recuado do espelho + focinho boleado (volta nas pontas) + rodape + filete de prata sob o focinho
        wbox(mb, side, -hw + 0.1, hw - 0.1, 0.0, dd - 0.14, z0, top - 0.16, OBS, 0.03)
        wbox(mb, side, -hw, hw, 0.0, dd + 0.04, top - 0.16, top, OBS, 0.06)
        wbox(mb, side, -hw + 0.02, hw - 0.02, 0.0, dd - 0.04, z0, prev + 0.1, OBS, 0.03)
        wbox(mb, side, -hw + 0.06, hw - 0.06, 0.0, dd - 0.1, top - 0.24, top - 0.18, SILVER, 0.0)
        nxt = STEPS[i + 1][1] if i + 1 < len(STEPS) else 0.3
        wbox(mb, side, -RUN_HW, RUN_HW, nxt, dd - 0.02, top, top + 0.04, CLOTH, 0.0)
        wcol("SG_HallThrone", side, -hw, hw, 0.0, dd, -0.5, top)
        prev = top
    b = STEPS[-1][2]
    # nicho de honra atras do trono: fundo de obsidiana com arco ogival de prata (recorta a silhueta contra o violeta)
    arch_panel(mb, side, 0.0, 4.3, 2.3, 8.0, b, 0.0, 0.22, OBS, n=5)
    arch_band(mb, side, 0.0, 4.3, 2.3, 8.0, b, 0.3, 0.0, 0.35, SILVER, n=5)
    zb = Z + b
    # soco do trono (plinto moldurado) e caixa do assento com AVENTAL moldurado
    CA.ledge(mb, W, -3.45, 3.45, [(0.1, zb), (2.2, zb), (2.2, zb + 0.18), (2.08, zb + 0.3), (0.1, zb + 0.3)], OBS)
    CA.ledge(mb, W, -2.55, 2.55, [(0.2, zb + 0.3), (1.92, zb + 0.3), (1.92, zb + 0.5), (1.82, zb + 0.6),
                                  (1.82, zb + 1.62), (1.94, zb + 1.72), (1.98, zb + 1.88), (1.9, zb + 2.0),
                                  (0.2, zb + 2.0)], OBS)
    inner = [(-1.9, b + 0.82), (1.9, b + 0.82), (1.9, b + 1.46), (-1.9, b + 1.46)]
    outer = [(-2.1, b + 0.66), (2.1, b + 0.66), (2.1, b + 1.62), (-2.1, b + 1.62)]
    band(mb, side, inner, outer, 1.8, 1.88, SILVER, closed=True)
    slab(mb, side, inner, 1.8, 1.85, VIOST)
    # almofada do assento com volume (chanfro largo em 2 segmentos)
    mb.box((4.3, 1.28, 0.48), wp(side, 0.0, 1.2, b + 2.2), (0, 0, 0), CLOTH, 0.16, 2)
    # bracos: perfil lateral (avental -> braco -> VOLUTA na frente) extrudado; botao de prata no olho da voluta
    cx_, cz_, rv = 1.9, 3.12, 0.56
    scroll = [(cx_ + rv * math.cos(math.radians(a)), cz_ + rv * math.sin(math.radians(a)))
              for a in (-90, -50, -15, 20, 55, 90)]
    arm = [(0.3, 0.3), (2.02, 0.3), (2.02, 0.6), (1.9, 0.72), (1.9, 2.56)] + scroll[1:] + [(0.62, 3.62), (0.3, 3.5)]
    for k in (-1, 1):
        a0, a1 = sorted((k * 2.55, k * 3.15))
        CA.ledge(mb, W, a0, a1, [(d, zb + h) for d, h in arm], OBS)
        # capa de prata no alto do braco e botao da voluta nas 2 faces
        CA.ledge(mb, W, a0 - 0.04, a1 + 0.04, [(0.55, zb + 3.56), (1.9, zb + 3.64), (1.9, zb + 3.74), (0.55, zb + 3.68)],
                 SILVER)
        for u in (a0 - 0.05, a1 + 0.05):
            c = wp(side, u, cx_, b + cz_)
            mb.cyl(0.26, 0.1, c, (0, math.pi / 2, 0), m=SILVER, n=10, bevel=0.0)
        # filete de prata acompanhando a VOLUTA e o alto do braco na face de fora (le a espiral no Roblox)
        uo = k * 3.15 + k * 0.03
        rb = rv - 0.13
        bead = [(cx_ + rb * math.cos(math.radians(a)), cz_ + rb * math.sin(math.radians(a)))
                for a in (-70, -35, 0, 35, 70, 100)] + [(1.3, 3.52), (0.62, 3.45)]
        mb.tube([wp(side, uo, d, b + h) for d, h in bead], 0.06, SILVER, 5)
        # pe em PATA: bojo de obsidiana + 3 garras de prata para a frente
        p = wp(side, k * 2.85, 1.85, b + 0.3)
        EM._lathe(mb, p, [(0.36, 0.0), (0.46, 0.12), (0.44, 0.3), (0.28, 0.46), (0.0, 0.52)], OBS, 10,
                  caps=(True, False))
        for du in (-0.22, 0.0, 0.22):
            q = wp(side, k * 2.85 + du, 2.1, b + 0.42)
            mb.rod(q, wp(side, k * 2.85 + du * 1.15, 2.46, b + 0.34), 0.085, SILVER, 5)
    # espaldar: obsidiana, moldura escalonada (prata + obsidiana), almofada em 2 niveis, crista em ogiva vazada
    bw, bt, bp = 2.85, b + 7.3, b + 8.7
    back = [(-bw, b + 2.0), (bw, b + 2.0), (bw, bt)] + ogive(0.0, bw, bp - bt, bt, 4)[::-1][1:-1] + [(-bw, bt)]
    slab(mb, side, back, 0.0, 0.55, OBS)

    def outline(off):
        w_ = bw - off
        return [(-w_, b + 2.0 + off * 0.9), (w_, b + 2.0 + off * 0.9), (w_, bt)] + \
            ogive(0.0, w_, (bp - bt) * w_ / bw, bt, 4)[::-1][1:-1] + [(-w_, bt)]
    band(mb, side, outline(0.55), outline(0.18), 0.5, 0.8, SILVER, closed=True)
    band(mb, side, outline(0.85), outline(0.55), 0.5, 0.7, OBS, closed=True)
    slab(mb, side, outline(0.85), 0.5, 0.74, CLOTH)
    slab(mb, side, outline(1.2), 0.74, 0.86, CLOTH)
    # crista: ogiva vazada (anel de obsidiana com filete de prata) + florao
    ci = [(u, h) for u, h in ogive(0.0, 0.62, 1.15, bp - 0.1, 4)]
    co = [(u, h) for u, h in ogive(0.0, 1.02, 1.75, bp - 0.4, 4)]
    ci = [(-0.62, bp - 0.25)] + ci + [(0.62, bp - 0.25)]
    co = [(-1.02, bp - 0.55)] + co + [(1.02, bp - 0.55)]
    band(mb, side, ci, co, 0.1, 0.46, OBS)
    band(mb, side, ci, [(u * 1.12, h + (0.08 if abs(u) < 0.01 else 0.0)) for u, h in ci], 0.06, 0.5, SILVER)
    tip = wp(side, 0.0, 0.28, bp + 1.3)
    CA.finial(mb, tip[0], tip[1], tip[2], 0.6)
    # montantes com pinaculos do kit (no lugar das agulhas n=4)
    for k in (-1, 1):
        a0, a1 = sorted((k * 2.85, k * 3.55))
        wprism(mb, side, rect_sd(a0, a1, 0.0, 0.85, 0.12), b, b + 7.3, OBS, 0.04)
        wprism(mb, side, rect_sd(a0 - 0.08, a1 + 0.08, 0.0, 0.95, 0.12), b + 7.3, b + 7.55, SILVER)
        c = wp(side, k * 3.2, 0.45, b + 7.55)
        CA.pinnacle(mb, c[0], c[1], c[2], s=0.34, hb=0.9, hn=1.9, body_m=OBS, spire_m=OBS, cap_m=SILVER, crock=False)
    wcol("SG_HallThrone", side, -3.55, 3.55, 0.0, 2.1, b, b + 7.3)


# ------------------------------------------------------------------ ferro: lustres
CHAND = [(-15.0, PIER_Y[1]), (15.0, PIER_Y[1]), (-15.0, PIER_Y[-2]), (15.0, PIER_Y[-2])]
CHAND_H = 19.5


def chandelier(mb, x, y):
    """LUSTRE (04.05): aro em tubo, 6 BRACOS em curva S (tubo), cubo em balaustre de torno, pingente em gota,
    velas do kit (prato, vela creme, chama em gota) e haste presa na nervura por uma ROSETA"""
    h = Z + CHAND_H
    R = 3.1
    n = 16
    mb.tube([(x + R * math.cos(2 * math.pi * k / n), y + R * math.sin(2 * math.pi * k / n), h) for k in range(n + 1)],
            0.13, IRONL, 5)

    def arm(t):
        u = 1 - t
        rr = u ** 3 * 0.4 + 3 * u * u * t * 1.5 + 3 * u * t * t * 2.4 + t ** 3 * R
        zz = u ** 3 * (h - 0.05) + 3 * u * u * t * (h - 0.75) + 3 * u * t * t * (h + 0.85) + t ** 3 * (h + 0.16)
        return rr, zz
    EM._lathe(mb, (x, y, h - 1.0), [(0.0, 0.0), (0.42, 0.55), (0.48, 0.95), (0.2, 1.55), (0.32, 1.86), (0.12, 2.1),
                                    (0.12, 2.5)], IRON, 6, caps=(False, True))
    EM._lathe(mb, (x, y, h - 2.1), [(0.0, 0.0), (0.2, 0.55), (0.16, 0.9), (0.24, 1.02), (0.0, 1.12)], SILVER, 6)
    for k in range(6):
        a = 2 * math.pi * k / 6 + math.pi / 6
        ca, sa = math.cos(a), math.sin(a)
        P = lambda rr, zz: (x + rr * ca, y + rr * sa, zz)
        pts = [P(*arm(i / 4.0)) for i in range(5)]
        mb.tube(pts, 0.075, IRON, 4)
        cx, cy, _ = P(R, h)
        candle(mb, cx, cy, h + 0.08, 0.9, 1.35, dish=False, cup=True)
    # haste ate o arco transversal (o lustre fica no eixo de uma nervura) + ROSETA de ferro presa sob a nervura
    top = Z + zv(x, y) - 0.9
    mb.rod((x, y, h + 1.45), (x, y, top - 0.2), 0.1, IRON, 6)
    EM._lathe(mb, (x, y, top - 0.55), [(0.12, 0.0), (0.62, 0.35), (0.66, 0.5), (0.0, 0.58)], IRON, 6,
              caps=(True, False))


def ironwork(mb):
    for x, y in CHAND:
        chandelier(mb, x, y)
    finish(mb)


# ------------------------------------------------------------------ luz propria do salao (6)
def lights():
    for (x, y), nm in zip(CHAND, ["SW", "SE", "NW", "NE"]):
        light("L_SGHall_Chandelier_%s" % nm, "POINT", (x, y, Z + CHAND_H - 0.2), 3600.0, (1.0, 0.68, 0.40), 0.8)
    light("L_SGHall_Moon_W", "POINT", (X0 + 6.0, WIN_Y[2], Z + 22.0), 1600.0, (0.58, 0.68, 1.0), 2.0)
    light("L_SGHall_Throne", "POINT", (0.0, Y1 - 6.5, Z + 12.0), 3600.0, (0.60, 0.36, 1.0), 1.5)


def build():
    iw = MB("SG_Hall_Ironwork", "03_MINING_HALL", random.Random(351), detail="near")   # lustres + candeias + vasos
    floor()
    walls(iw)
    vitrais()
    vault()
    altar()
    ironwork(iw)
    lights()
