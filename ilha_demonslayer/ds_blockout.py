# ds_blockout - BLOCKOUT da Ilha 4 (DEMON SLAYER), zona por zona (secao 27 do PROMPT_USUARIO): SO massa da ilha,
# entrada, vila (volumes com telhado), clareira, forja (volumes + torre + roda), plato do summon (torre AMS aprovada)
# e saida para One Piece. Materiais simples da paleta DSMATS, sem textura, sem props detalhados, vegetacao so como
# PROXY leve de composicao (copas/touceiras), VFX nenhum, poucas luzes (hierarquia: fornalha > summon > janelas >
# lanternas de no).
# Cada zona cria: massas visuais (detail="far"), a colisao dos PROPRIOS volumes (casas, forja, torii, toro, arvores)
# e as luzes basicas. O chao, as escadas, as pontes, as guardas e TODOS os marcadores sao do ds_core/ds_col (sempre).
# O modulo de detalhe de uma zona SUBSTITUI a funcao dela aqui (build(skip={...})).
import math, random, os
import bmesh
from mathutils import Vector
import ds_lib as DL
from ds_lib import MB, col_box, col_box2, yaw_to, Frame, light, ccw
import fm_lib
import ds_layout as L
import ds_col

ZONES = ["terrain", "entry", "village", "clearing", "forge", "summon", "water", "exit", "dressing"]
T0, T1, T2, T3, T4 = L.T0, L.T1, L.T2, L.T3, L.T4
BASE = 44.0                     # fundo das massas dos patamares (a quilha cobre o resto)
WARM = (1.0, 0.62, 0.30)
fm_lib.MATS.setdefault("PREVIEW_Water", (fm_lib.S(28, 44, 78), 0.08, 0.0, 0.05, fm_lib.S(40, 70, 120), 0.0))


# ------------------------------------------------------------------ primitivas proprias
def faces_solid(mb, verts_co, faces_idx, m):
    """solido a partir de vertices e faces (indices); normais recalculadas no finish"""
    bm = mb.bm
    vs = [bm.verts.new(c) for c in verts_co]
    for f in faces_idx:
        try:
            bm.faces.new([vs[i] for i in f])
        except ValueError:
            pass
    mb._post(vs, m, None, 0, 1)
    return vs


def uz_prism(mb, F, pts_uz, y0, y1, m):
    """prisma de um contorno no plano vertical local (u = x local, z) extrudado de y0 a y1 (eixo y local do Frame)"""
    n = len(pts_uz)
    co = [F.p(u, y0, z) for u, z in pts_uz] + [F.p(u, y1, z) for u, z in pts_uz]
    fs = [list(range(n)), list(range(2 * n - 1, n - 1, -1))]
    for i in range(n):
        j = (i + 1) % n
        fs.append([i, j, n + j, n + i])
    faces_solid(mb, co, fs, m)


def irimoya(mb, F, w, d, z0, rise, over, m="Roof_DS_Tile", ridge_m="Roof_DS_Ridge", gable_m="Wood_DS_Dark", th=0.7):
    """telhado IRIMOYA (silhueta japonesa): saia de 4 aguas (do beiral ate 55% da altura) + empena de 2 aguas em cima,
    com o triangulo da empena recuado; cumeeira com onigawara nas pontas. F = frame no centro da planta (x local ao
    longo de w = cumeeira). Beiral com espessura (th) e balanco (over) em volta."""
    W, Dd = w / 2 + over, d / 2 + over
    z1 = z0 + rise * 0.55
    zr = z0 + rise
    hd = 0.45 * Dd                          # meia profundidade da empena (mesma inclinacao da saia)
    hw = max(W - (Dd - hd), W * 0.55)      # meia largura do topo da saia
    co = [F.p(-W, -Dd, z0), F.p(W, -Dd, z0), F.p(W, Dd, z0), F.p(-W, Dd, z0),
          F.p(-hw, -hd, z1), F.p(hw, -hd, z1), F.p(hw, hd, z1), F.p(-hw, hd, z1),
          F.p(-W, -Dd, z0 - th), F.p(W, -Dd, z0 - th), F.p(W, Dd, z0 - th), F.p(-W, Dd, z0 - th)]
    fs = [[0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7], [4, 5, 6, 7],
          [8, 9, 1, 0], [9, 10, 2, 1], [10, 11, 3, 2], [11, 8, 0, 3], [11, 10, 9, 8]]
    faces_solid(mb, co, fs, m)
    # empena (2 aguas) sobre a saia: um pouco mais larga que o topo da saia (balanco da empena)
    gw = hw + 0.9
    co = [F.p(-gw, -hd - 0.5, z1 - 0.25), F.p(gw, -hd - 0.5, z1 - 0.25), F.p(gw, 0, zr), F.p(-gw, 0, zr),
          F.p(gw, hd + 0.5, z1 - 0.25), F.p(-gw, hd + 0.5, z1 - 0.25),
          F.p(-gw, -hd - 0.5, z1 - 0.25 - th), F.p(gw, -hd - 0.5, z1 - 0.25 - th),
          F.p(gw, hd + 0.5, z1 - 0.25 - th), F.p(-gw, hd + 0.5, z1 - 0.25 - th)]
    fs = [[0, 1, 2, 3], [4, 5, 3, 2], [6, 7, 1, 0], [8, 9, 5, 4], [7, 8, 4, 2, 1], [9, 6, 0, 3, 5], [9, 8, 7, 6]]
    faces_solid(mb, co, fs, m)
    # triangulo da empena (recuado 0,6 do balanco) - madeira escura
    for s in (-1, 1):
        x = s * (gw - 0.6)
        co = [F.p(x, -hd, z1 - 0.1), F.p(x, hd, z1 - 0.1), F.p(x, 0, zr - 0.6),
              F.p(x - s * 0.3, -hd, z1 - 0.1), F.p(x - s * 0.3, hd, z1 - 0.1), F.p(x - s * 0.3, 0, zr - 0.6)]
        faces_solid(mb, co, [[0, 1, 2], [5, 4, 3], [0, 3, 4, 1], [1, 4, 5, 2], [2, 5, 3, 0]], gable_m)
    # cumeeira + onigawara
    mb.box((2 * gw + 0.6, 1.0, 0.9), F.p(0, 0, zr + 0.2), F.r(), ridge_m, 0.0)
    for s in (-1, 1):
        mb.box((0.8, 1.3, 1.8), F.p(s * (gw + 0.2), 0, zr + 0.6), F.r(), ridge_m, 0.0)


def kirizuma(mb, F, w, d, z0, rise, over, m="Roof_DS_Tile", ridge_m="Roof_DS_Ridge", gable_m="Plaster_DS", th=0.6):
    """telhado de 2 aguas (cumeeira ao longo do x local) com empena cheia (gable_m) e beiral com espessura"""
    W, Dd = w / 2 + over, d / 2 + over
    zr = z0 + rise
    co = [F.p(-W, -Dd, z0), F.p(W, -Dd, z0), F.p(W, 0, zr), F.p(-W, 0, zr), F.p(W, Dd, z0), F.p(-W, Dd, z0),
          F.p(-W, -Dd, z0 - th), F.p(W, -Dd, z0 - th), F.p(W, Dd, z0 - th), F.p(-W, Dd, z0 - th)]
    fs = [[0, 1, 2, 3], [4, 5, 3, 2], [6, 7, 1, 0], [8, 9, 5, 4], [7, 8, 4, 2, 1], [9, 6, 0, 3, 5], [9, 8, 7, 6]]
    faces_solid(mb, co, fs, m)
    for s in (-1, 1):
        x = s * (w / 2)
        co = [F.p(x, -d / 2, z0 - 0.05), F.p(x, d / 2, z0 - 0.05), F.p(x, 0, zr - 0.5)]
        co += [F.p(x - s * 0.4, -d / 2, z0 - 0.05), F.p(x - s * 0.4, d / 2, z0 - 0.05), F.p(x - s * 0.4, 0, zr - 0.5)]
        faces_solid(mb, co, [[0, 1, 2], [5, 4, 3], [0, 3, 4, 1], [1, 4, 5, 2], [2, 5, 3, 0]], gable_m)
    mb.box((2 * W + 0.4, 0.9, 0.8), F.p(0, 0, zr + 0.15), F.r(), ridge_m, 0.0)


def hip_roof(mb, F, w, d, z0, rise, over, ridge_len=0.0, m="Roof_DS_Tile", ridge_m="Roof_DS_Ridge", th=0.6):
    """4 aguas (chapeu da torre / pavilhao): cumeeira curta (ridge_len) no x local"""
    W, Dd = w / 2 + over, d / 2 + over
    zr = z0 + rise
    r = ridge_len / 2
    co = [F.p(-W, -Dd, z0), F.p(W, -Dd, z0), F.p(W, Dd, z0), F.p(-W, Dd, z0), F.p(-r - 0.01, 0, zr), F.p(r + 0.01, 0, zr),
          F.p(-W, -Dd, z0 - th), F.p(W, -Dd, z0 - th), F.p(W, Dd, z0 - th), F.p(-W, Dd, z0 - th)]
    fs = [[0, 1, 5, 4], [2, 3, 4, 5], [1, 2, 5], [3, 0, 4], [6, 7, 1, 0], [7, 8, 2, 1], [8, 9, 3, 2], [9, 6, 0, 3],
          [9, 8, 7, 6]]
    faces_solid(mb, co, fs, m)
    if ridge_len > 0.5:
        mb.box((ridge_len + 0.8, 0.9, 0.8), F.p(0, 0, zr + 0.15), F.r(), ridge_m, 0.0)


def timber_box(mb, F, w, d, z0, h, wall_m="Plaster_DS", post_m="Wood_DS_Dark", band=True, posts=True):
    """corpo de parede (reboco) com pilares de canto e frechal de madeira escura (o enxaimel le de longe)"""
    mb.box((w, d, h), F.p(0, 0, z0 + h / 2), F.r(), wall_m, 0.0)
    if posts:
        for sx in (-1, 1):
            for sy in (-1, 1):
                mb.box((0.9, 0.9, h + 0.2), F.p(sx * (w / 2 - 0.15), sy * (d / 2 - 0.15), z0 + h / 2), F.r(), post_m, 0.0)
        n = max(1, int(w / 6.0))
        for k in range(1, n):
            x = -w / 2 + w * k / n
            for sy in (-1, 1):
                mb.box((0.6, 0.5, h), F.p(x, sy * (d / 2 + 0.12), z0 + h / 2), F.r(), post_m, 0.0)
    if band:
        mb.box((w + 0.5, d + 0.5, 0.8), F.p(0, 0, z0 + h - 0.4), F.r(), post_m, 0.0)
        mb.box((w + 0.3, d + 0.3, 0.6), F.p(0, 0, z0 + 0.3), F.r(), post_m, 0.0)


def window(mb, F, u, v_face, z, ww, wh, out=1.0, frame_m="Wood_DS_Dark", glass_m="Window_DS_Warm"):
    """janela acesa RECUADA: moldura de madeira saliente (0,25) com o shoji aceso 0,15 atras da face da moldura;
    out = +1 se a face da parede e +v (frente local +y), -1 se -v. u = posicao ao longo da parede."""
    mb.box((ww + 0.7, 0.35, wh + 0.7), F.p(u, v_face + out * 0.12, z), F.r(), frame_m, 0.0)
    mb.box((ww, 0.2, wh), F.p(u, v_face + out * 0.2, z), F.r(), glass_m, 0.0)


def tree(mb, x, y, z, h, r, m_leaf="Leaf_DS_Broad", m_bark="Bark_DS", lobes=3, rng=None, col=True):
    """arvore larga stylized (PROXY de composicao): tronco + 3 copas achatadas"""
    rng = rng or random.Random(int(x * 7 + y * 3) & 0xffff)
    mb.cyl(r * 0.12 + 0.6, h * 0.55, (x, y, z + h * 0.27), m=m_bark, n=7, r2=r * 0.08 + 0.4, bevel=0.0)
    for k in range(lobes):
        a = 2.4 * k + rng.uniform(0, 1)
        d = r * 0.35 if k else 0.0
        rr = r * (1.0 if k == 0 else 0.7)
        mb.ico(rr, (x + d * math.cos(a), y + d * math.sin(a), z + h * (0.62 + 0.12 * k)), m_leaf, 1,
               scale=(1.0, 1.0, 0.62))
    if col:
        col_box("DS_VegTrunk", (r * 0.24 + 1.0, r * 0.24 + 1.0, 8.0), (x, y, z + 4.0))


def cedar(mb, x, y, z, h, rng=None):
    mb.cyl(0.6, h * 0.35, (x, y, z + h * 0.17), m="Bark_DS", n=6, bevel=0.0)
    for k, (fr, fz) in enumerate(((1.0, 0.32), (0.72, 0.56), (0.42, 0.78))):
        mb.cyl(h * 0.17 * fr, h * 0.32, (x, y, z + h * fz), m="Leaf_DS_Cedar", n=7, r2=0.2, bevel=0.0)


def bamboo_clump(mb, x, y, z, h, rng):
    for k in range(6):
        a = rng.uniform(0, 6.28)
        d = rng.uniform(0.0, 2.2)
        hh = h * rng.uniform(0.75, 1.05)
        px, py = x + d * math.cos(a), y + d * math.sin(a)
        mb.cyl(0.32, hh, (px, py, z + hh / 2), m="Bamboo_DS", n=5, bevel=0.0)
    mb.ico(3.2, (x, y, z + h * 0.88), "Leaf_DS_Shrub", 1, scale=(1.0, 1.0, 1.6))


def wisteria(mb, x, y, z, h=10.0, r=6.0):
    """glicinia (ACENTO, PROXY): tronco em S simplificado + copa em guarda-chuva + cachos conicos pendentes"""
    mb.cyl(0.7, h * 0.7, (x, y, z + h * 0.35), m="Bark_DS", n=7, r2=0.5, bevel=0.0)
    mb.ico(r, (x, y, z + h * 0.82), "Leaf_DS_Shrub", 1, scale=(1.0, 1.0, 0.35))
    for k in range(8):
        a = k * math.pi / 4 + 0.3
        mb.cyl(1.1, 3.2, (x + r * 0.75 * math.cos(a), y + r * 0.75 * math.sin(a), z + h * 0.82 - 2.0),
               m="Wisteria_DS" if k % 2 else "Wisteria_DS_Light", n=6, r2=0.15, bevel=0.0)
    col_box("DS_VegTrunk", (1.6, 1.6, 6.0), (x, y, z + 3.0))


def lantern_post(mb, x, y, z, h=7.0, name_light=None, energy=180.0):
    """lanterna de poste (PROXY de blockout): pilar, braco, caixa com armacao escura e papel aceso DENTRO, chapeu"""
    mb.box((0.7, 0.7, h), (x, y, z + h / 2), (0, 0, 0), "Wood_DS_Dark", 0.0)
    mb.box((1.9, 1.9, 0.35), (x, y, z + h + 0.15), (0, 0, 0), "Wood_DS_Dark", 0.0)
    mb.box((1.3, 1.3, 1.6), (x, y, z + h + 1.15), (0, 0, 0), "Glass_DS_Lantern", 0.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.box((0.22, 0.22, 1.7), (x + sx * 0.7, y + sy * 0.7, z + h + 1.15), (0, 0, 0), "Wood_DS_Dark", 0.0)
    mb.cyl(1.5, 0.7, (x, y, z + h + 2.3), m="Roof_DS_Ridge", n=4, r2=0.2, bevel=0.0, rot=(0, 0, math.pi / 4))
    col_box("DS_PropLamp", (0.8, 0.8, h), (x, y, z + h / 2))
    if name_light:
        light(name_light, "POINT", (x, y, z + h + 1.0), energy, WARM, 0.4)


def toro(mb, x, y, z, s=1.0, name_light=None):
    """lanterna de pedestal (toro, PROXY): base, fuste, camara com papel aceso recuado, chapeu, hoju"""
    mb.box((2.6 * s, 2.6 * s, 0.6 * s), (x, y, z + 0.3 * s), (0, 0, 0), "Stone_DS", 0.0)
    mb.cyl(0.55 * s, 2.6 * s, (x, y, z + 1.9 * s), m="Stone_DS", n=8, bevel=0.0)
    mb.box((2.0 * s, 2.0 * s, 0.4 * s), (x, y, z + 3.4 * s), (0, 0, 0), "Stone_DS", 0.0)
    mb.box((1.7 * s, 1.7 * s, 1.5 * s), (x, y, z + 4.35 * s), (0, 0, 0), "Stone_DS", 0.0)
    mb.box((1.76 * s, 1.0 * s, 0.9 * s), (x, y, z + 4.35 * s), (0, 0, 0), "Glass_DS_Lantern", 0.0)
    mb.box((1.0 * s, 1.76 * s, 0.9 * s), (x, y, z + 4.35 * s), (0, 0, 0), "Glass_DS_Lantern", 0.0)
    mb.cyl(1.9 * s, 1.0 * s, (x, y, z + 5.6 * s), m="Stone_DS", n=6, r2=0.4 * s, bevel=0.0)
    mb.ico(0.4 * s, (x, y, z + 6.4 * s), "Stone_DS", 1)
    col_box("DS_PropToro", (2.6 * s, 2.6 * s, 6.0 * s), (x, y, z + 3.0 * s))
    if name_light:
        light(name_light, "POINT", (x, y, z + 4.35 * s), 160.0, WARM, 0.3)


def torii(mb, x, y, z, ang, w=None, h=None, area="DS_EntTorii"):
    """torii de laca vermelha escura com kasagi de telha escura (o 2o e ultimo: entrada e saida). ang = rumo de quem
    atravessa (rad); vao livre w x h"""
    w = w or L.TORII_W
    h = h or L.TORII_H
    F = Frame(x, y, z, ang - math.pi / 2)        # +x local = atravessado; +y local = quem atravessa
    px = w / 2 + 0.9
    for s in (-1, 1):
        mb.cyl(1.2, 0.8, F.p(s * px, 0, 0.4), m="Stone_DS_Dark", n=10, bevel=0.0)
        mb.cyl(0.9, h + 2.2, F.p(s * px, 0, 0.8 + (h + 2.2) / 2), m="Wood_DS_Lacquer", n=12, r2=0.82, bevel=0.0)
        col_box(area, (2.2, 2.2, h + 3.0), F.p(s * px, 0, (h + 3.0) / 2), F.r())
    mb.box((w + 6.4, 1.0, 1.1), F.p(0, 0, h - 0.8), F.r(), "Wood_DS_Lacquer", 0.0)            # nuki
    mb.box((0.9, 0.8, 2.4), F.p(0, 0, h + 0.9), F.r(), "Wood_DS_Lacquer", 0.0)              # gakuzuka
    mb.box((w + 7.0, 1.6, 1.0), F.p(0, 0, h + 2.4), F.r(), "Wood_DS_Lacquer", 0.0)          # shimaki
    # kasagi com as pontas levantadas (3 pecas) e telha escura por cima
    span = w + 9.0
    mb.box((span * 0.6, 2.2, 0.9), F.p(0, 0, h + 3.35), F.r(), "Roof_DS_Ridge", 0.0)
    for s in (-1, 1):
        mb.box((span * 0.24, 2.2, 0.9), F.p(s * span * 0.39, 0, h + 3.55), F.r(0, -s * 0.12, 0), "Roof_DS_Ridge", 0.0)
    mb.box((span * 0.62, 2.6, 0.5), F.p(0, 0, h + 4.0), F.r(), "Roof_DS_Tile", 0.0)


# ------------------------------------------------------------------ terreno
def _edge_walls(mb, nm, poly, z, mat="Stone_DS", cap="Stone_DS_Path"):
    """muro de arrimo (ishigaki do blockout) nas bordas INTERNAS: onde o vizinho e um piso mais baixo (> 1). Fica do
    lado de baixo, cobrindo a face do patamar de cima; aberto nas escadas e pontes; capa 0,4 acima do piso de cima."""
    pts = ccw(poly)
    n = len(pts)
    zf = lambda x, y: L._zval(z, x, y)
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy)
        if ln < 0.5:
            continue
        nx, ny = dy / ln, -dx / ln
        k = max(1, int(ln / 1.5))
        run = []

        def flush(run):
            if len(run) < 2:
                return
            p0, p1 = run[0], run[-1]
            zt = max(zf(*p0), zf(*p1))
            zb = min(min(L.zone_of(p[0] + nx * 1.6, p[1] + ny * 1.6) or zt for p in run), zt) - 0.6
            sl = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
            cx, cy = (p0[0] + p1[0]) / 2 + nx * 0.55, (p0[1] + p1[1]) / 2 + ny * 0.55
            ang = math.atan2(dy, dx)
            mb.box((sl + 1.2, 1.1, zt - zb), (cx, cy, (zb + zt) / 2), (0, 0, ang), mat, 0.0)
            mb.box((sl + 1.3, 1.5, 0.45), (cx - nx * 0.2, cy - ny * 0.2, zt + 0.2), (0, 0, ang), cap, 0.0)
        for s in range(k + 1):
            t = s / k
            x, y = a[0] + dx * t, a[1] + dy * t
            ok = L.floor_name(x - nx * 0.6, y - ny * 0.6) == nm
            zo = L.zone_of(x + nx * 1.6, y + ny * 1.6)
            ok = ok and zo is not None and zf(x, y) - zo > 1.0 and not ds_col.opening(x + nx * 1.6, y + ny * 1.6)
            if ok:
                run.append((x, y))
            else:
                flush(run)
                run = []
        flush(run)


def terrain():
    rng = random.Random(11)
    rim = DL.rim()
    c = DL.centroid(rim)
    # quilha em ESTRATOS horizontais (faixas recuadas/salientes alternadas, quinas com musgo): penhasco cinza-azulado
    mk = MB("DS_Ter_Keel", "02_TERRAIN", rng, detail="far", floor=-999)
    mk.prism(rim, 36.0, L.SHOULDER - 0.4, "Cliff_DS")
    mk.prism(rim, L.SHOULDER - 0.4, L.SHOULDER, "Cliff_DS_Moss")
    # estratos: recuo/saliencia de cada faixa varia em volta da ilha (senoides dirigidas) e as faixas tem alturas
    # diferentes -> quebra o "bolo em camadas" sem sorteio
    sw = lambda k, ph, amp, base: (lambda i, a: base + amp * math.sin(k * a + ph) + 0.5 * amp * math.sin((k + 3) * a + 2 * ph))
    mk.prism(ccw(DL.offset_poly_var(rim, sw(3, 0.4, 2.2, -2.4))), 27.0, 36.0, "Cliff_DS_Dark")
    mk.prism(ccw(DL.offset_poly_var(rim, sw(4, 1.7, 2.6, 0.6))), 14.0, 27.0, "Cliff_DS")
    mk.prism(ccw(DL.scale_poly(DL.offset_poly_var(rim, sw(5, 2.9, 3.0, -2.0)), 0.92, c)), 4.0, 14.0, "Cliff_DS_Dark")
    mk.prism(ccw(DL.scale_poly(DL.offset_poly_var(rim, sw(3, 0.9, 6.0, -4.0)), 0.8, c)), -10.0, 4.0, "Cliff_DS")
    mk.prism(ccw(DL.scale_poly(DL.offset_poly_var(rim[::2], sw(2, 2.2, 8.0, -6.0)), 0.6, c)), -22.0, -10.0, "Cliff_DS_Dark")
    mk.prism(ccw(DL.scale_poly(rim[::3], 0.3, c)), L.KEEL, -22.0, "Cliff_DS")
    mk.finish()
    # patamares (pisos): massa de penhasco ate o piso + tampo do material do chao
    top = {"Entry": "Stone_DS_Path", "T1": "Grass_DS", "VillageHigh": "Grass_DS", "Berm": "Grass_DS",
           "Summon": "Stone_DS", "Forge": "Dirt_DS_Dark", "ExitLand": "Grass_DS", "Bamboo": "Grass_DS"}
    mt = MB("DS_Ter_Terraces", "02_TERRAIN", rng, detail="far", floor=-999)
    for nm, poly, z, pr in L.floors():
        if callable(z):
            DL.sloped_prism(mt, poly, BASE, z, "Cliff_DS", top_m=top[nm])
            continue
        for piece in L.floor_pieces(nm):          # sem os entalhes das escadas (a escada e cortada no arrimo)
            DL.prism(mt, piece, BASE, z, "Cliff_DS", top_m=top[nm])
    for nm, up, rect, zf, zt in L.stair_notches():
        fill = L.clip_rect(ccw(L.floor_poly(up)), rect) if up else []
        if len(fill) >= 3:                        # fundo do entalhe ate a cota do pe (o chao de baixo continua)
            low = L.floor_name(*L.stair_frame(nm)[0][:2])
            DL.prism(mt, fill, BASE, zf, "Cliff_DS", top_m=top.get(low, "Grass_DS"))
    mt.finish()
    # arrimos (ishigaki do blockout) nas bordas internas entre patamares
    mw = MB("DS_Ter_RetainingWalls", "02_TERRAIN", rng, detail="far", floor=-999)
    for nm, poly, z, pr in L.floors():
        _edge_walls(mw, nm, poly, z)
    mw.finish()
    # crista oeste (gargalo da trilha), barranco nordeste (cascata) e rochas da montanha atras da forja
    mr = MB("DS_Ter_Rocks", "02_TERRAIN", rng, detail="far", floor=-999)
    DL.prism(mr, L.WEST_RIDGE, BASE, L.WEST_RIDGE_Z, "Cliff_DS", top_m="Cliff_DS_Moss")
    for x, y, r, h in ((-44.0, 34.0, 8.0, 74.0), (-50.0, 66.0, 7.0, 76.0), (-54.0, 92.0, 6.0, 72.0)):
        DL.prism(mr, DL.blob_poly(x, y, r, 9, rng, 0.2), L.WEST_RIDGE_Z - 1.0, h, "Cliff_DS")
    DL.prism(mr, L.NE_BANK, BASE, L.NE_BANK_Z, "Cliff_DS", top_m="Cliff_DS_Moss")
    for x, y, r, h in ((140.0, 400.0, 6.0, 80.0), (134.0, 360.0, 6.0, 77.0)):
        DL.prism(mr, DL.blob_poly(x, y, r, 9, rng, 0.2), L.NE_BANK_Z - 1.0, h, "Cliff_DS")
    DL.prism(mr, L.BACK_ROCKS, BASE, 90.0, "Cliff_DS", top_m="Cliff_DS_Moss")
    # rochas da montanha (Tier C): moldura da silhueta da forja; a da nascente passa de 104
    for x, y, r, h in ((-50.0, 548.0, 16.0, 100.0), (-6.0, 560.0, 20.0, 108.0), (40.0, 556.0, 18.0, 104.0),
                       (82.0, 540.0, 15.0, 98.0), (104.0, 552.0, 11.0, 110.0), (-30.0, 572.0, 12.0, 96.0),
                       (18.0, 576.0, 10.0, 94.0)):
        DL.prism(mr, DL.blob_poly(x, y, r, 10, rng, 0.18), 89.0, h - 4.0, "Cliff_DS")
        DL.prism(mr, DL.blob_poly(x, y, r * 0.78, 9, rng, 0.18), h - 4.0, h, "Cliff_DS_Moss")
    mr.finish()


# ------------------------------------------------------------------ entrada: ponte de 100, torii, patio, toro, escada
def entry():
    rng = random.Random(33)
    mb = MB("DS_Ent_Blockout", "18_ENTRY", rng, detail="far", floor=-999)
    ln = L.BRIDGE_IN_LEN
    pitch = math.atan2(L.T0 - L.DECK, ln)
    zc = (L.DECK + L.T0) / 2
    mb.box((L.DECK_W, ln + 0.5, 1.2), (0.0, L.PREV_Y + ln / 2, zc - 0.6), (pitch, 0, 0), "Wood_DS_Mid", 0.0)
    for s in (-1, 1):
        x = s * (L.DECK_W / 2 + 0.4)
        mb.box((0.9, ln + 0.5, 1.4), (x, L.PREV_Y + ln / 2, zc - 0.5), (pitch, 0, 0), "Wood_DS_Dark", 0.0)  # viga de bordo
        mb.box((0.5, ln + 0.5, 0.45), (x, L.PREV_Y + ln / 2, zc + 3.6), (pitch, 0, 0), "Wood_DS_Dark", 0.0)  # corrimao
        for k in range(0, int(ln) + 1, 5):
            y = L.PREV_Y + k
            zz = L.DECK + (L.T0 - L.DECK) * k / ln
            mb.box((0.6, 0.6, 3.8), (x, y, zz + 1.9), (0, 0, 0), "Wood_DS_Dark", 0.0)
    # pilares (pares de estacas com travessa) a cada 20 e o patamar de descanso no meio com 2 postes-lanterna
    for k in (14, 34, 54, 74, 92):
        y = L.PREV_Y + k
        zz = L.DECK + (L.T0 - L.DECK) * k / ln
        for s in (-1, 1):
            mb.box((1.4, 1.4, zz - 12.0), (s * 7.0, y, (zz + 12.0) / 2 - 0.6), (0, 0, 0), "Wood_DS_Dark", 0.0)
        mb.box((16.0, 1.2, 1.2), (0.0, y, zz - 4.0), (0, 0, 0), "Wood_DS_Dark", 0.0)
        mb.box((14.0, 0.8, 0.8), (0.0, y, zz - 9.0), (0, 0, 0), "Wood_DS_Dark", 0.0)
    for s in (-1, 1):
        zz = L.DECK + (L.T0 - L.DECK) * 0.5
        lantern_post(mb, s * (L.DECK_W / 2 + 0.4), L.PREV_Y + 50.0, zz, 6.0,
                     "L_DSProp_Lamp_Bridge_%s" % ("L" if s < 0 else "R"), 160.0)
    # soleira de pedra escura na ancora (a pedra da SG que entra) e encontro de pedra no patio
    mb.box((L.DECK_W + 3.0, 10.0, 1.6), (0.0, L.PREV_Y + 5.0, L.DECK - 0.75), (pitch, 0, 0), "Stone_DS_Dark", 0.0)
    mb.box((L.DECK_W + 6.0, 6.0, 12.0), (0.0, -3.5, L.T0 - 6.2), (0, 0, 0), "Stone_DS", 0.0)
    # torii de entrada + 2 toro (as unicas luzes do patio)
    tx, ty = L.TORII_IN
    torii(mb, tx, ty, T0, math.pi / 2)
    toro(mb, -12.0, 16.0, T0, 1.0, "L_DSProp_Toro_In_L")
    toro(mb, 12.0, 16.0, T0, 1.0, "L_DSProp_Toro_In_R")
    DL.plan_stair(mb, "Trilha")
    mb.finish()


# ------------------------------------------------------------------ vila (6 construcoes + poco + oratorio + portao)
def house(mb, spec):
    nm, tp, x, y, w, d, deg, z, fl = spec
    F = Frame(x, y, z, math.radians(deg) - math.pi / 2)     # +y local = FRENTE (rumo deg); x local ao longo da fachada
    # a planta da w (x do mundo) x d (y do mundo); com rumo 0 (frente +X) a fachada corre em y do mundo (d)
    fw, fd = d, w                                            # fachada (x local) x fundo (y local)
    soco = 1.2 if z == T1 else 1.6
    mb.box((fw + 1.0, fd + 1.0, soco), F.p(0, 0, soco / 2), F.r(), "Stone_DS", 0.0)
    z0 = soco
    if nm == "V1":                                           # pavilhao aberto (chaya): estrado, postes e telhado
        mb.box((fw, fd, 0.5), F.p(0, 0, z0 + 0.25), F.r(), "Wood_DS_Mid", 0.0)
        for sx in (-1, 1):
            for sy in (-1, 0, 1):
                mb.box((0.8, 0.8, 7.0), F.p(sx * (fw / 2 - 0.6), sy * (fd / 2 - 0.6), z0 + 3.5), F.r(), "Wood_DS_Dark", 0.0)
        mb.box((fw * 0.7, 0.4, 3.0), F.p(0, fd / 2 - 0.4, z0 + 5.3), F.r(), "Cloth_DS_Red", 0.0)   # noren
        hip_roof(mb, F, fw, fd, z0 + 7.0, 4.5, 2.2, ridge_len=fw * 0.4)
        for sx in (-1, 1):
            col_box("DS_VilHouse%s" % nm, (0.9, fd, 7.0), F.p(sx * (fw / 2 - 0.6), 0, z0 + 3.5), F.r())
        return
    h1 = {"V2": 7.0, "V3": 7.5, "V4": 15.0, "V5": 7.0, "V6": 8.5}[nm]
    wall = "Plaster_DS_Kura" if nm == "V4" else "Plaster_DS"
    if nm == "V4":                                           # kura: soco alto + faixa escura + paredes brancas grossas
        mb.box((fw + 0.4, fd + 0.4, 2.0), F.p(0, 0, z0 + 1.0), F.r(), "Stone_DS_Dark", 0.0)
        mb.box((fw, fd, h1), F.p(0, 0, z0 + h1 / 2), F.r(), wall, 0.0)
        mb.box((fw + 0.3, fd + 0.3, 0.6), F.p(0, 0, z0 + 9.0), F.r(), "Wood_DS_Dark", 0.0)
        mb.box((3.0, 0.4, 5.0), F.p(0, fd / 2 + 0.15, z0 + 2.5 + 2.0), F.r(), "Metal_DS_Iron", 0.0)   # porta de ferro
        window(mb, F, 0.0, fd / 2, z0 + 11.5, 1.6, 1.6)
        kirizuma(mb, F, fw, fd, z0 + h1, 4.0, 1.4, gable_m="Plaster_DS_Kura")
    else:
        timber_box(mb, F, fw, fd, z0, h1, wall)
        if nm == "V3":                                       # oficina: frente aberta (vao escuro) com toldo
            mb.box((fw * 0.62, 0.3, 5.2), F.p(0, fd / 2 + 0.16, z0 + 2.8), F.r(), "Wood_DS_Dark", 0.0)
            mb.box((fw * 0.56, 0.3, 4.6), F.p(0, fd / 2 + 0.32, z0 + 2.6), F.r(), "Window_DS_Warm", 0.0)
            mb.box((fw * 0.8, 3.0, 0.35), F.p(0, fd / 2 + 1.5, z0 + 5.8), F.r(-0.25, 0, 0), "Roof_DS_Tile", 0.0)
        else:
            for u in (-fw * 0.28, fw * 0.28):
                window(mb, F, u, fd / 2, z0 + 3.6, 2.6, 2.0)
            mb.box((2.8, 0.35, 5.0), F.p(0, fd / 2 + 0.14, z0 + 2.5), F.r(), "Wood_DS_Dark", 0.0)       # porta
        if nm in ("V2", "V6"):                               # engawa na frente
            mb.box((fw + 1.0, 3.0, 0.5), F.p(0, fd / 2 + 1.5, z0 - 0.2), F.r(), "Wood_DS_Mid", 0.0)
        if nm == "V5":                                       # 2o piso recuado + sacada para a clareira + saia de telhado
            hip_roof(mb, F, fw, fd, z0 + h1 + 0.2, 1.6, 1.8, ridge_len=fw)
            timber_box(mb, F, fw - 2.0, fd - 2.0, z0 + h1, 6.0, wall)
            window(mb, F, 0.0, (fd - 2.0) / 2, z0 + h1 + 3.0, 4.0, 1.8)
            mb.box((fw - 4.0, 2.0, 0.4), F.p(0, (fd - 2.0) / 2 + 1.0, z0 + h1 + 0.8), F.r(), "Wood_DS_Mid", 0.0)
            mb.box((fw - 4.0, 0.3, 1.2), F.p(0, (fd - 2.0) / 2 + 1.9, z0 + h1 + 1.5), F.r(), "Wood_DS_Dark", 0.0)
            irimoya(mb, F, fw - 2.0, fd - 2.0, z0 + h1 + 6.0, 5.5, 2.2)
        else:
            rise = {"V2": 6.0, "V3": 5.5, "V6": 8.0}[nm]
            irimoya(mb, F, fw, fd, z0 + h1, rise, 2.6 if nm == "V6" else 2.2)
    col_box("DS_VilHouse%s" % nm, (fw + 0.4, fd + 0.4, h1 + soco), F.p(0, 0, (h1 + soco) / 2), F.r())
    light("L_DSVil_Win_%s" % nm, "POINT", F.p(0, fd / 2 + 2.0, z0 + 3.0), 90.0, WARM, 0.4)


def village():
    rng = random.Random(55)
    mb = MB("DS_Vil_Blockout", "05_VILLAGE", rng, detail="far", floor=None)
    for spec in L.HOUSES:
        house(mb, spec)
    # V6: muro baixo do jardim + portao proprio (kabuki-mon) + a glicinia em trelica (acento) fica no dressing
    nm, tp, x, y, w, d, deg, z, fl = L.HOUSES[-1]
    gx0, gx1, gy0, gy1 = x - w / 2 - 6.0, x + w / 2 + 10.0, y - d / 2 - 4.0, y + d / 2 + 6.0
    for p0, p1 in (((gx1, gy0), (gx1, y - 4.0)), ((gx1, y + 4.0), (gx1, gy1)), ((gx0, gy1), (gx1, gy1))):
        DL.wall_ribbon(mb, [p0, p1], z, z + 2.6, 0.8, "Plaster_DS", cap_m="Roof_DS_Tile", cap_h=0.5)
        col_box2("DS_VilWall", (min(p0[0], p1[0]) - 0.6, min(p0[1], p1[1]) - 0.6, z),
                 (max(p0[0], p1[0]) + 0.6, max(p0[1], p1[1]) + 0.6, z + 2.6))
    F = Frame(gx1 + 0.4, y, z, 0.0)
    for s in (-1, 1):
        mb.box((0.9, 0.9, 6.5), F.p(0, s * 4.6, 3.25), F.r(), "Wood_DS_Dark", 0.0)
        col_box("DS_VilGate", (1.0, 1.0, 6.5), F.p(0, s * 4.6, 3.25), F.r())
    kirizuma(mb, Frame(gx1 + 0.4, y, z, math.pi / 2), 11.0, 2.4, z + 6.5 - z, 1.4, 0.8, gable_m="Wood_DS_Dark")
    # rua da vila (lajes claras sobre o chao) e portao de postes com lanternas (nao e torii)
    mp = MB("DS_Vil_Street", "05_VILLAGE", rng, detail="far", floor=-999)
    for pts, zz in ((L.VILLAGE_STREET, T1), (L.VILLAGE_STREET_HIGH, T2)):
        poly = L.ribbon(pts, 3.5)
        mp.prism(ccw(poly), zz - 0.2, zz + 0.12, "Stone_DS_Path")
    mp.finish()
    gx, gy = L.VILLAGE_GATE
    (ax_, ay_), (bx_, by_) = L.VILLAGE_STREET[0], L.VILLAGE_STREET[2]
    sl = math.hypot(bx_ - ax_, by_ - ay_)
    px_, py_ = (by_ - ay_) / sl, -(bx_ - ax_) / sl              # perpendicular a rua no portao
    for s in (-1, 1):
        lantern_post(mb, gx + s * 4.6 * px_, gy + s * 4.6 * py_, T1, 8.5,
                     "L_DSProp_Lamp_VilGate_%s" % ("L" if s < 0 else "R"), 140.0)
    mb.box((2.0, 1.2, 3.4), (gx - 6.5, gy - 4.0, T1 + 1.7), (0, 0, 0.5), "Stone_DS", 0.0)       # marco de pedra
    col_box("DS_VilMarker", (2.0, 1.2, 3.4), (gx - 6.5, gy - 4.0, T1 + 1.7), (0, 0, 0.5))
    for nm in ("VilaAlta", "VilaClareira", "OesteForja"):
        DL.plan_stair(mb, nm)
    # poco coberto + oratorio (hokora) na borda oeste da clareira
    wx, wy = L.WELL
    mb.cyl(2.2, 1.6, (wx, wy, T1 + 0.8), m="Stone_DS", n=10, bevel=0.0)
    for s in (-1, 1):
        mb.box((0.5, 0.5, 6.0), (wx + s * 2.6, wy, T1 + 3.0), (0, 0, 0), "Wood_DS_Dark", 0.0)
    kirizuma(mb, Frame(wx, wy, T1, 0.0), 6.4, 5.0, 6.0, 1.6, 0.4, gable_m="Wood_DS_Dark")
    col_box("DS_VilWell", (5.0, 5.0, 6.0), (wx, wy, T1 + 3.0))
    hx, hy = L.HOKORA
    mb.box((2.4, 2.0, 1.2), (hx, hy, T1 + 0.6), (0, 0, 0), "Stone_DS", 0.0)
    mb.box((1.8, 1.6, 1.8), (hx, hy, T1 + 2.1), (0, 0, 0), "Wood_DS_Dark", 0.0)
    kirizuma(mb, Frame(hx, hy, T1, 0.0), 1.8, 1.6, 3.0, 0.9, 0.4, gable_m="Wood_DS_Dark")
    col_box("DS_VilHokora", (2.4, 2.0, 3.6), (hx, hy, T1 + 1.8))
    lantern_post(mb, -64.0, 232.0, T2, 7.0, "L_DSProp_Lamp_VilAlta", 130.0)
    lantern_post(mb, -60.0, 336.0, T2, 7.0, "L_DSProp_Lamp_OesteForja", 130.0)
    mb.finish()


# ------------------------------------------------------------------ clareira (chao, bordas, cercas em setores)
def clearing(ore_proxies=False):
    rng = random.Random(66)
    mb = MB("DS_Clr_Ground", "03_CLEARING", rng, detail="far", floor=-999)
    mb.prism(ccw(L.CLEARING), T1 - 0.3, T1 + 0.1, "Dirt_DS")
    # manchas de grama SO na borda (o meio fica livre e legivel)
    for x, y, r in ((-30.0, 150.0, 9.0), (8.0, 140.0, 7.0), (90.0, 170.0, 10.0), (112.0, 220.0, 7.0),
                    (-34.0, 240.0, 8.0), (-36.0, 320.0, 9.0), (110.0, 300.0, 6.0), (60.0, 372.0, 8.0),
                    (-12.0, 360.0, 7.0), (112.0, 350.0, 7.0)):
        mb.prism(ccw(DL.blob_poly(x, y, r, 10, rng, 0.25)), T1 - 0.2, T1 + 0.22, "Grass_DS_B")
    mb.finish()
    mf = MB("DS_Clr_Edges", "03_CLEARING", rng, detail="far", floor=None)
    # cerca baixa SO em setores: borda do bambuzal (sul-leste), junto da vila e no pe da subida
    for pts in ([(36.0, 133.0), (56.0, 138.0)], [(76.0, 145.0), (98.0, 155.0)], [(-42.0, 214.0), (-44.0, 256.0)],
                [(-20.0, 369.0), (8.0, 377.0)], [(26.0, 378.5), (54.0, 380.0), (76.0, 382.0)]):
        DL.vis_fence(mf, [(x, y, T1) for x, y in pts], h=2.6)
    # pedras soltas so nas bordas (fora da zona + 6)
    for x, y, r in ((-40.0, 176.0, 2.2), (-42.0, 296.0, 1.8), (120.0, 200.0, 2.0), (96.0, 160.0, 1.6),
                    (-24.0, 366.0, 1.8), (112.0, 326.0, 1.6)):
        mf.rock((x, y, T1 + r * 0.3), (r * 2.0, r * 1.6, r * 1.3), "Stone_DS", 1, jitter=0.2)
        col_box("DS_ClrRock", (r * 1.6, r * 1.3, r * 1.2), (x, y, T1 + r * 0.6))
    mf.finish()
    if ore_proxies:
        mo = MB("DS_Clr_OreProxy", "03_CLEARING", rng, detail="far", floor=-999)
        for kind, i, x, y, r in L.ore_points():
            mo.cyl(r * 0.6, r * 0.9, (x, y, T1 + r * 0.45), m="DS_OreProxy", n=6, r2=r * 0.25, bevel=0.0)
        mo.finish()


# ------------------------------------------------------------------ forja (heroi): salao, torre-chamine, oficina, ala, roda
def forge():
    rng = random.Random(77)
    mb = MB("DS_Frg_Blockout", "04_FORGE", rng, detail="far", floor=None)
    z = T4
    # patio de trabalho (lajes) e patio do carvao (terra)
    x0, y0, x1, y1 = L.FORGE_YARD
    mb.box2((x0, y0, z - 0.2), (x1, y1, z + 0.12), "Stone_DS", 0.0)
    # SALAO DA FORNALHA: soco de pedra escura (3) + parede de reboco com enxaimel ate o beiral 13 + irimoya ate 24 +
    # lanternim de fumaca na cumeeira; boca da fornalha 10 x 9 em arco na fachada sul, NO EIXO, acesa
    hx0, hy0, hx1, hy1, eave, ridge = L.FORGE["hall"]
    F = Frame((hx0 + hx1) / 2, (hy0 + hy1) / 2, z, 0.0)
    w, d = hx1 - hx0, hy1 - hy0
    mb.box((w + 1.2, d + 1.2, 3.0), F.p(0, 0, 1.5), F.r(), "Stone_DS_Dark", 0.0)
    timber_box(mb, F, w, d, 3.0, eave - 3.0)
    irimoya(mb, F, w, d, eave, ridge - eave, 3.2)
    mb.box((10.0, 5.0, 3.0), F.p(0, 0, ridge + 1.6), F.r(), "Wood_DS_Dark", 0.0)            # lanternim (koshi-yane)
    hip_roof(mb, F, 10.0, 5.0, ridge + 3.1, 1.8, 1.0, ridge_len=8.0)
    fx, fy, fw, fh = L.FURNACE_MOUTH
    Fm = Frame(fx, fy, z, 0.0)
    arch = [(-fw / 2 - 2.2, 0.0), (fw / 2 + 2.2, 0.0), (fw / 2 + 2.2, fh + 2.6), (-fw / 2 - 2.2, fh + 2.6)]
    uz_prism(mb, Fm, arch, -1.6, 0.2, "Stone_DS_Dark")                                       # moldura de pedra
    mouth = [(-fw / 2, 0.0), (fw / 2, 0.0), (fw / 2, fh - fw / 2)] + \
        [(fw / 2 * math.cos(math.radians(a)), fh - fw / 2 + fw / 2 * math.sin(math.radians(a))) for a in range(15, 180, 15)] + \
        [(-fw / 2, fh - fw / 2)]
    uz_prism(mb, Fm, mouth, -1.75, -1.55, "Ember_DS_Glow")                                     # boca (arco) acesa
    inner = [(-fw / 2 + 1.2, 0.0), (fw / 2 - 1.2, 0.0), (fw / 2 - 1.2, fh - 3.0), (-fw / 2 + 1.2, fh - 3.0)]
    uz_prism(mb, Fm, inner, -1.9, -1.78, "Fire_DS_Glow")                                       # fogo la dentro
    col_box("DS_FrgHall", (w + 1.2, d + 1.2, eave), F.p(0, 0, eave / 2), F.r())
    light("L_DSFrg_Furnace", "POINT", (fx, fy - 3.0, z + 4.0), 2600.0, (1.0, 0.45, 0.14), 1.0)
    light("L_DSFrg_FurnaceIn", "POINT", (fx, fy + 3.0, z + 3.0), 1200.0, (1.0, 0.38, 0.10), 0.8)
    # TORRE-CHAMINE: alvenaria escura ate +16, reboco com enxaimel ate +50, chapeu de 4 aguas ate +58, chamine de
    # pedra ate +72 (152,2: o ponto mais alto da ilha). Janelas estreitas quentes.
    tx0, ty0, tx1, ty1, teave, tridge = L.FORGE["tower"]
    Ft = Frame((tx0 + tx1) / 2, (ty0 + ty1) / 2, z, 0.0)
    tw, td = tx1 - tx0, ty1 - ty0
    mb.box((tw + 0.8, td + 0.8, 16.0), Ft.p(0, 0, 8.0), Ft.r(), "Stone_DS_Dark", 0.0)
    timber_box(mb, Ft, tw, td, 16.0, teave - 16.0, wall_m="Wood_DS_Mid")   # corpo de madeira (le como torre, nao farol)
    mb.box((tw + 1.0, td + 1.0, 0.8), Ft.p(0, 0, 33.0), Ft.r(), "Wood_DS_Dark", 0.0)           # cinta do meio
    for zz in (24.0, 41.0):
        window(mb, Ft, 0.0, -td / 2, zz, 1.4, 3.2, out=-1.0)
    hip_roof(mb, Ft, tw, td, teave, tridge - teave, 2.4, ridge_len=0.0)
    cx, cy, cs = L.CHIMNEY
    mb.box((cs, cs, L.CHIMNEY_TOP - (z + tridge - 2.0)), (cx, cy, (L.CHIMNEY_TOP + z + tridge - 2.0) / 2), (0, 0, 0),
           "Stone_DS_Dark", 0.0)
    mb.box((cs + 1.2, cs + 1.2, 1.0), (cx, cy, L.CHIMNEY_TOP - 0.5), (0, 0, 0), "Stone_DS", 0.0)
    col_box("DS_FrgTower", (tw + 0.8, td + 0.8, teave), Ft.p(0, 0, teave / 2), Ft.r())
    light("L_DSFrg_TowerWin", "POINT", Ft.p(0, -td / 2 - 1.5, 30.0), 300.0, WARM, 0.5)
    # OFICINA-RESIDENCIA do mestre (2 pisos, sacada, 2 noren vermelhos) e ALA LESTE (polimento/armazem)
    for key, two in (("workshop", True), ("east", False)):
        bx0, by0, bx1, by1, beave, bridge_ = L.FORGE[key]
        Fb = Frame((bx0 + bx1) / 2, (by0 + by1) / 2, z, 0.0)
        bw, bd = bx1 - bx0, by1 - by0
        mb.box((bw + 0.8, bd + 0.8, 1.2), Fb.p(0, 0, 0.6), Fb.r(), "Stone_DS", 0.0)
        timber_box(mb, Fb, bw, bd, 1.2, beave - 1.2)
        if two:
            mb.box((bw + 2.4, 2.4, 0.5), Fb.p(0, -bd / 2 - 1.2, 6.6), Fb.r(), "Wood_DS_Mid", 0.0)    # sacada
            for u in (-6.0, 6.0):
                mb.box((3.0, 0.3, 3.4), Fb.p(u, -bd / 2 - 0.2, 3.6), Fb.r(), "Cloth_DS_Red", 0.0)   # noren
                window(mb, Fb, u, -bd / 2, 9.0, 3.0, 1.8, out=-1.0)
        else:
            window(mb, Fb, 0.0, -bd / 2, 4.6, 4.0, 2.0, out=-1.0)
        irimoya(mb, Fb, bw, bd, beave, bridge_ - beave, 2.4)
        col_box("DS_Frg%s" % key.capitalize(), (bw + 0.8, bd + 0.8, beave), Fb.p(0, 0, beave / 2), Fb.r())
    light("L_DSFrg_Workshop", "POINT", (-52.0, 472.0, z + 4.0), 160.0, WARM, 0.4)
    # RODA D'AGUA (peca movel VFX_DS_Wheel): aros, raios e pas; eixo leste-oeste entrando na ala leste
    wx, wy, wd, ww = L.WHEEL
    zc = L.WHEEL_AXLE_Z
    mw = MB("VFX_DS_Wheel", "12_VFX_HELPERS", rng, detail="far", floor=-999)
    R = wd / 2
    n = 16
    for k in range(n):
        a = 2 * math.pi * (k + 0.5) / n
        for xo in (-ww / 2 + 0.3, ww / 2 - 0.3):
            ch = 2 * R * math.sin(math.pi / n) + 0.1
            mw.box((0.5, ch, 0.9), (wx + xo, wy + (R - 0.45) * math.cos(a), zc + (R - 0.45) * math.sin(a)), (a, 0, 0),
                   "Wood_DS_Dark", 0.0)
        mw.box((ww - 0.2, 0.3, 1.8), (wx, wy + (R - 0.6) * math.cos(a), zc + (R - 0.6) * math.sin(a)), (a, 0, 0),
               "Wood_DS_Mid", 0.0)
    for k in range(4):
        a = math.pi * k / 4
        for xo in (-ww / 2 + 0.3, ww / 2 - 0.3):
            mw.box((0.4, 2 * R - 1.0, 0.6), (wx + xo, wy, zc), (a, 0, 0), "Wood_DS_Dark", 0.0)
    mw.cyl(0.8, ww + 1.0, (wx, wy, zc), (0, math.pi / 2, 0), m="Metal_DS_Iron", n=8, bevel=0.0)
    ob = mw.finish()
    ob["pivot"] = (wx, wy, zc)
    ob["axis"] = (1.0, 0.0, 0.0)
    ob["rpm"] = 3.0
    ob["vfx_zone"] = "forge"
    mb.cyl(0.6, wx - 74.0, ((74.0 + wx) / 2, wy, zc), (0, math.pi / 2, 0), m="Metal_DS_Iron", n=8, bevel=0.0)   # eixo
    for s in (-1, 1):
        mb.box((1.2, 1.2, zc - z + 0.6), (wx + s * (ww / 2 + 1.0), wy, (zc + z) / 2), (0, 0, 0), "Wood_DS_Dark", 0.0)
    col_box("DS_FrgWheel", (ww + 3.0, wd + 1.0, wd), (wx, wy, z + wd / 2))
    # aqueduto de madeira (calha sobre cavaletes): nascente -> topo da roda
    pts = [(L.SPRING[0], L.SPRING[1] - 4.0, L.SPRING[2] - 1.0)] + \
          [(x_, y_, z_) for (x_, y_), z_ in zip(L.FLUME[1:], (L.SPRING[2] - 1.6, zc + R + 0.8))]
    for a, b in zip(pts, pts[1:]):
        mb.beam(a, b, 2.4, 1.4, "Wood_DS_Mid", 0.0)
        k = max(1, int(math.dist(a[:2], b[:2]) / 9.0))
        for i in range(1, k + 1):
            t = i / (k + 0.0001)
            px, py, pz = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t
            zg = L.zone_of(px, py) or 92.0
            zg = 92.0 if L.point_in_poly(px, py, L.BACK_ROCKS) else zg
            if pz - zg > 1.0:
                for s in (-1, 1):
                    mb.box((0.6, 0.6, pz - zg), (px + s * 1.4, py, (pz + zg) / 2 - 0.7), (0, 0, 0), "Wood_DS_Dark", 0.0)
    # patio do carvao: carvoeira de pedra + pilhas de lenha (volumes)
    mb.cyl(5.0, 6.0, (-112.0, 400.0, z + 3.0), m="Stone_DS_Dark", n=10, r2=3.6, bevel=0.0)
    col_box("DS_FrgKiln", (8.0, 8.0, 6.0), (-112.0, 400.0, z + 3.0))
    for x, y in ((-84.0, 390.0), (-130.0, 420.0)):
        mb.box((8.0, 3.0, 2.6), (x, y, z + 1.3), (0, 0, 0.3), "Wood_DS_Mid", 0.0)
        col_box("DS_FrgWood", (8.0, 3.0, 2.6), (x, y, z + 1.3), (0, 0, 0.3))
    # cerca baixa da borda do terraco (aberta nas escadas)
    for pts in ([(-34.0, 397.0), (-21.0, 434.0)], [(-19.0, 436.4), (22.0, 435.2)], [(38.0, 434.8), (116.0, 428.6)]):
        DL.vis_fence(mb, [(x_, y_, z) for x_, y_ in pts], h=2.8)
    DL.plan_stair(mb, "SubidaA")                  # subida em 2 lances (cortados no arrimo), patamar-mirante no meio
    DL.plan_stair(mb, "SubidaB")
    mb.box2((L.CLIMB_LAND[0], L.CLIMB_LAND[1], T3 - 0.2), (L.CLIMB_LAND[2], L.CLIMB_LAND[3], T3 + 0.12), "Stone_DS_Path", 0.0)
    lantern_post(mb, 42.0, 440.0, z, 7.0, "L_DSProp_Lamp_SubidaTop", 150.0)
    lantern_post(mb, -56.0, 380.0, z, 7.0, None)
    mb.finish()


# ------------------------------------------------------------------ summon: a TORRE AMS aprovada (Ilha 1) + plato DS
SUMMON_ALIAS = {
    "Summon_Stone": "Stone_DS_Dark", "Stone_SumBlock": "Stone_DS", "Summon_Stone_Dark": "Stone_DS_Dark",
    "Stone_Wall_Light": "Stone_DS", "Stone_SumFloor_Pale": "Stone_DS_Path", "Summon_Floor": "Stone_DS_Dark",
    "Stone_Paving_Warm": "Stone_DS_Path", "Cloth_Royal_Blue": "Cloth_DS_Indigo", "Wood_Dark": "Wood_DS_Dark",
}
_TOWER = None


def tower_mod():
    """importa il_summon com a planta DESTA ilha (valores do il_layout trocados so durante o import, como o
    sg_summon.tower_mod da Ilha 3 e o db_summon da Ilha 2)"""
    global _TOWER
    if _TOWER is not None:
        return _TOWER
    import sys, importlib
    import il_layout as NL
    want = {"SUMMON_TOWER": L.SUMMON_TOWER, "SUMMON_FACE_DEG": L.SUMMON_FACE_DEG, "T1": T3, "SUMMON_C": L.SUMMON_C,
            "SUMMON_R": L.SUMMON_R}
    saved = {k: getattr(NL, k) for k in want}
    for k, v in want.items():
        setattr(NL, k, v)
    try:
        if "il_summon" in sys.modules:
            T = importlib.reload(sys.modules["il_summon"])
        else:
            T = importlib.import_module("il_summon")
    finally:
        for k, v in saved.items():
            setattr(NL, k, v)
    assert abs(T.Z0 - T3) < 1e-6 and abs(T.TX - L.SUMMON_TOWER[0]) < 1e-6 and abs(T.TY - L.SUMMON_TOWER[1]) < 1e-6
    _TOWER = T
    return T


def build_tower():
    """estrela + aneis + torre + nucleo SEM redesenho (codigo da Ilha 1): corpo, nicho do portal (nucleo azul), base com
    os 4 pedestais de lanterna, mastros, esfera armilar (aneis moveis + estrela). Fora: praca redonda, cristais (liam
    como minerio) e a constelacao (estrelas a mais). Materiais: so a pedra/tecido trocados por apelido (pedra escura e
    madeira escura DS); ouro, nucleo azul e estrela dourada = identidade AMS."""
    import bpy
    T = tower_mod()
    before = {o.name for o in bpy.data.objects}
    saved = dict(fm_lib.MAT_ALIAS)
    for k, v in SUMMON_ALIAS.items():
        fm_lib.MAT_ALIAS[k] = v
        fam = fm_lib.FAMILIES.get(k)
        if fam:
            for n, _ in fam[1]:
                fm_lib.MAT_ALIAS[n] = v
    try:
        stone = MB("SUM_Tower_Stone", "06_SUMMON", random.Random(620), detail="near")
        gold = MB("SUM_Tower_Gold", "06_SUMMON", random.Random(622), detail="near")
        glow = MB("SUM_Tower_Glow", "06_SUMMON", random.Random(623), detail="hero")
        T.tower_stone(stone, gold, glow)
        cr = T.tower_details(stone, gold, glow)
        cr.bm.free()
        T.masts_and_lanterns(stone, gold, glow)
        c = T.sphere(gold, glow)
        stone.finish()
        gold.finish()
        glow.finish()
        T.tower_collision()
    finally:
        fm_lib.MAT_ALIAS.clear()
        fm_lib.MAT_ALIAS.update(saved)
    dst = fm_lib.coll("06_SUMMON")
    for ob in [o for o in bpy.data.objects if o.name not in before]:
        n = ob.name
        if n.startswith("VFX_SUM_"):
            ob.name = "VFX_DSSUM_" + n[len("VFX_SUM_"):]
            ob["vfx_zone"] = "summon"
        elif n.startswith("SUM_"):
            ob.name = "DS_Sum_" + n[len("SUM_"):]
        elif n.startswith("COL_Summon"):
            ob.name = "COL_DSSum" + n[len("COL_Summon"):]
        if ob.type == "MESH":
            ob.data.name = ob.name
        if not n.startswith(("COL_", "VFX_")):
            for cl in list(ob.users_collection):
                if cl.name == "05_SUMMON":
                    cl.objects.unlink(ob)
                    if ob.name not in dst.objects:
                        dst.objects.link(ob)
    c05 = bpy.data.collections.get("05_SUMMON")
    if c05 is not None and not c05.objects and not c05.children:
        bpy.data.collections.remove(c05)
    return T, c


def summon():
    import bpy
    rng = random.Random(71)
    mb = MB("DS_Sum_Blockout", "06_SUMMON", rng, detail="far", floor=None)
    DL.plan_stair(mb, "Summon", side_floor=T1)
    # balaustrada baixa de madeira escura na borda do plato (aberta na escada) + mirante leste (lugar do torii das refs)
    P = ccw(L.SUMMON_PLAT)
    ring = DL.offset_poly(P, -1.2)
    pts = []
    for i in range(len(ring)):
        a, b = ring[i], ring[(i + 1) % len(ring)]
        k = max(1, int(math.dist(a, b) / 2.0))
        pts += [(a[0] + (b[0] - a[0]) * t / k, a[1] + (b[1] - a[1]) * t / k, T3) for t in range(k)]
    pts.append(pts[0])
    runs, cur = [], []
    for p in pts:
        if p[0] < 153.0 and 290.0 < p[1] < 310.0:
            if len(cur) > 1:
                runs.append(cur)
            cur = []
            continue
        cur.append(p)
    if len(cur) > 1:
        runs.append(cur)
    for r in runs:
        DL.vis_fence(mb, r, h=2.4, post_step=3.5)
    # abrigo pequeno de madeira escura (as refs mostram um pavilhao ao lado da torre)
    sx, sy, sw, sd = L.SUMMON_SHELTER
    Fs = Frame(sx, sy, T3, 0.0)
    for ax in (-1, 1):
        for ay in (-1, 1):
            mb.box((0.7, 0.7, 6.0), Fs.p(ax * (sw / 2 - 0.4), ay * (sd / 2 - 0.4), 3.0), Fs.r(), "Wood_DS_Dark", 0.0)
    irimoya(mb, Fs, sw, sd, 6.0, 3.6, 1.6)
    col_box("DS_SumShelter", (sw, sd, 6.0), Fs.p(0, 0, 3.0), Fs.r())
    # 4 lanternas de pedestal (toro): 2 no topo da escada, 2 no mirante
    for i, (x, y) in enumerate(((153.5, 291.0), (153.5, 309.0), (198.0, 288.0), (198.0, 312.0))):
        toro(mb, x, y, T3, 0.9, "L_DSSum_Toro_%d" % i if i < 2 else None)
    mb.finish()
    T, c = build_tower()
    light("L_DSSum_Core", "POINT", (L.SUMMON_TOWER[0] - 1.5, L.SUMMON_TOWER[1], T3 + 9.0), 1600.0, (0.36, 0.52, 1.0), 1.0)
    light("L_DSSum_Star", "POINT", tuple(c), 3000.0, (1.0, 0.74, 0.34), 2.0)


# ------------------------------------------------------------------ agua: SO a pedra estanque (a agua e do Roblox)
def water():
    rng = random.Random(88)
    mb = MB("DS_Water_Stone", "07_WATER", rng, detail="far", floor=-999)
    # meio-fio da lagoa e do canal; calha de pedra da roda ate a borda da cascata
    P = ccw(L.POND)
    DL.wall_ribbon(mb, P + [P[0]], T1 - 0.4, T1 + 0.5, 1.0, "Stone_DS", side=-1.0)
    for pts, zz in ((L.CHANNEL, T1), (L.TAILRACE, T4)):
        for s in (-1.0, 1.0):
            off = L.ribbon(pts, 2.2)
            n = len(pts)
            side = off[:n] if s > 0 else list(reversed(off[n:]))
            DL.wall_ribbon(mb, side, zz - 0.6, zz + 0.4, 0.8, "Stone_DS", side=s)
    # pontezinha de madeira sobre o canal (acesso a escada do summon). ONDA 1 (1d): com a zona summon em detalhe a
    # pontezinha e do ds_summon (arqueada, com guarda-corpo e colisao propria) -> o blockout nao a desenha
    a0, a1, w = L.FOOTBRIDGE
    if "summon" not in DETAILED:
        mb.box((a1[0] - a0[0], w, 0.6), ((a0[0] + a1[0]) / 2, a0[1], T1 + 0.4), (0, 0, 0), "Wood_DS_Mid", 0.0)
        for s in (-1, 1):
            mb.box((a1[0] - a0[0], 0.4, 1.2), ((a0[0] + a1[0]) / 2, a0[1] + s * (w / 2 - 0.2), T1 + 1.3), (0, 0, 0),
                   "Wood_DS_Dark", 0.0)
    mb.finish()
    # PREVIA da agua (00_REFERENCE: fora do export) para ler a composicao nos renders do blockout
    pw = MB("PREVIEW_Water", "00_REFERENCE", rng, detail="far", floor=-999)
    pw.prism(P, T1 - 0.4, T1 + 0.25, "PREVIEW_Water")
    for pts, zz in ((L.CHANNEL, T1 + 0.2), (L.TAILRACE, T4 + 0.1)):
        pw.prism(ccw(L.ribbon(pts, 1.4)), zz - 0.3, zz, "PREVIEW_Water")
    cx, cy, ztop, zbot = L.CASCADE
    pw.box((5.0, 0.8, ztop - zbot), (cx, cy - 0.8, (ztop + zbot) / 2), (0, 0, 0), "PREVIEW_Water", 0.0)
    pw.finish()


# ------------------------------------------------------------------ saida: caminho, torii, ponte de 56, cabeceira
def exit_():
    rng = random.Random(111)
    mb = MB("DS_Exit_Blockout", "08_NEXT_ISLAND", rng, detail="far", floor=-999)
    mb.prism(ccw(L.ribbon(L.EXIT_PATH, 5.0)), T4 - 0.2, T4 + 0.12, "Stone_DS_Path")
    ux, uy = L.exit_dir()
    ang = math.atan2(uy, ux)
    tx, ty = L.TORII_OUT
    torii(mb, tx, ty, T4, ang, area="DS_ExitTorii")
    Ln = L.EXIT_BRIDGE_LEN
    c = L.exit_point(Ln / 2)
    mb.box((Ln + 1.0, L.EXIT_W, 1.2), (c[0], c[1], T4 - 0.6), (0, 0, ang), "Wood_DS_Mid", 0.0)
    for s in (-1, 1):
        q = L.exit_point(Ln / 2, s * (L.EXIT_W / 2 + 0.4))
        mb.box((Ln + 1.0, 0.9, 1.4), (q[0], q[1], T4 - 0.5), (0, 0, ang), "Wood_DS_Dark", 0.0)
        mb.box((Ln + 1.0, 0.5, 0.45), (q[0], q[1], T4 + 3.6), (0, 0, ang), "Wood_DS_Dark", 0.0)
        for k in range(0, int(Ln) + 1, 5):
            p = L.exit_point(float(k), s * (L.EXIT_W / 2 + 0.4))
            mb.box((0.6, 0.6, 3.8), (p[0], p[1], T4 + 1.9), (0, 0, ang), "Wood_DS_Dark", 0.0)
    # 2 pilares de pedra sob a ponte (afinando para baixo) - a ponte existe de verdade
    for d in (Ln * 0.36, Ln * 0.72):
        p = L.exit_point(d)
        mb.box((3.0, L.EXIT_W - 2.0, 3.0), (p[0], p[1], T4 - 2.7), (0, 0, ang), "Stone_DS", 0.0)
        mb.cyl(3.2, 40.0, (p[0], p[1], T4 - 24.0), m="Stone_DS_Dark", n=8, r2=1.8, bevel=0.0)
    # cabeceira de pedra 30 x 30 sobre pilar de rocha
    pp = L.pier_poly()
    mb.prism(ccw(pp), T4 - 6.0, T4 - 0.3, "Stone_DS")
    mb.prism(ccw(pp), T4 - 0.3, T4, "Stone_DS_Path")
    pc = DL.centroid(pp)
    for k, (r, z0, z1) in enumerate(((17.0, 40.0, T4 - 6.0), (12.0, 10.0, 40.0), (6.0, -14.0, 10.0))):
        mb.prism(ccw(DL.blob_poly(pc[0], pc[1], r, 10, rng, 0.12)), z0, z1, "Cliff_DS" if k % 2 == 0 else "Cliff_DS_Dark")
    mb.finish()
    # guarda PROVISORIA da ancora (visual): corda baixa entre 2 mouroes de pedra; a integracao da One Piece remove
    mg = MB("DS_Exit_AnchorGuard", "08_NEXT_ISLAND", rng, detail="far", floor=-999)
    ap = L.anchor_op_pos()
    for s in (-1, 1):
        p = (ap[0] - ux * 1.0 - uy * s * (L.EXIT_W / 2 + 0.6), ap[1] - uy * 1.0 + ux * s * (L.EXIT_W / 2 + 0.6))
        mg.box((1.2, 1.2, 3.4), (p[0], p[1], T4 + 1.7), (0, 0, ang), "Stone_DS_Dark", 0.0)
    q = (ap[0] - ux * 1.0, ap[1] - uy * 1.0)
    mg.box((0.3, L.EXIT_W + 1.2, 0.3), (q[0], q[1], T4 + 2.6), (0, 0, ang), "Wood_DS_Mid", 0.0)
    ob = mg.finish()
    ob["next_island_guard"] = True
    ml = MB("DS_Exit_Lamps", "08_NEXT_ISLAND", rng, detail="far", floor=-999)
    for i, (x, y) in enumerate(((-116.0, 470.0), (-118.0, 524.0), (-110.0, 566.0))):
        lantern_post(ml, x, y, T4, 7.0, "L_DSProp_Lamp_Exit_%d" % i, 130.0)
    ml.finish()


# ------------------------------------------------------------------ vestir (PROXIES leves de composicao)
def dressing():
    rng = random.Random(121)
    mv = MB("DS_Veg_Blockout", "10_VEGETATION", rng, detail="far", floor=-999)
    # bambuzal: touceiras dos dois lados do caminho calcado (o caminho fica livre)
    for i in range(26):
        for _ in range(20):
            x = rng.uniform(16.0, 96.0)
            y = rng.uniform(16.0, 140.0)
            if not L.point_in_poly(x, y, L.BAMBOO) or L.polyline_dist(x, y, L.BAMBOO_RAMP) < 7.0:
                continue
            if L.poly_edge_dist(x, y, L.BAMBOO) < 2.5:
                continue
            break
        else:
            continue
        z = L.bamboo_z(x, y)
        bamboo_clump(mv, x, y, z, rng.uniform(16.0, 22.0), rng)
        col_box("DS_VegBamboo", (2.4, 2.4, 8.0), (x, y, z + 4.0))
    # arvores largas: 3 na borda da clareira, 1 arvore-marco no patio, 2 na vila, 3 grandes atras da forja (moldura)
    for x, y, r in L.CLEARING_TREES:
        tree(mv, x, y, T1, 22.0, r)
    tree(mv, -20.0, 23.0, T0, 18.0, 6.5)
    tree(mv, -86.0, 120.0, T1, 20.0, 6.0)
    tree(mv, -146.0, 316.0, T2, 22.0, 6.5)
    for x, y, h, r in ((-60.0, 528.0, 34.0, 10.0), (14.0, 532.0, 38.0, 11.0), (70.0, 528.0, 32.0, 9.0)):
        tree(mv, x, y, 90.0, h, r, col=False)
    # cedros da saida (densidade baixa) e da crista oeste
    for x, y, h in ((-124.0, 506.0, 26.0), (-84.0, 556.0, 24.0), (-118.0, 550.0, 22.0), (-134.0, 468.0, 24.0),
                    (-46.0, 52.0, 20.0), (-52.0, 84.0, 18.0)):
        zg = L.zone_of(x, y) or L.WEST_RIDGE_Z
        cedar(mv, x, y, zg, h)
        if L.zone_of(x, y) is not None:
            col_box("DS_VegTrunk", (1.6, 1.6, 8.0), (x, y, zg + 4.0))
    # pinheiro torto do patamar-mirante
    cedar(mv, -8.0, 410.0, T3, 16.0)
    col_box("DS_VegTrunk", (1.6, 1.6, 8.0), (-8.0, 410.0, T3 + 4.0))
    # 4 glicinias (ACENTO): 2 no plato do summon, 1 no jardim da casa principal (trelica), 1 pergola do bambuzal
    for x, y in L.WISTERIA[:2]:
        if "summon" in DETAILED:      # ONDA 1 (1d): as 2 glicinias do plato sao do ds_summon (wisteria_tree)
            continue
        wisteria(mv, x, y, T3, 10.0, 5.5)
    wx, wy = L.WISTERIA[2]
    wisteria(mv, wx, wy, T2, 9.0, 5.0)
    px, py = L.WISTERIA[3]
    pz = L.bamboo_z(px, py)
    for sx in (-1, 1):
        for sy in (-1, 1):
            mv.box((0.6, 0.6, 7.0), (px + sx * 5.0, py + sy * 4.0, pz + 3.5), (0, 0, 0), "Wood_DS_Dark", 0.0)
    mv.box((12.0, 10.0, 0.6), (px, py, pz + 7.2), (0, 0, 0.42), "Wood_DS_Mid", 0.0)
    for k in range(10):
        mv.cyl(0.9, 3.0, (px + rng.uniform(-5, 5), py + rng.uniform(-4, 4), pz + 5.4),
               m="Wisteria_DS" if k % 2 else "Wisteria_DS_Light", n=6, r2=0.15, bevel=0.0)
    mv.finish()
    # lanternas de no (NightOnly no Roblox): topo da escada da trilha, antecampo, pe da subida, patamar
    mp = MB("DS_Prop_Lamps", "09_PROPS", rng, detail="far", floor=-999)
    for nm, x, y, z in (("Trilha", -20.0, 58.0, T1), ("Antecampo", 22.0, 138.0, T1), ("PeSubida", 4.0, 374.0, T1),
                        ("Patamar", 40.0, 404.0, T3), ("SummonFoot", 124.0, 290.0, T1),
                        ("Bambuzal", 40.0, 44.0, L.bamboo_z(40.0, 44.0))):
        lantern_post(mp, x, y, z, 7.0, "L_DSProp_Lamp_%s" % nm, 140.0)
    mp.finish()


DETAILED = set()      # ONDA 1 (1d): zonas que estao em detalhe nesta montagem (o build/estudio passam em skip)


def build(skip=(), ore_proxies=False):
    DETAILED.clear()
    DETAILED.update(skip)
    fns = {"terrain": terrain, "entry": entry, "village": village, "clearing": lambda: clearing(ore_proxies),
           "forge": forge, "summon": summon, "water": water, "exit": exit_, "dressing": dressing}
    for z in ZONES:
        if z not in skip:
            fns[z]()
