# sg_hall - INTERIOR do Mining Hall da Ilha 3 (Shadow Garden): a mineracao principal, dentro da nave do castelo.
# Substitui sg_blockout.hall(). A CASCA (paredes, porta, janelas por fora, teto colidivel em HALL_CEIL, telhado) e do
# sg_castle; aqui so o que fica DENTRO do retangulo HALL_X0..X1 x HALL_Y0..Y1 (84 x 88, piso HALL 52,2).
# REFINAMENTO 2026-09-28 (salao de uma ORDEM, nao nave generica): tudo obedece ao sistema de identidade (sg_emblem) e a
# paleta com funcao (sg_lib.SMATS):
#   - PISO de marmore negro particionado (sem sobreposicao coplanar): borda de obsidiana ate as paredes, filete de prata
#     fino no contorno da zona de minerio, faixas de obsidiana com filete de prata no ritmo das pilastras, tacos de prata
#     nos cruzamentos, MEDALHAO com o emblema da ordem DEITADO (aneis e lamina de prata, crescente SG_Rune_Glow fino,
#     8 raios) e um tapete roxo estreito com bordas de prata da porta ao estrado do trono (tudo rente: +0,03..0,05);
#   - PAREDES: pilastras com soco de obsidiana, fuste de pedra, anel fino SG_VioletDeep_Glow sob o capitel; arcada cega
#     com fundo violeta escuro e candeia quente; faixas de obsidiana (rodape, laje da galeria); galeria alta com
#     balaustrada de ferro negro e corrimao de prata sobre fundo violeta; paramento de pedra fria cobrindo a pele cinza;
#   - TETO: panos em azul-noite, arcos transversais e formeiros de obsidiana, diagonais e cumeeira de prata, chaves com
#     o emblema pequeno (face para baixo);
#   - FOCO (fundo norte, y >= 129, fora da zona): TRONO DE SHADOW sobre estrado de 3 degraus de obsidiana com o tapete
#     subindo os degraus, EMBLEMA MONUMENTAL diante do vitral violeta, 2 lancetas de luar com medalhao violeta,
#     3 arquivoltas (prata-pedra / violeta / obsidiana com fio de energia) e 2 estandartes da ordem ladeando;
#   - JANELAS: vitrais de luar com chumbo e medalhao violeta no topo de cada lanceta;
#   - 4 estandartes da ordem (sg_emblem.banner) nas pilastras; 4 lustres de ferro negro;
#   - LUZ (6): 4 lustres quentes (pocas de luz com sombra entre elas), 1 violeta no trono/emblema, 1 luar pelo vitral NO.
# NAO modela minerio nem pedra/cristal flutuante (sao do jogo). Dentro da MINE_RECT nada colidivel e nada solto no chao;
# nada no eixo do salao abaixo de piso+24; o corredor da porta fica livre.
# Colisao propria: bases das pilastras, pilares do altar, ombreiras da porta, estrado (3 degraus) e trono (fora da zona).
import math, random
import sg_lib as SL
from sg_lib import MB, col_box2, light
import fm_lib
import sg_layout as L
import sg_emblem as EM

S = fm_lib.S
# ------------------------------------------------------------------ materiais novos da zona (4 de 7)
NEW_MATS = {
    "Stone_SGHallVault": (S(22, 26, 56), 0.85, 0.0, 0, None, 0.06),       # panos da abobada: azul-noite profundo
    "Stone_SGHallNiche": (S(40, 26, 64), 0.85, 0.0, 0, None, 0.05),       # fundo dos nichos / retabulo: violeta escuro
    "Glass_SGHallMoon": (S(96, 124, 186), 0.4, 0.0, 0.4, S(110, 145, 220), 0.0),   # vitral de luar (= sg_castle)
    "Glass_SGHallViolet": (S(112, 56, 196), 0.3, 0.0, 0.9, S(130, 70, 230), 0.0),   # medalhoes / vitral do trono
}
for _k, _v in NEW_MATS.items():
    fm_lib.MATS.setdefault(_k, _v)

MARBLE, OBS, SILVER, IRON = "Stone_SG_MarbleBlack", "Stone_SG_Obsidian", "Metal_SG_Silver", "Metal_SG_BlackIron"
CLOTH, VIOST, RUNE, VGLOW = "Cloth_SG_Purple", "Stone_SG_Violet", "SG_Rune_Glow", "SG_VioletDeep_Glow"
# passe de ACABAMENTO (2026-09-29): brilho magico do salao BAIXO - os aneis das pilastras viram pedra violeta SEM brilho
# (16 placas de neon competiam com a arquitetura); fio da arquivolta do altar e crescentes do piso e das chaves em violeta
# SUAVE (Neon escuro). Violeta forte so no vitral/emblema do trono.
VSOFT = "SG_VioletSoft_Glow"
CS, TR, VA, NI = "Stone_SG_Castle", "Stone_SG_Trim", "Stone_SGHallVault", "Stone_SGHallNiche"
MOON, VGLASS = "Glass_SGHallMoon", "Glass_SGHallViolet"

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


# ------------------------------------------------------------------ emblema DEITADO (piso e chaves do teto)
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
    baixo). Geometria unica do sg_emblem (emblem_flat, acabamento 2026-09-29): anel continuo chanfrado, crescente de
    um poligono, espada em losango; sobe no maximo ~0,056 da superficie (nada em que tropecar), fundos embutidos.
    Sem campo negro proprio: o medalhao do piso e as chaves ja sao de obsidiana. Lamina apontando para v."""
    EM.emblem_flat(mb, mb, mb, (cx, cy, zf), math.atan2(v[1], v[0]), r, monumental=rays, up=sgn, glow=glow,
                   field=False, seg=seg)


def finish(mb):
    """mb.finish() + remove faces de area nula (o tubo do anel do sg_emblem, congelado, torce 180 graus no plano x-z
    dos simbolos voltados para o sul: sobram quads de area zero que nao desenham nada)"""
    import bmesh
    ob = mb.finish()
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
    field = (MX0, MY0, MX1, MY1)
    outer = (MX0 - FW, MY0 - FW, MX1 + FW, MY1 + FW)
    holes = [(-RUN_OUT, Y0, RUN_OUT, ecy - MED), (-RUN_OUT, ecy + MED, RUN_OUT, Y1 - DAIS_D),
             (ecx - MED, ecy - MED, ecx + MED, ecy + MED)]
    groups = {MARBLE: [], OBS: [], SILVER: []}
    # borda de obsidiana (entre as paredes e o filete; as pilastras pousam nela)
    groups[OBS] += [(X0, Y0, X1, outer[1]), (X0, outer[3], X1, Y1), (X0, outer[1], outer[0], outer[3]),
                    (outer[2], outer[1], X1, outer[3])]
    groups[SILVER] += [(outer[0], outer[1], outer[2], MY0), (outer[0], MY1, outer[2], outer[3]),
                       (outer[0], MY0, MX0, MY1), (MX1, MY0, outer[2], MY1)]
    # faixas: transversais (inteiras) nas pilastras internas; longitudinais cortadas nos cruzamentos
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
    # marmore: celulas entre as faixas
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
    # tapete: miolo roxo + filete de prata (rente +0,04) sobre margem de obsidiana, da porta ao estrado
    for ya, yb in ((Y0, ecy - MED), (ecy + MED, Y1 - DAIS_D)):
        for s in (-1, 1):
            mb.box2((s * RUN_EDGE, ya, zb), (s * RUN_OUT, yb, zt), OBS, 0.0)
            mb.box2((s * RUN_HW, ya, zb), (s * RUN_EDGE, yb, zt + 0.035), SILVER, 0.0)
        mb.box2((-RUN_HW, ya, zb), (RUN_HW, yb, zt + 0.04), CLOTH, 0.0)
    # tacos de prata (losangos) nos cruzamentos das faixas, rentes
    for y in TY:
        for x in LX:
            q = 0.75
            mb.prism([(x, y - q), (x + q, y), (x, y + q), (x - q, y)], zt - 0.05, zt + 0.03, SILVER)
    # medalhao: quadrado de obsidiana -> aro de prata -> campo de obsidiana; emblema deitado por cima (rente)
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
    # raio 0,97 * EMB_R: as pontas dos raios longos (0,98 r + 0,34 r) ficam dentro do campo de obsidiana (R1 = 8,3)
    flat_emblem(mb, ecx, ecy, zt, EMB_R * 0.97, 1, rays=True, glow=VSOFT)
    finish(mb)


# ------------------------------------------------------------------ paredes internas: pilastras, arcada, galeria
def _curve_top(side, s0, s1, top_fn, h0, k=5):
    """poligono convexo (s, h): base reta em h0 e topo seguindo a curva top_fn(s) de s0 a s1"""
    pts = [(s0, h0), (s1, h0)]
    for i in range(k + 1):
        s = s1 + (s0 - s1) * i / k
        pts.append((s, top_fn(s)))
    return pts


S_NICHES, S_NICHE_HW = (18.5, 30.5), 4.3          # nichos da parede sul (ladeiam a porta)
N_NICHES, N_NICHE_HW = (24.6, 34.0), 3.4          # nichos da parede norte (ladeiam o altar)


def niche(mb, side, cs, hw, rise=5.4, spring=7.0):
    """nicho da arcada cega: fundo violeta escuro, arquivolta de cantaria, fecho de obsidiana"""
    arch_panel(mb, side, cs, hw, rise, spring, 0.9, 0.1, 0.3, NI, n=5)
    arch_band(mb, side, cs, hw, rise, spring, 0.9, 0.8, 0.0, 0.8, TR, n=5)
    wbox(mb, side, cs - 0.55, cs + 0.55, 0.0, 1.0, spring + rise - 0.4, spring + rise + 1.0, OBS, 0.06)


def gallery(mb, side, sa, sb, corbels):
    """galeria alta: faixa de obsidiana por baixo, laje de obsidiana, fundo violeta, balaustrada de ferro negro com
    corrimao de prata e montantes com remate de prata (ritmo: pontas + meio)"""
    wbox(mb, side, sa, sb, 0.0, 0.45, GAL_H - 1.0, GAL_H, OBS, 0.0)
    wbox(mb, side, sa, sb, 0.0, 2.6, GAL_H, GAL_H + 0.8, OBS, 0.08)
    wbox(mb, side, sa, sb, 0.0, 0.1, GAL_H + 0.8, GAL_H + 3.0, NI, 0.0)
    wbox(mb, side, sa, sb, 2.2, 2.5, GAL_H + 0.8, GAL_H + 1.05, IRON, 0.0)
    wbox(mb, side, sa - 0.1, sb + 0.1, 2.1, 2.6, GAL_H + 2.7, GAL_H + 2.95, SILVER, 0.0)
    npost = max(2, int((sb - sa - 0.8) / 1.05))
    for q in range(npost + 1):
        s = sa + 0.4 + q * (sb - sa - 0.8) / npost
        heavy = q in (0, npost) or q == npost // 2
        t = 0.2 if not heavy else 0.4
        wbox(mb, side, s - t / 2, s + t / 2, 2.35 - t / 2, 2.35 + t / 2, GAL_H + 1.05, GAL_H + 2.7, IRON, 0.0)
        if heavy:
            mb.cyl(0.3, 0.55, wp(side, s, 2.35, GAL_H + 3.22), m=SILVER, n=4, r2=0.06, bevel=0.0)
    for c in corbels:
        wbox(mb, side, c - 0.45, c + 0.45, 0.0, 2.0, GAL_H - 1.4, GAL_H, OBS, 0.06)


def walls():
    mb = MB("SG_Hall_Piers", "03_MINING_HALL", random.Random(311), detail="near")

    def pier(side, s, corner=None):
        """pilastra engastada: soco de obsidiana, fuste de pedra (nucleo + colunelos), anel de obsidiana na galeria,
        anel fino de energia violeta sob o capitel, capitel de cantaria"""
        if corner is None:
            wbox(mb, side, s - PIER_HW - 0.3, s + PIER_HW + 0.3, 0.0, PIER_D + 0.2, 0.0, 1.5, OBS, 0.12)
            wbox(mb, side, s - PIER_HW - 0.1, s + PIER_HW + 0.1, 0.0, PIER_D, 1.5, 1.8, TR, 0.06)
            wbox(mb, side, s - 1.5, s + 1.5, 0.0, 2.0, 1.8, SPRING, CS, 0.1)
            wcyl(mb, side, s, 2.1, 1.8, SPRING, 0.85, CS, 8)
            for k in (-1, 1):
                wcyl(mb, side, s + k * 1.75, 0.55, 1.8, SPRING, 0.45, CS, 6)
            wbox(mb, side, s - 2.1, s + 2.1, 0.0, 3.1, GAL_H - 0.6, GAL_H + 0.4, OBS, 0.08)
            wbox(mb, side, s - 2.25, s + 2.25, 0.0, 3.05, SPRING - 1.3, SPRING - 1.05, VIOST, 0.0)
            wbox(mb, side, s - 1.9, s + 1.9, 0.0, 2.7, SPRING - 1.05, SPRING, TR, 0.06)
            wbox(mb, side, s - PIER_HW - 0.2, s + PIER_HW + 0.2, 0.0, PIER_D + 0.3, SPRING, SPRING + 1.1, TR, 0.12)
            wcol("SG_HallPier", side, s - PIER_HW - 0.3, s + PIER_HW + 0.3, 0.0, PIER_D + 0.2, -0.5, SPRING)
        else:
            # pilar de canto (ocupa o canto das duas paredes): corner = sinal da parede transversal (+1 = sul)
            a = s + corner * 2.4
            wbox(mb, side, min(s, a), max(s, a), 0.0, 2.6, 0.0, 1.5, OBS, 0.12)
            wbox(mb, side, min(s, a), max(s, a), 0.0, 2.2, 1.5, SPRING, CS, 0.1)
            wbox(mb, side, min(s, a), max(s, a), 0.0, 2.35, SPRING - 1.3, SPRING - 1.05, VIOST, 0.0)
            wbox(mb, side, min(s, a), max(s, a), 0.0, 2.6, SPRING, SPRING + 1.1, TR, 0.12)
            wcol("SG_HallPier", side, min(s, a), max(s, a), 0.0, 2.6, -0.5, SPRING)

    for side in ("W", "E"):
        for y in PIER_Y:
            pier(side, y)
        pier(side, Y0, corner=1)
        pier(side, Y1, corner=-1)
        bays = [(Y0 + 2.4, PIER_Y[0] - PIER_HW - 0.3)] + \
               [(a + PIER_HW + 0.3, b - PIER_HW - 0.3) for a, b in zip(PIER_Y, PIER_Y[1:])] + \
               [(PIER_Y[-1] + PIER_HW + 0.3, Y1 - 2.4)]
        for bi, (sa, sb) in enumerate(bays):
            wbox(mb, side, sa, sb, 0.0, 0.5, 0.0, 0.9, OBS, 0.06)                       # rodape de obsidiana
            cs = (sa + sb) / 2.0
            hw = (sb - sa) / 2.0 - 0.9
            if hw > 4.0:
                # paramento de pedra fria (cobre a pele cinza da casca) + faixa de obsidiana sob a galeria
                wbox(mb, side, sa, sb, 0.0, 0.1, 0.9, GAL_H - 1.0, CS, 0.0)
                niche(mb, side, cs, hw)
                gallery(mb, side, sa, sb, (cs - 4.6, cs + 4.6))
                # acima da galeria: paramento dos dois lados do vitral ate o formeiro
                wc = WIN_Y[min(range(4), key=lambda i: abs(WIN_Y[i] - cs))]
                for a, b in ((sa, wc - 3.6), (wc + 3.6, sb)):
                    slab(mb, side, _curve_top(side, a, b, lambda s: zf(s) - 0.05, GAL_H + 3.0), 0.0, 0.1, CS)
            else:
                # tramo estreito das pontas: paramento inteiro ate o formeiro
                slab(mb, side, _curve_top(side, sa, sb, lambda s: zf(s) - 0.05, 0.9, 3), 0.0, 0.1, CS)
    # parede sul: rodape, paramento, moldura interna da porta (ombreiras + verga + cornija ogival)
    dw = L.HALL_DOOR_W / 2.0
    dh = L.HALL_DOOR_H
    endwall = lambda s: SPRING + (ZC - SPRING) * math.sqrt(max(0.0, 1.0 - (s / HALF_W) ** 2)) - 0.05
    for k in (-1, 1):
        a, b = sorted((k * (dw + 1.6), k * (HALF_W - 2.4)))
        wbox(mb, "S", a, b, 0.0, 0.5, 0.0, 0.9, OBS, 0.06)
        slab(mb, "S", _curve_top("S", a, b, endwall, 0.9, 6), 0.0, 0.1, CS)
        for c in S_NICHES:
            niche(mb, "S", k * c, S_NICHE_HW)
        gallery(mb, "S", a, b, [k * c for c in (13.0, 24.5, 36.0)])
        a, b = sorted((k * dw, k * (dw + 1.6)))
        wbox(mb, "S", a, b, 0.0, 1.2, 0.0, 1.5, OBS, 0.1)
        wbox(mb, "S", a, b, 0.0, 1.2, 1.5, dh + 0.8, TR, 0.1)
        wcol("SG_HallDoor", "S", a, b, 0.0, 1.2, -0.5, dh)
    slab(mb, "S", _curve_top("S", -dw - 1.6, dw + 1.6, endwall, dh + 1.4, 4), 0.0, 0.1, CS)
    wbox(mb, "S", -dw - 1.6, dw + 1.6, 0.0, 1.2, dh, dh + 1.4, OBS, 0.1)
    arch_band(mb, "S", 0.0, dw + 1.0, 5.2, dh + 1.4, dh + 1.4, 0.7, 0.0, 0.8, TR)
    arch_band(mb, "S", 0.0, dw + 1.7, 5.9, dh + 1.4, dh + 1.4, 0.5, 0.0, 0.55, VIOST)
    # parede norte: rodape e paramento fora do altar
    for k in (-1, 1):
        a, b = sorted((k * 18.8, k * (HALF_W - 2.4)))
        wbox(mb, "N", a, b, 0.0, 0.5, 0.0, 0.9, OBS, 0.06)
        for c in N_NICHES:
            niche(mb, "N", k * c, N_NICHE_HW)
        gallery(mb, "N", a + (0.4 if k > 0 else 0.0), b - (0.4 if k < 0 else 0.0), [k * c for c in (19.9, 29.3, 38.6)])
    slab(mb, "N", _curve_top("N", -(HALF_W - 2.4), HALF_W - 2.4, endwall, 0.9, 10), 0.0, 0.1, CS)
    finish(mb)


# ------------------------------------------------------------------ vitrais (lado de dentro das janelas altas)
def lancet(mb, side, cs, hw, sill, spring, rise, m_gl=MOON, tracery=True, med=None, lead=True, d_gl=0.3):
    """vitral ogival: vidro, moldura de cantaria, peitoril, chumbo (ferro negro) e medalhao violeta no topo.
    med = (altura do centro acima do arranque, raio) ou None (sem medalhao)."""
    arch_panel(mb, side, cs, hw, rise, spring, sill, 0.05, d_gl, m_gl)
    arch_band(mb, side, cs, hw, rise, spring, sill, 0.55, 0.0, 0.6, TR)
    wbox(mb, side, cs - hw - 0.8, cs + hw + 0.8, 0.0, 0.9, sill - 0.45, sill, TR, 0.06)
    if lead:
        # chumbo: travessas a cada 2,1 + montante central quando nao ha rendilhado (grade de vitral, nao persiana)
        h = sill + 2.1
        while h < spring - 0.6:
            wbox(mb, side, cs - hw, cs + hw, d_gl, d_gl + 0.1, h - 0.1, h + 0.1, IRON, 0.0)
            h += 2.1
        if not tracery:
            wbox(mb, side, cs - 0.1, cs + 0.1, d_gl, d_gl + 0.1, sill, spring + rise * 0.3, IRON, 0.0)
    if tracery:
        sub = (hw - 0.2) / 2.0
        wbox(mb, side, cs - 0.2, cs + 0.2, 0.05, 0.5, sill, spring + 0.5, TR, 0.0)
        for k in (-1, 1):
            arch_band(mb, side, cs + k * (0.2 + sub), sub - 0.3, 1.8, spring - 0.4, spring - 0.4, 0.3, 0.05, 0.5,
                      TR, n=4)
    if med:
        dh, r = med
        disk(mb, side, cs, spring + dh, r, 0.05, d_gl + 0.06, VGLASS, n=12)
        ring(mb, side, cs, spring + dh, r, r + 0.3, 0.05, 0.5, TR, n=12)


def vitrais():
    mb = MB("SG_Hall_Windows", "03_MINING_HALL", random.Random(321), detail="near")
    for side in ("W", "E"):
        for y in WIN_Y:
            lancet(mb, side, y, 3.0, GAL_H + 3.2, 21.8, 3.9, med=(2.3, 0.8))
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


def vault():
    mb = MB("SG_Hall_Vault", "03_MINING_HALL", random.Random(331), detail="near")
    bm = mb.bm
    # panos: casca fechada (intradorso + extradorso 0,35 acima), grade densa junto das paredes
    K = 6
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
    # nervuras alternadas: arcos transversais e formeiros de OBSIDIANA (estrutura), diagonais e cumeeira de PRATA (fio)
    prof = [(-0.5, 0.12), (0.5, 0.12), (0.5, -0.9), (-0.5, -0.9)]
    prof_w = [(-0.35, 0.12), (0.35, 0.12), (0.35, -0.7), (-0.35, -0.7)]
    prof_s = [(-0.26, 0.12), (0.26, 0.12), (0.26, -0.5), (-0.26, -0.5)]
    x_end = HALF_W - 1.3
    tx = sorted(set([x_end * math.sin(0.5 * math.pi * k / 9) for k in range(10)] +
                    [-x_end * math.sin(0.5 * math.pi * k / 9) for k in range(10)]))

    def rib(pts2, pr, m):
        mb.sweep([(x, y, Z + zv(x, y) - 0.02) for x, y in pts2], pr, m)

    for y in VAULT_Y:
        yy = min(max(y, Y0 + 0.5), Y1 - 0.5)
        rib([(x, yy) for x in tx], prof if Y0 < y < Y1 else prof_w, OBS)
    for ya, yb in zip(VAULT_Y, VAULT_Y[1:]):
        if yb - ya < 10.0:
            continue                      # tramos estreitos das pontas: so o arco transversal
        ya2, yb2 = max(ya, Y0 + 0.5), min(yb, Y1 - 0.5)
        n = 12
        for s in (1, -1):
            pts = []
            for k in range(n + 1):
                t = k / n
                x = -x_end + 2 * x_end * t
                pts.append((x * s, ya2 + (yb2 - ya2) * t))
            rib(pts, prof_s, SILVER)
    rib([(0.0, Y0 + 0.5 + (Y1 - Y0 - 1.0) * k / 24.0) for k in range(25)], prof_s, SILVER)
    for s in (-1, 1):
        rib([(s * (HALF_W - 0.45), Y0 + 0.5 + (Y1 - Y0 - 1.0) * k / 44.0) for k in range(45)], prof_w, OBS)
    # chaves: nas linhas das pilastras, disco de obsidiana com o emblema da ordem (face para baixo); nos meios dos
    # tramos, chave simples de obsidiana com aro de prata
    for y in PIER_Y:
        zb = Z + zv(0.0, y) - 1.35
        mb.cyl(1.8, 0.5, (0.0, y, zb + 0.25), m=OBS, n=16, bevel=0.0)
        mb.cyl(1.3, 0.75, (0.0, y, zb + 0.75), m=OBS, n=12, bevel=0.0)
        flat_emblem(mb, 0.0, y, zb, 1.4, -1, rays=False, seg=16, glow=VSOFT)
    for ya, yb in zip(VAULT_Y, VAULT_Y[1:]):
        y = (ya + yb) / 2.0
        if yb - ya < 10.0:
            continue
        zb = Z + zv(0.0, y) - 1.05
        mb.cyl(0.95, 0.6, (0.0, y, zb + 0.3), m=OBS, n=10, bevel=0.0)
        _ann(mb, 0.0, y, 0.6, 0.95, zb - 0.04, zb + 0.02, SILVER, 10)
    finish(mb)


# ------------------------------------------------------------------ FOCO: altar do fundo norte (trono + emblema)
SP = 12.5              # arranque das arquivoltas
PS = 16.4              # eixo dos pilares compostos
AR = [(13.4, 0.9, 2.4, 10.4, OBS), (14.3, 0.8, 1.7, 11.3, VIOST), (15.1, 0.8, 1.0, 12.1, TR)]
STEPS = [(10.0, DAIS_D, 0.45), (8.4, 2.4, 0.9), (6.8, 1.75, 1.35)]     # (meia largura, profundidade, topo)
EMB_H = 16.4           # centro do emblema monumental (acima do trono)


def altar():
    mb = MB("SG_Hall_Altar", "03_MINING_HALL", random.Random(341), detail="hero")
    side = "N"
    # pilares compostos que sustentam a moldura (fora da MINE_RECT: saliencia <= 3)
    for k in (-1, 1):
        s = k * PS
        wbox(mb, side, s - 2.4, s + 2.4, 0.0, 3.0, 0.0, 1.6, OBS, 0.14)
        wbox(mb, side, s - 2.1, s + 2.1, 0.0, 2.8, 1.6, 1.9, TR, 0.06)
        wbox(mb, side, s - 1.7, s + 1.7, 0.0, 2.2, 1.9, SP - 1.0, CS, 0.12)
        wcyl(mb, side, s, 2.2, 1.9, SP - 1.0, 0.8, CS, 8)
        for j in (-1, 1):
            wcyl(mb, side, s + j * 1.9, 0.9, 1.9, SP - 1.0, 0.5, CS, 6)
        wbox(mb, side, s - 2.3, s + 2.3, 0.0, 3.05, SP - 1.35, SP - 1.1, VIOST, 0.0)
        wbox(mb, side, s - 2.5, s + 2.5, 0.0, 3.0, SP - 1.1, SP, TR, 0.12)
        # pinaculo sobre o pilar: agulha de cantaria com remate de prata
        wbox(mb, side, s - 1.1, s + 1.1, 0.4, 2.6, SP, SP + 4.2, CS, 0.08)
        wbox(mb, side, s - 1.4, s + 1.4, 0.2, 2.9, SP + 4.2, SP + 4.8, OBS, 0.08)
        c = wp(side, s, 1.55, SP + 4.8)
        SL.spire(mb, (c[0], c[1]), 1.5, c[2], 5.2, TR, n=4)
        mb.ico(0.4, (c[0], c[1], c[2] + 5.3), SILVER, 1)
        wcol("SG_HallAltar", side, s - 2.4, s + 2.4, 0.0, 3.0, -0.5, SP)
    # retabulo de fundo violeta escuro + 3 arquivoltas escalonadas (obsidiana / pedra violeta / cantaria) e o fio de
    # energia violeta no intradorso
    arch_panel(mb, side, 0.0, AR[0][0], AR[0][3], SP, 0.9, 0.0, 0.2, NI, n=8)
    wbox(mb, side, -14.0, 14.0, 0.0, 0.5, 0.0, 0.9, OBS, 0.06)
    for hw, t, dep, rise, m in AR:
        arch_band(mb, side, 0.0, hw, rise, SP, SP, t, 0.0, dep, m, n=8)
    arch_band(mb, side, 0.0, AR[0][0] - 0.25, AR[0][3] - 0.25, SP, SP, 0.25, 1.9, 2.25, VSOFT, n=8)
    # vitral violeta central (o fundo do emblema) + 2 lancetas de luar com medalhao violeta
    lancet(mb, side, 0.0, 4.4, 11.0, EMB_H, 5.0, m_gl=VGLASS, tracery=False)
    for k in (-1, 1):
        lancet(mb, side, k * 7.9, 1.8, 11.2, 16.0, 3.2, tracery=False, med=(1.2, 0.45))
    # EMBLEMA MONUMENTAL da ordem diante do vitral violeta
    EM.emblem(mb, mb, mb, wp(side, 0.0, 0.45, EMB_H), -math.pi / 2, 3.8, depth=0.8, monumental=True)
    # estandartes da ordem ladeando o trono (verga presa no pilar e numa misula no retabulo)
    for k in (-1, 1):
        s = k * 12.05
        EM.banner(mb, mb, mb, mb, wp(side, s, 1.0, 15.0), -math.pi / 2, 2.8, 10.5)
        wbox(mb, side, s - k * 1.75 - 0.15, s - k * 1.75 + 0.15, 0.2, 1.0, 14.8, 15.2, IRON, 0.0)
    finish(mb)
    throne()


def throne():
    """TRONO DE SHADOW sobre estrado de 3 degraus de obsidiana (fora da zona de minerio: y >= 128,9). Espaldar ogival
    alto com almofada roxa emoldurada de prata, bracos e montantes com agulhas de prata; o tapete sobe os degraus."""
    mb = MB("SG_Hall_Throne", "03_MINING_HALL", random.Random(345), detail="hero")
    side = "N"
    prev = 0.0
    for i, (hw, dd, top) in enumerate(STEPS):
        wbox(mb, side, -hw, hw, 0.0, dd, prev - 0.1 if i == 0 else prev, top, OBS, 0.05)
        wbox(mb, side, -hw - 0.02, hw + 0.02, dd - 0.22, dd + 0.02, top - 0.2, top + 0.02, SILVER, 0.0)
        nxt = STEPS[i + 1][1] if i + 1 < len(STEPS) else 0.3
        wbox(mb, side, -RUN_HW, RUN_HW, nxt, dd - 0.22, top, top + 0.04, CLOTH, 0.0)
        wcol("SG_HallThrone", side, -hw, hw, 0.0, dd, -0.5, top)
        prev = top
    b = STEPS[-1][2]
    # nicho de honra atras do trono: fundo de obsidiana com arco ogival de prata (recorta a silhueta contra o violeta)
    arch_panel(mb, side, 0.0, 4.3, 2.3, 8.0, b, 0.0, 0.22, OBS, n=5)
    arch_band(mb, side, 0.0, 4.3, 2.3, 8.0, b, 0.3, 0.0, 0.35, SILVER, n=5)
    # assento, aro de prata e almofada
    wbox(mb, side, -2.6, 2.6, 0.4, 1.7, b, b + 2.0, OBS, 0.08)
    wbox(mb, side, -2.7, 2.7, 0.35, 1.8, b + 2.0, b + 2.25, SILVER, 0.0)
    wbox(mb, side, -2.2, 2.2, 0.55, 1.65, b + 2.25, b + 2.65, CLOTH, 0.12)
    # bracos
    for k in (-1, 1):
        a0, a1 = sorted((k * 2.6, k * 3.35))
        wbox(mb, side, a0, a1, 0.3, 1.75, b, b + 3.6, OBS, 0.08)
        wbox(mb, side, a0 - 0.08, a1 + 0.08, 0.25, 1.85, b + 3.6, b + 3.85, SILVER, 0.0)
        mb.ico(0.3, wp(side, k * 2.975, 1.7, b + 4.1), SILVER, 1)
    # espaldar ogival: obsidiana, moldura de prata, almofada roxa
    back = [(-2.8, b + 2.0), (2.8, b + 2.0), (2.8, b + 7.8), (0.0, b + 9.65), (-2.8, b + 7.8)]
    slab(mb, side, back, 0.0, 0.55, OBS)
    inner = [(-2.0, b + 2.8), (2.0, b + 2.8), (2.0, b + 7.4), (0.0, b + 8.7), (-2.0, b + 7.4)]
    outer = [(-2.35, b + 2.5), (2.35, b + 2.5), (2.35, b + 7.6), (0.0, b + 9.15), (-2.35, b + 7.6)]
    slab(mb, side, inner, 0.55, 0.68, CLOTH)
    band(mb, side, inner, outer, 0.55, 0.78, SILVER, closed=True)
    # montantes com agulhas de prata
    for k in (-1, 1):
        a0, a1 = sorted((k * 2.8, k * 3.5))
        wbox(mb, side, a0, a1, 0.0, 0.8, b, b + 7.6, OBS, 0.06)
        wbox(mb, side, a0 - 0.1, a1 + 0.1, 0.0, 0.9, b + 7.6, b + 7.9, SILVER, 0.0)
        c = wp(side, k * 3.15, 0.45, b + 7.9)
        SL.spire(mb, (c[0], c[1]), 0.5, c[2], 1.7, SILVER, n=4)
    mb.ico(0.35, wp(side, 0.0, 0.3, b + 9.85), SILVER, 1)
    wcol("SG_HallThrone", side, -3.5, 3.5, 0.0, 1.75, b, b + 7.6)
    finish(mb)


# ------------------------------------------------------------------ ferro: lustres, candeias dos nichos
CHAND = [(-15.0, PIER_Y[1]), (15.0, PIER_Y[1]), (-15.0, PIER_Y[-2]), (15.0, PIER_Y[-2])]
CHAND_H = 19.5


def chandelier(mb, x, y):
    h = CHAND_H
    n = 16
    ring_lo = [(x + 3.2 * math.cos(2 * math.pi * k / n), y + 3.2 * math.sin(2 * math.pi * k / n), Z + h)
               for k in range(n + 1)]
    ring_hi = [(x + 1.9 * math.cos(2 * math.pi * k / n), y + 1.9 * math.sin(2 * math.pi * k / n), Z + h + 1.8)
               for k in range(n + 1)]
    mb.tube(ring_lo, 0.2, IRON, 4)
    mb.tube(ring_hi, 0.16, SILVER, 4)
    mb.cyl(0.5, 3.2, (x, y, Z + h + 1.9), m=IRON, n=8, r2=0.3, bevel=0.0)
    mb.cyl(0.42, 0.9, (x, y, Z + h + 0.35), m=SILVER, n=6, r2=0.08, rot=(math.pi, 0, 0), bevel=0.0)   # pingente
    for k in range(8):
        a = 2 * math.pi * k / 8 + math.pi / 8
        ca, sa = math.cos(a), math.sin(a)
        mb.beam((x + 0.4 * ca, y + 0.4 * sa, Z + h + 2.4), (x + 1.9 * ca, y + 1.9 * sa, Z + h + 1.8), 0.22, 0.22, IRON, 0.0)
        mb.beam((x + 1.9 * ca, y + 1.9 * sa, Z + h + 1.8), (x + 3.2 * ca, y + 3.2 * sa, Z + h), 0.22, 0.22, IRON, 0.0)
        cx, cy = x + 3.2 * ca, y + 3.2 * sa
        mb.cyl(0.36, 0.3, (cx, cy, Z + h + 0.3), m=IRON, n=6, bevel=0.0)
        mb.cyl(0.22, 0.75, (cx, cy, Z + h + 0.8), m="Lantern_Glow", n=6, bevel=0.0)
    # haste ate o arco transversal (o lustre fica no eixo de uma nervura) + ROSETA de ferro aparafusada sob a nervura:
    # o lustre esta visivelmente preso ao teto (acabamento)
    top = zv(x, y) - 0.9
    mb.rod((x, y, Z + h + 2.6), (x, y, Z + top + 0.3), 0.13, IRON, 6)
    mb.cyl(0.62, 0.34, (x, y, Z + top - 0.17), m=IRON, n=8, r2=0.4, rot=(math.pi, 0, 0), bevel=0.0)
    mb.cyl(0.26, 0.3, (x, y, Z + top - 0.45), m=SILVER, n=6, bevel=0.0)


def ironwork():
    mb = MB("SG_Hall_Ironwork", "03_MINING_HALL", random.Random(351), detail="near")
    for x, y in CHAND:
        chandelier(mb, x, y)
    # candeias: uma no fundo de cada nicho da arcada (luz quente baixa no perimetro, contra o violeta escuro)
    spots = [(sd, y) for sd in ("W", "E") for y in WIN_Y] + \
            [("N", k * c) for k in (-1, 1) for c in N_NICHES] + [("S", k * c) for k in (-1, 1) for c in S_NICHES]
    for side, y in spots:
        wbox(mb, side, y - 0.2, y + 0.2, 0.3, 1.3, 8.1, 8.4, IRON, 0.0)
        wcyl(mb, side, y, 1.3, 8.4, 8.75, 0.5, IRON, 6)
        wcyl(mb, side, y, 1.3, 8.75, 9.7, 0.28, "Lantern_Glow", 6)
    finish(mb)


# ------------------------------------------------------------------ estandartes da ordem nas pilastras (4)
def banners():
    mb = MB("SG_Hall_Banners", "03_MINING_HALL", random.Random(361), detail="near")
    for side, yaw in (("W", 0.0), ("E", math.pi)):
        for y in (PIER_Y[1], PIER_Y[3]):
            EM.banner(mb, mb, mb, mb, wp(side, y, 3.4, 18.0), yaw, 2.6, 8.6)
            for k in (-1, 1):
                wbox(mb, side, y + k * 1.15 - 0.12, y + k * 1.15 + 0.12, 1.3, 3.4, 17.86, 18.14, IRON, 0.0)
    finish(mb)


# ------------------------------------------------------------------ luz propria do salao (6)
def lights():
    for (x, y), nm in zip(CHAND, ["SW", "SE", "NW", "NE"]):
        light("L_SGHall_Chandelier_%s" % nm, "POINT", (x, y, Z + CHAND_H - 0.2), 3600.0, (1.0, 0.68, 0.40), 0.8)
    # luar frio pelo vitral noroeste (lado da lua) e o brilho violeta do trono/emblema
    light("L_SGHall_Moon_W", "POINT", (X0 + 6.0, WIN_Y[2], Z + 22.0), 1600.0, (0.58, 0.68, 1.0), 2.0)
    light("L_SGHall_Throne", "POINT", (0.0, Y1 - 6.5, Z + 12.0), 3600.0, (0.60, 0.36, 1.0), 1.5)


def build():
    floor()
    walls()
    vitrais()
    vault()
    altar()
    ironwork()
    banners()
    lights()
