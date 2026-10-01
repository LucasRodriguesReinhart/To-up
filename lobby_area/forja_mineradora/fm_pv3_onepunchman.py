# fm_pv3_onepunchman - portal ONE PUNCH MAN v3 (passe final): "UM SOCO"
# Conceito: um trecho de MURO DE CONCRETO da cidade (cunhais com contorno escuro, laje/peitoril, faixa de janelas,
# cornija e capa escura) com um SOCO atravessando - o furo E o portal. Coroa: OUTDOOR amarelo com o PUNHO vermelho,
# preso na fachada e rompendo a linha da cornija (topo da silhueta T+26.45). Sem torres: a moldura e so o muro + o
# outdoor (area frontal ~2.9x o disco).
# O furo le como SOCO pela ESTRELA DE IMPACTO de quadrinho, em degraus de valor de fora para dentro:
#   face clara -> LABIO claro levantado 0.15 no contorno em estrela (arestas retas, 12 pontas desiguais, r 8.55..12.6;
#   as 4 grandes e finas nas diagonais, maiores em cima-esquerda / embaixo-direita, nao espelhadas) -> cratera QUASE
#   PRETA lisa (cuia + garganta conica, P_OPM_Crater) -> aro de brilho -> espiral. Costas: outra estrela.
# Rachaduras = CUNHAS: saem das pontas da estrela, afunilam ate zero (expoente 0.5), zigue-zague baixo, um garfo por
# rachadura longa. Vergalhoes GROSSOS (r 0.2, ferrugem) em 2 grupos de 3 nas duas pontas maiores: saem da cuia,
# projetam 1-1.8 para a frente e dobram seco (fora, para baixo, para o lado). Nada encosta no aro (sem lajes soltas
# na boca). Escombros: UM monte a direita na frente (laje encostada + bloco com outro em cima + bloco solto) e UM
# monte a direita atras do furo (laje encostada + bloco grande com outro em cima + bloco, tocos de vergalhao nos 2
# maiores); blocos = troncos de piramide irregulares, topo inclinado, altos (0.85-1.6), todos com COL.
# Esquerda: barreira new jersey + 2 cones. Base: friso zebrado amarelo/preto continuo no embasamento (frente,
# laterais e costas). Piso: calcada de placas + meio-fio amarelo na frente e atras; 2 degraus ate o furo.
# Espiral: AMARELO-DOURADO (ambar na borda, bracos amarelo-claros) com nucleo branco quente - a cor do Saitama;
# textura propria T_swirl_opm_v6.png (gerada aqui, como o DB). Aro e filetes das janelas em amarelo claro
# (emissao 1.8). Vedacao escura atras do aro: no Roblox (backface culling) nao sobra fresta para o fundo.
#
# Plano (studs; px = 108, disco r7.5 em z T+11.2, plano PY = 113):
#   muro   x px-10.3..px+10.3 (cunhais ate 10.45, cornija 10.75, capa 10.9), y PY-0.8..PY+2.4, z T+0.5..T+24.15
#   furo r7.8, garganta r7.8-8.25, boca r~8.35, cuia ate a estrela (r 8.55..12.6) com labio claro
#   laje/peitoril T+21.2..T+21.95 | janelas ..T+23.25 | cornija ..T+23.85 | capa ..T+24.15
#   outdoor x px+-4.8, z T+20.95..T+26.45, costas rentes na fachada (topo da silhueta)
#   degraus: T+1.45 / T+2.4 (x px+-5.8) ate o fundo do furo em T+3.4
#   lote: tudo em px+-13.8; penhasco leste em px+24.4
import math, os
import numpy as np
import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import fm_lib
from fm_lib import D, S, col_box, col_box2, col_ramp
import fm_portal_kit as K
from fm_portal_kit import V
import fm_layout as L
import fm_mat_textures as TX

_M = fm_lib.MATS.setdefault
_M("P_OPM_ConcreteLight", ((0.385, 0.405, 0.445), 0.85, 0.0, 0, None, 0.06))  # concreto claro frio (muro)
_M("P_OPM_ConcreteMid", ((0.135, 0.142, 0.158), 0.9, 0.0, 0, None, 0.05))     # cuia da cratera, quebras, degraus
_M("P_OPM_ConcreteDark", ((0.050, 0.052, 0.058), 0.95, 0.0, 0, None, 0.05))   # garganta, rachaduras, capa
_M("P_OPM_RebarSteel", (S(118, 60, 34), 0.7, 0.35, 0, None, 0.0))           # vergalhao enferrujado (Metal)
_M("P_OPM_Crater", ((0.024, 0.025, 0.029), 0.92, 0.0, 0, None, 0.0))         # cuia da cratera: quase preta, lisa
_M("P_OPM_DarkGlassT", ((0.03, 0.05, 0.09), 0.22, 0.25, 0, None, 0.03))       # vidro escuro das janelas (Glass)
# brilho (aro do furo + filetes das janelas): AMARELO claro e saturado, emissao moderada (cor do Saitama). O Roblox
# usa RBX_CAL (Neon). A luz do pad/espiral (fm_portals.swirl le LIGHT_COL) tambem vira amarela.
fm_lib.MATS["P_OPM_Glow"] = (S(255, 232, 90), 0.3, 0.0, 1.8, S(255, 232, 90), 0.0)
fm_lib.MATS["P_OPM_Swirl"] = (S(232, 175, 0), 0.3, 0.0, 1.15, S(232, 175, 0), 0.0)
fm_lib.RBX_CAL["P_OPM_Glow"] = (None, (255, 228, 80))
fm_lib.RBX_CAL["P_OPM_Swirl"] = (None, (232, 175, 0))
K.LIGHT_COL["OnePunchMan"] = (1.0, 0.78, 0.28)

KEY = "OnePunchMan"
C = "06_PORTALS"
A = "Portal"
T = L.TERR
PY = L.PORTAL_Y
Y0 = L.FLIGHT2_Y1
ZC = T + 2.0 + 9.2           # centro da espiral (fm_portals.SZ)

CL = "P_OPM_ConcreteLight"
CM = "P_OPM_ConcreteMid"
CR = "P_OPM_Crater"
CG = "P_OPM_ConcreteDark"
DG = "P_OPM_DarkGlassT"
RB = "P_OPM_RebarSteel"
YE = "P_OPM_Yellow"
RD = "P_OPM_Red"
GL = "P_OPM_Glow"
SW = "P_OPM_Swirl"


# ------------------------------------------------------------------ espiral propria (textura v6, amarelo-dourado)
def _ss(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def _mixn(a, b, t):
    t = np.asarray(t)[..., None]
    return a * (1 - t) + b * t


def opm_swirl_tex(spec, n=None):
    """espiral do OPM: fundo DOURADO saturado (ambar na borda -> ouro -> amarelo vivo no meio), 3 bracos largos
    amarelo-claro com filete branco-quente na borda de ataque, nucleo branco quente pequeno. Sem raios/rachaduras.
    Alfa 0 fora do circulo (mesma convencao de fm_mat_textures.tex_swirl)."""
    n = n or TX.SWIRL_N
    c = (np.arange(n) + 0.5) / n * 2 - 1
    X, Y = np.meshgrid(c, -c)
    r = np.sqrt(X * X + Y * Y)
    th = np.arctan2(Y, X)

    def col(v):
        return np.array(v, float) / 255.0
    BG_OUT, BG_MID, BG_IN = col(spec["border"]), col(spec["bg_mid"]), col(spec["bg_in"])
    ARM, ARM_HI = col(spec["arm"]), col(spec["arm_hi"])
    CORE, HALO = col(spec["core"]), col(spec["halo"])
    rgb = _mixn(_mixn(np.broadcast_to(BG_IN, r.shape + (3,)), BG_MID, _ss(0.10, 0.55, r)), BG_OUT, _ss(0.55, 0.97, r))
    ph = spec["arms"] * th / (2 * math.pi) + spec["twist"] * r ** 0.85
    s = ph % 1.0 - 0.5
    wl = spec["width"] * (0.45 + 0.65 * np.clip(r, 0, 1))
    lead = np.exp(-(np.maximum(s, 0) / (wl * 0.24)) ** 2)
    trail = np.exp(-(np.maximum(-s, 0) / (wl * 0.85)) ** 2)
    env = _ss(0.05, 0.20, r) * (1 - _ss(0.88, 0.985, r))
    arm = np.where(s >= 0, lead, trail) * env * (1.0 - 0.2 * _ss(0.6, 0.98, r))
    line = np.exp(-((s + wl * 0.04) / (wl * 0.10)) ** 2) * env
    rgb = _mixn(rgb, ARM, np.clip(arm, 0, 1))
    rgb = _mixn(rgb, ARM_HI, np.clip(line * spec["line"], 0, 1))
    rgb = _mixn(rgb, HALO, np.exp(-(r / spec["halo_r"]) ** 2) * 0.85)
    rgb = _mixn(rgb, CORE, np.exp(-(r / spec["core_r"]) ** 3))
    alpha = (1 - _ss(0.985, 1.0, r))[..., None]
    return np.concatenate([np.clip(rgb, 0, 1), alpha], axis=2)


SWIRL_OPM = dict(border=(135, 88, 0), bg_mid=(232, 175, 0), bg_in=(252, 214, 12), arm=(255, 244, 120),
                 arm_hi=(255, 254, 210), core=(255, 252, 232), halo=(255, 246, 150), arms=3, twist=3.3,
                 width=0.36, line=0.75, halo_r=0.18, core_r=0.085, style="opm_gold")
SWIRL_FILE = "T_swirl_opm_v6.png"


def _patch_swirl():
    """registra o desenho novo do OPM em fm_mat_textures (so em memoria, como o DB): SWIRL_SPEC/SWIRL_TEX apontam
    para a v6 e tex_swirl despacha o estilo 'opm_gold'. Blender (fm_lib._swirl_nodes), export_roblox e export_vfx
    leem a mesma PNG. Nome novo (v6): o 3D Importer nao reaproveita o cache da v5 (ciano)."""
    spec = dict(TX.SWIRL_SPEC["P_OPM_Swirl"])
    spec.update(SWIRL_OPM)
    TX.SWIRL_SPEC["P_OPM_Swirl"] = spec
    TX.SWIRL_TEX["P_OPM_Swirl"] = (SWIRL_FILE, spec["arm"], spec["core"])
    if not getattr(TX.tex_swirl, "_opm_gold", False):
        orig = TX.tex_swirl

        def tex_swirl(sp, n=None):
            return opm_swirl_tex(sp, n) if sp.get("style") == "opm_gold" else orig(sp, n)
        tex_swirl._opm_gold = True
        for attr in ("_db_ki",):
            if getattr(orig, attr, False):
                setattr(tex_swirl, attr, True)
        TX.tex_swirl = tex_swirl
    p = os.path.join(TX.TEX_DIR, SWIRL_FILE)
    if not os.path.exists(p):
        os.makedirs(TX.TEX_DIR, exist_ok=True)
        TX.write_png(p, opm_swirl_tex(spec))


_patch_swirl()

# muro
WX = 10.3                    # miolo (continua atras dos cunhais)
PIL = 9.6                    # face interna dos cunhais
CUN = 10.45                  # face externa dos cunhais
YF = PY - 0.8                # face da frente
YB = PY + 2.4                # face de tras
ZW0 = T + 0.5                # topo da calcada
ZPL = ZW0 + 1.3              # topo do embasamento
ZCORE = T + 21.2             # topo do miolo furado (base da laje/peitoril)
ZBAND = T + 21.95            # topo da laje/peitoril
ZWIN = T + 23.25             # topo das janelas = base da cornija (topo dos cunhais)
ZTOP = T + 23.85             # topo da cornija
ZCAP = ZTOP + 0.3            # topo da capa escura
BORE = 7.8                   # furo
BAND_R = 8.25                # borda da garganta escura (conica: le de frente)
MOUTH = 8.45                 # boca (fim da cuia)
DISH = 0.6                   # afundamento da cuia
LIP = 0.15                   # labio claro levantado no contorno da estrela
# outdoor (coroa)
BW = 4.8
BZ0, BZ1 = T + 20.95, T + 26.45
# estrela de impacto (angulo, raio) alternando vale/ponta; arestas RETAS entre os pontos (quadrinho). Vales rentes a
# garganta (8.55-8.65: sobra face clara ate o cunhal); 12 pontas desiguais, as 4 grandes e FINAS nas diagonais (onde o
# muro tem espaco), maiores em 133 (cima-esq., 12.6) e 318 (baixo-dir., 12.3); as de baixo ficam rasas (degraus).
# Costas: outra estrela, pontas em outros angulos.
STAR_F = [(4, 8.6), (22, 9.6), (36, 8.65), (50, 11.6), (64, 8.6), (78, 9.5), (91, 8.6), (104, 9.4), (118, 8.65),
          (133, 12.6), (146, 8.6), (160, 9.8), (174, 8.6), (188, 9.2), (206, 8.65), (224, 11.2), (240, 8.6),
          (256, 8.9), (273, 8.55), (290, 9.2), (304, 8.6), (318, 12.3), (332, 8.6), (346, 9.4)]
STAR_B = [(8, 9.3), (24, 8.6), (40, 11.4), (53, 8.65), (66, 9.5), (81, 8.6), (96, 9.5), (109, 8.65), (122, 9.8),
          (133, 8.6), (145, 12.0), (158, 8.6), (172, 9.4), (186, 8.65), (200, 9.3), (209, 8.6), (221, 11.0),
          (240, 8.6), (262, 9.1), (274, 8.6), (285, 9.3), (297, 8.6), (310, 12.1), (324, 8.6), (338, 9.5),
          (353, 8.6)]


def _t_rect(a, x0, x1, z0, z1):
    c, s = math.cos(a), math.sin(a)
    ts = []
    if c > 1e-9:
        ts.append(x1 / c)
    elif c < -1e-9:
        ts.append(x0 / c)
    if s > 1e-9:
        ts.append(z1 / s)
    elif s < -1e-9:
        ts.append(z0 / s)
    return min(ts)


def _lim(a):
    return _t_rect(a, -PIL, PIL, ZPL - ZC, ZCORE - ZC)


def _star_raw(a, pts):
    """raio do poligono estrela (arestas retas entre pontas e vales) na direcao a"""
    P = [(math.cos(D(d)) * r, math.sin(D(d)) * r) for d, r in pts]
    dx, dz = math.cos(a), math.sin(a)
    best = None
    for (x0, z0), (x1, z1) in zip(P, P[1:] + P[:1]):
        ex, ez = x1 - x0, z1 - z0
        den = dx * ez - dz * ex
        if abs(den) < 1e-12:
            continue
        t = (x0 * ez - z0 * ex) / den
        s = (x0 * dz - z0 * dx) / den
        if -1e-9 <= s <= 1 + 1e-9 and t > 0:
            best = t if best is None else min(best, t)
    return best


def _rs(a):
    """contorno da estrela da frente: sem invadir cunhais/peitoril/embasamento; acima dos degraus, fundo em T+2.6"""
    r = _star_raw(a, STAR_F)
    s, c = math.sin(a), math.cos(a)
    if s < -1e-6 and abs(r * c) < 5.6:
        r = min(r, 8.6 / -s)
    return min(r, _lim(a) - 0.3)


def _rsb(a):
    return min(_star_raw(a, STAR_B), _lim(a) - 0.3)


def _lipin(r):
    return r - 0.22


def _mouth(li, j=0.0):
    lo, hi = BAND_R + 0.06, li - 0.06
    if hi < lo:
        return (li + BAND_R) / 2
    return max(lo, min(hi, MOUTH + j))


def _bowl_y(a, r):
    """profundidade (y) da superficie da cuia da frente no raio r"""
    li = _lipin(_rs(a))
    mo = _mouth(li, 0.05)
    k = max(0.0, min(1.0, (li - r) / max(0.05, li - mo)))
    return YF + 0.05 + (DISH - 0.05) * k


def _holed_core(mb, px, rng):
    """miolo do muro: bloco retangular com o furo do soco (toro fechado). Frente, de fora para dentro: face plana ->
    labio claro levantado no contorno em ESTRELA -> cuia escura LISA (afunda DISH) -> garganta conica escura ->
    furo; atras: estrela propria, cuia escura, garganta"""
    x0, x1, z0, z1 = -WX, WX, ZW0 - ZC, ZCORE - ZC
    cand = [(math.tau * (i + 0.5) / 64, 0) for i in range(64)]
    for cx, cz in ((x1, z1), (x0, z1), (x0, z0), (x1, z0)):
        cand.append((math.atan2(cz, cx) % math.tau, 2))
    for d, _r in STAR_F + STAR_B:
        cand.append((D(d) % math.tau, 3))
    cand.sort()
    angs = []
    for a, pr in cand:
        if angs and a - angs[-1][0] < 0.022:
            if pr > angs[-1][1]:
                angs[-1] = (a, pr)
            continue
        angs.append((a, pr))
    if len(angs) > 1 and angs[0][0] + math.tau - angs[-1][0] < 0.022:
        if angs[-1][1] > angs[0][1]:
            angs[0] = angs[-1]
        angs.pop()
    angs = [a for a, _ in angs]
    bm = mb.bm

    def ring(rad, y):
        return [bm.verts.new((px + math.cos(a) * r, y, ZC + math.sin(a) * r)) for a, r in zip(angs, rad)]
    tt = [_t_rect(a, x0, x1, z0, z1) for a in angs]
    rs = [min(_rs(a), t_ - 0.12) for a, t_ in zip(angs, tt)]
    li = [_lipin(r) for r in rs]
    mo = [_mouth(l_, rng.uniform(-0.04, 0.14)) for l_ in li]
    rb = [min(_rsb(a), t_ - 0.12) for a, t_ in zip(angs, tt)]
    mb_ = [max(BAND_R + 0.06, min(r - 0.3, MOUTH + rng.uniform(-0.04, 0.14))) for r in rb]
    rings = [
        ring(tt, YF),                               # 0 borda externa (frente)
        ring(rs, YF),                               # 1 contorno da estrela (pe do labio)
        ring([r - 0.08 for r in rs], YF - LIP),     # 2 crista do labio (levantada para quem chega)
        ring(li, YF + 0.05),                        # 3 pe interno do labio = borda da cuia
        ring(mo, YF + DISH),                        # 4 boca (fim da cuia)
        ring([BAND_R] * len(angs), YF + DISH + 0.3),  # 5 borda da garganta escura
        ring([BORE] * len(angs), YF + 1.35),        # 6 furo (frente)
        ring([BORE] * len(angs), YB - 1.0),         # 7 furo (tras)
        ring([BAND_R] * len(angs), YB - 0.65),      # 8 garganta (tras)
        ring(mb_, YB - 0.4),                        # 9 boca de saida
        ring(rb, YB),                               # 10 contorno da estrela de tras
        ring(tt, YB),                               # 11 borda externa (tras)
    ]
    k = len(angs)
    nr = len(rings)
    groups = {}
    for ri in range(nr):
        ra, rbv = rings[ri], rings[(ri + 1) % nr]
        for i in range(k):
            j = (i + 1) % k
            f = bm.faces.new((ra[i], ra[j], rbv[j], rbv[i]))
            groups.setdefault(ri, []).append(f)
    allv = [v for r in rings for v in r]
    mb._post(allv, CL, 0.0, 0, 1)
    mi = {CR: mb._mi_for(CR)}
    for ri, m in ((3, CR), (4, CR), (5, CR), (6, CR), (7, CR), (8, CR), (9, CR)):
        for f in groups[ri]:
            f.material_index = mi[m]
    for ri in (3, 9):                          # cuias: sombreamento suave (sem mosaico de facetas)
        for f in groups[ri]:
            f.smooth = True


# ------------------------------------------------------------------ marcas na face (decal rente, sem volume)
def _zigzag(p0, p1, n, amp, rng):
    """linha quebrada de p0 a p1: n segmentos com desvios alternados (quinas vivas, amplitude baixa)"""
    dx, dz = p1[0] - p0[0], p1[1] - p0[1]
    ln = math.hypot(dx, dz) or 1.0
    px_, pz_ = -dz / ln, dx / ln
    pts = [p0]
    for i in range(1, n):
        f = (i + rng.uniform(-0.15, 0.15)) / n
        off = amp * (1 if i % 2 else -1) * rng.uniform(0.6, 1.0)
        pts.append((p0[0] + dx * f + px_ * off, p0[1] + dz * f + pz_ * off))
    pts.append(p1)
    return pts


def _clip(pts, ok):
    """corta a polilinha na borda permitida (interpola o ultimo trecho ate a borda)"""
    out = []
    for p in pts:
        if not ok(p):
            if out:
                q = out[-1]
                lo, hi = 0.0, 1.0
                for _ in range(12):
                    m = (lo + hi) / 2
                    if ok((q[0] + (p[0] - q[0]) * m, q[1] + (p[1] - q[1]) * m)):
                        lo = m
                    else:
                        hi = m
                if lo > 0.05:
                    out.append((q[0] + (p[0] - q[0]) * lo, q[1] + (p[1] - q[1]) * lo))
            break
        out.append(p)
    return out


def _hit(bvh, x, z, side, off=0.045):
    """ponto da face do muro (frente side=-1 / costas +1) em (x, z), `off` para fora da superficie"""
    if side < 0:
        o, d = Vector((x, YF - 2.5, z)), Vector((0, 1, 0))
    else:
        o, d = Vector((x, YB + 2.5, z)), Vector((0, -1, 0))
    loc, nrm, _i, _d = bvh.ray_cast(o, d, 6.0)
    if loc is None:
        return None
    if side < 0 and not (YF - 0.8 < loc.y < YF + 1.2):
        return None
    if side > 0 and not (YB - 1.2 < loc.y < YB + 0.8):
        return None
    if nrm.dot(d) > 0:
        nrm = -nrm
    return loc + nrm * off, nrm


def _crack(dec, bvh, pts, w0, w1, side, step=0.25, expo=0.5):
    """CUNHA afunilada (w0 -> w1, largura cai rapido: expoente 0.5) colada na superficie real do muro por raio,
    0.045 para fora (sem volume, sem cintilar no Roblox): so a face de fora, orientada pela normal da superficie"""
    rs = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        ln = math.hypot(b[0] - a[0], b[1] - a[1])
        n = max(1, int(math.ceil(ln / step)))
        for i in range(1, n + 1):
            f = i / n
            rs.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f))
    for _pass in range(2):
        out = [rs[0]]
        for a, b in zip(rs, rs[1:]):
            ha, hb = _hit(bvh, a[0], a[1], side), _hit(bvh, b[0], b[1], side)
            m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            hm = _hit(bvh, m[0], m[1], side)
            if ha and hb and hm and (hm[0] - (ha[0] + hb[0]) / 2).dot(hm[1]) > 0.004:
                out.append(m)
            out.append(b)
        rs = out
    cum = [0.0]
    for a, b in zip(rs, rs[1:]):
        cum.append(cum[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    tot = cum[-1] or 1.0
    L_, R_, N_ = [], [], []
    for i, p in enumerate(rs):
        a = rs[min(i + 1, len(rs) - 1)]
        b = rs[max(i - 1, 0)]
        tx, tz = a[0] - b[0], a[1] - b[1]
        ln = math.hypot(tx, tz) or 1.0
        nx, nz = -tz / ln, tx / ln
        w = (w0 + (w1 - w0) * (cum[i] / tot) ** expo) / 2
        hl = _hit(bvh, p[0] + nx * w, p[1] + nz * w, side)
        hr = _hit(bvh, p[0] - nx * w, p[1] - nz * w, side)
        if hl is None or hr is None:
            break
        L_.append(hl[0])
        R_.append(hr[0])
        N_.append((hl[1] + hr[1]).normalized())
    if len(L_) < 2:
        return
    bm = dec.bm
    vl = [bm.verts.new(p) for p in L_]
    vr = [bm.verts.new(p) for p in R_]
    for i in range(len(vl) - 1):
        f = bm.faces.new((vl[i], vr[i], vr[i + 1], vl[i + 1]))
        f.normal_update()
        if f.normal.dot(N_[i] + N_[i + 1]) < 0:
            f.normal_flip()
    dec._post(vl + vr, CG, 0.0, 0, 1)


def _okf(px, reach):
    """face permitida para as rachaduras: miolo (plano, labio, cuia); `reach` deixa chegar rente ao cunhal/peitoril"""
    mx, mz = (0.1, 0.1) if reach else (0.35, 0.3)

    def ok(q):
        dx = abs(q[0] - px)
        if dx > PIL - mx or q[1] > ZCORE - mz:
            return False
        return q[1] > (T + 2.55 if dx < 5.3 else ZPL + 0.12)
    return ok


def _along(pts, f):
    """ponto e direcao na fracao f do comprimento da polilinha"""
    segs = list(zip(pts, pts[1:]))
    lens = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in segs]
    goal = f * sum(lens)
    for (a, b), ln in zip(segs, lens):
        if goal <= ln or (a, b) == segs[-1]:
            t = goal / ln if ln else 0.0
            return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t), math.atan2(b[1] - a[1], b[0] - a[0])
        goal -= ln
    return pts[-1], 0.0


def _web(dec, bvh, px, side, rfun, cracks, rng):
    """rachaduras de impacto: CUNHAS que continuam as pontas da estrela (nascem 0.25 dentro da ponta) e afinam ate
    zero no alvo (ponto (dx, dz) relativo ao centro do furo); cada longa ganha um garfo curto"""
    for a0, (tx, tz), w0, reach, fork in cracks:
        a = D(a0)
        r0 = rfun(a) - 0.25
        p0 = (px + math.cos(a) * r0, ZC + math.sin(a) * r0)
        p1 = (px + tx, ZC + tz)
        ln = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        ok = _okf(px, reach)
        pts = _clip(_zigzag(p0, p1, max(2, int(round(ln / 2.2))), 0.12, rng), ok)
        if len(pts) < 2:
            continue
        _crack(dec, bvh, pts, w0, 0.02, side)
        if fork:
            ff, dang, fl = fork
            q, ang = _along(pts, ff)
            wq = w0 * (1.0 - ff ** 0.5) * 0.9
            b = ang + D(dang)
            q1 = (q[0] + math.cos(b) * fl, q[1] + math.sin(b) * fl)
            fp = _clip(_zigzag(q, q1, 2, 0.08, rng), ok)
            if len(fp) >= 2:
                _crack(dec, bvh, fp, max(0.12, wq), 0.02, side)


def _zebra(dec, a, b, z0, z1, out, w=0.42, per=0.95, sk=0.4):
    """faixa zebrada: listras amarelas inclinadas (decal) numa face vertical escura de a ate b (xy)"""
    a = Vector((a[0], a[1], 0))
    b = Vector((b[0], b[1], 0))
    ln = (b - a).length
    u = (b - a) / ln
    n = Vector((out[0], out[1], 0)).normalized()
    off = n * 0.04
    bm = dec.bm
    vs = []
    s = 0.1
    while s + w + sk <= ln - 0.08:
        q = [a + u * s + Vector((0, 0, z0)), a + u * (s + w) + Vector((0, 0, z0)),
             a + u * (s + w + sk) + Vector((0, 0, z1)), a + u * (s + sk) + Vector((0, 0, z1))]
        f = bm.faces.new([bm.verts.new(p + off) for p in q])
        f.normal_update()
        if f.normal.dot(n) < 0:
            f.normal_flip()
        vs.extend(f.verts)
        s += per
    if vs:
        dec._post(vs, YE, 0.0, 0, 1)


def _back_disc(px, rng):
    """costas do furo: a MESMA espiral da frente (P_OPM_Swirl) num disco proprio de 64 lados, voltado para tras,
    no fundo do furo. Objeto separado: o material da espiral usa as coordenadas GENERATED do objeto (bbox = o disco)
    e o export_roblox da UV de disco (0..1) a cada malha com a espiral."""
    sb = K.LeanMB("PORTAL_%s_SwirlBack" % KEY, C, rng, vcap=2)
    bm = sb.bm
    n = 64
    R = fm_lib.SWIRL_R
    c = bm.verts.new((0.0, 0.0, 0.0))
    rim = [bm.verts.new((math.cos(math.tau * i / n) * R, 0.0, math.sin(math.tau * i / n) * R)) for i in range(n)]
    for i in range(n):
        f = bm.faces.new((c, rim[(i + 1) % n], rim[i]))
        f.normal_update()
        if f.normal.y < 0:
            f.normal_flip()
    sb._post([c] + rim, SW, 0.0, 0, 1)
    ob = sb.finish(recalc=False)
    ob.location = (px, YB - 0.1, ZC)
    return ob


def _glow_annulus(mb, px, yface, r0, r1, dirn, depth, n=64):
    """aro de brilho LISO (n segmentos): face anular voltada para dirn (-1 frente / +1 costas) + faixas externa e
    interna com `depth` para tras. Na frente cobre o aro de 32 lados do fm_portals.swirl (sem segmentos retos)."""
    bm = mb.bm
    yb = yface - dirn * depth

    def rg(r, y):
        return [bm.verts.new((px + math.cos(math.tau * i / n) * r, y, ZC + math.sin(math.tau * i / n) * r))
                for i in range(n)]
    of, inf_, ob, ib = rg(r1, yface), rg(r0, yface), rg(r1, yb), rg(r0, yb)
    c = Vector((px, 0, ZC))
    for i in range(n):
        j = (i + 1) % n
        for quad, want in (((of[i], of[j], inf_[j], inf_[i]), None),
                           ((of[i], of[j], ob[j], ob[i]), 1), ((inf_[i], inf_[j], ib[j], ib[i]), -1)):
            f = bm.faces.new(quad)
            f.normal_update()
            if want is None:
                if f.normal.y * dirn < 0:
                    f.normal_flip()
            else:
                m = f.calc_center_median()
                rad = Vector((m.x - c.x, 0, m.z - c.z))
                if f.normal.dot(rad) * want < 0:
                    f.normal_flip()
    mb._post(of + inf_ + ob + ib, GL, 0.0, 0, 1)


def _seal(dec, px, y, r0, r1, n=64):
    """anel escuro voltado para a FRENTE (-y) fechando o tubo entre a tampa da espiral (r7.56) e o furo (r7.8):
    no Roblox (backface culling) nao sobra fresta para o fundo. No objeto de decal (normais fixas, sem recalc)."""
    bm = dec.bm
    o = [bm.verts.new((px + math.cos(math.tau * i / n) * r1, y, ZC + math.sin(math.tau * i / n) * r1)) for i in range(n)]
    ii = [bm.verts.new((px + math.cos(math.tau * i / n) * r0, y, ZC + math.sin(math.tau * i / n) * r0)) for i in range(n)]
    for i in range(n):
        j = (i + 1) % n
        f = bm.faces.new((o[i], o[j], ii[j], ii[i]))
        f.normal_update()
        if f.normal.y > 0:
            f.normal_flip()
    dec._post(o + ii, CG, 0.0, 0, 1)


def _swirl_unlit():
    """no Roblox o disco e uma SurfaceGui SEM luz (LightInfluence 0): no Blender a espiral do OPM fica so emissiva
    (base preta, sem especular) para bater com isso - com luz difusa o sol/ceu/luz do pad lavam o amarelo em bege.
    So muda a pre-visualizacao: o export usa a PNG (SWIRL_TEX)."""
    m = bpy.data.materials.get(SW)
    if m is None or not m.use_nodes:
        return
    nt = m.node_tree
    bs = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bs is None:
        return
    for l in list(nt.links):
        if l.to_socket == bs.inputs["Base Color"]:
            nt.links.remove(l)
    bs.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1.0)
    if "Specular IOR Level" in bs.inputs:
        bs.inputs["Specular IOR Level"].default_value = 0.0


# ------------------------------------------------------------------ vergalhoes
def _round_path(pts, rad):
    """polilinha com os cantos arredondados (Bezier quadratica de 3 pontos por canto); rad pequeno = dobra seca"""
    pts = [Vector(p) for p in pts]
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        a, b, c = pts[i - 1], pts[i], pts[i + 1]
        r = min(rad, (b - a).length * 0.45, (c - b).length * 0.45)
        if r < 0.02:
            out.append(b)
            continue
        p0 = b + (a - b).normalized() * r
        p2 = b + (c - b).normalized() * r
        for j in range(3):
            t = j / 2
            out.append(p0 * (1 - t) ** 2 + b * (2 * t * (1 - t)) + p2 * (t * t))
    out.append(pts[-1])
    return out


def _ptube(mb, pts, r, m, n=6):
    """barra redonda (sombreado liso) com referencial de transporte paralelo: nao torce nem estrangula nas dobras"""
    pts = [Vector(p) for p in pts]
    k = len(pts)
    tans = []
    for i in range(k):
        if i == 0:
            t = pts[1] - pts[0]
        elif i == k - 1:
            t = pts[-1] - pts[-2]
        else:
            t = (pts[i + 1] - pts[i]).normalized() + (pts[i] - pts[i - 1]).normalized()
        tans.append(t.normalized())
    nrm = tans[0].orthogonal().normalized()
    bm = mb.bm
    rings = []
    for i, p in enumerate(pts):
        if i:
            nrm = tans[i - 1].rotation_difference(tans[i]) @ nrm
            nrm = (nrm - tans[i] * nrm.dot(tans[i])).normalized()
        bi = tans[i].cross(nrm)
        rings.append([bm.verts.new(p + (nrm * math.cos(math.tau * j / n) + bi * math.sin(math.tau * j / n)) * r)
                      for j in range(n)])
    side = []
    for r0, r1 in zip(rings, rings[1:]):
        for j in range(n):
            j2 = (j + 1) % n
            side.append(bm.faces.new((r0[j], r0[j2], r1[j2], r1[j])))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    mb._post([v for rr in rings for v in rr], m, 0.0, 0, 1)
    for f in side:
        f.smooth = True


def _bar(mb, root_in, root_out, moves, rad, r=0.2):
    """vergalhao: nasce dentro do concreto (root_in), sai na superficie (root_out) e segue os `moves`
    (direcao, comprimento); ponta cortada seca (tampa plana)"""
    pts = [Vector(root_in), Vector(root_out)]
    for d, ln in moves:
        pts.append(pts[-1] + Vector(d).normalized() * ln)
    _ptube(mb, _round_path(pts, rad), r, RB)


def _rebars(mb, px):
    """2 grupos de 3 vergalhoes GROSSOS (r 0.2) nas duas pontas maiores da estrela (133 cima-esq., 318 baixo-dir.):
    saem da cuia, avancam 1.0-1.8 para a frente e dobram SECO (para fora e para baixo | para baixo | para o lado)"""
    c = Vector((px, 0, ZC))
    F = Vector((0, -1, 0))
    Z = Vector((0, 0, 1))
    groups = [
        # (angulo da ponta, [(desvio em graus, recuo do raio, moves(d, t))])
        (133, [(-6.0, 1.05, lambda d, t: [(F + d * 0.12, 1.25), (d * 0.9 - Z * 0.5 + F * 0.15, 1.15)]),
               (0.0, 0.8, lambda d, t: [(F + d * 0.08, 1.8), (-Z + F * 0.3 + t * 0.15, 0.85)]),
               (6.5, 1.1, lambda d, t: [(F - t * 0.1, 1.05), (t + d * 0.35 + F * 0.1, 1.2)])]),
        (318, [(-6.5, 1.1, lambda d, t: [(F + t * 0.1, 1.15), (-t * 0.9 + d * 0.4 + F * 0.15, 1.1)]),
               (0.0, 0.8, lambda d, t: [(F + d * 0.1, 1.65), (d * 0.8 + Z * 0.55 + F * 0.1, 1.0)]),
               (6.0, 1.05, lambda d, t: [(F + d * 0.15, 1.0), (-Z + d * 0.35 + F * 0.2, 1.05)])]),
    ]
    for a0, bars in groups:
        for da, back, mv in bars:
            a = D(a0 + da)
            d = Vector((math.cos(a), 0, math.sin(a)))
            t = Vector((-math.sin(a), 0, math.cos(a)))
            rr = max(MOUTH + 0.4, _lipin(_rs(a)) - back)
            base = c + d * rr
            yb = _bowl_y(a, rr)
            _bar(mb, base + Vector((0, yb + 0.8, 0)), base + Vector((0, yb - 0.04, 0)), mv(d, t), 0.14)


# ------------------------------------------------------------------ pecas
def _slab2(mb, pts, o, u, v, th, mtop, mside, bevel=0.07, top=(0, 0, 1)):
    """placa partida (K.plate) em DOIS materiais: a face de cima (a tampa voltada para `top`) em mtop; laterais,
    fundo e chanfros (as faces de quebra) em mside. As faces novas sao as que nao existiam antes do plate (o bevel
    do _post limpa as tags do bmesh inteiro: nao usar f.tag)."""
    bm = mb.bm
    before = set(bm.faces)
    K.plate(mb, pts, o, u, v, th, mside, bevel=bevel)
    u, v, o = Vector(u).normalized(), Vector(v).normalized(), Vector(o)
    nrm = u.cross(v).normalized()
    if nrm.dot(Vector(top)) < 0:
        nrm = -nrm
    mi = mb._mi_for(mtop)
    for f in bm.faces:
        if f in before:
            continue
        f.normal_update()
        if abs(f.normal.dot(nrm)) > 0.97 and (f.calc_center_median() - o).dot(nrm) > th * 0.3:
            f.material_index = mi


def _rock(mb, x, y, zf, s, h, yaw, slope, rng, k=5, elong=1.25, shrink=(0.62, 0.86), embed=0.06):
    """bloco de concreto ARRANCADO: tronco de piramide irregular (base de k lados, topo menor, deslocado e
    INCLINADO), topo claro e quebras escuras; apoiado em zf (enterra `embed`). Devolve (lo, hi, ztop(x, y), info)"""
    bm = mb.bm
    before = set(bm.faces)
    a0 = rng.uniform(0, math.tau)
    base = []
    for i in range(k):
        a = a0 + math.tau * i / k + rng.uniform(-0.3, 0.3)
        r = s / 2 * rng.uniform(0.74, 1.08)
        base.append((math.cos(a) * r * elong, math.sin(a) * r))
    sh = (rng.uniform(-0.1, 0.1) * s, rng.uniform(-0.1, 0.1) * s)
    top = []
    for bx, by in base:
        f = rng.uniform(*shrink)
        top.append((bx * f + sh[0], by * f + sh[1]))
    phi = rng.uniform(0, math.tau)
    gx, gy = math.cos(phi) * slope, math.sin(phi) * slope
    cy, sy = math.cos(yaw), math.sin(yaw)
    z0 = zf - embed

    def W(lx, ly, z):
        return Vector((x + lx * cy - ly * sy, y + lx * sy + ly * cy, z))
    pb = [W(bx, by, z0) for bx, by in base]
    pt = [W(tx, ty, z0 + max(h * 0.5, h + gx * tx + gy * ty)) for tx, ty in top]
    vb = [bm.verts.new(p) for p in pb]
    vt = [bm.verts.new(p) for p in pt]
    res = bmesh.ops.convex_hull(bm, input=vb + vt)
    junk = [g for g in res.get("geom_interior", []) + res.get("geom_unused", []) if isinstance(g, bmesh.types.BMVert)]
    if junk:
        bmesh.ops.delete(bm, geom=junk, context="VERTS")
    vs = [v for v in vb + vt if v.is_valid]
    mb._post(vs, CM, None, 0.06, 1)
    mi = mb._mi_for(CL)
    for f in bm.faces:
        if f in before:
            continue
        f.normal_update()
        if f.normal.z > 0.8:
            f.material_index = mi
    ps = pb + pt
    lo = Vector((min(p.x for p in ps), min(p.y for p in ps), min(p.z for p in ps)))
    hi = Vector((max(p.x for p in ps), max(p.y for p in ps), max(p.z for p in ps)))

    def ztop(qx, qy):
        lx = (qx - x) * cy + (qy - y) * sy
        ly = -(qx - x) * sy + (qy - y) * cy
        return z0 + max(h * 0.5, h + gx * lx + gy * ly)
    info = dict(base=pb, top=pt, c=Vector((x, y, z0)), tmin=min(p.z for p in pt))
    return lo, hi, ztop, info


def _rock_col(lo, hi, tmin, shrink=0.25):
    col_box2(A, (lo.x + shrink, lo.y + shrink, T), (hi.x - shrink, hi.y - shrink, max(lo.z + 0.3, tmin - 0.1)))


def _rock_stubs(mb, info, picks):
    """tocos de vergalhao saindo da quebra de um bloco: do meio da face lateral i para fora e dobrando para cima"""
    base, top, c = info["base"], info["top"], info["c"]
    Z = Vector((0, 0, 1))
    for i, l1, l2 in picks:
        j = (i + 1) % len(base)
        mb_ = (base[i] + base[j]) / 2
        mt = (top[i] + top[j]) / 2
        m = mb_ * 0.45 + mt * 0.55
        out = Vector((m.x - c.x, m.y - c.y, 0)).normalized()
        _bar(mb, m - out * 0.55, m + out * 0.02, [(out + Z * 0.2, l1), (Z + out * 0.3, l2)], 0.12, r=0.17)


def _lean_slab(mb, x, yb, zf, w, ln, th, alpha, toward, notch=0.0, mtop=CL, mside=CM):
    """laje partida ENCOSTADA: aresta de baixo no piso (x, yb, zf), sobe inclinada alpha em direcao a `toward`
    (-1: -y, +1: +y); topo quebrado irregular; face de cima clara, quebras escuras. Devolve (base, topo) da linha
    central para a COL em rampa"""
    u = Vector((1, 0, 0))
    v = Vector((0, toward * math.cos(alpha), math.sin(alpha)))
    pts = [(-w / 2, 0.0), (w / 2, 0.0), (w / 2 + 0.1, ln * 0.62), (w / 2 - 0.55, ln), (0.15 + notch, ln - 0.35),
           (-w / 2 + 0.45, ln * 0.94), (-w / 2 - 0.1, ln * 0.45)]
    o = Vector((x, yb, zf + th * 0.35))
    _slab2(mb, pts, o, u, v, th, mtop, mside, bevel=0.07)
    return o, o + v * (ln * 0.8)


def _jersey(mb, cx, cy, ang, length):
    """barreira de concreto (perfil new jersey) com faixa de alerta preta e amarela nas duas faces"""
    a = D(ang)
    ld = Vector((math.cos(a), math.sin(a), 0))
    u = Vector((-math.sin(a), math.cos(a), 0))
    zv = Vector((0, 0, 1))
    prof = [(-0.85, 0.0), (0.85, 0.0), (0.85, 0.3), (0.5, 0.85), (0.35, 2.5), (-0.35, 2.5), (-0.5, 0.85), (-0.85, 0.3)]
    o = Vector((cx, cy, ZW0 - 0.05))
    K.plate(mb, prof, o, u, zv, length, CL, bevel=0.1)
    za, zb = 1.35, 2.15
    ua = 0.5 - 0.15 * (za - 0.85) / 1.65
    ub = 0.5 - 0.15 * (zb - 0.85) / 1.65
    for s in (-1, 1):
        pa = o + u * (s * ua) + zv * za
        pb = o + u * (s * ub) + zv * zb
        up = (pb - pa).normalized()
        hn = (pb - pa).length
        nrm = (u * (s * 1.65) + zv * 0.15).normalized()
        base = pa + nrm * 0.03
        half = length / 2 - 0.2
        K.plate(mb, [(-half, 0), (half, 0), (half, hn), (-half, hn)], base, ld, up, 0.06, CG)
        w, sk, gap = 0.42, 0.5, 0.95
        xk = -half + 0.1
        while xk + w + sk < half:
            K.plate(mb, [(xk, 0.04), (xk + w, 0.04), (xk + w + sk, hn - 0.04), (xk + sk, hn - 0.04)],
                    base + nrm * 0.05, ld, up, 0.06, YE)
            xk += gap


def _cone(mb, x, y, s=1.0):
    mb.box((1.3 * s, 1.3 * s, 0.18), (x, y, ZW0 + 0.09), (0, 0, 0.3), CG, 0.05)
    K.cone(mb, V(x, y, ZW0 + 0.15), V(x, y, ZW0 + 1.95 * s), 0.6 * s, 0.1 * s, YE, 10)
    mb.cyl(0.43 * s, 0.34 * s, (x, y, ZW0 + 0.95 * s), (0, 0, 0), CG, 10, r2=0.34 * s, bevel=0.0)


def _rrect(w, h, r, n=3):
    """retangulo arredondado centrado (anti-horario)"""
    pts = []
    for cx, cz, a0 in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180),
                       (w / 2 - r, -h / 2 + r, 270)):
        for i in range(n + 1):
            a = D(a0 + 90 * i / n)
            pts.append((cx + math.cos(a) * r, cz + math.sin(a) * r))
    return pts


def _fist(mb, bx, yface, zc, s, depth=0.75):
    """PUNHO de luva vermelha visto de frente, em relevo sobre a face yface (-y): 4 dedos de pontas redondas lado a
    lado, polegar cruzando por baixo, costas da mao e punho da luva. zc = centro visual do punho"""
    u = Vector((1, 0, 0))
    up = Vector((0, 0, 1))
    zc = zc + 0.185 * s

    def P(dx, dy, dz):
        return Vector((bx + dx * s, yface + dy * s * depth, zc + dz * s))
    zf = 0.15
    e = s * depth
    K.plate(mb, _rrect(2.7 * s, 1.9 * s, 0.5 * s), P(0.05, -0.22, zf - 0.2), u, up, 0.44 * e, RD)
    K.plate(mb, _rrect(1.9 * s, 0.85 * s, 0.22 * s, 2), P(0.15, -0.22, zf - 1.45), u, up, 0.44 * e, RD)
    for k in range(4):
        dz = 0.08 if k in (1, 2) else 0.0
        K.plate(mb, _rrect(0.6 * s, 1.25 * s, 0.29 * s, 3), P(-0.99 + k * 0.66, -0.62, zf + 0.5 + dz), u, up,
                0.5 * e, RD)
    K.plate(mb, _rrect(1.8 * s, 0.58 * s, 0.28 * s, 3), P(-0.42, -1.0, zf - 0.36), u, up, 0.42 * e, RD)


def _board(mb, px):
    """OUTDOOR da coroa (topo da silhueta), preso RENTE na fachada no eixo do furo e rompendo a linha da cornija:
    caixa escura, painel amarelo, moldura saliente, PUNHO vermelho e linhas de impacto pretas dos dois lados"""
    yb = YF - 0.02                 # costas na fachada
    yk = YF - 0.5                  # frente da caixa
    yp = yk - 0.06                 # frente do painel amarelo
    mb.box2((px - BW, yk, BZ0), (px + BW, yb, BZ1), CG, 0.1)
    mb.box2((px - BW + 0.3, yp, BZ0 + 0.3), (px + BW - 0.3, yk + 0.1, BZ1 - 0.3), YE, 0.0)
    ym = yp - 0.2                  # frente da moldura
    for z0, z1 in ((BZ0, BZ0 + 0.45), (BZ1 - 0.45, BZ1)):
        mb.box2((px - BW, ym, z0), (px + BW, yk + 0.05, z1), CG, 0.08)
    for s in (-1, 1):
        xa, xb = sorted((px + s * BW, px + s * (BW - 0.45)))
        mb.box2((xa, ym, BZ0 + 0.43), (xb, yk + 0.05, BZ1 - 0.43), CG, 0.08)
    zm = (BZ0 + BZ1) / 2
    k = (BZ1 - BZ0) / 4.9
    _fist(mb, px, yp, zm - 0.2 * k, 1.12 * k)
    u = Vector((1, 0, 0))
    up = Vector((0, 0, 1))
    for s in (-1, 1):
        for ang, r0, r1, hw in ((-27, 2.2, 3.45, 0.19), (0, 2.1, 3.6, 0.23), (27, 2.2, 3.45, 0.19)):
            a = D(ang)
            dx, dz = math.cos(a) * s, math.sin(a)
            nx, nz = -dz, dx
            r0, r1, hw = r0 * k, r1 * k, hw * k
            pts = [(dx * r0, dz * r0), (dx * r1 + nx * hw, dz * r1 + nz * hw), (dx * r1 - nx * hw, dz * r1 - nz * hw)]
            if (pts[1][0] - pts[0][0]) * (pts[2][1] - pts[0][1]) - (pts[1][1] - pts[0][1]) * (pts[2][0] - pts[0][0]) < 0:
                pts = [pts[0], pts[2], pts[1]]
            K.plate(mb, pts, (px, yp - 0.03, zm), u, up, 0.06, CG)


def _broken_step(mb, x0, x1, y0, y1, ztop, splits, yaws, m=CM):
    """degrau de placas de concreto (partidas pelas linhas `splits`, x em funcao de y); cada placa gira um pouco no
    proprio centro; topo horizontal (andavel), nariz amarelo na frente de cada placa"""
    cuts = [[(x0, y0), (x0, y1)]] + splits + [[(x1, y0), (x1, y1)]]
    g = 0.09
    for i in range(len(cuts) - 1):
        left = [(x + (g if i > 0 else 0.0), y) for x, y in cuts[i]]
        right = [(x - (g if i < len(cuts) - 2 else 0.0), y) for x, y in cuts[i + 1]]
        poly = [left[0], right[0]] + right[1:] + list(reversed(left[1:]))
        cx = sum(p[0] for p in poly) / len(poly)
        cy = sum(p[1] for p in poly) / len(poly)
        a = D(yaws[i])
        ca, sa = math.cos(a), math.sin(a)
        rp = [(cx + (p[0] - cx) * ca - (p[1] - cy) * sa, cy + (p[0] - cx) * sa + (p[1] - cy) * ca) for p in poly]
        mb.prism(rp, ZW0 - 0.2, ztop, m, bevel=0.12)
        fa, fb = rp[0], rp[1]
        dx, dy = fb[0] - fa[0], fb[1] - fa[1]
        ln = math.hypot(dx, dy)
        mb.box((ln - 0.5, 0.36, 0.08), ((fa[0] + fb[0]) / 2 - dy / ln * 0.22, (fa[1] + fb[1]) / 2 + dx / ln * 0.22,
                                         ztop + 0.03), (0, 0, math.atan2(dy, dx)), YE, 0.0)


def build(rng):
    import fm_portals
    px = L.PORTAL_X[L.PORTAL_KEYS.index(KEY)]

    def X(dx):
        return px + dx
    mb = K.LeanMB("PORTAL_%s_Wall" % KEY, C, rng, vcap=2)
    dec = K.LeanMB("PORTAL_%s_Decal" % KEY, C, rng, vcap=2)     # rachaduras, zebrado, filetes de luz, vedacao

    # ---------------------------------------------------------------- calcada (placas com juntas + meio-fio amarelo
    # na frente e atras)
    ys0, ys1 = Y0 + 0.2, PY + 9.6
    xs0, xs1 = X(-13.8), X(13.8)
    mb.box2((xs0 + 0.05, ys0 + 0.05, T - 0.4), (xs1 - 0.05, ys1 - 0.05, ZW0 - 0.14), CG, 0.0)
    mb.box2((xs0, ys0, T - 0.3), (xs1, ys0 + 0.8, ZW0 + 0.14), YE, 0.1)
    mb.box2((xs0, ys1 - 0.8, T - 0.3), (xs1, ys1, ZW0 + 0.14), YE, 0.1)
    for s in (-1, 1):
        xa, xb = (xs0, xs0 + 0.7) if s < 0 else (xs1 - 0.7, xs1)
        mb.box2((xa, ys0 + 0.8, T - 0.3), (xb, ys1 - 0.8, ZW0 + 0.1), CL, 0.08)

    def covered(x, y):
        if abs(x - px) < CUN + 0.2 and YF - 0.4 < y < YB + 0.4:
            return True
        if abs(x - px) < 5.6 and 107.2 < y < YF:
            return True
        return False
    nx, ny = 8, 7
    tw_ = (xs1 - xs0 - 1.4) / nx
    th_ = (ys1 - ys0 - 1.6) / ny
    for i in range(nx):
        for j in range(ny):
            x = xs0 + 0.7 + (i + 0.5) * tw_
            y = ys0 + 0.8 + (j + 0.5) * th_
            if covered(x, y):
                continue
            mb.box((tw_ - 0.18, th_ - 0.18, 0.22), (x, y, ZW0 - 0.11), (0, 0, 0), CL, 0.0)
    col_box2(A, (xs0, ys0, T - 1.0), (xs1, ys1, ZW0))

    # ---------------------------------------------------------------- degraus ate o fundo do furo: o de baixo inteiro,
    # o de cima partido por UMA emenda (continua a boca partida logo acima dele)
    ye = YF + 0.6
    _broken_step(mb, X(-5.8), X(5.8), 107.0, ye, T + 1.45, [], (0.0,))
    _broken_step(mb, X(-5.0), X(5.0), 109.6, ye, T + 2.4,
                 [[(X(-1.7), 109.6), (X(-1.2), 110.6), (X(-1.9), 111.4), (X(-1.5), ye)]], (-0.35, 0.45))
    col_box2(A, (X(-5.8), 107.0, T), (X(5.8), ye, T + 1.45))
    col_box2(A, (X(-5.0), 109.6, T), (X(5.0), ye, T + 2.4))

    # ---------------------------------------------------------------- MURO: miolo furado + parte de cima
    _holed_core(mb, px, rng)
    mb.box2((X(-WX), YF, ZCORE), (X(WX), YB, ZWIN), CL, 0.0)
    mb.box2((X(-CUN - 0.15), YF - 0.45, ZW0 - 0.1), (X(CUN + 0.15), YB + 0.45, ZPL), CG, 0.15)
    for s in (-1, 1):
        xa, xb = sorted((X(s * PIL), X(s * CUN)))
        mb.box2((xa, YF - 0.4, ZPL), (xb, YB + 0.4, ZWIN), CL, 0.15)
        # contorno escuro GROSSO nas quinas externas do cunhal (frente e costas): recorta o muro do penhasco
        xa, xb = sorted((X(s * (CUN - 0.45)), X(s * (CUN + 0.04))))
        mb.box2((xa, YF - 0.44, ZPL), (xb, YF + 0.7, ZWIN), CG, 0.05)
        mb.box2((xa, YB - 0.7, ZPL), (xb, YB + 0.44, ZWIN), CG, 0.05)
    # laje/peitoril (frente interrompida pelo outdoor; costas corridas)
    for s in (-1, 1):
        xa, xb = sorted((X(s * PIL), X(s * (BW - 0.05))))
        mb.box2((xa, YF - 0.36, ZCORE), (xb, YF + 0.2, ZBAND), CL, 0.12)
    mb.box2((X(-PIL), YB - 0.2, ZCORE), (X(PIL), YB + 0.36, ZBAND), CL, 0.12)
    # faixa de janelas: vidro escuro, montantes finos e escuros; a luz (filete amarelo) vai no objeto de decal
    for s, yy in ((-1, YF), (1, YB)):
        segs = [(-PIL, -BW), (BW, PIL)] if s < 0 else [(-PIL, PIL)]
        for xa, xb in segs:
            mb.box2((X(xa), yy - 0.1 if s < 0 else yy - 0.05, ZBAND), (X(xb), yy + 0.05 if s < 0 else yy + 0.1, ZWIN),
                    DG, 0.0)
            dec.box2((X(xa), yy + s * 0.2, ZWIN - 0.66), (X(xb), yy + s * 0.08, ZWIN - 0.2), GL, 0.0)
        if s < 0:
            sp = (PIL - BW) / 3
            xm = [-(BW + sp * 2), -(BW + sp), BW + sp, BW + sp * 2]
        else:
            xm = [-6.4, -3.2, 0.0, 3.2, 6.4]
        for x in xm:
            mb.box((0.2, 0.34, ZWIN - ZBAND), (X(x), yy + s * 0.14, (ZBAND + ZWIN) / 2), (0, 0, 0), CM, 0.0)
    # cornija + capa escura (interrompidas na frente pelo outdoor)
    for s in (-1, 1):
        xa, xb = sorted((X(s * (CUN + 0.3)), X(s * BW)))
        mb.box2((xa, YF - 0.6, ZWIN), (xb, YB + 0.6, ZTOP), CL, 0.15)
        xa, xb = sorted((X(s * (CUN + 0.45)), X(s * BW)))
        mb.box2((xa, YF - 0.75, ZTOP), (xb, YB + 0.75, ZCAP), CG, 0.1)
    mb.box2((X(-BW), YF, ZWIN), (X(BW), YB + 0.6, ZTOP), CL, 0.15)
    mb.box2((X(-BW), YF, ZTOP), (X(BW), YB + 0.75, ZCAP), CG, 0.1)

    # marcas rentes (frente e costas), coladas na superficie real (raio contra o que ja foi construido)
    bvh = BVHTree.FromBMesh(mb.bm)
    # rachaduras = cunhas saindo das pontas da estrela: (angulo da ponta, alvo (dx, dz), largura, chega na borda?,
    # garfo (fracao, desvio em graus, comprimento))
    _web(dec, bvh, px, -1, _rs,
         [(133, (-PIL + 0.1, ZCORE - 0.1 - ZC), 0.95, True, (0.4, -40, 1.0)),
          (318, (PIL - 0.1, ZPL + 0.15 - ZC), 0.95, True, (0.4, 40, 1.0)),
          (50, (PIL - 0.1, ZCORE - 0.1 - ZC), 0.85, True, (0.4, 36, 0.9)),
          (224, (-PIL + 0.1, ZPL + 0.15 - ZC), 0.85, True, (0.45, -35, 0.9)),
          (78, (2.6, ZCORE - 0.1 - ZC), 0.5, True, None),
          (160, (-PIL + 0.1, 4.6), 0.45, True, None),
          (22, (PIL - 0.1, 4.9), 0.45, True, None)], rng)
    _web(dec, bvh, px, 1, _rsb,
         [(145, (-PIL + 0.1, ZCORE - 0.1 - ZC), 0.85, True, (0.45, 35, 0.9)),
          (310, (PIL - 0.1, ZPL + 0.15 - ZC), 0.85, True, (0.45, -35, 0.9)),
          (40, (PIL - 0.1, ZCORE - 0.1 - ZC), 0.7, True, None),
          (221, (-PIL + 0.1, ZPL + 0.15 - ZC), 0.7, True, None),
          (96, (-0.9, ZCORE - 0.1 - ZC), 0.45, True, None)], rng)

    # friso zebrado amarelo/preto CONTINUO no embasamento: frente (fora dos degraus), laterais e costas
    zz0, zz1 = ZW0 + 0.25, ZW0 + 1.05
    yb0, yb1 = YF - 0.45, YB + 0.45
    for s in (-1, 1):
        _zebra(dec, (X(s * 5.95), yb0), (X(s * (CUN + 0.15)), yb0), zz0, zz1, (0, -1))
        _zebra(dec, (X(s * (CUN + 0.15)), yb0), (X(s * (CUN + 0.15)), yb1), zz0, zz1, (s, 0))
    _zebra(dec, (X(-CUN - 0.15), yb1), (X(CUN + 0.15), yb1), zz0, zz1, (0, 1))

    # vergalhoes nas duas pontas maiores (nada encosta no aro: sem lajes soltas na boca)
    _rebars(mb, px)

    # colisao do muro: laterais (|x| >= 7), verga, soleira do furo (a partir da borda visivel, YF+0.6), parada
    col_box2(A, (X(-CUN - 0.2), YF - 0.5, T), (X(-7.0), YB + 0.5, ZCAP))
    col_box2(A, (X(7.0), YF - 0.5, T), (X(CUN + 0.2), YB + 0.5, ZCAP))
    col_box2(A, (X(-7.0), YF, ZC + 5.8), (X(7.0), YB, ZCAP))
    col_box2(A, (X(-3.6), ye, T), (X(3.6), YB, ZC - BORE))
    col_box2(A, (X(-7.0), ye, T), (X(-3.6), YB, ZC - 6.6))
    col_box2(A, (X(3.6), ye, T), (X(7.0), YB, ZC - 6.6))
    col_box2(A, (X(-6.0), YB - 0.9, ZC - BORE), (X(6.0), YB, ZC + 5.8))

    # ---------------------------------------------------------------- escombros: UM monte a direita atras do furo
    zf = ZW0
    ra, rb_ = _lean_slab(mb, X(2.9), YB + 0.45 + 2.1, zf, 3.8, 2.6, 0.6, D(36), -1)
    col_ramp(A, (ra.x, ra.y, ra.z + 0.1), (rb_.x, rb_.y, rb_.z + 0.1), 3.4, 0.8)
    lo, hi, zt, inf = _rock(mb, X(6.4), 119.0, zf, 3.6, 1.6, D(18), 0.08, rng, k=5)
    _rock_col(lo, hi, inf["tmin"])
    _rock_stubs(mb, inf, [(0, 0.6, 0.85), (3, 0.8, 0.5)])
    lo2, hi2, _z2, inf2 = _rock(mb, X(5.9), 119.2, zt(X(5.9), 119.2) - 0.14, 2.3, 1.1, D(70), 0.32, rng, k=5,
                                embed=0.0)
    col_box2(A, (lo2.x + 0.35, lo2.y + 0.35, hi.z - 0.4), (hi2.x - 0.35, hi2.y - 0.35, inf2["tmin"] - 0.1))
    lo, hi, _zt, inf = _rock(mb, X(2.3), 120.6, zf, 3.0, 1.3, D(-25), 0.28, rng, k=5)
    _rock_col(lo, hi, inf["tmin"])
    _rock_stubs(mb, inf, [(1, 0.7, 0.65)])

    # ---------------------------------------------------------------- escombros: UM monte a direita na frente (laje
    # encostada no embasamento + bloco com outro em cima + bloco solto ao lado da escada)
    fa, fb = _lean_slab(mb, X(8.1), YF - 0.45 - 1.36 + 0.08, zf - 0.06, 2.4, 1.95, 0.45, D(46), 1, notch=0.3)
    col_ramp(A, (fa.x, fa.y, fa.z + 0.1), (fb.x, fb.y, fb.z + 0.1), 2.2, 0.8)
    lo, hi, zt, inf = _rock(mb, X(9.7), 109.2, zf, 2.1, 1.15, D(-20), 0.1, rng, k=5, elong=1.15)
    _rock_col(lo, hi, inf["tmin"])
    lo2, hi2, _z2, inf2 = _rock(mb, X(9.4), 109.4, zt(X(9.4), 109.4) - 0.12, 1.45, 0.75, D(40), 0.35, rng, k=4,
                                embed=0.0)
    col_box2(A, (lo2.x + 0.3, lo2.y + 0.3, hi.z - 0.4), (hi2.x - 0.3, hi2.y - 0.3, inf2["tmin"] - 0.1))
    lo, hi, _zt, inf = _rock(mb, X(7.2), 107.8, zf, 1.4, 0.85, D(30), 0.34, rng, k=5, elong=1.1)
    _rock_col(lo, hi, inf["tmin"], 0.2)

    # ---------------------------------------------------------------- cordao de isolamento (esq.): barreira + 2 cones
    bx, by, bang, blen = X(-9.0), Y0 + 4.3, 24.0, 4.4
    _jersey(mb, bx, by, bang, blen)
    col_box(A, (blen, 1.2, 2.95), (bx, by, T + 1.475), (0, 0, D(bang)))
    for (dx, y, s) in ((-7.7, 108.6, 1.0), (-8.8, 110.0, 0.85)):
        _cone(mb, X(dx), y, s)
        col_box(A, (0.8 * s, 0.8 * s, 1.95 * s + 0.5), (X(dx), y, T + (1.95 * s + 0.5) / 2))

    # ---------------------------------------------------------------- coroa: outdoor com o punho
    _board(mb, px)

    fm_portals.swirl(KEY, px, SW, mb, CG, rim_y=-0.35)
    # aro liso de 64 lados na frente (cobre o de 32 do swirl) e na saida (cobre do disco ate r8.12, alem do furo r7.8)
    _glow_annulus(mb, px, PY - 0.35 - 0.3, 7.18, 7.8, -1, 0.5)
    _glow_annulus(mb, px, YB - 0.02, 7.45, 8.12, 1, 0.4)
    _seal(dec, px, PY + 0.5, 7.45, 7.86)
    _back_disc(px, rng)
    _swirl_unlit()
    mb.finish()
    dec.finish(recalc=False)


# ================================================================== DRESSING DA ESCADA (lance 2): "OBRA INTERDITADA"
# Faixa ao lado do poco, no terraco (z=T): y 85.5..99.6, 7.8 <= |x-px| <= 13.9 (nada no poco, nada sobre a escada).
# Continua a leitura do portal descendo a escada (cordao a esquerda, escombros a direita):
#   ESQUERDA: CORDAO de barreiras new jersey (mesmo perfil e faixa zebrada preta/amarela da barreira do portal) na
#     borda do poco, fazendo de guarda-corpo: duas em pe (a de cima um pouco torta) e a mais perto do portal TOMBADA
#     de lado pelo impacto do soco.
#   DIREITA: MONTE DE ESCOMBROS do soco (a linguagem dos montes do portal): bloco arrancado com outro em cima, laje
#     partida encostada neles com vergalhoes tortos saindo da quebra, bloco menor ao lado; na frente, placa rachada no
#     chao com um toco de vergalhao. Maior perto do portal, menor perto da borda.
# So a paleta do portal (concreto claro/medio/escuro, amarelo, vergalhao); semente propria (o estudio e o build dao a
# mesma geometria); 4 COL: as 3 barreiras e o monte (com o cone).
ST_SEED = 4051
# monte da direita: laje dobrada (pe em x/y, rumo phi, pecas a1/b1 e a2/b2, torcao roll; dz enterra), bloco em cunha
# por baixo (costas recuadas bin do plano de tras da COL), COL em rampa (largura cw, labio maximo lip sobre o pe, sobra
# over alem da ponta), cone (cx, cy) e bloco solto (sx, sy)
ST_MOUND = dict(x=10.2, y=92.15, phi=88.0, w=3.6, th=0.6, a1=46.0, b1=2.7, a2=24.0, b2=3.0, roll=-5.0, dz=-0.12,
                bin=0.04, ridge=0.5, cw=3.2, lip=0.3, over=0.0, cx=9.0, cy=91.0, sx=12.8, sy=95.3)
ST_DBG = {}
ST_PROF =[(-0.85, 0.0), (0.85, 0.0), (0.85, 0.3), (0.5, 0.85), (0.35, 2.5), (-0.35, 2.5), (-0.5, 0.85), (-0.85, 0.3)]


def _st_frame(cx, cy, ang, z0, tip=0):
    """referencial da barreira: ld (comprimento), origem O e eixos U/W do perfil (a, b) no mundo.
    tip=0: em pe (U horizontal, W = +Z, O = (cx, cy, z0)); tip=+-1: DEITADA de lado, tombada para +-u, apoiada na
    aresta do fecho convexo (0.85, 0.3)-(0.35, 2.5) do lado da queda; (cx, cy) = essa aresta no chao, no meio"""
    a = D(ang)
    ld = Vector((math.cos(a), math.sin(a), 0))
    u = Vector((-math.sin(a), math.cos(a), 0))
    zv = Vector((0, 0, 1))
    if not tip:
        return ld, u, Vector((cx, cy, z0)), u, zv
    s = tip
    p0 = Vector((0.85 * s, 0.3))
    e = (Vector((0.35 * s, 2.5)) - p0).normalized()
    n = Vector((e.y, -e.x)) if s > 0 else Vector((-e.y, e.x))   # normal para fora do perfil (lado da queda)
    U = u * (s * e.x) + zv * (-n.x)
    W = u * (s * e.y) + zv * (-n.y)
    O = Vector((cx, cy, z0)) - U * p0.x - W * p0.y
    return ld, u, O, U, W


def _st_jersey(mb, cx, cy, ang, length, z0=T - 0.06, tip=0, faces=(-1, 1)):
    """barreira new jersey (perfil e faixa zebrada da _jersey do portal) em pe ou tombada; `faces` = lados do perfil
    que recebem a faixa (a face de baixo da tombada fica virada para o chao e nao leva)"""
    ld, _u, O, U, W = _st_frame(cx, cy, ang, z0, tip)
    K.plate(mb, ST_PROF, O, U, W, length, CL, bevel=0.1)
    za, zb = 1.35, 2.15
    ua = 0.5 - 0.15 * (za - 0.85) / 1.65
    ub = 0.5 - 0.15 * (zb - 0.85) / 1.65
    half = length / 2 - 0.2
    for s in faces:
        pa = O + U * (s * ua) + W * za
        pb = O + U * (s * ub) + W * zb
        up = (pb - pa).normalized()
        hn = (pb - pa).length
        nrm = (U * (s * 1.65) + W * 0.15).normalized()
        base = pa + nrm * 0.03
        K.plate(mb, [(-half, 0), (half, 0), (half, hn), (-half, hn)], base, ld, up, 0.06, CG)
        w, sk, gap = 0.42, 0.5, 0.95
        xk = -half + 0.1
        while xk + w + sk < half:
            K.plate(mb, [(xk, 0.04), (xk + w, 0.04), (xk + w + sk, hn - 0.04), (xk + sk, hn - 0.04)],
                    base + nrm * 0.05, ld, up, 0.06, YE)
            xk += gap


def _st_slab(mb, x, y, zf, w, ln, th, alpha, phi, pts=None):
    """laje partida ENCOSTADA com rumo livre: aresta de baixo centrada em (x, y) no chao zf, sobe `alpha` na direcao
    horizontal phi (graus); face de cima clara, quebras escuras (_slab2). Devolve (o, u, v): plano medio da laje"""
    p = D(phi)
    u = Vector((math.sin(p), -math.cos(p), 0))
    v = Vector((math.cos(p) * math.cos(alpha), math.sin(p) * math.cos(alpha), math.sin(alpha)))
    pts = pts or [(-w / 2, 0.0), (w / 2, 0.0), (w / 2 + 0.1, ln * 0.62), (w / 2 - 0.55, ln), (0.15, ln - 0.35),
                  (-w / 2 + 0.45, ln * 0.94), (-w / 2 - 0.1, ln * 0.45)]
    o = Vector((x, y, zf + th * 0.35))
    _slab2(mb, pts, o, u, v, th, CL, CM, bevel=0.07)
    return o, u, v


def _st_fold(mb, x, y, zf, w, th, phi, b1, a1, b2, a2, crack, top, gap=0.1, roll=0.0, sides=None):
    """laje partida e DOBRADA sobre um bloco: a peca de baixo sobe a1 do chao (aresta de baixo centrada em (x, y)) ate
    a quebra em b1 (linha `crack` [(a, db)] da esquerda para a direita); a de cima continua da quebra deitada a2 ate
    o contorno quebrado `top` [(a, b)] (da direita para a esquerda), torcida `roll` no proprio eixo (nao assenta
    reta no bloco). `sides` = ((a, b) direita, (a, b) esquerda): uma quebra em cada lado da peca de baixo (tira o
    retangulo limpo, como o _lean_slab do portal). Faces de cima claras, quebras escuras.
    Devolve (o, u, v1, n1, o2, u2, v2, n2): origem/eixos/normal de cima de cada peca"""
    p = D(phi)
    u = Vector((math.sin(p), -math.cos(p), 0))
    dh = Vector((math.cos(p), math.sin(p), 0))
    Z = Vector((0, 0, 1))
    v1 = dh * math.cos(a1) + Z * math.sin(a1)
    v2 = dh * math.cos(a2) + Z * math.sin(a2)
    o = Vector((x, y, zf + th * 0.35))
    sr, sl = sides if sides else ([], [])
    _slab2(mb, [(-w / 2, 0.0), (w / 2, 0.0)] + list(sr) + [(a, b1 + db) for a, db in reversed(crack)] + list(sl),
           o, u, v1, th, CL, CM)
    o2 = o + v1 * b1
    n2 = u.cross(v2).normalized()
    u2 = u * math.cos(roll) + n2 * math.sin(roll)
    _slab2(mb, [(a, db + gap) for a, db in crack] + list(top), o2, u2, v2, th, CL, CM)
    return o, u, v1, u.cross(v1).normalized(), o2, u2, v2, u2.cross(v2).normalized()


def _st_bar(mb, pts, r=0.16, ch=0.14):
    """vergalhao barato (5 lados): polilinha com as dobras chanfradas (dobra seca), ponta cortada"""
    pts = [Vector(p) for p in pts]
    out = [pts[0]]
    for a, b, c in zip(pts, pts[1:], pts[2:]):
        out += [b + (a - b).normalized() * ch, b + (c - b).normalized() * ch]
    out.append(pts[-1])
    _ptube(mb, out, r, RB, n=5)


def _st_block(mb, pts):
    """bloco de concreto arrancado em CUNHA: fecho convexo de pontos dados (mundo), no acabamento do _rock (quebras
    escuras, topo claro, bevel 0.06). Serve de nucleo do monte: frente sob a laje, costas num plano dado"""
    bm = mb.bm
    before = set(bm.faces)
    vs = [bm.verts.new(p) for p in pts]
    res = bmesh.ops.convex_hull(bm, input=vs)
    junk = [g for g in res.get("geom_interior", []) + res.get("geom_unused", []) if isinstance(g, bmesh.types.BMVert)]
    if junk:
        bmesh.ops.delete(bm, geom=junk, context="VERTS")
    mb._post([v for v in vs if v.is_valid], CM, None, 0.06, 1)
    mi = mb._mi_for(CL)
    for f in bm.faces:
        if f in before:
            continue
        f.normal_update()
        if f.normal.z > 0.8:
            f.material_index = mi


def _st_cone(mb, x, y, s=1.0, z0=T):
    """cone de obra (o _cone do portal, 8 lados) apoiado no terraco"""
    mb.box((1.3 * s, 1.3 * s, 0.18), (x, y, z0 + 0.09), (0, 0, 0.3), CG, 0.05)
    K.cone(mb, V(x, y, z0 + 0.15), V(x, y, z0 + 1.95 * s), 0.6 * s, 0.1 * s, YE, 8)
    mb.cyl(0.43 * s, 0.34 * s, (x, y, z0 + 0.95 * s), (0, 0, 0), CG, 8, r2=0.34 * s, bevel=0.0)


def stairs(mb, px, rng):
    """dressing da faixa ao lado do lance 2 (objeto PORTAL_OnePunchMan_Stairs): cordao de barreiras a esquerda,
    monte de escombros a direita. Usa semente propria (ST_SEED): o rng recebido nao e consumido."""
    import random
    r = random.Random(ST_SEED)
    Z = Vector((0, 0, 1))

    # ---------------------------------------------------------------- ESQUERDA: cordao na borda do poco: barreira em
    # pe, a do meio TOMBADA de lado pelo impacto (o cordao fica com um buraco; o perfil da ponta fica para a escada),
    # a de cima em pe e um pouco torta, emendando com a barreira do portal
    _st_jersey(mb, px - 8.95, 88.85, 90.0, 3.7)
    col_box2(A, (px - 10.05, 86.95, T), (px - 8.05, 90.75, T + 2.45))
    ang2, g2 = 150.0, Vector((px - 9.8, 93.9, 0))
    _ld, ub, _o, _U, _W = _st_frame(g2.x, g2.y, ang2, T - 0.06, 1)
    _st_jersey(mb, g2.x, g2.y, ang2, 3.6, tip=1, faces=(-1,))
    c2 = g2 + ub * 1.0
    col_box(A, (3.5, 2.5, 1.6), (c2.x, c2.y, T + 0.8), (0, 0, D(ang2)))
    _st_jersey(mb, px - 9.05, 97.45, 94.0, 3.7)
    col_box(A, (3.7, 1.8, 2.45), (px - 9.05, 97.45, T + 1.225), (0, 0, D(94.0)))

    # ---------------------------------------------------------------- DIREITA: monte de escombros perto do portal,
    # desenhado como UMA CUNHA para caber numa COL so (col_ramp): na frente a LAJE PARTIDA dobrada sobre o bloco
    # arrancado (sobe do chao, quebra na quina do bloco e deita em cima; dobra moderada, para o topo das duas pecas
    # ficar a menos de ~0.35 de um plano so); o bloco e uma cunha macica que enche o monte por baixo da laje, com as
    # costas (lado do portal) NO plano da face de tras da rampa de colisao (a caixa da rampa tem a face de tras
    # perpendicular ao topo: costas a 90-p graus). Vergalhoes tortos expostos na dobra e saindo da quebra de cima;
    # cone de obra na borda do poco, na frente do pe.
    M = ST_MOUND
    zf = T + M["dz"]
    w, th, b1, b2 = M["w"], M["th"], M["b1"], M["b2"]
    o, u, v1, n1, o2, u2, v2, n2 = _st_fold(
        mb, px + M["x"], M["y"], zf, w, th, M["phi"], b1, D(M["a1"]), b2, D(M["a2"]),
        [(-w / 2 - 0.1, 0.1), (-0.9, -0.15), (0.2, 0.18), (w / 2 + 0.1, -0.05)],
        [(w / 2 + 0.05, b2 - 0.2), (0.4, b2), (-0.5, b2 - 0.2), (-w / 2, b2 - 0.35)], roll=D(M["roll"]),
        sides=([(w / 2 + 0.28, b1 * 0.32)], [(-w / 2 + 0.42, b1 * 0.5)]))
    # COL: plano da rampa = corda do topo (pe da peca de baixo -> ponta da deitada, no eixo) subida metade da flecha da
    # dobra (erro +-flecha/2 no pe, na dobra e na ponta); a caixa desce ate o chao pela face de tras (= costas do bloco)
    dh = Vector((math.cos(D(M["phi"])), math.sin(D(M["phi"])), 0))
    q0 = o + n1 * (th / 2) + dh * 0.12
    q1 = o + v1 * b1 + n1 * (th / 2)
    q2 = o2 + v2 * (b2 - 0.15) + n2 * (th / 2)
    h1, h2 = (q1 - q0).dot(dh), (q2 - q0).dot(dh)
    sl = (q2.z - q0.z) / h2
    sag = q1.z - (q0.z + sl * h1)
    pa = q0 + Z * max(0.05, min(sag / 2, M["lip"]))
    pb = pa + (dh + Z * sl) * (h2 + M["over"])
    pit = math.atan(sl)
    dn = dh * math.cos(pit) + Z * math.sin(pit)          # normal da face de tras da rampa
    thick = (pb.z - (T - 0.05)) / math.cos(pit)
    col_ramp(A, pa, pb, M["cw"], thick)
    # nucleo: bloco em cunha. Frente e topo abaixo das faces de baixo das duas pecas (planos por o -/+ n*th/2), costas
    # no plano da face de tras da rampa (recuadas `bin`); larguras irregulares por canto
    base0 = Vector((o.x, o.y, 0))
    c0 = (base0 - Vector((pb.x, pb.y, 0))).dot(dn)
    cp, sp = math.cos(pit), math.sin(pit)

    def s_back(z):                                   # s (ao longo de dh a partir do pe) do plano de tras na altura z
        return -(c0 + (z - pb.z) * sp) / cp - M["bin"]

    def under(P, n, s, t, off):                      # z da face de baixo de uma peca em (s, t), menos off
        X = base0 + dh * s + u * t
        return P.z - ((X.x - P.x) * n.x + (X.y - P.y) * n.y) / n.z - off

    P1, P2, P2t = o - n1 * (th / 2), o2 - n2 * (th / 2), o2 + n2 * (th / 2)
    sc = (o2 - o).dot(dh) - 0.1
    pts = []
    for t, tb, sf, dsc, dzt, off in ((-1.3, -1.55, 0.95, 0.0, 0.15, 0.12), (1.2, 1.5, 0.75, -0.3, 0.45, 0.3)):
        zt = min(under(P1, n1, sc + dsc, t, dzt), under(P2, n2, sc + dsc, t, dzt))
        pts.append(base0 + dh * (sc + dsc) + u * t + Z * zt)                  # topo, na quina da dobra
        # crista de tras logo abaixo da crista da rampa (`ridge`): a laje deitada assenta no bloco e a ponta quebrada
        # dela fica rente as costas dele (o topo do bloco entra por baixo da ponta da laje, sem furar a face de cima)
        zr = pb.z - M["ridge"] - (off - 0.12)
        sr = s_back(zr)
        if t > 0:   # canto de tras de fora LASCADO: um ponto mais baixo no plano de tras e outro recuado no topo
            pts.append(base0 + dh * s_back(zr - 0.8) + u * (t * 1.1) + Z * (zr - 0.8))
            pts.append(base0 + dh * (sr - 0.6) + u * (t * 0.85) + Z * min(zr - 0.3, under(P2t, n2, sr - 0.6, t * 0.85, 0.3)))
        else:
            pts.append(base0 + dh * sr + u * (t * 1.12) + Z * zr)            # topo, na aresta de tras
        pts.append(base0 + dh * sf + u * tb + Z * (zf - 0.06))                # pe da frente
        pts.append(base0 + dh * s_back(zf - 0.06) + u * (tb * 1.02) + Z * (zf - 0.06))   # pe de tras
    pts.append(base0 + dh * 3.0 + u * -1.66 + Z * (zf + 0.85))               # barriga no lado do poco
    _st_block(mb, pts)
    # tocos de vergalhao saindo das quebras do bloco: nas costas (para o portal) e no lado do poco (para a escada)
    zs = zf + 1.35
    r0 = base0 + dh * (s_back(zs) - 0.45) + u * 0.45 + Z * zs
    r1 = r0 + dn * 0.95
    _st_bar(mb, [r0, r1, r1 + (Z * 0.8 + dn * 0.35 - u * 0.25).normalized() * 0.7])
    r0 = base0 + dh * 3.3 + u * -1.0 + Z * (zf + 0.75)
    r1 = r0 - u * 0.95
    _st_bar(mb, [r0, r1, r1 + (Z * 0.85 - dh * 0.4 - u * 0.2).normalized() * 0.65])
    ST_DBG.update(pit=math.degrees(pit), sag=sag, pa=pa.copy(), pb=pb.copy(), thick=thick,
                  yend=pb.y + thick * math.sin(pit), block=[p.copy() for p in pts])
    _st_cone(mb, px + M["cx"], M["cy"], 0.9, z0=T - 0.08)
    # vergalhoes expostos na dobra (entram na peca de baixo, arqueiam sobre a quebra, entram na de cima)
    for a_ in (-0.75, 0.65):
        _st_bar(mb, [o + u * a_ + v1 * (b1 - 0.5), o + u * a_ + v1 * b1 + (n1 + n2).normalized() * 0.6,
                     o2 + u2 * (a_ + 0.15) + v2 * 0.6])
    # e saindo da quebra de cima da peca deitada
    for a_, be, d2, l2 in ((0.4, b2 - 0.05, Z * 0.9 + v2 * 0.2 + u * 0.2, 0.95),
                           (-0.5, b2 - 0.4, Z * 0.6 - u * 0.8, 0.6)):
        m = o2 + u2 * a_ + v2 * (be + 0.55)
        _st_bar(mb, [o2 + u2 * a_ + v2 * (be - 0.5), m, m + d2.normalized() * l2])
    _rock(mb, px + M["sx"], M["sy"], T, 1.4, 0.8, D(-30), 0.3, r, k=5, elong=1.1)

    # ---------------------------------------------------------------- DIREITA, frente: placa rachada no chao + toco
    fo, fu, fv = _st_slab(mb, px + 10.3, 88.0, T - 0.08, 2.6, 2.3, 0.45, D(9), 100.0,
                          pts=[(-1.3, 0.0), (1.2, 0.0), (1.35, 1.2), (0.55, 2.3), (-1.25, 2.0)])
    q = fo + fu * 0.4 + fv * 1.5
    _st_bar(mb, [q - Z * 0.4, q + Z * 0.55 + fv * 0.15, q + Z * 0.8 + fv * 0.15 - fu * 0.6])
    _rock(mb, px + 12.3, 90.4, T, 1.1, 0.65, D(20), 0.3, r, k=4, elong=1.1)
