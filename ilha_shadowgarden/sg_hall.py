# sg_hall - INTERIOR do Mining Hall da Ilha 3 (Shadow Garden): a mineracao principal, dentro da nave do castelo.
# Substitui sg_blockout.hall(). A CASCA (paredes, porta, janelas por fora, teto colidivel em HALL_CEIL, telhado) e do
# sg_castle; aqui so o que fica DENTRO do retangulo HALL_X0..X1 x HALL_Y0..Y1 (84 x 88, piso HALL 52,2):
#   - piso de pedra escura polida (topo EXATO no piso; a colisao e do sg_col), faixas de cantaria clara no ritmo das
#     pilastras, friso da zona de minerio (MINE_RECT) e um medalhao central muito sutil;
#   - nave gotica: pilastras engastadas (fora da MINE_RECT), arcada cega ogival em baixo, galeria alta (acima de
#     piso+14), vitrais de luar nas lunetas, abobada de nervuras (nada abaixo de piso+24 no meio do salao);
#   - parede norte = "altar" da nave: moldura monumental de 3 arquivoltas, triplo lanceta e retabulo (os minerios
#     SUPERLEGENDARY ficam na frente dela); porta sul com moldura interna;
#   - luz propria (6): 4 lustres de ferro quentes (acima de piso+18, correntes ate a nervura) + 2 luares frios pelos
#     vitrais (noroeste e altar). 4 estandartes (2 ladeiam o altar, 2 a porta).
# NAO modela minerio nem pedra/cristal flutuante (sao do jogo). Dentro da MINE_RECT nada colidivel e nada solto no chao.
# Colisao propria: so as bases das pilastras, os pilares do altar, o retabulo e as ombreiras da porta (fora da MINE_RECT).
import math, random
import sg_lib as SL
from sg_lib import MB, col_box2, light
import fm_lib
import sg_layout as L

S = fm_lib.S
# ------------------------------------------------------------------ materiais novos da zona (3)
NEW_MATS = {
    "Stone_SGHallFloor": (S(38, 40, 56), 0.25, 0.0, 0, None, 0.05),      # piso escuro polido (azul-ardosia)
    "Stone_SGHallVault": (S(38, 42, 66), 0.8, 0.0, 0, None, 0.06),       # panos da abobada / fundo dos nichos (navy)
    "Glass_SGHallMoon": (S(96, 124, 186), 0.4, 0.0, 0.4, S(110, 145, 220), 0.0),   # vitral de luar (frio)
}
for _k, _v in NEW_MATS.items():
    fm_lib.MATS.setdefault(_k, _v)

Z = L.HALL
X0, X1, Y0, Y1 = L.HALL_X0, L.HALL_X1, L.HALL_Y0, L.HALL_Y1
HALF_W = (X1 - X0) / 2.0                 # 42
CEIL_H = L.HALL_CEIL - Z                 # 28
MX0, MY0, MX1, MY1 = L.MINE_RECT

# ritmo da nave: vitrais no eixo das janelas da casca (blockout do castelo: 4 por lado) e pilastras entre eles
WIN_Y = [Y0 + 16.0 + k * (Y1 - Y0 - 32.0) / 3.0 for k in range(4)]            # 60, 78.67, 97.33, 116
PIER_Y = [WIN_Y[0] - (WIN_Y[1] - WIN_Y[0]) / 2.0] + [(a + b) / 2.0 for a, b in zip(WIN_Y, WIN_Y[1:])] + \
         [WIN_Y[-1] + (WIN_Y[1] - WIN_Y[0]) / 2.0]                             # 50.67 ... 125.33
VAULT_Y = [Y0] + PIER_Y + [Y1]                                                   # linhas de apoio da abobada

SPRING = 20.0          # arranque das nervuras (topo dos capiteis)
ZC = CEIL_H - 0.1      # fecho da abobada (logo abaixo do teto colidivel da casca)
PIER_D = 3.0           # saliencia maxima das pilastras (x fica >= 39: fora da MINE_RECT, que vai ate 38)
PIER_HW = 2.0
GAL_H = 14.4           # piso da galeria alta (acima de piso+14: fora do alcance)

CAMS = {
    "CAM_SGHall_Door": ((0.0, Y0 + 2.0, Z + 7.0), (0.0, Y1, Z + 12.0), 18),
    "CAM_SGHall_Back": ((0.0, Y1 - 5.0, Z + 9.0), (0.0, Y0, Z + 11.0), 18),
    "CAM_SGHall_Diag": ((X0 + 8.0, Y0 + 6.0, Z + 15.0), (22.0, 120.0, Z + 12.0), 18),
    "CAM_SGHall_West": ((34.0, 90.0, Z + 8.0), (X0, 90.0, Z + 15.0), 18),
    "CAM_SGHall_East": ((-34.0, 82.0, Z + 8.0), (X1, 94.0, Z + 15.0), 18),
    "CAM_SGHall_PlayerMid": ((6.0, 86.0, Z + 5.2), (-4.0, Y1, Z + 9.0), 22),
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


def wbox(mb, side, s0, s1, d0, d1, h0, h1, m, bevel=0.0):
    mb.box2(wp(side, s0, d0, h0), wp(side, s1, d1, h1), m, bevel)


def wcol(area, side, s0, s1, d0, d1, h0, h1):
    a, b = wp(side, s0, d0, h0), wp(side, s1, d1, h1)
    col_box2(area, tuple(min(p, q) for p, q in zip(a, b)), tuple(max(p, q) for p, q in zip(a, b)))


def wcyl(mb, side, s, d, h0, h1, r, m, n=8, bevel=0.0):
    mb.cyl(r, h1 - h0, wp(side, s, d, (h0 + h1) / 2.0), m=m, n=n, bevel=bevel)


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
    """placa no plano da parede a partir de um poligono CONVEXO (s, h)"""
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


# ------------------------------------------------------------------ piso
def floor():
    """piso escuro polido com topo EXATO em HALL (so visual: a colisao e do sg_col). Particao sem sobreposicao:
    margens junto as paredes, friso da MINE_RECT, 3 faixas longitudinais, faixas transversais no ritmo das pilastras e
    o medalhao central (quadrado -> anel -> campo -> anel -> disco)."""
    mb = MB("SG_Hall_Floor", "03_MINING_HALL", random.Random(301), detail="near")
    zt, zb = Z, Z - 0.4
    FM, TR = "Stone_SGHallFloor", "Stone_SG_Trim"

    def rect(x0, y0, x1, y1, m):
        if x1 - x0 > 0.01 and y1 - y0 > 0.01:
            mb.box2((x0, y0, zb), (x1, y1, zt), m, 0.0)

    fw, bw = 0.4, 0.3            # meia-largura do friso da zona e das faixas
    # margens (entre a parede e o friso)
    rect(X0, Y0, X1, MY0 - fw, FM)
    rect(X0, MY1 + fw, X1, Y1, FM)
    rect(X0, MY0 - fw, MX0 - fw, MY1 + fw, FM)
    rect(MX1 + fw, MY0 - fw, X1, MY1 + fw, FM)
    # friso da zona de minerio (moldura legivel so no chao)
    rect(MX0 - fw, MY0 - fw, MX1 + fw, MY0 + fw, TR)
    rect(MX0 - fw, MY1 - fw, MX1 + fw, MY1 + fw, TR)
    rect(MX0 - fw, MY0 + fw, MX0 + fw, MY1 - fw, TR)
    rect(MX1 - fw, MY0 + fw, MX1 + fw, MY1 - fw, TR)
    # colunas (x): lateral O | faixa | nave central | faixa | lateral L
    NAVE = 10.0
    cols = [(MX0 + fw, -NAVE - bw), (-NAVE + bw, NAVE - bw), (NAVE + bw, MX1 - fw)]
    for xb in (-NAVE, NAVE):
        rect(xb - bw, MY0 + fw, xb + bw, MY1 - fw, TR)
    ya, yb = MY0 + fw, MY1 - fw
    cy = (MY0 + MY1) / 2.0
    MED = 9.7                                          # meia-aresta do quadrado do medalhao
    for ci, (xa, xb) in enumerate(cols):
        cuts = PIER_Y[1:-1] if ci != 1 else [PIER_Y[1], cy - MED - bw, cy + MED + bw, PIER_Y[-2]]
        ys = [ya]
        for c in cuts:
            ys += [c - bw, c + bw]
        ys.append(yb)
        for k in range(0, len(ys), 2):
            y0_, y1_ = ys[k], ys[k + 1]
            if ci == 1 and abs((y0_ + y1_) / 2.0 - cy) < 1.0:
                continue                                  # celula do medalhao
            rect(xa, y0_, xb, y1_, FM)
        for k in range(1, len(ys) - 1, 2):
            rect(xa, ys[k], xb, ys[k + 1], TR)
    # medalhao (muito sutil: so dois aneis finos de cantaria no campo escuro)
    n = 32
    ang = [2 * math.pi * k / n for k in range(n)]

    def circ(r):
        return [(r * math.cos(a), cy + r * math.sin(a)) for a in ang]
    sq = [(MED * math.cos(a) / max(abs(math.cos(a)), abs(math.sin(a))),
           cy + MED * math.sin(a) / max(abs(math.cos(a)), abs(math.sin(a)))) for a in ang]
    rings = [(sq, circ(7.2), FM), (circ(7.2), circ(6.6), TR), (circ(6.6), circ(3.1), FM), (circ(3.1), circ(2.6), TR)]
    bm = mb.bm
    for outer, inner, m in rings:
        oT = [bm.verts.new((x, y, zt)) for x, y in outer]
        iT = [bm.verts.new((x, y, zt)) for x, y in inner]
        oB = [bm.verts.new((x, y, zb)) for x, y in outer]
        iB = [bm.verts.new((x, y, zb)) for x, y in inner]
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((oT[i], oT[j], iT[j], iT[i]))
            bm.faces.new((iB[i], iB[j], oB[j], oB[i]))
            bm.faces.new((oB[i], oB[j], oT[j], oT[i]))
            bm.faces.new((iT[i], iT[j], iB[j], iB[i]))
        mb._post(oT + iT + oB + iB, m, None, 0, 1)
    mb.prism(circ(2.6), zb, zt, FM)
    mb.finish()


# ------------------------------------------------------------------ paredes internas: pilastras, arcada, galeria
def walls():
    mb = MB("SG_Hall_Piers", "03_MINING_HALL", random.Random(311), detail="near")
    CS, TR, VA = "Stone_SG_Castle", "Stone_SG_Trim", "Stone_SGHallVault"

    def pier(side, s, corner=None):
        """pilastra engastada: plinto, nucleo, colunelo frontal + 2 laterais, anel na galeria, capitel"""
        if corner is None:
            wbox(mb, side, s - PIER_HW - 0.3, s + PIER_HW + 0.3, 0.0, PIER_D + 0.2, 0.0, 1.3, TR, 0.12)
            wbox(mb, side, s - 1.5, s + 1.5, 0.0, 2.0, 1.3, SPRING, CS, 0.1)
            wcyl(mb, side, s, 2.1, 1.3, SPRING, 0.85, CS, 8)
            for k in (-1, 1):
                wcyl(mb, side, s + k * 1.75, 0.55, 1.3, SPRING, 0.45, CS, 6)
            wbox(mb, side, s - 2.1, s + 2.1, 0.0, 3.1, GAL_H - 0.6, GAL_H + 0.4, TR, 0.08)
            wbox(mb, side, s - PIER_HW - 0.2, s + PIER_HW + 0.2, 0.0, PIER_D + 0.3, SPRING, SPRING + 1.1, TR, 0.12)
            wbox(mb, side, s - 1.7, s + 1.7, 0.0, 2.5, SPRING - 0.7, SPRING, TR, 0.06)
            wcol("SG_HallPier", side, s - PIER_HW - 0.3, s + PIER_HW + 0.3, 0.0, PIER_D + 0.2, -0.5, SPRING)
        else:
            # pilar de canto (ocupa o canto das duas paredes): corner = sinal da parede transversal (+1 = sul)
            a = s + corner * 2.4
            wbox(mb, side, min(s, a), max(s, a), 0.0, 2.6, 0.0, 1.3, TR, 0.12)
            wbox(mb, side, min(s, a), max(s, a), 0.0, 2.2, 1.3, SPRING, CS, 0.1)
            wbox(mb, side, min(s, a), max(s, a), 0.0, 2.6, SPRING, SPRING + 1.1, TR, 0.12)
            wcol("SG_HallPier", side, min(s, a), max(s, a), 0.0, 2.6, -0.5, SPRING)

    for side in ("W", "E"):
        for y in PIER_Y:
            pier(side, y)
        pier(side, Y0, corner=1)
        pier(side, Y1, corner=-1)
        # rodape entre as pilastras + arcada cega ogival (nicho escuro) + galeria alta com parapeito
        bays = [(Y0 + 2.4, PIER_Y[0] - PIER_HW - 0.3)] + \
               [(a + PIER_HW + 0.3, b - PIER_HW - 0.3) for a, b in zip(PIER_Y, PIER_Y[1:])] + \
               [(PIER_Y[-1] + PIER_HW + 0.3, Y1 - 2.4)]
        for bi, (sa, sb) in enumerate(bays):
            wbox(mb, side, sa, sb, 0.0, 0.5, 0.0, 0.9, TR, 0.06)
            cs = (sa + sb) / 2.0
            hw = (sb - sa) / 2.0 - 0.9
            if hw > 4.0:
                arch_panel(mb, side, cs, hw, 5.4, 7.0, 0.9, 0.0, 0.25, VA)
                arch_band(mb, side, cs, hw, 5.4, 7.0, 0.9, 0.8, 0.0, 0.8, TR)
                # galeria: laje, parapeito com remate, misulas
                wbox(mb, side, sa, sb, 0.0, 2.6, GAL_H, GAL_H + 0.8, TR, 0.08)
                wbox(mb, side, sa, sb, 2.0, 2.6, GAL_H + 0.8, GAL_H + 2.6, CS, 0.06)
                wbox(mb, side, sa - 0.1, sb + 0.1, 1.9, 2.75, GAL_H + 2.6, GAL_H + 2.95, TR, 0.06)
                npan = 4
                pw = (sb - sa - 0.6) / npan
                for q in range(npan):
                    p0 = sa + 0.3 + q * pw
                    wbox(mb, side, p0 + 0.25, p0 + pw - 0.25, 2.6, 2.8, GAL_H + 1.15, GAL_H + 2.25, VA, 0.0)
                for k in (-1, 1):
                    wbox(mb, side, cs + k * 4.6 - 0.45, cs + k * 4.6 + 0.45, 0.0, 2.0, GAL_H - 1.0, GAL_H, TR, 0.06)
    # parede sul: rodape e moldura interna da porta (ombreiras + verga + cornija ogival)
    dw = L.HALL_DOOR_W / 2.0
    dh = L.HALL_DOOR_H
    for k in (-1, 1):
        a, b = sorted((k * (dw + 0.05), k * (HALF_W - 2.4)))
        wbox(mb, "S", a, b, 0.0, 0.5, 0.0, 0.9, TR, 0.06)
        a, b = sorted((k * dw, k * (dw + 1.6)))
        wbox(mb, "S", a, b, 0.0, 1.2, 0.0, dh + 0.8, TR, 0.1)
        wcol("SG_HallDoor", "S", a, b, 0.0, 1.2, -0.5, dh)
    wbox(mb, "S", -dw - 1.6, dw + 1.6, 0.0, 1.2, dh, dh + 1.4, TR, 0.1)
    arch_band(mb, "S", 0.0, dw + 1.0, 5.2, dh + 1.4, dh + 1.4, 0.7, 0.0, 0.8, TR)
    # parede norte: rodape fora do altar
    for k in (-1, 1):
        a, b = sorted((k * 17.3, k * (HALF_W - 2.4)))
        wbox(mb, "N", a, b, 0.0, 0.5, 0.0, 0.9, TR, 0.06)
    mb.finish()


# ------------------------------------------------------------------ vitrais (lado de dentro das janelas altas)
def lancet(mb, side, cs, hw, sill, spring, rise, m_fr="Stone_SG_Trim", m_gl="Glass_SGHallMoon", tracery=True):
    arch_panel(mb, side, cs, hw, rise, spring, sill, 0.05, 0.3, m_gl)
    arch_band(mb, side, cs, hw, rise, spring, sill, 0.55, 0.0, 0.6, m_fr)
    wbox(mb, side, cs - hw - 0.8, cs + hw + 0.8, 0.0, 0.9, sill - 0.45, sill, m_fr, 0.06)
    if tracery:
        sub = (hw - 0.2) / 2.0
        wbox(mb, side, cs - 0.2, cs + 0.2, 0.05, 0.5, sill, spring + 0.5, m_fr, 0.0)
        for k in (-1, 1):
            arch_band(mb, side, cs + k * (0.2 + sub), sub - 0.3, 1.8, spring - 0.4, spring - 0.4, 0.3, 0.05, 0.5,
                      m_fr, n=4)
        ring(mb, side, cs, spring + 2.35, 0.65, 0.95, 0.05, 0.5, m_fr, n=12)


def vitrais():
    mb = MB("SG_Hall_Windows", "03_MINING_HALL", random.Random(321), detail="near")
    for side in ("W", "E"):
        for y in WIN_Y:
            lancet(mb, side, y, 3.0, GAL_H + 3.2, 21.8, 3.9)
    mb.finish()


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


def vault():
    mb = MB("SG_Hall_Vault", "03_MINING_HALL", random.Random(331), detail="near")
    VA, TR = "Stone_SGHallVault", "Stone_SG_Trim"
    bm = mb.bm
    # panos: casca fechada (intradorso + extradorso 0,35 acima), grade densa junto das paredes
    K = 7
    half = [HALF_W * math.sin(0.5 * math.pi * k / K) for k in range(K + 1)]
    xs = sorted(set([-v for v in half] + half))
    ys = []
    for ya, yb in zip(VAULT_Y, VAULT_Y[1:]):
        ny = max(3, int(round((yb - ya) / 3.0)))
        ys += [ya + (yb - ya) * k / ny for k in range(ny)]
    ys.append(VAULT_Y[-1])
    nx, ny = len(xs), len(ys)
    lo = [[bm.verts.new((x, y, Z + zv(x, y))) for x in xs] for y in ys]
    hi = [[bm.verts.new((x, y, Z + zv(x, y) + 0.35)) for x in xs] for y in ys]
    for j in range(ny - 1):
        for i in range(nx - 1):
            bm.faces.new((lo[j][i], lo[j + 1][i], lo[j + 1][i + 1], lo[j][i + 1]))
            bm.faces.new((hi[j][i], hi[j][i + 1], hi[j + 1][i + 1], hi[j + 1][i]))
    for j in range(ny - 1):
        for i in (0, nx - 1):
            bm.faces.new((lo[j][i], hi[j][i], hi[j + 1][i], lo[j + 1][i]))
    for i in range(nx - 1):
        for j in (0, ny - 1):
            bm.faces.new((lo[j][i], lo[j][i + 1], hi[j][i + 1], hi[j][i]))
    mb._post([v for r in lo + hi for v in r], VA, None, 0, 1)
    # nervuras (cantaria clara): arcos transversais, diagonais de cada tramo, cumeeira e formeiros
    prof = [(-0.45, 0.12), (0.45, 0.12), (0.45, -0.85), (-0.45, -0.85)]
    prof_w = [(-0.35, 0.12), (0.35, 0.12), (0.35, -0.7), (-0.35, -0.7)]
    x_end = HALF_W - 1.3
    tx = sorted(set([x_end * math.sin(0.5 * math.pi * k / 12) for k in range(13)] +
                    [-x_end * math.sin(0.5 * math.pi * k / 12) for k in range(13)]))

    def rib(pts2, pr, m="Stone_SG_Castle"):
        mb.sweep([(x, y, Z + zv(x, y) - 0.02) for x, y in pts2], pr, m)

    for y in VAULT_Y:
        yy = min(max(y, Y0 + 0.5), Y1 - 0.5)
        rib([(x, yy) for x in tx], prof if Y0 < y < Y1 else prof_w, TR)
    for ya, yb in zip(VAULT_Y, VAULT_Y[1:]):
        if yb - ya < 10.0:
            continue                      # tramos estreitos das pontas: so o arco transversal
        ya2, yb2 = max(ya, Y0 + 0.5), min(yb, Y1 - 0.5)
        n = 22
        for s in (1, -1):
            pts = []
            for k in range(n + 1):
                t = k / n
                x = -x_end + 2 * x_end * t
                pts.append((x * s, ya2 + (yb2 - ya2) * t))
            rib(pts, prof)
    rib([(0.0, Y0 + 0.5 + (Y1 - Y0 - 1.0) * k / 60.0) for k in range(61)], prof)
    for s in (-1, 1):
        rib([(s * (HALF_W - 0.45), Y0 + 0.5 + (Y1 - Y0 - 1.0) * k / 80.0) for k in range(81)], prof_w)
    # chaves (bossas) nos cruzamentos do eixo
    for y in PIER_Y + [(a + b) / 2.0 for a, b in zip(VAULT_Y, VAULT_Y[1:])]:
        mb.cyl(1.05, 0.7, (0.0, y, Z + ZC - 1.1), m=TR, n=8, bevel=0.0)
    mb.finish()


# ------------------------------------------------------------------ altar (parede norte)
def altar():
    mb = MB("SG_Hall_Altar", "03_MINING_HALL", random.Random(341), detail="hero")
    CS, TR, VA, SV = "Stone_SG_Castle", "Stone_SG_Trim", "Stone_SGHallVault", "Metal_SG_Silver"
    side = "N"
    # pilares compostos que sustentam a moldura (fora da MINE_RECT: saliencia <= 3)
    SP = 12.5                                  # arranque das arquivoltas
    PS = 16.4                                  # eixo dos pilares compostos
    for k in (-1, 1):
        s = k * PS
        wbox(mb, side, s - 2.4, s + 2.4, 0.0, 3.0, 0.0, 1.4, TR, 0.14)
        wbox(mb, side, s - 1.7, s + 1.7, 0.0, 2.2, 1.4, SP - 1.0, CS, 0.12)
        wcyl(mb, side, s, 2.2, 1.4, SP - 1.0, 0.8, CS, 8)
        for j in (-1, 1):
            wcyl(mb, side, s + j * 1.9, 0.9, 1.4, SP - 1.0, 0.5, CS, 6)
        wbox(mb, side, s - 2.5, s + 2.5, 0.0, 3.0, SP - 1.0, SP, TR, 0.12)
        # pinaculo sobre o pilar (agulha de 4 faces): silhueta gotica que emoldura o altar
        wbox(mb, side, s - 1.1, s + 1.1, 0.4, 2.6, SP, SP + 4.2, CS, 0.08)
        wbox(mb, side, s - 1.4, s + 1.4, 0.2, 2.9, SP + 4.2, SP + 4.8, TR, 0.08)
        c = wp(side, s, 1.55, SP + 4.8)
        SL.spire(mb, (c[0], c[1]), 1.5, c[2], 5.2, TR, n=4)
        wcol("SG_HallAltar", side, s - 2.4, s + 2.4, 0.0, 3.0, -0.5, SP)
    # 3 arquivoltas escalonadas (a interna mais funda)
    AR = [(13.4, 0.9, 2.4, 10.4), (14.3, 0.8, 1.7, 11.3), (15.1, 0.8, 1.0, 12.1)]
    for hw, t, dep, rise in AR:
        arch_band(mb, side, 0.0, hw, rise, SP, SP, t, 0.0, dep, TR, n=8)
    # fundo da moldura (navy) atras dos vitrais
    arch_panel(mb, side, 0.0, AR[0][0], AR[0][3], SP, 8.6, 0.0, 0.2, VA, n=8)
    # triplo lanceta de luar
    lancet(mb, side, 0.0, 2.7, 9.2, 17.2, 4.6, tracery=True)
    for k in (-1, 1):
        lancet(mb, side, k * 6.9, 2.1, 10.0, 16.0, 3.5, tracery=False)
    # retabulo (base da moldura): corpo, remate e arcada cega miuda
    wbox(mb, side, -13.9, 13.9, 0.0, 1.2, 0.0, 8.0, CS, 0.1)
    wbox(mb, side, -14.5, 14.5, 0.0, 1.6, 8.0, 8.6, TR, 0.1)
    wbox(mb, side, -14.2, 14.2, 0.0, 1.5, 0.0, 0.9, TR, 0.08)
    for i in (0, 1, 3, 4):
        cs = -10.4 + i * 5.2
        arch_band(mb, side, cs, 1.4, 1.6, 4.4, 1.6, 0.35, 1.2, 1.5, TR, n=4)
    wcol("SG_HallAltar", side, -14.5, 14.5, 0.0, 1.6, -0.5, 8.6)
    # emblema de prata (estrela de 8 pontas do Shadow Garden) no centro do retabulo
    pts = []
    for k in range(16):
        r = 2.8 if k % 4 == 0 else (1.9 if k % 2 == 0 else 0.9)
        a = math.pi / 2 + k * math.pi / 8
        pts.append((r * math.cos(a), 4.5 + r * math.sin(a)))
    for k in range(16):
        a, b = pts[k], pts[(k + 1) % 16]
        slab(mb, side, [(0.0, 4.5), a, b], 1.2, 1.45, SV)
    mb.finish()


# ------------------------------------------------------------------ ferro: lustres, candeias dos nichos, varoes
CHAND = [(-15.0, PIER_Y[1]), (15.0, PIER_Y[1]), (-15.0, PIER_Y[-2]), (15.0, PIER_Y[-2])]
CHAND_H = 19.5


def chandelier(mb, x, y):
    IR, GL = "Metal_SG_Iron", "Lantern_Glow"
    h = CHAND_H
    n = 16
    ring_lo = [(x + 3.2 * math.cos(2 * math.pi * k / n), y + 3.2 * math.sin(2 * math.pi * k / n), Z + h)
               for k in range(n + 1)]
    ring_hi = [(x + 1.9 * math.cos(2 * math.pi * k / n), y + 1.9 * math.sin(2 * math.pi * k / n), Z + h + 1.8)
               for k in range(n + 1)]
    mb.tube(ring_lo, 0.2, IR, 6)
    mb.tube(ring_hi, 0.16, IR, 6)
    mb.cyl(0.5, 3.2, (x, y, Z + h + 1.9), m=IR, n=8, r2=0.3, bevel=0.0)          # fuste central (sem pingente:
    # a luz fica no miolo vazio do aro, abaixo do fuste)
    for k in range(8):
        a = 2 * math.pi * k / 8 + math.pi / 8
        ca, sa = math.cos(a), math.sin(a)
        mb.beam((x + 0.4 * ca, y + 0.4 * sa, Z + h + 2.4), (x + 1.9 * ca, y + 1.9 * sa, Z + h + 1.8), 0.22, 0.22, IR, 0.0)
        mb.beam((x + 1.9 * ca, y + 1.9 * sa, Z + h + 1.8), (x + 3.2 * ca, y + 3.2 * sa, Z + h), 0.22, 0.22, IR, 0.0)
        cx, cy = x + 3.2 * ca, y + 3.2 * sa
        mb.cyl(0.36, 0.3, (cx, cy, Z + h + 0.3), m=IR, n=6, bevel=0.0)
        mb.cyl(0.22, 0.75, (cx, cy, Z + h + 0.8), m=GL, n=6, bevel=0.0)
    top = zv(x, y) - 0.85
    mb.rod((x, y, Z + h + 2.6), (x, y, Z + top), 0.13, IR, 6)


def ironwork():
    mb = MB("SG_Hall_Ironwork", "03_MINING_HALL", random.Random(351), detail="near")
    IR, GL = "Metal_SG_Iron", "Lantern_Glow"
    for x, y in CHAND:
        chandelier(mb, x, y)
    # candeias: uma no fundo de cada nicho da arcada (luz quente baixa no perimetro, como na concept)
    for side in ("W", "E"):
        for y in WIN_Y:
            wbox(mb, side, y - 0.2, y + 0.2, 0.25, 1.3, 8.1, 8.4, IR, 0.0)
            wcyl(mb, side, y, 1.3, 8.4, 8.75, 0.5, IR, 6)
            wcyl(mb, side, y, 1.3, 8.75, 9.7, 0.28, GL, 6)
    mb.finish()


# ------------------------------------------------------------------ estandartes (4): ladeiam o altar e a porta
def banners():
    mb = MB("SG_Hall_Banners", "03_MINING_HALL", random.Random(361), detail="near")
    NV, SV, IR = "Cloth_SG_Navy", "Metal_SG_Silver", "Metal_SG_Iron"
    for side, ss in (("N", (-26.0, 26.0)), ("S", (-25.0, 25.0))):
        for s in ss:
            top, bot, hw = 21.0, 10.2, 2.4
            wbox(mb, side, s - 3.0, s + 3.0, 0.5, 0.8, top + 0.2, top + 0.5, IR, 0.0)
            for k in (-1, 1):
                wbox(mb, side, s + k * 2.7 - 0.15, s + k * 2.7 + 0.15, 0.0, 0.8, top + 0.2, top + 0.9, IR, 0.0)
            slab(mb, side, [(s - hw, bot), (s + hw, bot), (s + hw, top), (s - hw, top)], 0.3, 0.5, NV)
            slab(mb, side, [(s - hw, bot), (s, bot), (s - hw, bot - 2.0)], 0.3, 0.5, NV)
            slab(mb, side, [(s, bot), (s + hw, bot), (s + hw, bot - 2.0)], 0.3, 0.5, NV)
            # emblema de prata (losango estrelado) + barra de prata no pe da faixa
            c = 16.6
            pts = [(s + (1.5 if k % 2 == 0 else 0.5) * math.cos(math.pi / 2 + k * math.pi / 4),
                    c + (1.5 if k % 2 == 0 else 0.5) * math.sin(math.pi / 2 + k * math.pi / 4)) for k in range(8)]
            for k in range(8):
                slab(mb, side, [(s, c), pts[k], pts[(k + 1) % 8]], 0.5, 0.65, SV)
            wbox(mb, side, s - hw, s + hw, 0.5, 0.65, top - 1.2, top - 0.9, SV, 0.0)
    mb.finish()


# ------------------------------------------------------------------ luz propria do salao (6)
def lights():
    for (x, y), nm in zip(CHAND, ["SW", "SE", "NW", "NE"]):
        light("L_SGHall_Chandelier_%s" % nm, "POINT", (x, y, Z + CHAND_H - 0.2), 5000.0, (1.0, 0.70, 0.42), 1.0)
    # luar frio pelos vitrais: noroeste (lado da lua) e o triplo lanceta do altar
    light("L_SGHall_Moon_W", "POINT", (X0 + 6.0, WIN_Y[2], Z + 22.0), 3200.0, (0.58, 0.68, 1.0), 2.0)
    light("L_SGHall_Moon_Altar", "POINT", (0.0, Y1 - 7.0, Z + 18.0), 2600.0, (0.60, 0.70, 1.0), 2.0)


def build():
    floor()
    walls()
    vitrais()
    vault()
    altar()
    ironwork()
    banners()
    lights()
