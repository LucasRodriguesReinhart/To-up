# il_water - ZONA WATER da Ilha 1 (Naruto / Vila da Folha). Substitui il_blockout.water().
# Poucas quedas grandes, cada uma com origem e destino:
#   FUNDO (x +-80): nascente no plato (L.CLIFF_TOP) -> queda larga de 50 -> poco redondo com borda de pedra no T2
#   LESTE: poco NE -> canal de pedra no T2 (L.STREAM) -> cascata no muro y 126 (T2 -> G) -> riacho do vale na cota
#          L.G - 0.3 entre margens de pedra e seixos -> roda d'agua (VFX_WATER_Wheel, apoio WATER_Wheel_Frame) ->
#          ponte em arco (pisavel) -> funil ate a sangria SE -> queda longa ate o mar
#   OESTE: poco NO -> canal de pedra no T2 (entre a casa T2 NO e a borda) -> cascata T2 -> T1 -> canal no T1 ->
#          bacia na borda oeste -> queda longa ate o mar (a oeste/atras do summon)
#   DRENAGEM DO FOSSO: boca de galeria de pedra (testa de cantaria) na face SO, cota ~0 -> queda ate o mar
# As 3 quedas da borda nascem nas SANGRIAS do terreno (il_terrain_rock: COVES/SPILL - a prateleira abre e as colunas
# de cima baixam 1,3 ali): a lamina passa por cima das colunas e comeca a cair SPILL_OUT para fora da borda, livre das
# colunas do penhasco (que saem ate ~2,2 da borda). Quedas do fundo: dentro dos sulcos do paredao (x +-80).
# Espuma em todo ponto de impacto (pocos, pe das cascatas e mar). Colisao: SO a ponte em arco (area WaterFootbridge).
# Sem luzes. O riacho do vale fica ABAIXO do gramado (L.G - 0.3): o terreno detalhado abre o leito em L.STREAM
# (ver il_water_preview.py, que abre o mesmo corte no terreno de blockout so para a revisao).
import math, random
from mathutils import Vector
import fm_lib
from fm_lib import MB, S, col_box, col_ramp, resample
import fm_water_kit as WK
import il_lib as IL
import il_layout as L

C = "06_WATER"
VFX = "12_VFX_HELPERS"
# material novo (1/4): o escuro do tunel da galeria de drenagem (le como buraco, nao como pedra)
fm_lib.MATS.setdefault("Stone_WtrVoid", (S(30, 32, 38), 0.95, 0.0, 0, None, 0.0))
# material novo (2/4): corpo das quedas, ciano claro das referencias (o Water_Fall do lobby, quase branco, lia como
# papel contra o penhasco); os riscos brancos por cima sao Foam
fm_lib.MATS.setdefault("Water_WtrFall", (S(104, 184, 232), 0.2, 0.0, 0.35, S(104, 184, 232), 0.0))

# ------------------------------------------------------------------ cotas da agua
ZW = L.G - 0.3             # riacho do vale (o chao de colisao do nucleo fica em L.G)
ZT2 = L.T2 + 0.2           # canais de pedra no T2 (lamina contida pela mureta de cantaria)
ZT1 = L.T1 + 0.2           # canal de pedra no T1 (oeste)
ZPOOL = L.T2 + 0.35        # pocos do pe das quedas do fundo
POOL_R = 8.6
FALL_W = 11.0              # largura das quedas do fundo
CANAL_E_W = 8.4            # lamina do canal leste no T2 (a cantaria fecha a faixa de L.STREAM_W)
CANAL_W_W = 3.8            # lamina do canal oeste
FB_LEN, FB_W, FB_RISE = 21.0, 6.0, 2.4   # ponte em arco: vao, largura do tabuleiro, flecha

# ------------------------------------------------------------------ tracados (planta: L.STREAM + canais proprios)
# L.STREAM no T2, deslocado ~0,6-1 para leste junto a casa T2 (98,150), que invade a faixa do riacho na planta
STREAM_T2 = [(86.5, 177.4), (104.6, 168.2), (112.6, 140.5), (112.8, 126.0)]
STREAM_G = [(112.8, 126.0)] + [p for p in L.STREAM if p[1] < 120.0]              # vale (ate a borda SE)
WEST_T2 = [(-88.0, 177.0), (-100.0, 175.2), (-110.0, 170.5), (-118.5, 163.5), (-126.0, 157.0), (-131.5, 151.0),
           (-135.5, 145.0), (-137.5, 139.0), (-139.5, 132.0), (-140.5, 126.0)]
WEST_T1 = [(-140.5, 126.0), (-142.0, 115.0), (-144.0, 102.0), (-145.8, 90.0), (-147.8, 80.5), (-150.2, 76.4),
           (-151.5, 75.7)]
# bacia na borda oeste (entra pelo leste em y 75,7; o vertedouro e a borda, no vertice (-158, 76) do contorno)
WEST_BASIN = [(-157.9, 71.8), (-151.8, 71.8), (-151.8, 79.6), (-157.35, 79.6), (-157.9, 76.0)]
RIM_SE = ((96.0, -80.0), (112.0, -64.0))   # segmento de L.ISLAND_RIM onde o riacho sai (obliquo: ~31 graus)
SE_SPILL = (101.0, -75.0)          # sangria SE do terreno (il_terrain_rock.SPILL)
W_SPILL = (-158.0, 76.0)           # sangria oeste do terreno (il_terrain_rock.SPILL)
W_OUT = (-0.9959, 0.0903)          # normal para fora no vertice (-158, 76)
SPILL_OUT = 2.9                    # a queda comeca a este tanto para fora da borda
SE_FALL_W = 9.0
W_FALL_W = 7.8
DRAIN_DIR = math.radians(219.0)    # raio do centro do fosso ate a boca da galeria (face SO; sangria (-88.5, -71))
DRAIN_OFF = 2.6                    # testa da galeria: a frente das colunas do penhasco (saem ate ~2,2 da borda)

# ------------------------------------------------------------------ cameras de revisao (360 graus + altura do jogador)
CAMS = {
    "CAM_Water_Wheel": ((104.0, -16.0, L.G + 5.5), (118.0, 12.0, L.G + 8.5), 20),
    "CAM_Water_Footbridge": ((91.0, -58.0, L.G + 5.5), (113.4, -39.7, L.G + 2.5), 20),
    "CAM_Water_BackFalls": ((0.0, 96.0, 140.0), (0.0, 184.0, 30.0), 18),
    "CAM_Water_NEPool": ((90.0, 159.0, L.T2 + 5.5), (80.0, 182.0, L.T2 + 9.0), 18),
    "CAM_Water_SE": ((205.0, -200.0, 26.0), (102.0, -86.0, -38.0), 22),
    "CAM_Water_Cascade": ((121.0, 90.0, L.G + 5.5), (112.8, 126.0, L.G + 9.0), 18),
    "CAM_Water_West": ((-300.0, 96.0, 24.0), (-160.0, 76.0, -34.0), 22),
    "CAM_Water_Drain": ((-195.0, -175.0, 4.0), (-92.0, -76.0, -32.0), 22),
    "CAM_Water_NWCanal": ((-151.0, 98.0, L.T1 + 7.0), (-138.0, 132.0, L.T1 + 4.0), 18),
    "CAM_Water_Back": ((170.0, 262.0, 118.0), (86.0, 150.0, 26.0), 22),
    "CAM_Water_East": ((250.0, 20.0, 64.0), (112.0, 10.0, 4.0), 22),
    "CAM_Water_Front": ((0.0, -340.0, 40.0), (0.0, -70.0, -30.0), 22),
    "CAM_Water_North": ((0.0, 300.0, 150.0), (0.0, 175.0, 60.0), 22),
}


# ------------------------------------------------------------------ utilidades
def V(x, y, z=0.0):
    return Vector((x, y, z))


def chaikin(pts, it=2):
    """suaviza a polilinha (cantos arredondados), mantendo as pontas"""
    P = [tuple(p[:2]) for p in pts]
    for _ in range(it):
        Q = [P[0]]
        for a, b in zip(P, P[1:]):
            Q.append((a[0] * 0.75 + b[0] * 0.25, a[1] * 0.75 + b[1] * 0.25))
            Q.append((a[0] * 0.25 + b[0] * 0.75, a[1] * 0.25 + b[1] * 0.75))
        Q.append(P[-1])
        P = Q
    return P


def frames(pts):
    """[(p, tangente, normal_esquerda)] com tangente suavizada"""
    out = []
    n = len(pts)
    for i in range(n):
        a, b = pts[max(0, i - 1)], pts[min(n - 1, i + 1)]
        t = V(b[0] - a[0], b[1] - a[1]).normalized()
        out.append((V(pts[i][0], pts[i][1]), t, V(-t.y, t.x)))
    return out


def offset(pts, d):
    return [p + nn * d for p, t, nn in frames(pts)]


def rs(pts, step):
    return resample([V(p[0], p[1]) for p in pts], step)


def in_rects(p, rects, pad=0.3):
    return any(x0 - pad <= p.x <= x1 + pad and y0 - pad <= p.y <= y1 + pad for x0, y0, x1, y1 in rects)


def house_rects():
    """pegadas das casas (+0,45 do soco de pedra). A casa T2 (98,150) foi estreitada pelo agente de casas para o
    riacho passar (il_houses.house_T2_1: 13,5 x 12, centro 1,5 a oeste e 0,5 ao sul)"""
    out = []
    for (x, y, w, d, yaw, r) in L.HOUSES_T1 + L.HOUSES_T2 + L.EAST_HOUSES:
        if (x, y) == (98.0, 150.0):
            x, y, w, d = x - 1.5, y - 0.5, w * 0.9, 12.0
        out.append((x - w / 2 - 0.45, y - d / 2 - 0.45, x + w / 2 + 0.45, y + d / 2 + 0.45))
    return out


def water_strip(mb, pts, z_top, w, thick=0.4, m="Water"):
    """lamina fechada (sweep) de largura w ao longo da polilinha, topo em z_top"""
    P = [V(p[0], p[1], z_top - thick / 2) for p in pts]
    hw, ht = w / 2, thick / 2
    mb.sweep(P, [(-hw, -ht), (hw, -ht), (hw, ht), (-hw, ht)], m, True)


def coping(mb, rng, line, z_top, h=1.1, w=1.1, step=2.9, m="Stone_Wall_Light", skip=None, jog=0.05):
    """mureta de cantaria: blocos ao longo da linha (juntas visiveis, alturas e larguras levemente diferentes)"""
    P = rs(line, step)
    for a, b in zip(P, P[1:]):
        c = (a + b) / 2
        if skip and skip(c):
            continue
        d = b - a
        hh = h + rng.uniform(-0.1, 0.1)
        mb.box((d.length - 0.16, w * rng.uniform(0.92, 1.06), hh), (c.x, c.y, z_top - hh / 2 + rng.uniform(-jog, jog)),
               (0, 0, math.atan2(d.y, d.x) + rng.uniform(-0.03, 0.03)), m, 0.0)


def pebble(mb, rng, x, y, z, s, m="Cliff_Rock_Tan_Dark"):
    mb.rock((x, y, z), (s * rng.uniform(1.0, 1.4), s * rng.uniform(0.8, 1.1), s * rng.uniform(0.55, 0.8)), m, 1,
            (0, 0, rng.uniform(0, 3.1)), jitter=0.3)


def foam_blobs(mb, rng, c, radius, n, s, z, flat=0.35):
    """espuma em bolhas achatadas em volta de um ponto de impacto (icosaedros de 20 faces)"""
    a0 = rng.uniform(0, math.tau)
    for i in range(n):
        a = a0 + i * math.tau / n + rng.uniform(-0.3, 0.3)
        r = radius * rng.uniform(0.7, 1.1)
        rr = s * rng.uniform(0.7, 1.1)
        mb.ico(rr, (c.x + math.cos(a) * r, c.y + math.sin(a) * r, z + rr * flat * 0.3), "Foam", 1,
               (rng.uniform(1.2, 1.7), rng.uniform(1.0, 1.4), flat), (0, 0, rng.uniform(0, 3)), jitter=0.2)


def streaks(mb, rng, pts, hw, z, n, zones_skip=None, m="Water_WtrFall"):
    """ondulacao da correnteza: faixas claras e curtas ao longo do fluxo, aos pares (as linhas onduladas das
    referencias); espuma branca so atras das pedras e nos impactos"""
    P = rs(pts, 1.5)
    fr = frames([(p.x, p.y) for p in P])
    for k in range(n):
        i = rng.randint(1, len(fr) - 2)
        p, t, nn = fr[i]
        q = p + nn * rng.uniform(-hw * 0.75, hw * 0.75)
        if zones_skip and zones_skip(q):
            continue
        ang = math.atan2(t.y, t.x)
        for j in range(2):
            ln = rng.uniform(1.6, 3.2)
            qq = q + nn * (j * rng.uniform(0.7, 1.1)) + t * rng.uniform(-0.6, 0.6)
            mb.box((ln, rng.uniform(0.26, 0.4), 0.08), (qq.x, qq.y, z + 0.005), (0, 0, ang + rng.uniform(-0.15, 0.15)),
                   m, 0.0)


def vee(mb, rng, p, z, t):
    """V da correnteza a jusante de uma pedra: 2 faixas claras curtas abrindo rio abaixo + espuma colada na pedra"""
    for sd in (-1, 1):
        a = math.atan2(t.y, t.x) + sd * math.radians(rng.uniform(22, 32))
        ln = rng.uniform(1.4, 2.2)
        d = V(math.cos(a), math.sin(a))
        c = p + d * (ln / 2 + 0.2)
        mb.box((ln, 0.3, 0.08), (c.x, c.y, z + 0.005), (0, 0, a), "Water_WtrFall", 0.0)
    mb.ico(0.55, (p.x - t.x * 0.3, p.y - t.y * 0.3, z + 0.02), "Foam", 1, (1.6, 1.1, 0.3), (0, 0, math.atan2(t.y, t.x)),
           jitter=0.15)


def sea_foam(mb, rng, c, w):
    """espuma no mar onde a queda longa bate: mancha branca recortada, bolhas baixas e 2 nuvens de respingo"""
    z = L.SEA
    R = w * 0.62 + 2.2
    poly = []
    for k in range(11):
        a = math.tau * k / 11 + rng.uniform(-0.12, 0.12)
        r = R * rng.uniform(0.75, 1.25)
        poly.append((c.x + math.cos(a) * r, c.y + math.sin(a) * r))
    mb.prism(IL.ccw(poly), z - 0.2, z + 0.22, "Foam")
    foam_blobs(mb, rng, c, R * 0.95, 6, 1.2 + w * 0.12, z + 0.1, flat=0.22)
    for k in range(2):
        s = w * rng.uniform(0.24, 0.3)
        mb.ico(s, (c.x + rng.uniform(-1.5, 1.5), c.y + rng.uniform(-1.5, 1.5), z + s * 0.2), "Foam", 2,
               (1.5, 1.25, 0.55), (0, 0, rng.uniform(0, 3)), jitter=0.12)


def cheek(mb, rng, p, s, m="Stone_Wall_Light"):
    """pedra-mestra no canto de um bocal"""
    mb.box((s, s, s * 0.9), (p.x, p.y, p.z - s * 0.2), (0, 0, rng.uniform(-0.2, 0.2)), m, 0.2)


def fall(mb, rng, top, bottom_z, width, out=(0, -1), lip=1.5, widen=1.3, n=7, streaks_n=3, edge=True,
         lip_foam=True, base=True, base_s=1.0, drop=1.15, white=0.0):
    """queda estilizada das referencias: lamina ciano (Water_WtrFall) com bordas de agua mais escura, riscos brancos
    verticais comecando em alturas diferentes, labio de espuma no bocal e espuma baixa no pe.
    Retorna (ponto de impacto, largura no pe)."""
    o = V(out[0], out[1]).normalized()
    side = V(-o.y, o.x)
    pts = WK.fall_path(V(*top), bottom_z, o, lip, n, drop)
    wob = [0.0] + [rng.uniform(-0.06, 0.06) * width for _ in range(n)]
    pts = [p + side * wob[i] for i, p in enumerate(pts)]
    ws = [width * (1.0 + (widen - 1.0) * (i / n)) * (1.0 if i == 0 else rng.uniform(0.95, 1.05)) for i in range(n + 1)]
    WK.ribbon(mb, pts, ws, "Water_WtrFall", side, thick=0.35, bulge=min(0.6, 0.05 * width + 0.15))
    if edge and width > 2.5:
        for sd in (-1, 1):
            e = [p + side * sd * (ws[i] * 0.5 - max(0.2, ws[i] * 0.05)) + o * 0.06 for i, p in enumerate(pts)]
            WK.ribbon(mb, e, [max(0.35, ws[i] * 0.1) for i in range(n + 1)], "Water", side, thick=0.2, flat=True)
    for k in range(streaks_n):
        u = -0.34 + 0.68 * (k + 0.5) / streaks_n + rng.uniform(-0.05, 0.05)
        i0 = rng.randint(0, max(0, n // 3))
        sub = [p + side * (u * ws[j]) + o * (0.22 + 0.04 * (width > 6)) for j, p in enumerate(pts)][i0:]
        if len(sub) < 2:
            continue
        ks = len(sub) - 1
        sw = [ws[j + i0] * rng.uniform(0.06, 0.1) * (0.5 + 0.9 * j / ks) for j in range(len(sub))]
        WK.ribbon(mb, sub, sw, "Foam", side, thick=0.12, flat=True)
    if lip_foam:
        sg = pts[1] - pts[0]
        p1 = pts[0] + sg.normalized() * min(sg.length, max(1.2, min(2.4, width * 0.25)))
        lp = [pts[0], pts[0].lerp(p1, 0.5), p1]
        WK.ribbon(mb, [p + o * 0.25 + V(0, 0, 0.12) for p in lp], [ws[0] * 1.03, ws[0] * 0.97, ws[0] * 0.7], "Foam",
                  side, thick=0.22, bulge=0.25)
    if white > 0:
        # agua branca no pe (a queda longa vira espuma antes de bater, como nas referencias)
        i_w = max(1, int(round(n * (1.0 - white))))
        sub = [p + o * 0.3 for p in pts[i_w - 1:]]
        k = len(sub) - 1
        WK.ribbon(mb, sub, [ws[i_w - 1 + j] * (0.15 + 0.75 * j / k) for j in range(len(sub))], "Foam", side,
                  thick=0.14, flat=True)
    imp = pts[-1] + o * 0.5
    imp = V(imp.x, imp.y, bottom_z)
    if base:
        mb.cyl(ws[-1] * 0.42 + 0.5, 0.16, (imp.x, imp.y, bottom_z + 0.06), (0, 0, rng.uniform(0, 1)), "Foam", 9,
               bevel=0.0)
        foam_blobs(mb, rng, imp, ws[-1] * 0.45 + 0.4, 6 if width > 3 else 3, base_s * max(0.5, ws[-1] * 0.085),
                   bottom_z, flat=0.32)
        r = max(0.7, ws[-1] * 0.15) * base_s
        mb.ico(r, (imp.x, imp.y, bottom_z + r * 0.15), "Foam", 2 if width > 5 else 1, (1.7, 1.2, 0.6),
               (0, 0, rng.uniform(0, 3)), jitter=0.12)
    return imp, ws[-1]


# ------------------------------------------------------------------ quedas do fundo + pocos
def back_falls():
    rng = random.Random(1401)
    mb = MB("WATER_BackFalls", C, rng, detail="near")
    fy = L.BACK_CLIFF_Y
    for i, (fx, _) in enumerate(L.BACK_FALLS):
        s = 1 if fx > 0 else -1
        pc = V(fx, fy - POOL_R - 0.6)
        # ---- poco: lamina redonda + borda de cantaria (aberta no fundo = o paredao e na saida do canal)
        mb.cyl(POOL_R + 0.35, 0.5, (pc.x, pc.y, ZPOOL - 0.25), (0, 0, 0), "Water", 28, bevel=0.0)
        out_a = 0.0 if s > 0 else math.pi
        out_hw = (CANAL_E_W if s > 0 else CANAL_W_W) / 2 + 1.1
        rr = POOL_R + 0.62
        n = int(math.tau * rr / 2.9)
        for k in range(n):
            a = math.tau * (k + 0.5) / n
            p = V(pc.x + rr * math.cos(a), pc.y + rr * math.sin(a))
            if p.y > fy - 1.4:
                continue
            da = abs((a - out_a + math.pi) % math.tau - math.pi)
            if rr * math.sin(min(da, math.pi / 2)) < out_hw and da < math.pi / 2:
                continue
            hh = 1.25 + rng.uniform(-0.08, 0.08)
            mb.box((math.tau * rr / n - 0.18, 1.25, hh), (p.x, p.y, L.T2 + hh / 2 - 0.1), (0, 0, a + math.pi / 2),
                   "Stone_Wall_Light", 0.0)
        # pedras dentro do poco, junto ao pe da queda
        for dx in (-FALL_W * 0.55, FALL_W * 0.6):
            pebble(mb, rng, fx + dx, fy - 3.2, ZPOOL - 0.3, rng.uniform(1.8, 2.4))
        # ---- queda larga: o labio fica dentro do sulco do paredao (fundo recuado ~1,6 atras da face y 186)
        top = V(fx, fy + 1.3, L.CLIFF_TOP - 0.15)
        fall(mb, rng, top, ZPOOL, FALL_W, out=(0, -1), lip=3.4, widen=1.12, n=9, streaks_n=4, base_s=1.2, drop=1.3,
             white=0.14)
        foam_blobs(mb, rng, V(fx, fy - 5.0), 5.2, 5, 0.8, ZPOOL, flat=0.28)
        # ---- nascente no plato: rego curto entre pedras (o sulco do terreno emoldura a queda embaixo)
        mb.box((FALL_W - 1.0, 3.4, 0.4), (fx, fy + 2.9, L.CLIFF_TOP + 0.05), (0, 0, 0), "Water", 0.0)
        for sx in (-1, 1):
            x = fx + sx * (FALL_W / 2 + 1.3)
            mb.rock((x, fy + 2.6, L.CLIFF_TOP + 0.8), (3.8, 4.0, 3.6), "Cliff_Rock_Tan_Dark", 2,
                    (0, 0, rng.uniform(0, 3)), jitter=0.3)
        for k in range(3):
            mb.rock((fx + (k - 1) * 3.4, fy + 4.9 + rng.uniform(-0.2, 0.2), L.CLIFF_TOP + 0.6),
                    (3.0, 2.2, 2.2), "Cliff_Rock_Tan_Dark", 1, (0, 0, rng.uniform(0, 3)), jitter=0.3)
        foam_blobs(mb, rng, V(fx, fy + 4.0), 1.8, 4, 0.8, L.CLIFF_TOP + 0.2)
    mb.finish()


# ------------------------------------------------------------------ leste: canal no T2, cascata do muro, riacho do vale
def line_x(p, d, a, r):
    """intersecao da reta p + t d com a reta a + s r"""
    den = d.x * r.y - d.y * r.x
    t = ((a.x - p.x) * r.y - (a.y - p.y) * r.x) / den
    return p + d * t


def se_crossing():
    """o riacho encontra a borda SE em angulo: pontos das 2 margens sobre a borda, meio, normal para fora da ilha,
    direcao da correnteza, normal a esquerda e ate onde a lamina reta vai (t no ultimo trecho)"""
    (x0, y0), (x1, y1) = STREAM_G[-2], STREAM_G[-1]
    p0 = V(x0, y0)
    d = V(x1 - x0, y1 - y0).normalized()
    n = V(-d.y, d.x)
    a, b = V(*RIM_SE[0]), V(*RIM_SE[1])
    r = (b - a).normalized()
    hw = L.STREAM_W / 2 + 0.15
    pl = line_x(p0 + n * hw, d, a, r)
    pr = line_x(p0 - n * hw, d, a, r)
    t_cut = min((pl - p0).dot(d), (pr - p0).dot(d)) - 1.0
    return pl, pr, (pl + pr) / 2, V(r.y, -r.x), d, n, p0, t_cut


def valley_path():
    pl, pr, mid, out, d, n, p0, t_cut = se_crossing()
    e = p0 + d * t_cut
    return chaikin(STREAM_G[:-1] + [(e.x, e.y)], 2)


def se_lip():
    """onde o riacho encontra a borda da ilha (segmento de L.ISLAND_RIM entre (96,-80) e (112,-64))"""
    (x0, y0), (x1, y1) = STREAM_G[-2], STREAM_G[-1]
    a, b = V(96.0, -80.0), V(112.0, -64.0)
    d1 = V(x1 - x0, y1 - y0)
    d2 = b - a
    den = d1.x * d2.y - d1.y * d2.x
    t = ((a.x - x0) * d2.y - (a.y - y0) * d2.x) / den
    return V(x0 + d1.x * t, y0 + d1.y * t)


def east_stream():
    rng = random.Random(1411)
    mb = MB("WATER_Canal_East", C, rng, detail="near")
    H = house_rects()
    # ---- canal de pedra no T2 (poco NE -> muro y 126)
    t2 = chaikin(STREAM_T2, 2)
    water_strip(mb, t2, ZT2, CANAL_E_W)
    pc = V(L.BACK_FALLS[1][0], L.BACK_CLIFF_Y - POOL_R - 0.6)
    for sd in (-1, 1):
        line = offset(t2, sd * (CANAL_E_W / 2 + 0.5))
        coping(mb, rng, line, L.T2 + 0.6, step=3.0,
               skip=lambda c: (c - pc).length < POOL_R + 1.2 or in_rects(c, H) or c.y < 126.6)
    # soleira no muro + pedras-mestras nos cantos do bocal
    xe = STREAM_T2[-1][0]
    mb.box((CANAL_E_W + 0.4, 1.1, 0.5), (xe, 126.55, ZT2 - 0.3), (0, 0, 0), "Stone_Wall_Light", 0.1)
    for sd in (-1, 1):
        cheek(mb, rng, V(xe + sd * (CANAL_E_W / 2 + 0.8), 126.9, L.T2 + 0.9), 1.9)
    # ---- cascata T2 -> vale no muro y 126 (lamina + faixas claras + espuma no pe)
    fall(mb, rng, V(xe, 125.8, ZT2 - 0.05), ZW, CANAL_E_W, out=(0.02, -1), lip=1.7, widen=1.15, n=6, streaks_n=3)
    mb.box((CANAL_E_W + 2.4, 0.3, L.T2 - L.G + 0.2), (xe, 125.95, (L.T2 + L.G) / 2), (0, 0, 0),
           "Cliff_Rock_Tan_Dark", 0.0)
    foam_blobs(mb, rng, V(xe, 121.6), 3.2, 6, 1.0, ZW)
    # ---- riacho do vale
    vp = valley_path()
    lip = se_lip()
    wx, wy, wr = L.WHEEL
    fbc, fbu = footbridge_frame()

    def zone(p):
        if -3.0 < p.y < 27.0:
            return "wheel"
        if (p - fbc).length < FB_LEN / 2 + 1.5 and abs((p - fbc).dot(V(-fbu.y, fbu.x))) < FB_W / 2 + 1.6:
            return "bridge"
        if p.y > 115.0:
            return "cascade"
        if (p - lip).length < 7.0:
            return "lip"
        return None
    water_strip(mb, vp, ZW, L.STREAM_W + 0.3)
    hw = L.STREAM_W / 2
    # ultimo trecho: o leito afunila ate a sangria SE do terreno (a borda cruza o riacho em angulo), com pedras nas
    # 2 margens do funil e pedras-mestras nas pontas do vertedouro
    pl, pr, mid, out, dd, nn_, p0, t_cut = se_crossing()
    c0 = p0 + dd * (t_cut - 0.6)
    rv = V(-out.y, out.x)
    q_sw = V(*SE_SPILL) - rv * (SE_FALL_W / 2)
    q_ne = V(*SE_SPILL) + rv * (SE_FALL_W / 2)
    e0, w0 = c0 + nn_ * (hw + 0.15), c0 - nn_ * (hw + 0.15)
    poly = [e0, w0, q_sw + out * 0.1, q_ne + out * 0.1]
    mb.prism(IL.ccw([(q.x, q.y) for q in poly]), ZW - 0.4, ZW, "Water")
    for sd, a_, b_ in ((1, e0, q_ne), (-1, w0, q_sw)):
        e = (b_ - a_).normalized()
        o_ = V(-e.y, e.x) * sd
        ln = (b_ - a_).length
        t = 1.2
        while t < ln - 1.0:
            q = a_ + e * t + o_ * 0.9
            sz = rng.uniform(1.6, 2.3)
            mb.rock((q.x, q.y, L.G - 0.25), (sz * 1.25, sz, sz * 0.8), "Cliff_Rock_Tan_Dark", 1,
                    (0, 0, rng.uniform(0, 3)), jitter=0.3)
            t += 2.5
        q = b_ + rv * sd * 1.3 - out * 0.5
        mb.rock((q.x, q.y, L.G - 0.3), (3.0, 2.6, 2.2), "Cliff_Rock_Tan_Dark", 1, (0, 0, rng.uniform(0, 3)), jitter=0.3)
    for sd in (-1, 1):
        line = offset(vp, sd * (hw + 0.45))
        P = rs(line, 2.7)
        kinds = ("block", "boulder", "pebble", "open")
        wts = (0.34, 0.26, 0.26, 0.14)
        i = 0
        prev = None
        while i < len(P) - 1:
            k = prev
            while k == prev:
                r = rng.random()
                acc = 0.0
                for kk, w in zip(kinds, wts):
                    acc += w
                    if r <= acc:
                        k = kk
                        break
            run = rng.randint(2, 5) if k == "block" else rng.randint(1, 3)
            for j in range(run):
                if i >= len(P) - 1:
                    break
                a, b = P[i], P[i + 1]
                c = (a + b) / 2
                d = b - a
                ang = math.atan2(d.y, d.x)
                z = zone(c)
                kk = "block" if z in ("wheel", "cascade") else ("boulder" if z == "lip" else k)
                if z == "bridge":
                    kk = "skip"
                if kk == "block":
                    top = L.G + (0.55 if z == "wheel" else 0.35)
                    hh = 1.25 + rng.uniform(-0.1, 0.1)
                    mb.box((d.length - 0.16, 1.1 * rng.uniform(0.92, 1.06), hh),
                           (c.x, c.y, top - hh / 2 + rng.uniform(-0.05, 0.05)),
                           (0, 0, ang + rng.uniform(-0.04, 0.04)), "Stone_Wall_Light", 0.0)
                elif kk == "boulder":
                    if j % 2 == 0:
                        s = rng.uniform(1.9, 2.8)
                        mb.rock((c.x + sd * rng.uniform(-0.2, 0.5), c.y, L.G - 0.25),
                                (s * 1.25, s, s * 0.8), "Cliff_Rock_Tan_Dark" if rng.random() < 0.7
                                else "Stone_Wall_Light", 1, (0, 0, rng.uniform(0, 3)), jitter=0.3)
                    else:
                        pebble(mb, rng, c.x, c.y, L.G - 0.15, rng.uniform(0.8, 1.2))
                elif kk == "pebble":
                    for q in range(2):
                        pp = a + d * rng.uniform(0.1, 0.9)
                        pebble(mb, rng, pp.x - sd * rng.uniform(0.0, 0.6), pp.y, ZW + 0.05, rng.uniform(0.55, 0.95))
                elif kk == "open" and rng.random() < 0.5:
                    pebble(mb, rng, c.x, c.y, ZW + 0.05, rng.uniform(0.5, 0.8))
                i += 1
            prev = k
    # pedras no leito (furam a lamina) + chevrons de espuma rio abaixo
    fr = frames(rs(vp, 3.0))
    placed = tries = 0
    while placed < 7 and tries < 300:
        tries += 1
        p, t, nn = fr[rng.randint(3, len(fr) - 4)]
        q = p + nn * rng.uniform(-hw * 0.6, hw * 0.6)
        if zone(q) in ("wheel", "bridge", "cascade") or 100.0 < q.y < 122.0:
            continue
        s = rng.uniform(1.4, 2.0)
        mb.rock((q.x, q.y, ZW - 0.35), (s * 1.3, s, s * 0.7), "Cliff_Rock_Tan_Dark", 2, (0, 0, rng.uniform(0, 3)),
                jitter=0.22)
        vee(mb, rng, q + t * (s * 0.62), ZW, t)
        placed += 1
    streaks(mb, rng, vp, hw, ZW, 16, zones_skip=lambda q: zone(q) in ("wheel", "bridge"))
    # agua branca onde as pas da roda batem (lado de jusante, embaixo) e rastro rio abaixo
    for k in range(5):
        mb.ico(rng.uniform(0.7, 1.1), (wx + rng.uniform(-1.8, 1.8), wy - rng.uniform(0.5, 3.0), ZW + 0.05), "Foam", 1,
               (1.6, 1.2, 0.35), (0, 0, rng.uniform(0, 3)), jitter=0.2)
    for k in range(5):
        y = wy - 4.0 - k * 2.4
        mb.box((0.34, rng.uniform(1.6, 2.6), 0.08), (wx + rng.uniform(-3.0, 3.0), y, ZW + 0.005),
               (0, 0, rng.uniform(-0.12, 0.12)), "Water_WtrFall", 0.0)
    # labio SE: a agua acelera e espuma na borda
    for k in range(4):
        pebble(mb, rng, lip.x + rng.uniform(-3.5, 3.5), lip.y + rng.uniform(1.0, 4.0), ZW, rng.uniform(0.6, 1.0))
    mb.finish()


# ------------------------------------------------------------------ roda d'agua (peca movel) + apoio fixo
def wheel():
    wx, wy, R = L.WHEEL
    az = L.G + 8.0
    rng = random.Random(1431)
    mb = MB("VFX_WATER_Wheel", VFX, rng, detail="near")
    half = 2.0

    def ring(x, r, a, b, m, n):
        pts = [V(x, wy + math.cos(math.tau * k / n) * r, az + math.sin(math.tau * k / n) * r) for k in range(n + 1)]
        mb.sweep(pts, [(-a, -b), (a, -b), (a, b), (-a, b)], m, True, up=(1, 0, 0))
    for s in (-1, 1):
        x = wx + s * half
        ring(x, R - 0.95, 0.95, 0.3, "Wood_Dark", 24)       # aro externo largo (fecha as pas)
        ring(x, 5.4, 0.38, 0.22, "Wood_Dark", 14)           # aro interno
        for k in range(8):
            a = math.tau * k / 8 + (0.2 if s > 0 else 0.2)
            mb.beam((x, wy, az), (x, wy + math.cos(a) * (R - 1.7), az + math.sin(a) * (R - 1.7)), 0.5, 0.5,
                    "Wood_Dark", 0.0)
    # pas radiais entre os aros (22: abaixo do limiar de variantes -> 1 malha so), a ponta no raio R
    for k in range(22):
        a = math.tau * (k + 0.5) / 22
        rp = R - 1.05
        mb.box((2 * half - 0.3, 0.28, 2.1), (wx, wy + math.cos(a) * rp, az + math.sin(a) * rp), (a - math.pi / 2, 0, 0),
               "Wood_Plank", 0.0)
    # cubo e eixo (o eixo entra no moinho a oeste: parede leste em x = MILL_x + largura/2)
    mb.cyl(1.5, 2 * half + 1.6, (wx, wy, az), (0, math.pi / 2, 0), "Metal_Dark", 12, bevel=0.0)
    mill_e = L.MILL[0] + L.MILL[2] / 2
    mb.rod((mill_e, wy, az), (wx + 9.0, wy, az), 0.55, "Wood_Dark", 8)
    for x in (wx - half - 1.0, wx + half + 1.0):
        mb.cyl(0.9, 0.5, (x, wy, az), (0, math.pi / 2, 0), "Metal_Dark", 10, bevel=0.0)
    ob = mb.finish()
    ob["pivot"] = (wx, wy, az)
    ob["axis"] = (1.0, 0.0, 0.0)
    ob["rpm"] = -4.0
    ob["note"] = ("roda de baixo: o riacho corre para -Y e empurra as pas de baixo; rpm negativo em torno de +X = "
                  "pas de baixo andando para jusante (4 rpm)")
    # ---- apoio fixo: pilares de cantaria nas 2 margens, mancais de madeira com cinta de ferro, maos-francesas
    fm = MB("WATER_Wheel_Frame", C, random.Random(1432), detail="near")
    for x, sgn in ((wx - 7.6, -1), (wx + 7.6, 1)):
        fm.box((3.4, 4.4, 0.9), (x, wy, L.G + 0.25), (0, 0, 0), "Stone_Wall_Light", 0.15)
        h = az - 1.0 - L.G
        for k in range(3):
            hk = h / 3
            fm.box((2.6 - k * 0.12, 3.6 - k * 0.15, hk - 0.08), (x, wy, L.G + hk * (k + 0.5)), (0, 0, 0.02 * (k - 1)),
                   "Stone_Wall_Light", 0.14)
        fm.box((3.0, 4.2, 0.8), (x, wy, az - 0.6), (0, 0, 0), "Wood_Dark", 0.1)
        fm.box((1.9, 1.5, 1.9), (x, wy, az), (0, 0, 0), "Wood_Dark", 0.1)
        fm.box((2.0, 1.66, 0.3), (x, wy, az + 0.95), (0, 0, 0), "Metal_Dark", 0.0)
        for sy in (-1, 1):
            fm.box((0.3, 0.3, 2.0), (x + sgn * 0.0, wy + sy * 0.83, az), (0, 0, 0), "Metal_Dark", 0.0)
        # maos-francesas de madeira (lado de fora do pilar)
        for sy in (-1, 1):
            fm.beam((x + sgn * 0.2, wy + sy * 4.2, L.G), (x + sgn * 0.2, wy + sy * 1.7, az - 1.4), 0.55, 0.55,
                    "Wood_Dark", 0.05)
    fm.finish()


# ------------------------------------------------------------------ ponte em arco de madeira (pisavel, com colisao)
def footbridge_frame():
    """centro da ponte = projecao de L.FOOTBRIDGE no eixo do riacho; u = travessia (perpendicular a correnteza)"""
    p = V(*L.FOOTBRIDGE)
    best = None
    for a, b in zip(STREAM_G, STREAM_G[1:]):
        A, B = V(*a), V(*b)
        d = B - A
        t = max(0.0, min(1.0, (p - A).dot(d) / d.length_squared))
        q = A + d * t
        if best is None or (q - p).length < best[0]:
            best = ((q - p).length, q, d.normalized())
    _, c, f = best
    u = V(-f.y, f.x)
    if u.x < 0:
        u = -u
    return c, u


def footbridge():
    rng = random.Random(1451)
    mb = MB("WATER_Footbridge", C, rng, detail="near")
    c, u = footbridge_frame()
    v = V(-u.y, u.x)
    yaw = math.atan2(u.y, u.x)
    Lb, W, H = FB_LEN, FB_W, FB_RISE

    def zc(s):
        return L.G + H * math.cos(math.pi * s / Lb)

    def P(s, t, dz=0.0):
        return V(c.x + u.x * s + v.x * t, c.y + u.y * s + v.y * t, zc(s) + dz)
    # tabuleiro: 26 tabuas transversais acompanhando o arco
    n = 26
    ds = Lb / n
    for i in range(n):
        s = -Lb / 2 + (i + 0.5) * ds
        th = math.atan(-H * math.pi / Lb * math.sin(math.pi * s / Lb))
        q = P(s, rng.uniform(-0.06, 0.06), -0.18)
        mb.box((ds - 0.08, W + rng.uniform(-0.1, 0.1), 0.36), q, (0, -th, yaw), "Wood_Plank", 0.0)
    # longarinas curvas por baixo
    ks = [(-Lb / 2 + Lb * k / 12) for k in range(13)]
    for t in (-(W / 2 - 0.7), W / 2 - 0.7):
        mb.sweep([P(s, t, -0.9) for s in ks], [(-0.35, -0.55), (0.35, -0.55), (0.35, 0.55), (-0.35, 0.55)],
                 "Wood_Dark", True)
    # travessas sob o tabuleiro
    for s in (-Lb / 4, 0.0, Lb / 4):
        q = P(s, 0, -1.1)
        mb.box((0.6, W - 0.6, 0.5), q, (0, 0, yaw), "Wood_Dark", 0.0)
    # guarda-corpo: 5 montantes por lado, corrimao e travessa curvos; os 4 das pontas mais altos com lanterna
    rs_ = [-Lb / 2 + 0.6, -Lb / 4, 0.0, Lb / 4, Lb / 2 - 0.6]
    for sd in (-1, 1):
        t = sd * (W / 2 + 0.1)
        for j, s in enumerate(rs_):
            end = j in (0, len(rs_) - 1)
            h = 4.3 if end else 3.5
            q = P(s, t, h / 2 - 0.2)
            mb.box((0.62 if not end else 0.8, 0.62 if not end else 0.8, h), q, (0, 0, yaw), "Wood_Dark", 0.08)
            if end:
                top = P(s, t, h - 0.2)
                mb.box((1.05, 1.05, 1.0), top + V(0, 0, 0.55), (0, 0, yaw), "Lantern_Glow", 0.0)
                mb.box((1.5, 1.5, 0.32), top + V(0, 0, 1.2), (0, 0, yaw), "Wood_Dark", 0.06)
        rail = [P(s, t, 3.2) for s in [rs_[0] + (rs_[-1] - rs_[0]) * k / 10 for k in range(11)]]
        mb.sweep(rail, [(-0.28, -0.2), (0.28, -0.2), (0.28, 0.2), (-0.28, 0.2)], "Wood_Dark", True)
        mid = [P(s, t, 1.7) for s in [rs_[0] + (rs_[-1] - rs_[0]) * k / 10 for k in range(11)]]
        mb.sweep(mid, [(-0.18, -0.16), (0.18, -0.16), (0.18, 0.16), (-0.18, 0.16)], "Wood_Dark", True)
    # cabeceiras de pedra nas margens
    for sg in (-1, 1):
        q = P(sg * (Lb / 2 + 0.4), 0, 0)
        mb.box((2.6, W + 2.2, 1.3), V(q.x, q.y, L.G - 0.45), (0, 0, yaw), "Stone_Wall_Light", 0.15)
        for sd in (-1, 1):
            q2 = P(sg * (Lb / 2 - 3.2), sd * (W / 2 + 0.9), 0)
            mb.box((3.6, 1.2, 1.0), V(q2.x, q2.y, L.G - 0.1), (0, 0, yaw), "Stone_Wall_Light", 0.12)
    mb.finish()
    # ---- colisao: 6 rampas acompanhando o arco + 2 guarda-corpos
    A = "WaterFootbridge"
    k = 6
    for i in range(k):
        s0 = -Lb / 2 + Lb * i / k
        s1 = s0 + Lb / k
        col_ramp(A, P(s0, 0), P(s1, 0), W, 1.0)
    for sd in (-1, 1):
        q = c + v * sd * (W / 2 + 0.25)
        col_box(A, (Lb - 0.4, 0.6, H + 5.0), (q.x, q.y, L.G + (H + 5.0) / 2 - 0.5), (0, 0, yaw))


# ------------------------------------------------------------------ oeste: poco NO -> canal T2 -> T1 -> borda oeste
def west_canal():
    rng = random.Random(1461)
    mb = MB("WATER_Canal_West", C, rng, detail="near")
    H = house_rects()
    pc = V(L.BACK_FALLS[0][0], L.BACK_CLIFF_Y - POOL_R - 0.6)
    t2 = chaikin(WEST_T2, 2)
    t1 = chaikin(WEST_T1, 2)
    water_strip(mb, t2, ZT2, CANAL_W_W, 0.36)
    water_strip(mb, t1, ZT1, CANAL_W_W, 0.36)
    for sd in (-1, 1):
        coping(mb, rng, offset(t2, sd * (CANAL_W_W / 2 + 0.45)), L.T2 + 0.55, h=1.05, w=0.95, step=2.6,
               skip=lambda c: (c - pc).length < POOL_R + 1.2 or in_rects(c, H) or c.y < 126.5)
        coping(mb, rng, offset(t1, sd * (CANAL_W_W / 2 + 0.45)), L.T1 + 0.55, h=1.05, w=0.95, step=2.6,
               skip=lambda c: c.y > 125.4 or c.x < WEST_BASIN[1][0] + 0.4)
    # cascata T2 -> T1 no degrau y 126
    x0 = WEST_T2[-1][0]
    mb.box((CANAL_W_W + 0.4, 1.0, 0.5), (x0, 126.5, ZT2 - 0.3), (0, 0, 0), "Stone_Wall_Light", 0.1)
    for sd in (-1, 1):
        cheek(mb, rng, V(x0 + sd * (CANAL_W_W / 2 + 0.7), 126.8, L.T2 + 0.8), 1.6)
    fall(mb, rng, V(x0, 125.8, ZT2 - 0.05), ZT1, CANAL_W_W, out=(0, -1), lip=0.9, widen=1.12, n=4, streaks_n=1,
         base_s=0.8)
    # bacia na borda oeste: o canal entra pelo leste, o vertedouro e a propria borda (sangria do terreno)
    mb.prism(IL.ccw(WEST_BASIN), ZT1 - 0.4, ZT1, "Water")
    bx1, by0, by1 = WEST_BASIN[1][0], WEST_BASIN[0][1], WEST_BASIN[2][1]
    yc = WEST_T1[-1][1]
    cw = CANAL_W_W / 2 + 0.9
    sides = [[(bx1 + 0.55, by0 - 0.55), (bx1 + 0.55, yc - cw)],                # leste (sul do canal)
             [(bx1 + 0.55, yc + cw), (bx1 + 0.55, by1 + 0.55)],                # leste (norte do canal)
             [(-157.4, by0 - 0.55), (bx1 + 0.55, by0 - 0.55)],                 # sul
             [(-156.8, by1 + 0.55), (bx1 + 0.55, by1 + 0.55)]]                 # norte
    for a, b in sides:
        coping(mb, rng, [a, b], L.T1 + 0.55, h=1.05, w=0.95, step=2.4)
    cheek(mb, rng, V(-157.3, by0 - 0.4, L.T1 + 0.9), 1.8)
    cheek(mb, rng, V(-156.7, by1 + 0.4, L.T1 + 0.9), 1.8)
    mb.finish()


# ------------------------------------------------------------------ quedas no mar (SE, oeste) + galeria de drenagem
def overflow(mb, a, b, w):
    """lamina rasa que passa por cima das colunas rebaixadas da sangria (de a na borda ate b, SPILL_OUT para fora)"""
    mb.beam(a, b, w, 0.35, "Water", 0.0)


def sea_falls():
    rng = random.Random(1471)
    mb = MB("WATER_SeaFalls", C, rng, detail="far", floor=-999)
    # ---- SE: funil do riacho -> sangria (101, -75) -> lamina por cima das colunas -> queda longa -> mar
    pl, pr, mid, out, dd, nn_, p0, t_cut = se_crossing()
    f0 = V(*SE_SPILL)
    a = V(f0.x, f0.y, ZW - 0.2)
    b = V(f0.x + out.x * SPILL_OUT, f0.y + out.y * SPILL_OUT, L.G - 1.05)
    overflow(mb, a, b, SE_FALL_W)
    imp, wb = fall(mb, rng, b + V(0, 0, -0.1), L.SEA + 0.3, SE_FALL_W, out=(out.x, out.y), lip=1.8, widen=1.7,
                   n=12, streaks_n=5, base=False, drop=1.45, white=0.22)
    sea_foam(mb, rng, imp, wb)
    # ---- oeste: bacia -> sangria (-158, 76) -> lamina por cima das colunas -> queda longa -> mar
    wo = V(*W_OUT)
    f0 = V(-157.95, 75.7)
    a = V(f0.x, f0.y, ZT1 - 0.15)
    b = V(f0.x + wo.x * SPILL_OUT, f0.y + wo.y * SPILL_OUT, L.T1 - 1.05)
    overflow(mb, a, b, W_FALL_W)
    imp, wb = fall(mb, rng, b + V(0, 0, -0.1), L.SEA + 0.3, W_FALL_W, out=(wo.x, wo.y), lip=1.8, widen=1.7,
                   n=12, streaks_n=4, base=False, drop=1.45, white=0.22)
    sea_foam(mb, rng, imp, wb)
    # ---- galeria de drenagem do fosso (face SO, cota ~0): testa de cantaria a frente das colunas -> mar
    gm, gn, gt = drain_frame()
    z0 = -1.3                                   # soleira (o fosso esta em L.PIT; a galeria desce ate aqui)
    ow, oh = 4.2, 3.0                           # vao livre: largura, altura ate a nascente do arco
    o0 = DRAIN_OFF
    ang = math.atan2(gt.y, gt.x)

    def G(a, o, z):                             # a = ao longo da face, o = para fora da borda
        return V(gm.x + gt.x * a + gn.x * o, gm.y + gt.y * a + gn.y * o, z)
    z_top = z0 + oh + ow / 2 + 2.0
    # testa (muro de cantaria) cravada no penhasco: da borda ate DRAIN_OFF para fora
    mb.box((ow + 6.4, o0 + 1.6, z_top + 12.0), G(0, o0 / 2 - 0.8, (z_top - 12.0) / 2), (0, 0, ang), "Stone_Wall_Dark",
           0.0)
    mb.box((ow + 7.0, o0 + 2.0, 0.6), G(0, o0 / 2 - 0.6, z_top + 0.3), (0, 0, ang), "Stone_Wall_Dark", 0.0)
    # vazio escuro + moldura: ombreiras, aduelas em arco, fecho, soleira
    mb.box((ow + 0.3, 0.4, oh + ow / 2 + 0.3), G(0, o0 + 0.05, z0 + (oh + ow / 2) / 2), (0, 0, ang), "Stone_WtrVoid",
           0.0)
    for sd in (-1, 1):
        mb.box((1.5, 1.5, oh), G(sd * (ow / 2 + 0.75), o0 + 0.75, z0 + oh / 2), (0, 0, ang), "Stone_Wall_Dark", 0.0)
    rr = ow / 2 + 0.75
    for k in range(7):
        a = math.pi * (k + 0.5) / 7
        q = G(math.cos(a) * rr, o0 + 0.85, z0 + oh + math.sin(a) * rr)
        big = k == 3
        mb.box((1.55 if big else 1.35, 1.7 if big else 1.5, 1.5 if big else 1.25), q, (0, math.pi / 2 - a, ang),
               "Stone_Wall_Dark", 0.0)
    mb.box((ow + 1.2, 2.4, 1.6), G(0, o0 + 1.2, z0 - 0.8), (0, 0, ang), "Stone_Wall_Dark", 0.0)
    # grade (barras) no vao - a agua sai por baixo dela
    for k in range(5):
        a = -ow / 2 + ow * (k + 0.5) / 5
        hk = oh + math.sqrt(max(0.0, (ow / 2) ** 2 - a * a)) - 0.3
        mb.box((0.22, 0.22, hk - 0.6), G(a, o0 + 0.55, z0 + 0.6 + (hk - 0.6) / 2), (0, 0, ang), "Stone_Wall_Dark", 0.0)
    # agua saindo pela soleira -> queda longa -> mar
    q0, q1 = G(0, o0 + 0.1, 0), G(0, o0 + 2.3, 0)
    water_strip(mb, [(q0.x, q0.y), (q1.x, q1.y)], z0 + 0.12, ow - 0.6, 0.3)
    imp, wb = fall(mb, rng, G(0, o0 + 2.4, z0 + 0.08), L.SEA + 0.3, ow - 0.6, out=(gn.x, gn.y), lip=1.4, widen=1.9,
                   n=12, streaks_n=2, base=False, drop=1.45, white=0.22)
    sea_foam(mb, rng, imp, wb)
    mb.finish()


def drain_frame():
    """boca da galeria: onde o raio DRAIN_DIR a partir do centro do fosso fura a borda da ilha (face SO)"""
    d = V(math.cos(DRAIN_DIR), math.sin(DRAIN_DIR))
    t, seg = _ray(V(0, 0), d, L.ISLAND_RIM)
    a, b = V(*L.ISLAND_RIM[seg]), V(*L.ISLAND_RIM[(seg + 1) % len(L.ISLAND_RIM)])
    gt = (b - a).normalized()
    gn = V(gt.y, -gt.x)                         # contorno anti-horario: normal para fora
    return d * t, gn, gt


def _ray(p, d, poly):
    best = None
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        ex, ey = b[0] - a[0], b[1] - a[1]
        den = d.x * ey - d.y * ex
        if abs(den) < 1e-9:
            continue
        t = ((a[0] - p.x) * ey - (a[1] - p.y) * ex) / den
        s = ((a[0] - p.x) * d.y - (a[1] - p.y) * d.x) / den
        if t > 1e-6 and 0.0 <= s <= 1.0 and (best is None or t < best[0]):
            best = (t, i)
    return best


# ------------------------------------------------------------------ entrada do modulo
def build():
    back_falls()
    east_stream()
    wheel()
    footbridge()
    west_canal()
    sea_falls()
