# il_water - ZONA WATER da Ilha 1 (Naruto / Vila da Folha), rodada 2 (planta nova da agua).
# 7 quedas no total, cada uma com origem e destino (nao inventar outras):
#   PAREDAO (L.BACK_FALLS, x -80, +80, -30): rego no plato -> queda de 14 dentro da garganta do terreno (topo da coluna
#       de fundo em L.CLIFF_TOP-0,3) -> poco no T2. O poco -30 (atras do salao) escoa pelo canal L.CANAL_MID ate o poco
#       NO (-80); o poco NO escoa pelo canal oeste (T2 -> cascata -> T1 -> bacia) ate a QUEDA OESTE (16).
#   SISTEMA NE: poco (80) -> canal L.STREAM_T2 no T2 -> vertedouro ao longo da borda -> QUEDA NE (14) ate o mar, ao
#       lado da ponte de saida: a crista fica toda a >= 4 da borda do tabuleiro (eixo (96,96) a 45 graus, largura 18) e
#       a cortina anda a 40 graus (paralela a ponte), alargando so para o norte; nada cai sobre o tabuleiro.
#   VALE: BICA de pedra no nicho do muro x=108 (L.SPOUT) -> bacia de pedra -> riacho em L.STREAM com a lamina em
#       L.STREAM_WATER (4,6) no leito do contrato (il_col.stream_bed_poly) -> roda (VFX_WATER_Wheel) -> ponte em arco
#       (L.FOOTBRIDGE, colisao) -> QUEDA SE (16) pela borda.
#   DRENAGEM do fosso: galeria de cantaria na face SO (-88,5; -71) -> QUEDA SO (12).
# Quedas grandes como nas refs 14-18: lamina base clara (Water_WtrSheet), faixas Water_WtrFall, riscos de espuma,
# faixa de espuma na crista, 1-2 quebras (degrau para fora) onde a lamina cruza a prateleira / as faixas do penhasco,
# cortina que alarga embaixo e anel de espuma (r 10-14) em L.SEA+0,3 no pe das 4 que caem no mar.
# Camadas da cortina separadas >= 0,12 (regra de z-fighting do Roblox). Colisao: ponte em arco + pilares da roda.
# Sem luzes. O terreno escava o leito, o nicho da bica, as sangrias e as gargantas (contrato TERRENO x AGUA).
import math, random
from mathutils import Vector
import fm_lib
from fm_lib import MB, S, col_box, col_ramp, resample
import fm_water_kit as WK
import il_lib as IL
import il_layout as L

C = "06_WATER"
VFX = "12_VFX_HELPERS"
# materiais novos (3/4)
# 1: o escuro do tunel da galeria de drenagem (le como buraco, nao como pedra)
fm_lib.MATS.setdefault("Stone_WtrVoid", (S(30, 32, 38), 0.95, 0.0, 0, None, 0.0))
# 2: faixas das quedas (ciano medio das referencias) e ondulacao dos riachos
fm_lib.MATS.setdefault("Water_WtrFall", (S(104, 184, 232), 0.2, 0.0, 0.35, S(104, 184, 232), 0.0))
# 3: lamina base das quedas grandes (clara, quase branca-azulada como nas refs 14-18)
fm_lib.MATS.setdefault("Water_WtrSheet", (S(190, 228, 252), 0.25, 0.0, 0.3, S(190, 228, 252), 0.0))
SHEET, BAND = "Water_WtrSheet", "Water_WtrFall"

# ------------------------------------------------------------------ cotas da agua
ZW = L.STREAM_WATER        # lamina do riacho do vale = piso de colisao do leito (il_col)
ZT2 = L.T2 + 0.2           # canais de pedra no T2
ZT1 = L.T1 + 0.2           # canal de pedra no T1 (oeste)
ZPOOL = L.T2 + 0.35        # pocos do pe das quedas do paredao
POOL_R = 8.6               # pocos NO e NE (redondos)
MID_POOL = (-30.0, 180.4, 5.0, 5.0)   # poco atras do salao: centro, meio-comprimento em x, raio (estadio x -40..-20)
CANAL_E_W = 8.4            # lamina do canal NE no T2
CANAL_W_W = 3.8            # lamina dos canais oeste e do meio
FB_LEN, FB_W, FB_RISE = 21.0, 6.0, 2.4   # ponte em arco: vao, largura do tabuleiro, flecha
THROAT = 5.6               # a crista das quedas do paredao fica a isto atras do pe (a garganta tem 6-8)
WIDTH = dict(back=14.0, ne=14.0, se=16.0, west=16.0, drain=12.0)
SPILL_OUT = 2.9            # as quedas da borda comecam a este tanto para fora da borda
SEA_BREAKS = [(L.SHELF_Z - 11.0, 2.6), (-52.0, 2.3)]   # quebras: fundo da prateleira e faixa do penhasco baixo

# ------------------------------------------------------------------ tracados
WEST_T2 = [(-88.0, 177.0), (-100.0, 175.2), (-110.0, 170.5), (-118.5, 163.5), (-126.0, 157.0), (-131.5, 151.0),
           (-135.5, 145.0), (-137.5, 139.0), (-139.5, 132.0), (-140.5, 126.0)]
WEST_T1 = [(-140.5, 126.0), (-142.0, 115.0), (-144.0, 102.0), (-145.8, 90.0), (-147.8, 80.5), (-150.2, 76.4),
           (-151.5, 75.7)]
# bacia na borda oeste (T1): o canal entra pelo leste; o vertedouro e a borda (16 de crista em volta do vertice
# (-158, 76) do contorno)
WEST_BASIN = [(-157.9, 67.4), (-151.3, 67.4), (-151.3, 84.6), (-156.55, 84.6), (-157.9, 76.0)]
W_SPILL = (-158.0, 76.0)
W_TAN = Vector((-8.0, -90.0, 0.0)).normalized()     # tangente do contorno no vertice (sentido anti-horario)
W_OUT = Vector((W_TAN.y, -W_TAN.x, 0.0))              # normal para fora
# SE: segmento do contorno que o riacho cruza (obliquo ~31 graus) e a sangria do terreno
RIM_SE = ((96.0, -80.0), (112.0, -64.0))
SE_SPILL = (101.0, -75.0)
# NE: segmento do contorno entre (122,124) e (116,160); vertedouro ao longo dele
NE_T = Vector((-6.0, 36.0, 0.0)).normalized()        # tangente (para o norte)
NE_N = Vector((NE_T.y, -NE_T.x, 0.0))                  # normal para fora
NE_OUT = Vector((math.cos(math.radians(40.0)), math.sin(math.radians(40.0)), 0.0))
NE_Y = (140.7, 154.7)      # crista: trecho da borda (y) - a ponta sul fica a >= 4 do tabuleiro da ponte de saida
DRAIN_DIR = math.radians(219.0)    # raio do centro do fosso ate a boca da galeria (face SO; sangria (-88,5, -71))
DRAIN_OFF = 2.6                    # testa da galeria: a frente das colunas (na janela de 12 elas saem <= 2,4)

# ------------------------------------------------------------------ cameras de revisao (360 graus + altura do jogador)
CAMS = {
    "CAM_Water_Spout": ((123.0, 64.0, L.G + 5.5), (108.5, 80.0, 9.5), 20),
    "CAM_Water_Wheel": ((104.0, -16.0, L.G + 5.5), (118.0, 12.0, L.G + 8.5), 20),
    "CAM_Water_Margin": ((109.0, -24.0, L.G + 5.3), (114.0, 8.0, L.G + 3.0), 20),
    "CAM_Water_Footbridge": ((91.0, -58.0, L.G + 5.5), (113.4, -39.7, L.G + 2.5), 20),
    "CAM_Water_NEFall": ((150.0, 200.0, 40.0), (122.0, 146.0, 0.0), 18),
    "CAM_Water_NESea": ((175.0, 255.0, 5.0), (124.0, 148.0, -35.0), 22),
    "CAM_Water_NECanal": ((100.0, 170.0, 36.0), (117.0, 146.0, 21.0), 20),
    "CAM_Water_BackFalls": ((0.0, 96.0, 140.0), (0.0, 184.0, 30.0), 18),
    "CAM_Water_NEPool": ((90.0, 159.0, L.T2 + 5.5), (80.0, 182.0, L.T2 + 9.0), 18),
    "CAM_Water_MidPool": ((-30.0, 150.0, 62.0), (-30.0, 182.0, 26.0), 20),
    "CAM_Water_MidCanal": ((-46.0, 164.0, L.T2 + 9.0), (-60.0, 180.0, L.T2 + 2.0), 20),
    "CAM_Water_SE": ((205.0, -200.0, 26.0), (102.0, -86.0, -38.0), 22),
    "CAM_Water_SEClose": ((140.0, -120.0, 0.0), (102.0, -78.0, -15.0), 22),
    "CAM_Water_SELow": ((175.0, -160.0, -100.0), (104.0, -82.0, -80.0), 24),
    "CAM_Water_SERing": ((150.0, -125.0, -78.0), (106.0, -84.0, -110.0), 20),
    "CAM_Water_DrainClose": ((-112.0, -96.0, 6.0), (-89.0, -72.0, -3.0), 20),
    "CAM_Water_West": ((-300.0, 96.0, 24.0), (-160.0, 76.0, -34.0), 22),
    "CAM_Water_Drain": ((-195.0, -175.0, 4.0), (-92.0, -76.0, -32.0), 22),
    "CAM_Water_NWCanal": ((-132.0, 100.0, L.T1 + 10.0), (-141.0, 128.0, L.T1 + 3.0), 18),
    "CAM_Water_Back": ((170.0, 262.0, 118.0), (86.0, 150.0, 26.0), 22),
    "CAM_Water_East": ((250.0, 20.0, 64.0), (112.0, 10.0, 4.0), 22),
    "CAM_Water_Front": ((0.0, -340.0, 40.0), (0.0, -70.0, -30.0), 22),
    "CAM_Water_North": ((0.0, 300.0, 150.0), (0.0, 175.0, 60.0), 22),
}

# rota de QA pela margem oeste do riacho (chao G) desde a ponte em arco ate a roda (o leito fica em 4,6)
EXTRA_ROUTES = {"VALE:margem->roda": ([(100.0, -30.5), (105.5, -25.0), (108.3, -16.0), (109.0, -6.0),
                                       (109.3, 1.0), (109.4, 6.2)], L.G)}


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


def in_poly(p, poly):
    x, y = p[0], p[1]
    ins = False
    n = len(poly)
    for i in range(n):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % n]
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            ins = not ins
    return ins


def house_rects():
    """pegadas das casas (+0,45 do soco de pedra), da planta"""
    out = []
    for (x, y, w, d, yaw, r) in L.HOUSES_T1 + L.HOUSES_T2 + L.EAST_HOUSES:
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
        if d.length < 0.8:
            continue
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


def ripple(mb, rng, q, ang, z, ln=None, m=BAND):
    """faixa curta de ondulacao sobre a lamina (0,12 acima dela: nada rente entre materiais diferentes)"""
    ln = ln or rng.uniform(1.6, 3.0)
    mb.box((ln, rng.uniform(0.32, 0.44), 0.3), (q.x, q.y, z - 0.03), (0, 0, ang), m, 0.0)


def vee(mb, rng, p, z, t):
    """V da correnteza a jusante de uma pedra: 2 faixas claras abrindo rio abaixo + espuma colada na pedra"""
    for sd in (-1, 1):
        a = math.atan2(t.y, t.x) + sd * math.radians(rng.uniform(22, 32))
        ln = rng.uniform(1.4, 2.2)
        d = V(math.cos(a), math.sin(a))
        ripple(mb, rng, p + d * (ln / 2 + 0.2), a, z, ln)
    mb.ico(0.6, (p.x - t.x * 0.3, p.y - t.y * 0.3, z + 0.05), "Foam", 1, (1.6, 1.1, 0.3), (0, 0, math.atan2(t.y, t.x)),
           jitter=0.15)


def cheek(mb, rng, p, s, m="Stone_Wall_Light"):
    """pedra-mestra no canto de um bocal / vertedouro"""
    mb.box((s, s, s * 0.9), (p.x, p.y, p.z - s * 0.2), (0, 0, rng.uniform(-0.2, 0.2)), m, 0.0)


def line_x(p, d, a, r):
    """intersecao da reta p + t d com a reta a + s r"""
    den = d.x * r.y - d.y * r.x
    t = ((a.x - p.x) * r.y - (a.y - p.y) * r.x) / den
    return p + d * t


# ------------------------------------------------------------------ QUEDA GRANDE (refs 14-18)
def fall_keys(z_top, z_bot, lip, breaks):
    """perfil (avanco para fora, z) da cortina: labio parabolico curto, prumo, quebras (degrau para fora) e pe.
    Retorna (pontos, quebras usadas)"""
    P = [(0.0, z_top), (lip * 0.55, z_top - 0.9), (lip * 0.85, z_top - 2.3), (lip, z_top - 4.6)]
    adv = lip
    used = []
    for zb, st in sorted(breaks, reverse=True):
        if not (z_bot + 5.0 < zb < z_top - 6.0):
            continue
        P += [(adv, zb + 1.0), (adv + st * 0.6, zb - 0.4), (adv + st * 0.9, zb - 1.7), (adv + st, zb - 3.3)]
        adv += st
        used.append((zb, st))
    P.append((adv, z_bot))
    return P, used


class Fall:
    """cortina d'agua: crista (centro, direcao lateral 'side'), avanco para 'out', de z_top ate z_bot.
    w_crest -> w em 'flare' studs (bocal estreito que abre), depois alarga ate w*widen no pe. grow: +1 = alarga so
    para +side, -1 so para -side, 0 = simetrico."""

    def __init__(self, crest, side, out, z_top, z_bot, w, widen=1.35, grow=0.0, lip=1.8, breaks=(), w_crest=None,
                 flare=10.0):
        s = V(side[0], side[1]).normalized()
        o = V(out[0], out[1]).normalized()
        f = V(s.y, -s.x)
        if f.dot(o) < 0:
            s, f = -s, -f
            grow = -grow
        self.c, self.s, self.o, self.f = V(crest[0], crest[1]), s, o, f
        self.z_top, self.z_bot, self.w, self.widen, self.grow = z_top, z_bot, w, widen, grow
        self.w_crest = w if w_crest is None else w_crest
        self.flare = flare
        self.keys, self.breaks = fall_keys(z_top, z_bot, lip, breaks)
        self.bulge = min(0.7, 0.04 * w + 0.15)

    def width(self, z):
        h = max(1e-3, self.z_top - self.z_bot)
        t = min(1.0, max(0.0, (self.z_top - z) / h))
        k = min(1.0, max(0.0, (self.z_top - z) / self.flare))
        k = k * k * (3 - 2 * k)
        w0 = self.w_crest + (self.w - self.w_crest) * k
        return w0 * (1.0 + (self.widen - 1.0) * t ** 1.3)

    def adv(self, z):
        K = self.keys
        if z >= K[0][1]:
            return K[0][0]
        for (a0, z0), (a1, z1) in zip(K, K[1:]):
            if z1 <= z <= z0:
                return a0 + (a1 - a0) * ((z0 - z) / (z0 - z1) if z0 > z1 else 0.0)
        return K[-1][0]

    def P(self, u, z, off=0.0):
        """ponto na fracao lateral u (-0,5..0,5) da largura em z, 'off' para a frente (f)"""
        wz = self.width(z)
        shift = self.grow * (wz - self.w_crest) / 2
        q = self.c + self.o * self.adv(z) + self.s * (shift + u * wz) + self.f * off
        return V(q.x, q.y, z)

    def zs(self, z_from=None, z_to=None, gap=14.0):
        """cotas dos pontos da cortina entre z_from e z_to (pontos-chave + intermediarios a cada 'gap')"""
        z_from = self.z_top if z_from is None else z_from
        z_to = self.z_bot if z_to is None else z_to
        ks = [z_from] + [z for a, z in self.keys if z_to < z < z_from] + [z_to]
        if self.flare > 0:
            ks += [self.z_top - self.flare * f for f in (0.35, 0.7) if z_to < self.z_top - self.flare * f < z_from]
        ks = sorted(set(ks), reverse=True)
        out = [ks[0]]
        for z in ks[1:]:
            prev = out[-1]
            n = int((prev - z) / gap)
            for i in range(1, n + 1):
                out.append(prev - (prev - z) * i / (n + 1))
            out.append(z)
        return out

    def strip(self, mb, u, fw, z_from, z_to, off, m, thick, flat=True, bulge=0.0, wmin=0.3, gap=40.0):
        Z = self.zs(z_from, z_to, gap)
        if len(Z) < 2:
            return
        pts = [self.P(u, z, off) for z in Z]
        ws = [max(wmin, fw * self.width(z)) for z in Z]
        WK.ribbon(mb, pts, ws, m, self.s, thick=thick, bulge=bulge, flat=flat)


def big_fall(mb, rng, F, bands=None, streaks=None, edges=False, crest=True, foam_breaks=True):
    """lamina clara + faixas ciano + riscos de espuma + crista de espuma + espuma nas quebras. Retorna (pe, largura)"""
    b = F.bulge
    H = F.z_top - F.z_bot
    Z = F.zs(gap=20.0)
    WK.ribbon(mb, [F.P(0.0, z) for z in Z], [F.width(z) for z in Z], SHEET, F.s, thick=0.4, bulge=b)
    # bordas de agua mais escura (o recorte da cortina contra o penhasco)
    if edges:
        for sd in (-1, 1):
            F.strip(mb, sd * 0.455, 0.07, F.z_top - 0.8, F.z_bot + 0.6, 0.1 * b + 0.44, "Water", 0.3, wmin=0.4)
    # faixas ciano (Water_WtrFall): comecam em alturas diferentes, abrem com a cortina
    nb = bands if bands is not None else max(2, int(F.w / 5.0))
    cells = [(-0.34 + 0.68 * (k + 0.5) / nb) for k in range(nb)]
    for k, u in enumerate(cells):
        u += rng.uniform(-0.03, 0.03)
        fw = rng.uniform(0.05, 0.08)
        z0 = F.z_top - 1.4 - rng.uniform(0.0, 0.3) * H * (0.5 if k % 2 else 1.0)
        z1 = F.z_bot + rng.uniform(0.5, 4.0)
        F.strip(mb, u, fw, z0, z1, b + 0.42, BAND, 0.3)
    # riscos de espuma (brancos, finos) entre as faixas
    ns = streaks if streaks is not None else max(3, int(F.w / 1.8))
    for k in range(ns):
        u = -0.42 + 0.84 * (k + 0.5) / ns + rng.uniform(-0.04, 0.04)
        z0 = F.z_top - rng.uniform(1.2, 0.5 * H)
        z1 = max(F.z_bot + 0.4, z0 - rng.uniform(0.35, 0.95) * (z0 - F.z_bot))
        F.strip(mb, u, rng.uniform(0.02, 0.035), z0, z1, b + 0.84, "Foam", 0.3)
    # crista: faixa de espuma (~1,5) rolando por cima da borda
    if crest:
        Zc = [F.z_top + 0.14, F.z_top - 0.2, F.z_top - 0.8, F.z_top - 1.6]
        pts = [F.P(0.0, z, b + 0.96) for z in Zc]
        pts[0] = F.P(0.0, F.z_top, 0.0) - V(F.o.x, F.o.y, 0.0) * 0.7 + V(0.0, 0.0, 0.14)
        pts[1] = F.P(0.0, F.z_top, b * 0.6 + 0.5) + V(0.0, 0.0, -0.2)          # o labio rola por cima da borda
        WK.ribbon(mb, pts, [F.width(z) * w for z, w in zip(Zc, (1.0, 1.03, 1.03, 1.02))], "Foam", F.s, thick=0.3,
                  bulge=0.45)
    # espuma nas quebras (a agua bate no degrau e espirra para fora)
    if foam_breaks:
        for zb, st in F.breaks:
            Zb = [zb + 0.5, zb - 0.9, zb - 2.6]
            pts = [F.P(0.0, z, b + 0.96) for z in Zb]
            WK.ribbon(mb, pts, [F.width(z) * 1.03 for z in Zb], "Foam", F.s, thick=0.3, bulge=0.35)
    foot = F.P(0.0, F.z_bot)
    return foot, F.width(F.z_bot)


def sea_ring(mb, rng, foot, wb, o, R=None):
    """pe da queda no mar: disco de espuma irregular, anel irregular (r 10-14) em L.SEA+0,3, bolhas e nevoa"""
    z = L.SEA + 0.3
    R = R or max(10.0, min(14.0, wb * 0.62))
    c = V(foot.x + o.x * R * 0.25, foot.y + o.y * R * 0.25)
    poly = []
    for k in range(12):
        a = math.tau * k / 12 + rng.uniform(-0.1, 0.1)
        r = R * 0.58 * rng.uniform(0.8, 1.15)
        poly.append((c.x + math.cos(a) * r, c.y + math.sin(a) * r))
    mb.prism(IL.ccw(poly), z - 0.4, z, "Foam")
    ring = []
    a0 = rng.uniform(0, math.tau)
    for k in range(20):
        a = a0 + math.tau * k / 20
        r = R * rng.uniform(0.9, 1.06)
        ring.append(V(c.x + math.cos(a) * r, c.y + math.sin(a) * r, z - 0.2))
    loop_band(mb, ring, 2.6, 0.4, "Foam")
    foam_blobs(mb, rng, c, R * 0.8, 6, 1.4 + wb * 0.06, z - 0.1, flat=0.3)
    for k in range(3):
        s = wb * rng.uniform(0.19, 0.25)
        q = V(foot.x + (k - 1) * 0.3 * wb + rng.uniform(-0.05, 0.05) * wb, foot.y + rng.uniform(-0.1, 0.1) * wb)
        mb.ico(s, (q.x, q.y, z + s * 0.3), "Foam", 2, (1.4, 1.2, 0.7), (0, 0, rng.uniform(0, 3)), jitter=0.14)


def loop_band(mb, pts, w, h, m):
    """faixa fechada (anel) de secao w x h ao longo de um laco horizontal de pontos (sem costura aberta)"""
    bm = mb.bm
    n = len(pts)
    rings = []
    for i in range(n):
        t = (pts[(i + 1) % n] - pts[i - 1])
        t = V(t.x, t.y).normalized()
        sd = V(-t.y, t.x)
        p = pts[i]
        rings.append([bm.verts.new((p.x + sd.x * a, p.y + sd.y * a, p.z + b)) for a, b in
                      ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2))])
    for i in range(n):
        r0, r1 = rings[i], rings[(i + 1) % n]
        for j in range(4):
            j2 = (j + 1) % 4
            bm.faces.new((r0[j], r0[j2], r1[j2], r1[j]))
    mb._post([v for r in rings for v in r], m, None, 0, 1)


def pool_foam(mb, rng, foot, w, z):
    """pe de uma queda num poco: disco de espuma + bolhas + nevoa baixa"""
    mb.cyl(w * 0.42, 0.32, (foot.x, foot.y, z - 0.02), (0, 0, rng.uniform(0, 1)), "Foam", 10, bevel=0.0)
    foam_blobs(mb, rng, foot, w * 0.48, 7, max(0.8, w * 0.085), z, flat=0.32)
    for k in range(2):
        r = w * rng.uniform(0.14, 0.18)
        mb.ico(r, (foot.x + rng.uniform(-0.25, 0.25) * w, foot.y - rng.uniform(0.0, 1.5), z + r * 0.3), "Foam", 2,
               (1.6, 1.1, 0.7), (0, 0, rng.uniform(0, 3)), jitter=0.12)


def small_fall(mb, rng, top, bottom_z, width, out=(0, -1), lip=1.5, widen=1.3, n=5, m=BAND, streaks_n=1,
               base=True):
    """cascata pequena (bica, degrau T2 -> T1): lamina + riscos + labio de espuma + espuma no pe"""
    o = V(out[0], out[1]).normalized()
    side = V(-o.y, o.x)
    pts = WK.fall_path(V(*top), bottom_z, o, lip, n, 1.15)
    ws = [width * (1.0 + (widen - 1.0) * (i / n)) for i in range(n + 1)]
    WK.ribbon(mb, pts, ws, m, side, thick=0.3, bulge=min(0.35, 0.05 * width + 0.1))
    bl = min(0.35, 0.05 * width + 0.1)
    for k in range(streaks_n):
        u = -0.25 + 0.5 * (k + 0.5) / streaks_n
        sub = [p + side * (u * ws[j]) + o * (bl + 0.42) for j, p in enumerate(pts)][1:]
        WK.ribbon(mb, sub, [max(0.3, ws[j + 1] * 0.12) for j in range(len(sub))], "Foam", side, thick=0.3, flat=True)
    lp = [pts[0], pts[0].lerp(pts[1], 0.5), pts[1]]
    WK.ribbon(mb, [p + o * (bl + 0.42) + V(0, 0, 0.1) for p in lp], [ws[0] * 1.04, ws[0] * 0.98, ws[0] * 0.72], "Foam",
              side, thick=0.3, bulge=0.2)
    imp = pts[-1] + o * 0.4
    imp = V(imp.x, imp.y, bottom_z)
    if base:
        foam_blobs(mb, rng, imp, ws[-1] * 0.5 + 0.4, 5, max(0.55, ws[-1] * 0.16), bottom_z, flat=0.32)
        mb.cyl(ws[-1] * 0.45 + 0.4, 0.32, (imp.x, imp.y, bottom_z - 0.02), (0, 0, 0), "Foam", 9, bevel=0.0)
    return imp, ws[-1]


# ------------------------------------------------------------------ pocos e canais do T2
def stadium(cx, cy, hl, r, n=10):
    """contorno de um estadio (meio-comprimento hl em x, raio r), anti-horario"""
    pts = []
    for k in range(n + 1):
        a = -math.pi / 2 + math.pi * k / n
        pts.append((cx + hl + math.cos(a) * r, cy + math.sin(a) * r))
    for k in range(n + 1):
        a = math.pi / 2 + math.pi * k / n
        pts.append((cx - hl + math.cos(a) * r, cy + math.sin(a) * r))
    return pts


def pool(mb, rng, cx, cy, hl, r, openings=(), m="Stone_Wall_Light"):
    """poco no T2: lamina (estadio / circulo) + borda de cantaria, aberta no fundo (paredao) e nas saidas.
    openings = [(ponto (x, y) de passagem, meia-largura)]"""
    poly = stadium(cx, cy, hl, r + 0.35, 12 if hl == 0 else 8)
    mb.prism(IL.ccw(poly), ZPOOL - 0.5, ZPOOL, "Water")
    ring = stadium(cx, cy, hl, r + 0.62, 14 if hl == 0 else 9)
    ring.append(ring[0])

    def skip(c):
        if c.y > L.BACK_CLIFF_Y - 3.0:
            return True                     # junto ao pe do paredao: a rocha fecha o poco
        return any((c - V(*p)).length < hw for p, hw in openings)
    coping(mb, rng, ring, L.T2 + 1.15, h=1.25, w=1.25, step=2.9, m=m, skip=skip)


def canal(mb, rng, pts, w, z_water, z_top, skip=None, h=1.05, cw=0.95, step=2.6, sides=(-1, 1)):
    water_strip(mb, pts, z_water, w, 0.36)
    for sd in sides:
        coping(mb, rng, offset(pts, sd * (w / 2 + cw / 2)), z_top, h=h, w=cw, step=step,
               skip=(lambda c, sd=sd: skip(c, sd)) if skip else None)


# ------------------------------------------------------------------ quedas do paredao + pocos + canal do meio
def back_falls():
    rng = random.Random(1401)
    mb = MB("WATER_BackFalls", C, rng, detail="near")
    fy = L.BACK_CLIFF_Y
    W = WIDTH["back"]
    for i, (fx, _) in enumerate(L.BACK_FALLS):
        # ---- queda: crista sobre a coluna de fundo da garganta (topo em L.CLIFF_TOP - 0,3)
        zc = L.CLIFF_TOP - 0.3 + 0.45
        F = Fall((fx, fy + THROAT), (1, 0), (0, -1), zc, ZPOOL - 0.2, W, widen=1.1, lip=1.6,
                 breaks=[(L.CLIFF_TOP - 26.0 + (i - 1) * 2.5, 2.0)])
        foot, wb = big_fall(mb, rng, F, bands=3, streaks=7)
        # rego no plato: agua rasa entre pedras chegando na crista (0,2 acima do plato)
        mb.box((W - 0.6, 7.4, 0.3), (fx, fy + THROAT + 3.6, L.CLIFF_TOP + 0.05), (0, 0, 0), "Water", 0.0)
        for sx in (-1, 1):
            x = fx + sx * (W / 2 + 1.2)
            mb.rock((x, fy + THROAT + 2.8, L.CLIFF_TOP + 0.8), (3.6, 4.4, 3.4), "Cliff_Rock_Tan_Dark", 1,
                    (0, 0, rng.uniform(0, 3)), jitter=0.3)
        for k in range(3):
            mb.rock((fx + (k - 1) * 4.2, fy + THROAT + 7.9 + rng.uniform(-0.2, 0.2), L.CLIFF_TOP + 0.6),
                    (3.4, 2.4, 2.2), "Cliff_Rock_Tan_Dark", 1, (0, 0, rng.uniform(0, 3)), jitter=0.3)
        # lamina na boca da garganta (recebe a cortina) + espuma no pe
        mb.box((W + 0.6, THROAT + 1.2, 0.5), (fx, fy + THROAT / 2 - 0.3, ZPOOL - 0.25), (0, 0, 0), "Water", 0.0)
        pool_foam(mb, rng, V(foot.x, foot.y - 1.2), wb, ZPOOL)
        # ---- poco
        if abs(fx - MID_POOL[0]) < 1.0:
            cx, cy, hl, r = MID_POOL
            pool(mb, rng, cx, cy, hl, r, openings=[(L.CANAL_MID[1], CANAL_W_W / 2 + 1.4),
                                                   ((cx - hl - r, L.CANAL_MID[0][1] + 1.0), CANAL_W_W / 2 + 1.2)])
        else:
            pc = V(fx, fy - POOL_R - 0.6)
            if fx > 0:
                ops = [(L.STREAM_T2[0], CANAL_E_W / 2 + 1.3), ((pc.x + POOL_R + 0.6, L.STREAM_T2[0][1]),
                                                               CANAL_E_W / 2 + 1.2)]
            else:
                ops = [(WEST_T2[0], CANAL_W_W / 2 + 1.3), ((pc.x - POOL_R - 0.6, WEST_T2[0][1]), CANAL_W_W / 2 + 1.2),
                       (L.CANAL_MID[-1], CANAL_W_W / 2 + 1.3), ((pc.x + POOL_R + 0.6, L.CANAL_MID[-1][1]),
                                                                CANAL_W_W / 2 + 1.2)]
            pool(mb, rng, pc.x, pc.y, 0.0, POOL_R, openings=ops)
            for dx in (-W * 0.5, W * 0.52):
                pebble(mb, rng, fx + dx, fy - 3.4, ZPOOL - 0.3, rng.uniform(1.8, 2.3))
    # ---- canal do meio: poco -30 -> poco NO (-80), ao pe do paredao, atras da loja
    cm = chaikin(L.CANAL_MID, 2)
    pn = V(L.BACK_FALLS[0][0], fy - POOL_R - 0.6)
    mcx, mcy, mhl, mr = MID_POOL
    mid_poly = stadium(mcx, mcy, mhl, mr + 1.0, 8)

    def skip_mid(c, sd):
        return (c - pn).length < POOL_R + 1.3 or in_poly((c.x, c.y), mid_poly)
    canal(mb, rng, cm, CANAL_W_W, ZT2, L.T2 + 0.55, skip=skip_mid)
    streak_line(mb, rng, cm, CANAL_W_W / 2, ZT2, 4)
    mb.finish()


def streak_line(mb, rng, pts, hw, z, n):
    """ondulacao em pares ao longo de um canal"""
    P = rs(pts, 1.5)
    fr = frames([(p.x, p.y) for p in P])
    for k in range(n):
        p, t, nn = fr[rng.randint(1, len(fr) - 2)]
        q = p + nn * rng.uniform(-hw * 0.6, hw * 0.6)
        ang = math.atan2(t.y, t.x)
        for j in range(2):
            ripple(mb, rng, q + nn * (j * rng.uniform(0.7, 1.0)) + t * rng.uniform(-0.5, 0.5),
                   ang + rng.uniform(-0.12, 0.12), z)


# ------------------------------------------------------------------ leste: canal NE no T2 + vertedouro, bica, vale
def rim_ne_x(y):
    return 122.0 - (y - 124.0) / 6.0


def ne_crest():
    """crista da queda NE: pontos na borda (y0, y1), e os mesmos deslocados ao longo de NE_OUT ate SPILL_OUT de
    distancia da borda"""
    a = V(rim_ne_x(NE_Y[0]), NE_Y[0])
    b = V(rim_ne_x(NE_Y[1]), NE_Y[1])
    k = SPILL_OUT / NE_OUT.dot(NE_N)
    o = V(NE_OUT.x, NE_OUT.y)
    return a, b, a + o * k, b + o * k


def ne_spill_poly():
    """lamina do vertedouro NE entre o fim do canal e a borda (cobre a crista inteira)"""
    y0, y1 = NE_Y[0] - 0.7, NE_Y[1] + 0.7
    return [(112.2, y0), (rim_ne_x(y0) + 0.3, y0), (rim_ne_x(y1) + 0.3, y1), (113.0, y1)]


def bed_edges(hw):
    """margens do leito do contrato (mesmos pontos e normais de il_col.stream_bed_poly), meia-largura hw"""
    pts = list(L.STREAM)
    (x0, y0), (x1, y1) = pts[0], pts[1]
    d = math.hypot(x1 - x0, y1 - y0)
    pts.insert(0, (x0 - (x1 - x0) / d * 2.5, y0 - (y1 - y0) / d * 2.5))
    (xa, ya), (xb, yb) = pts[-2], pts[-1]
    d = math.hypot(xb - xa, yb - ya)
    pts.append((xb + (xb - xa) / d * 8.0, yb + (yb - ya) / d * 8.0))
    left, right = [], []
    n = len(pts)
    for i in range(n):
        x, y = pts[i]
        if i == 0:
            dx, dy = pts[1][0] - x, pts[1][1] - y
        elif i == n - 1:
            dx, dy = x - pts[i - 1][0], y - pts[i - 1][1]
        else:
            dx, dy = pts[i + 1][0] - pts[i - 1][0], pts[i + 1][1] - pts[i - 1][1]
        ln = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / ln, dx / ln
        left.append(V(x + nx * hw, y + ny * hw))
        right.append(V(x - nx * hw, y - ny * hw))
    return pts, left, right


def se_crossing(hw=(L.STREAM_W + 0.5) / 2):
    """onde as margens do ultimo trecho do riacho cruzam a borda SE: (pl, pr) sobre a borda, meio, normal para fora,
    tangente da borda (de pr para pl)"""
    (x0, y0), (x1, y1) = L.STREAM[-2], L.STREAM[-1]
    d = V(x1 - x0, y1 - y0).normalized()
    n = V(-d.y, d.x)
    a, b = V(*RIM_SE[0]), V(*RIM_SE[1])
    r = (b - a).normalized()
    p0 = V(x0, y0)
    pl = line_x(p0 + n * hw, d, a, r)
    pr = line_x(p0 - n * hw, d, a, r)
    return pl, pr, (pl + pr) / 2, V(r.y, -r.x), r


def east_stream():
    rng = random.Random(1411)
    mb = MB("WATER_Canal_East", C, rng, detail="near")
    H = house_rects()
    # ================= canal NE no T2 (poco NE -> vertedouro na borda)
    t2 = chaikin(L.STREAM_T2, 2)
    water_strip(mb, t2, ZT2, CANAL_E_W)
    sp = ne_spill_poly()
    mb.prism(IL.ccw(sp), ZT2 - 0.38, ZT2 - 0.02, "Water")
    pc = V(L.BACK_FALLS[1][0], L.BACK_CLIFF_Y - POOL_R - 0.6)

    def skip_e(c, sd):
        if (c - pc).length < POOL_R + 1.2 or in_rects(c, H):
            return True
        if sd > 0 and (c.y < NE_Y[1] + 1.4 or c.x > rim_ne_x(c.y) - 0.6):
            return True                     # lado da borda: vertedouro (a agua passa por cima)
        return False
    for sd in (-1, 1):
        line = offset(t2, sd * (CANAL_E_W / 2 + 0.55))
        coping(mb, rng, line, L.T2 + 0.6, step=3.0, skip=lambda c, sd=sd: skip_e(c, sd))
    # fecho do vertedouro: mureta oeste (continua a do canal) e sul, pedras-mestras nas 2 pontas da crista
    ra, rb, ca, cb = ne_crest()
    wl = offset(t2, -(CANAL_E_W / 2 + 0.55))[-1]
    coping(mb, rng, [(wl.x, wl.y), (sp[0][0] - 0.55, sp[0][1] - 0.55)], L.T2 + 0.6, step=2.6)
    coping(mb, rng, [(sp[0][0] - 0.55, sp[0][1] - 0.55), (rim_ne_x(sp[0][1] - 0.55) - 0.9, sp[0][1] - 0.55)],
           L.T2 + 0.6, step=2.6)
    q = ra - V(NE_T.x, NE_T.y) * 1.6
    cheek(mb, rng, V(q.x - NE_N.x * 0.9, q.y - NE_N.y * 0.9, L.T2 + 1.1), 2.0)
    streak_line(mb, rng, t2, CANAL_E_W / 2, ZT2, 6)
    # ================= bica no muro x=108 (nicho do terreno) + bacia de pedra
    sx, sy, sz = L.SPOUT
    x_out = sx + 2.2                        # boca da bica (a gargula sai 2,2 da face do muro)
    # gargula (sem rosto): colar redondo na boca do nicho, calha de pedra em U que sai 2,2 do muro, bico alargado
    # por baixo da ponta e 2 misulas escalonadas; a agua sai em arco da ponta
    zc = sz - 0.35
    mb.cyl(1.3, 0.7, (sx + 0.3, sy, zc), (0, math.pi / 2, 0), "Stone_Wall_Light", 10, bevel=0.0)
    mb.box((3.0, 1.84, 0.45), (sx + 0.7, sy, zc - 0.28), (0, 0, 0), "Stone_Wall_Light", 0.0)
    for s_ in (-1, 1):
        mb.box((3.0, 0.42, 0.8), (sx + 0.7, sy + s_ * 0.71, zc + 0.34), (0, 0, 0), "Stone_Wall_Light", 0.0)
    mb.box((0.8, 2.3, 1.0), (x_out - 0.4, sy, zc - 0.55), (0, 0, 0), "Stone_Wall_Light", 0.0)
    mb.box((1.5, 1.9, 1.3), (sx + 0.75, sy, zc - 1.3), (0, 0, 0), "Stone_Wall_Light", 0.0)
    mb.box((1.0, 1.4, 1.0), (sx + 0.5, sy, zc - 2.4), (0, 0, 0), "Stone_Wall_Light", 0.0)
    water_strip(mb, [(sx - 0.8, sy), (x_out + 0.1, sy)], zc + 0.3, 0.8, 0.2)
    imp, wbs = small_fall(mb, rng, (x_out + 0.1, sy, zc + 0.22), ZW, 0.8, out=(1, 0), lip=1.3, widen=2.3, n=5,
                          streaks_n=2, base=False)
    foam_blobs(mb, rng, imp, 1.5, 6, 0.75, ZW, flat=0.3)
    mb.cyl(1.9, 0.32, (imp.x, imp.y, ZW - 0.02), (0, 0, 0), "Foam", 9, bevel=0.0)
    # bacia: meio anel de cantaria colado ao muro, aberto rio abaixo (a lamina e a do leito)
    bc = V(111.3, 78.6)
    dn = V(L.STREAM[1][0] - L.STREAM[0][0], L.STREAM[1][1] - L.STREAM[0][1]).normalized()
    n_ = 16
    for k in range(n_):
        a = math.tau * (k + 0.5) / n_
        d = V(math.cos(a), math.sin(a))
        p = bc + d * 4.15
        if p.x < sx + 0.5 or d.dot(dn) > 0.72:
            continue
        mb.box((math.tau * 4.15 / n_ - 0.16, 0.95, L.G + 0.35 - 3.2), (p.x, p.y, (L.G + 0.35 + 3.2) / 2),
               (0, 0, a + math.pi / 2), "Stone_Wall_Light", 0.0)
    # ================= riacho do vale (lamina no leito do contrato)
    hw = (L.STREAM_W + 0.5) / 2              # 4,75: 0,05 dentro da margem do leito (4,8)
    pts, left, right = bed_edges(hw)
    for i in range(len(pts) - 1):
        q = [(right[i].x, right[i].y), (right[i + 1].x, right[i + 1].y), (left[i + 1].x, left[i + 1].y),
             (left[i].x, left[i].y)]
        q = IL.clip(q, -1.0, 0.0, -(sx + 0.05))          # face do muro x=108
        q = IL.clip(q, 1.0, -1.0, 176.0)                 # borda SE (x - y <= 176)
        if len(q) >= 3 and abs(IL.area(q)) > 0.05:
            mb.prism(IL.ccw(q), ZW - 0.4, ZW, "Water")
    wx, wy, wr = L.WHEEL
    fbc, fbu = footbridge_frame()
    pl, pr, pm, out_se, r_se = se_crossing()

    def zone(p):
        if -2.0 < p.y < 26.0:
            return "wheel"
        if (p - fbc).length < FB_LEN / 2 + 1.5 and abs((p - fbc).dot(V(-fbu.y, fbu.x))) < FB_W / 2 + 1.6:
            return "bridge"
        if p.y > 72.0:
            return "spout"
        if (p - pm).length < 11.0 or p.x - p.y > 170.0:
            return "lip"
        return None
    # margens: canal de cantaria na roda (bica de moinho), pedras/seixos no resto da linha d'agua
    for side, E in ((1, left), (-1, right)):
        line = [(e.x, e.y) for e in E]
        P = rs(line, 3.0)
        for a, b in zip(P, P[1:]):
            c = (a + b) / 2
            z = zone(c)
            d = b - a
            ang = math.atan2(d.y, d.x)
            if c.x < sx + 0.6 or c.x - c.y > 175.0:
                continue
            nrm = V(-d.y, d.x).normalized() * side     # para fora do leito
            if z == "wheel":
                hh = L.G + 0.35 - 3.2
                q = c + nrm * 0.1
                mb.box((d.length - 0.16, 1.1, hh), (q.x, q.y, 3.2 + hh / 2), (0, 0, ang + rng.uniform(-0.03, 0.03)),
                       "Stone_Wall_Light", 0.0)
                continue
            if z in ("bridge", "spout"):
                continue
            r = rng.random()
            if r < 0.34:
                s = rng.uniform(1.5, 2.3)
                q = c - nrm * rng.uniform(0.2, 0.6)
                mb.rock((q.x, q.y, ZW - 0.35), (s * 1.3, s, s * 0.8), "Cliff_Rock_Tan_Dark", 1,
                        (0, 0, rng.uniform(0, 3)), jitter=0.3)
            elif r < 0.62:
                for k in range(2):
                    q = a + d * rng.uniform(0.1, 0.9) - nrm * rng.uniform(0.3, 0.9)
                    pebble(mb, rng, q.x, q.y, ZW - 0.1, rng.uniform(0.55, 0.9))
    # pedras no leito (furam a lamina) + V de correnteza rio abaixo
    cl = chaikin(L.STREAM, 2)
    fr = frames(rs(cl, 3.0))
    placed = tries = 0
    while placed < 6 and tries < 300:
        tries += 1
        p, t, nn = fr[rng.randint(3, len(fr) - 4)]
        q = p + nn * rng.uniform(-hw * 0.55, hw * 0.55)
        if zone(q) in ("wheel", "bridge", "spout", "lip"):
            continue
        s = rng.uniform(1.4, 2.0)
        mb.rock((q.x, q.y, ZW - 0.45), (s * 1.3, s, s * 0.7), "Cliff_Rock_Tan_Dark", 1, (0, 0, rng.uniform(0, 3)),
                jitter=0.22)
        vee(mb, rng, q + t * (s * 0.62), ZW, t)
        placed += 1
    # ondulacao em pares ao longo do riacho
    P = rs(cl, 1.5)
    frs = frames([(p.x, p.y) for p in P])
    for k in range(16):
        p, t, nn = frs[rng.randint(2, len(frs) - 3)]
        q = p + nn * rng.uniform(-hw * 0.65, hw * 0.65)
        if zone(q) in ("wheel", "bridge", "spout"):
            continue
        ang = math.atan2(t.y, t.x)
        for j in range(2):
            ripple(mb, rng, q + nn * (j * rng.uniform(0.7, 1.0)) + t * rng.uniform(-0.5, 0.5),
                   ang + rng.uniform(-0.12, 0.12), ZW)
    # roda: agua branca onde as pas batem (jusante, embaixo) e rastro rio abaixo
    for k in range(6):
        mb.ico(rng.uniform(0.7, 1.1), (wx + rng.uniform(-2.2, 2.2), wy - rng.uniform(0.5, 3.5), ZW + 0.05), "Foam", 1,
               (1.6, 1.2, 0.35), (0, 0, rng.uniform(0, 3)), jitter=0.2)
    for k in range(5):
        ripple(mb, rng, V(wx + rng.uniform(-3.0, 3.0), wy - 5.0 - k * 2.4), math.pi / 2 + rng.uniform(-0.12, 0.12),
               ZW, rng.uniform(1.6, 2.6))
    # ponte: 2 pedras sob o arco com espuma (a agua quebra nelas) e rastro
    fv = V(-fbu.y, fbu.x)
    for sd in (-1, 1):
        q = fbc + fbu * sd * 2.3 + fv * rng.uniform(-0.6, 0.6)
        mb.rock((q.x, q.y, ZW - 0.45), (2.0, 1.6, 1.4), "Cliff_Rock_Tan_Dark", 1, (0, 0, rng.uniform(0, 3)),
                jitter=0.25)
        tt = V(fbu.y, -fbu.x)
        if tt.y > 0:
            tt = -tt                         # correnteza (para o sul)
        vee(mb, rng, q + tt * 1.2, ZW, tt)
    # labio SE: a agua acelera e espuma antes da borda
    for k in range(5):
        q = pm - out_se * rng.uniform(1.5, 4.0) + r_se * rng.uniform(-6.0, 6.0)
        mb.ico(rng.uniform(0.6, 0.9), (q.x, q.y, ZW + 0.05), "Foam", 1, (1.7, 1.1, 0.3), (0, 0, rng.uniform(0, 3)),
               jitter=0.2)
    mb.finish()


# ------------------------------------------------------------------ roda d'agua (peca movel) + apoio fixo
def wheel_hub_z():
    """eixo da roda: as pas de baixo mergulham ~0,5 na lamina do leito (L.STREAM_WATER) sem tocar o fundo"""
    return ZW - 0.45 + L.WHEEL[2]


def wheel():
    wx, wy, R = L.WHEEL
    az = wheel_hub_z()
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
            a = math.tau * k / 8 + 0.2
            mb.beam((x, wy, az), (x, wy + math.cos(a) * (R - 1.7), az + math.sin(a) * (R - 1.7)), 0.5, 0.5,
                    "Wood_Dark", 0.0)
    # pas radiais entre os aros (22: abaixo do limiar de variantes -> 1 malha so), a ponta no raio R
    for k in range(22):
        a = math.tau * (k + 0.5) / 22
        rp = R - 1.05
        mb.box((2 * half - 0.3, 0.3, 2.1), (wx, wy + math.cos(a) * rp, az + math.sin(a) * rp), (a - math.pi / 2, 0, 0),
               "Wood_Plank", 0.0)
    # cubo e eixo (o eixo entra no moinho a oeste: parede leste em x = MILL_x + largura/2 = 107)
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
                  "pas de baixo andando para jusante (4 rpm); pas mergulham ~0,5 na lamina (L.STREAM_WATER)")


def wheel_frame(fm):
    """apoio fixo da roda: pilares de cantaria nas 2 margens, mancais de madeira com cinta de ferro, maos-francesas.
    Colisao: os 2 pilares (area WaterWheel)."""
    wx, wy, R = L.WHEEL
    az = wheel_hub_z()
    for x, sgn in ((wx - 7.6, -1), (wx + 7.6, 1)):
        fm.box((3.4, 4.4, 0.9), (x, wy, L.G + 0.25), (0, 0, 0), "Stone_Wall_Light", 0.0)
        h = az - 1.0 - L.G
        for k in range(3):
            hk = h / 3
            fm.box((2.6 - k * 0.12, 3.6 - k * 0.15, hk - 0.08), (x, wy, L.G + hk * (k + 0.5)), (0, 0, 0.02 * (k - 1)),
                   "Stone_Wall_Light", 0.11)
        fm.box((3.0, 4.2, 0.8), (x, wy, az - 0.6), (0, 0, 0), "Wood_Dark", 0.0)
        fm.box((1.9, 1.5, 1.9), (x, wy, az), (0, 0, 0), "Wood_Dark", 0.07)
        fm.box((2.0, 1.66, 0.3), (x, wy, az + 0.95), (0, 0, 0), "Metal_Dark", 0.0)
        for sy in (-1, 1):
            fm.box((0.3, 0.3, 2.0), (x, wy + sy * 0.83, az), (0, 0, 0), "Metal_Dark", 0.0)
        for sy in (-1, 1):
            fm.beam((x + sgn * 0.2, wy + sy * 4.2, L.G), (x + sgn * 0.2, wy + sy * 1.7, az - 1.4), 0.55, 0.55,
                    "Wood_Dark", 0.0)
        col_box("WaterWheel", (3.4, 4.4, az - L.G + 1.0), (x, wy, L.G + (az - L.G + 1.0) / 2 - 0.5))


# ------------------------------------------------------------------ ponte em arco de madeira (pisavel, com colisao)
def footbridge_frame():
    """centro da ponte = projecao de L.FOOTBRIDGE no eixo do riacho; u = travessia (perpendicular a correnteza)"""
    p = V(*L.FOOTBRIDGE)
    best = None
    for a, b in zip(L.STREAM, L.STREAM[1:]):
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


def footbridge(mb):
    c, u = footbridge_frame()
    v = V(-u.y, u.x)
    yaw = math.atan2(u.y, u.x)
    Lb, W, H = FB_LEN, FB_W, FB_RISE
    rng = mb.rng

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
    for s in (-Lb / 4, 0.0, Lb / 4):
        mb.box((0.6, W - 0.6, 0.5), P(s, 0, -1.1), (0, 0, yaw), "Wood_Dark", 0.0)
    # guarda-corpo: 5 montantes por lado, corrimao e travessa curvos; os 4 das pontas mais altos com lanterna
    rs_ = [-Lb / 2 + 0.6, -Lb / 4, 0.0, Lb / 4, Lb / 2 - 0.6]
    for sd in (-1, 1):
        t = sd * (W / 2 + 0.1)
        for j, s in enumerate(rs_):
            end = j in (0, len(rs_) - 1)
            h = 4.3 if end else 3.5
            mb.box((0.62 if not end else 0.8, 0.62 if not end else 0.8, h), P(s, t, h / 2 - 0.2), (0, 0, yaw),
                   "Wood_Dark", 0.0)
            if end:
                top = P(s, t, h - 0.2)
                mb.box((1.05, 1.05, 1.0), top + V(0, 0, 0.55), (0, 0, yaw), "Lantern_Glow", 0.0)
                mb.box((1.5, 1.5, 0.32), top + V(0, 0, 1.2), (0, 0, yaw), "Wood_Dark", 0.0)
        rail = [P(s, t, 3.2) for s in [rs_[0] + (rs_[-1] - rs_[0]) * k / 10 for k in range(11)]]
        mb.sweep(rail, [(-0.28, -0.2), (0.28, -0.2), (0.28, 0.2), (-0.28, 0.2)], "Wood_Dark", True)
        mid = [P(s, t, 1.7) for s in [rs_[0] + (rs_[-1] - rs_[0]) * k / 10 for k in range(11)]]
        mb.sweep(mid, [(-0.18, -0.16), (0.18, -0.16), (0.18, 0.16), (-0.18, 0.16)], "Wood_Dark", True)
    # cabeceiras de pedra nas margens (fora do leito)
    for sg in (-1, 1):
        q = P(sg * (Lb / 2 + 0.4), 0, 0)
        mb.box((2.6, W + 2.2, 1.3), V(q.x, q.y, L.G - 0.45), (0, 0, yaw), "Stone_Wall_Light", 0.06)
        for sd in (-1, 1):
            q2 = P(sg * (Lb / 2 - 3.2), sd * (W / 2 + 0.9), 0)
            mb.box((3.6, 1.2, 1.0), V(q2.x, q2.y, L.G - 0.1), (0, 0, yaw), "Stone_Wall_Light", 0.05)
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


def valley_timber():
    mb = MB("WATER_Valley_Timber", C, random.Random(1451), detail="near")
    footbridge(mb)
    wheel_frame(mb)
    mb.finish()


# ------------------------------------------------------------------ oeste: poco NO -> canal T2 -> T1 -> bacia
def west_canal():
    rng = random.Random(1461)
    mb = MB("WATER_Canal_West", C, rng, detail="near")
    H = house_rects()
    pc = V(L.BACK_FALLS[0][0], L.BACK_CLIFF_Y - POOL_R - 0.6)
    t2 = chaikin(WEST_T2, 2)
    t1 = chaikin(WEST_T1, 2)
    canal(mb, rng, t2, CANAL_W_W, ZT2, L.T2 + 0.55,
          skip=lambda c, sd: (c - pc).length < POOL_R + 1.2 or in_rects(c, H) or c.y < 126.5)
    canal(mb, rng, t1, CANAL_W_W, ZT1, L.T1 + 0.55,
          skip=lambda c, sd: c.y > 125.4 or c.x < WEST_BASIN[1][0] + 0.4)
    streak_line(mb, rng, t2, CANAL_W_W / 2, ZT2, 3)
    streak_line(mb, rng, t1, CANAL_W_W / 2, ZT1, 3)
    # cascata T2 -> T1 no degrau y 126
    x0 = WEST_T2[-1][0]
    mb.box((CANAL_W_W + 0.4, 1.0, 0.5), (x0, 126.5, ZT2 - 0.3), (0, 0, 0), "Stone_Wall_Light", 0.0)
    for sd in (-1, 1):
        cheek(mb, rng, V(x0 + sd * (CANAL_W_W / 2 + 0.7), 126.8, L.T2 + 0.8), 1.6)
    small_fall(mb, rng, (x0, 125.8, ZT2 - 0.05), ZT1, CANAL_W_W, out=(0, -1), lip=0.9, widen=1.12, n=4, streaks_n=1)
    # bacia na borda oeste: o canal entra pelo leste, o vertedouro e a propria borda (crista de 16)
    mb.prism(IL.ccw(WEST_BASIN), ZT1 - 0.4, ZT1, "Water")
    bx1, by0, by1 = WEST_BASIN[1][0], WEST_BASIN[0][1], WEST_BASIN[2][1]
    yc = WEST_T1[-1][1]
    cw = CANAL_W_W / 2 + 0.9
    sides = [[(bx1 + 0.55, by0 - 0.55), (bx1 + 0.55, yc - cw)],
             [(bx1 + 0.55, yc + cw), (bx1 + 0.55, by1 + 0.55)],
             [(-157.4, by0 - 0.55), (bx1 + 0.55, by0 - 0.55)],
             [(-156.4, by1 + 0.55), (bx1 + 0.55, by1 + 0.55)]]
    for a, b in sides:
        coping(mb, rng, [a, b], L.T1 + 0.55, h=1.05, w=0.95, step=2.4)
    cheek(mb, rng, V(-157.3, by0 - 0.5, L.T1 + 0.9), 1.9)
    cheek(mb, rng, V(-156.2, by1 + 0.5, L.T1 + 0.9), 1.9)
    streak_line(mb, rng, [(-152.0, 76.0), (-157.0, 76.0)], 5.0, ZT1, 3)
    mb.finish()


# ------------------------------------------------------------------ quedas no mar (NE, SE, oeste) + drenagem SO
def overflow(mb, a, b, side, wa, wb, za, zb):
    """lamina rasa que passa por cima das colunas rebaixadas da sangria: de a (na borda, largura wa, cota za) ate b
    (SPILL_OUT para fora, largura wb, cota zb)"""
    WK.ribbon(mb, [V(a.x, a.y, za), V(b.x, b.y, zb)], [wa, wb], "Water", V(side.x, side.y, 0.0), thick=0.35,
              flat=True)


def sea_falls():
    rng = random.Random(1471)
    mb = MB("WATER_SeaFalls", C, rng, detail="far", floor=-999)
    # ---- NE: vertedouro ao longo da borda -> cortina a 40 graus (paralela a ponte), alarga so para o norte
    ra, rb, ca, cb = ne_crest()
    rm, cm = (ra + rb) / 2, (ca + cb) / 2
    wn = WIDTH["ne"]
    overflow(mb, rm - V(NE_OUT.x, NE_OUT.y) * 0.8, cm, NE_T, (rb - ra).length + 0.4, wn, ZT2, ZT2 - 0.75)
    F = Fall(cm, NE_T, NE_OUT, ZT2 - 0.75, L.SEA + 0.1, wn, widen=1.5, grow=1.0, lip=2.0, breaks=SEA_BREAKS)
    foot, wb = big_fall(mb, rng, F)
    sea_ring(mb, rng, foot, wb, F.o, R=11.0)
    # ---- SE: fim do riacho (lamina em 4,6) -> sangria -> cortina de 16
    pl, pr, pm, out_se, r_se = se_crossing()
    ws = WIDTH["se"]
    c_se = pm + out_se * SPILL_OUT
    overflow(mb, pm - out_se * 0.8, c_se, r_se, (pl - pr).length, ws, ZW, ZW - 0.6)
    F = Fall(c_se, r_se, out_se, ZW - 0.6, L.SEA + 0.1, ws, widen=1.5, lip=1.8, breaks=SEA_BREAKS)
    foot, wb = big_fall(mb, rng, F)
    sea_ring(mb, rng, foot, wb, F.o, R=13.0)
    # ---- oeste: bacia -> sangria (-158, 76) -> cortina de 16
    wo = W_OUT
    f0 = V(*W_SPILL)
    cw = f0 + V(wo.x, wo.y) * SPILL_OUT
    ww = WIDTH["west"]
    overflow(mb, f0 - V(wo.x, wo.y) * 1.0, cw, W_TAN, (WEST_BASIN[3][1] - WEST_BASIN[0][1]) - 0.4, ww, ZT1, ZT1 - 0.7)
    F = Fall(cw, W_TAN, wo, ZT1 - 0.7, L.SEA + 0.1, ww, widen=1.5, lip=1.8, breaks=SEA_BREAKS)
    foot, wb = big_fall(mb, rng, F)
    sea_ring(mb, rng, foot, wb, F.o, R=13.0)
    # ---- galeria de drenagem do fosso (face SO): testa de cantaria a frente das colunas -> cortina de 12
    gm, gn, gt = drain_frame()
    z0 = -3.6                                   # soleira (a galeria desce do fosso ate aqui)
    ow, oh = 9.0, 2.2                           # vao livre: largura, altura ate a nascente do arco
    o0 = DRAIN_OFF
    ang = math.atan2(gt.y, gt.x)

    def G(a, o, z):                             # a = ao longo da face, o = para fora da borda
        return V(gm.x + gt.x * a + gn.x * o, gm.y + gt.y * a + gn.y * o, z)
    z_top = z0 + oh + ow / 2 + 2.0              # 5,1: abaixo do chao G (6,2)
    mb.box((ow + 6.4, o0 + 1.6, z_top + 14.0), G(0, o0 / 2 - 0.8, (z_top - 14.0) / 2), (0, 0, ang),
           "Stone_Wall_Dark", 0.0)
    mb.box((ow + 7.0, o0 + 2.0, 0.6), G(0, o0 / 2 - 0.6, z_top + 0.3), (0, 0, ang), "Stone_Wall_Dark", 0.0)
    # vazio escuro + moldura: ombreiras, aduelas em arco, fecho, soleira
    mb.box((ow + 0.3, 0.4, oh + ow / 2 + 0.3), G(0, o0 + 0.05, z0 + (oh + ow / 2) / 2), (0, 0, ang), "Stone_WtrVoid",
           0.0)
    for sd in (-1, 1):
        mb.box((1.6, 1.6, oh), G(sd * (ow / 2 + 0.8), o0 + 0.8, z0 + oh / 2), (0, 0, ang), "Stone_Wall_Dark", 0.0)
    rr = ow / 2 + 0.8
    for k in range(9):
        a = math.pi * (k + 0.5) / 9
        q = G(math.cos(a) * rr, o0 + 0.9, z0 + oh + math.sin(a) * rr)
        big = k == 4
        mb.box((1.7 if big else 1.5, 1.8 if big else 1.6, 1.6 if big else 1.35), q, (0, math.pi / 2 - a, ang),
               "Stone_Wall_Dark", 0.0)
    mb.box((ow + 1.4, 2.6, 1.6), G(0, o0 + 1.3, z0 - 0.8), (0, 0, ang), "Stone_Wall_Dark", 0.0)
    # grade (barras) no vao - a agua sai por baixo dela
    for k in range(7):
        a = -ow / 2 + ow * (k + 0.5) / 7
        hk = oh + math.sqrt(max(0.0, (ow / 2) ** 2 - a * a)) - 0.3
        mb.box((0.35, 0.35, hk - 0.9), G(a, o0 + 0.55, z0 + 0.9 + (hk - 0.9) / 2), (0, 0, ang), "Stone_Wall_Dark", 0.0)
    # agua saindo pela soleira -> cortina que abre de 8,4 para 12
    wd = WIDTH["drain"]
    q0, q1 = G(0, o0 - 0.2, 0), G(0, o0 + 2.5, 0)
    overflow(mb, q0, q1, gt, ow - 0.6, ow - 0.4, z0 + 0.25, z0 + 0.05)
    F = Fall(G(0, o0 + 2.5, 0), gt, gn, z0 + 0.05, L.SEA + 0.1, wd, widen=1.35, lip=1.6,
             breaks=[(z0 - 12.0, 2.4), (-52.0, 2.2)], w_crest=ow - 0.4, flare=12.0)
    foot, wb = big_fall(mb, rng, F)
    sea_ring(mb, rng, foot, wb, F.o, R=10.5)
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
    valley_timber()
    west_canal()
    sea_falls()
