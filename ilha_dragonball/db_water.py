# db_water - AGUA da Ilha 2 (Dragon Ball): agua MODERADA (poucas quedas, canais coerentes).
#   POCO SW e POCO SE (chao GROUND): lamina em GROUND-0,8 (leito de colisao do db_col em GROUND-1,6), borda de
#       cantaria irregular (falhas com pedra baixa) + massas de rocha na boca do canal, canal de 4,8 (a mesma faixa do
#       db_col.water_polys) ate o LABIO na borda da ilha (o terreno deixa o entalhe) -> QUEDA LARGA que sai do labio e
#       cai LIVRE (o avanco nunca diminui: so cresce onde a rocha avanca, raios BVH nas malhas DB_Ter_* da cena), abre
#       de 5,4 no labio para ~11 a 14 studs abaixo e ~19 no pe; bate numa LAJE saliente (DB_Water_, sem colisao, fora
#       de alcance) uns 30 abaixo do labio (degrau com espuma, como na concept) e termina numa SAIA de espuma/nevoa
#       no pe (-60): o export nao leva as nuvens, entao o pe nunca fica cortado no ar.
#   POCO NW (terraco da vila, HUB-0,8) com CASCATA da mesa NW em 3 degraus que mudam de rumo (zigue-zague):
#       bica do terreno (L.CASCADE_NW_TOP, 70) -> rocha A (coluna no bolsao entre a mesa e o muro do terraco, fora da
#       guarda, com um bloco de topo em balanco sobre o guarda-corpo, topo 47,5) -> rocha B (dentro do terraco,
#       entre a borda e o poco, topo PLANO 36,4) -> poco. Cada cortina: estreita no labio, larga no pe, crista em
#       tufos de espuma de tamanhos diferentes, corpo azul (Water_DB) com fios claros (Water_Fall) e riscos (Foam).
# COLISAO: so das rochas desta zona, AJUSTADA ao visual: a secao de cada rocha e medida por raios (72 angulos x 6
#   cotas) e as caixas sao encaixadas DENTRO dela (nada de parede invisivel); o topo da caixa sai do topo medido da
#   rocha (-0,05). O leito dos pocos e do db_col. Pedras sem colisao so fora de alcance (atras da guarda de 4,6 da
#   borda da ilha ou abaixo do labio) ou rentes ao piso (<= piso + 0,3, como a cantaria).
# Materiais: Water_DB, Water_Fall, Foam + paleta de rocha/cantaria (nenhum material novo). Sem luz.
import math, random
import numpy as np
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import db_lib as DL
from db_lib import MB, FP, col_box
import db_layout as L
import fm_lib
import fm_water_kit as WK

C = "07_WATER"
WATER, FALL, FOAM = "Water_DB", "Water_Fall", "Foam"
ROCK, DARK, TOP = "Cliff_Rock_DB", "Cliff_Rock_DB_Dark", "Cliff_Rock_DB_Top"
BLOCK = "Stone_DB_Block"
G, HB = L.GROUND, L.HUB
ZW_G = G - L.WATER_DROP          # 23,4: lamina dos pocos do chao
ZW_H = HB - L.WATER_DROP         # 27,4: lamina do poco da vila
BED = 1.6                        # leito de colisao (db_col.floors): piso - 1,6
CH_HW = 2.4                      # meia-largura do canal (db_col.water_polys)
Z_END = -60.0                    # pe das quedas (nuvens / nevoa do jogo nos FX_Fall_*_Base)
COPE = 0.28                      # topo da cantaria acima do piso (anda por cima; >= 0,15 acima da grama do terreno)
RIM_GUARD = 4.6                  # profundidade da guarda invisivel da borda da ilha (db_col.rim_guard)
COL_AREA = "DB_WaterRock"
DEBUG = False
STATS = []                       # (nome, gap_max, gap_medio, topo_col, topo_vis_min, topo_vis_max) quando DEBUG
FEET = {}                        # pes medidos das quedas (para os FX_Fall_*_Base do db_core)

# cameras de revisao (loc, alvo, lente): cada queda do chao e de fora da ilha e das plataformas satelite, os pocos
# na altura do jogador, a cascata NW de frente, de lado, de cima e de tras
CAMS = {
    "CAM_DBWater_FallSW_Out": ((-150.0, -196.0, 2.0), (-96.0, -118.0, -16.0), 24),
    "CAM_DBWater_FallSE_Out": ((150.0, -186.0, 0.0), (90.0, -106.0, -18.0), 24),
    "CAM_DBWater_FallSW_Ground": ((-86.3, -105.0, G + 5.2), (-96.8, -118.8, G - 8.0), 22),
    "CAM_DBWater_FallSE_Ground": ((86.7, -90.5, G + 5.2), (90.4, -107.5, G - 8.0), 22),
    "CAM_DBWater_FallSW_Bridge": ((-7.0, -152.0, L.DECK + 5.2), (-96.0, -118.0, -8.0), 22),
    "CAM_DBWater_FallSE_Bridge": ((7.0, -152.0, L.DECK + 5.2), (90.0, -106.0, -8.0), 22),
    "CAM_DBWater_FallSE_Pad": ((131.5, -80.5, G + 5.2), (91.0, -107.0, -4.0), 24),
    "CAM_DBWater_PoolSW_Player": ((-66.0, -72.0, G + 5.2), (-86.0, -96.0, G), 22),
    "CAM_DBWater_PoolSE_Player": ((96.0, -68.0, G + 5.2), (80.0, -92.0, G), 22),
    "CAM_DBWater_NW_Player": ((-86.0, 100.0, HB + 5.2), (-124.0, 108.0, 44.0), 22),
    "CAM_DBWater_NW_Pool": ((-100.0, 121.0, HB + 5.2), (-116.0, 104.0, 32.0), 20),
    "CAM_DBWater_NW_South": ((-102.0, 86.0, HB + 5.2), (-122.0, 108.0, 36.0), 22),
    "CAM_DBWater_NW_Top": ((-70.0, 80.0, 74.0), (-124.0, 108.0, 46.0), 22),
    "CAM_DBWater_NW_Back": ((-136.0, 80.0, G + 5.2), (-124.0, 108.0, 42.0), 20),
}
# rota da margem norte do poco NW (a rocha B e as pedras da borda nao fecham a passagem entre a barraca oeste do
# mercado e o pe da mesa)
EXTRA_ROUTES = {"NW_margem_norte": ([(-101.0, 119.5), (-110.0, 118.8), (-118.0, 118.5), (-126.0, 121.0)], HB)}
# sondas: o canal perto do labio encosta na guarda invisivel da borda (ninguem sai pela queda)
EXTRA_PROBES = []


def _probe_list():
    out = []
    for nm, (px, py, pr), f in (("SW", L.POOL_SW, L.FALL_SW), ("SE", L.POOL_SE, L.FALL_SE)):
        d = math.hypot(f[0] - px, f[1] - py)
        ux, uy = (f[0] - px) / d, (f[1] - py) / d
        t = lip_t(px, py, ux, uy)
        q = (px + ux * (t - 5.5), py + uy * (t - 5.5))
        out.append(("AGUA_%s_canal_labio" % nm, q[0], q[1], G - BED, ux, uy))
    return out


# ------------------------------------------------------------------ geometria da planta
RIM_CL = list(L.ISLAND_RIM) + [L.ISLAND_RIM[0]]


def lip_t(px, py, ux, uy):
    """distancia do centro do poco ate a borda da ilha ao longo do canal"""
    t = 0.0
    while t < 80.0 and L.point_in_poly(px + ux * t, py + uy * t, L.ISLAND_RIM):
        t += 0.05
    return t


def rim_depth(x, y):
    """quanto (x, y) esta para dentro da borda da ilha (negativo = fora)"""
    d = L.polyline_dist(x, y, RIM_CL)
    return d if L.point_in_poly(x, y, L.ISLAND_RIM) else -d


def pool_poly(px, py, pr, ux, uy, hw, t_end, extra=0.0, n=30):
    """circulo do poco + faixa do canal (meia-largura hw ate t_end ao longo de (ux, uy)), anti-horario"""
    R = pr + extra
    H = hw + extra
    ang = math.atan2(uy, ux)
    dd = math.asin(min(0.98, H / R))
    a0, a1 = ang + dd, ang - dd + math.tau
    pts = [(px + R * math.cos(a0 + (a1 - a0) * i / n), py + R * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]
    sx, sy = -uy, ux
    pts.append((px + ux * t_end - sx * H, py + uy * t_end - sy * H))
    pts.append((px + ux * t_end + sx * H, py + uy * t_end + sy * H))
    return pts


# ------------------------------------------------------------------ raios contra o terreno
class Face:
    """BVH das malhas DB_Ter_* (poligonos a menos de R de (cx, cy)) + BVHs extras (as rochas desta zona)"""

    def __init__(self, cx, cy, R, prefix=("DB_Ter_",)):
        verts, polys = [], []
        for o in bpy.data.objects:
            if o.type != "MESH" or not o.name.startswith(prefix):
                continue
            me = o.data
            nv, npoly = len(me.vertices), len(me.polygons)
            if not nv or not npoly:
                continue
            co = np.empty(nv * 3, dtype=np.float64)
            me.vertices.foreach_get("co", co)
            co = co.reshape(nv, 3)
            M = np.array(o.matrix_world)
            co = co @ M[:3, :3].T + M[:3, 3]
            ls = np.empty(npoly, dtype=np.int64)
            lt = np.empty(npoly, dtype=np.int64)
            me.polygons.foreach_get("loop_start", ls)
            me.polygons.foreach_get("loop_total", lt)
            vi = np.empty(len(me.loops), dtype=np.int64)
            me.loops.foreach_get("vertex_index", vi)
            dl = np.hypot(co[vi, 0] - cx, co[vi, 1] - cy)
            mind = np.minimum.reduceat(dl, ls)
            for i in np.nonzero(mind < R)[0]:
                idx = vi[ls[i]:ls[i] + lt[i]]
                base = len(verts)
                verts.extend(Vector(co[k]) for k in idx)
                polys.append(list(range(base, base + len(idx))))
        self.trees = [BVHTree.FromPolygons(verts, polys)] if polys else []
        self.npolys = len(polys)

    def add_bmesh(self, bm):
        self.trees.append(BVHTree.FromBMesh(bm))

    def ray(self, org, d, dist):
        best = None
        for t in self.trees:
            h = t.ray_cast(org, d, dist)
            if h[0] is not None and (best is None or h[3] < best):
                best = h[3]
        return best

    def out(self, c, o, s, lat, z, reach=40.0):
        """avanco (ao longo de o, a partir de c) da primeira superficie vista de FORA na linha lateral lat, cota z"""
        org = Vector((c.x + o.x * reach + s.x * lat, c.y + o.y * reach + s.y * lat, z))
        h = self.ray(org, Vector((-o.x, -o.y, 0.0)), reach * 2.0)
        return None if h is None else reach - h

    def down(self, x, y, z0, dist=80.0):
        h = self.ray(Vector((x, y, z0)), Vector((0.0, 0.0, -1.0)), dist)
        return None if h is None else z0 - h


# ------------------------------------------------------------------ cortina d'agua
ARC_K = 0.11                     # flecha do arco da secao da cortina / largura (convexa para fora)
ARC_N = 6                        # segmentos do arco


def sheet(mb, pts, widths, side, m, k=ARC_K, thick=0.4, fwd=None):
    """lamina varrida por pts com secao em ARCO (flecha k * largura para fora, espessura 'thick'): de frente
    sombreia macio (sem quina no meio), de lado ainda tem volume"""
    bm = mb.bm
    side = Vector(side).normalized()
    rings = []
    n = len(pts)
    for i, p in enumerate(pts):
        p = Vector(p)
        t = (Vector(pts[min(n - 1, i + 1)]) - Vector(pts[max(0, i - 1)]))
        t = t.normalized() if t.length > 1e-9 else Vector((0, 0, -1))
        f = Vector(fwd).normalized() if fwd is not None else t.cross(side)
        f = f.normalized() if f.length > 1e-6 else Vector((0, 0, 1))
        w = widths[i]
        D = k * w
        prof = []
        for j in range(ARC_N + 1):
            x = -0.5 + j / ARC_N
            prof.append((x * w, D * (1.0 - 4.0 * x * x)))
        for j in range(ARC_N, -1, -1):
            x = -0.5 + j / ARC_N
            prof.append((x * w * 0.96, D * (1.0 - 4.0 * x * x) - thick))
        rings.append([bm.verts.new(p + side * a + f * b) for a, b in prof])
    kk = len(rings[0])
    for r0, r1 in zip(rings, rings[1:]):
        for j in range(kk):
            j2 = (j + 1) % kk
            try:
                bm.faces.new((r0[j], r0[j2], r1[j2], r1[j]))
            except ValueError:
                pass
    for cap in (list(reversed(rings[0])), rings[-1]):
        try:
            bm.faces.new(cap)
        except ValueError:
            pass
    return mb._post([v for r in rings for v in r], m, None, 0, 1)


def arc_off(u, k=ARC_K):
    """avanco da frente do arco na fracao lateral u (-0,5..0,5), em fracoes da largura"""
    u = max(-0.5, min(0.5, u))
    return k * (1.0 - 4.0 * u * u)


class Curtain:
    """cortina que sai de uma crista c (Vector 3D) para fora (o, horizontal) e cai ate z_bot.
    Largura wprof = (no labio, depois de abrir, altura da abertura, no pe): estreita no labio, abre rapido e continua
    abrindo ate o pe. Perfil (avanco x cota): parabola curta no labio + deriva para fora; o avanco NUNCA diminui (a
    agua cai livre, nao volta para a rocha); onde a rocha (raios) avanca alem do jato, a agua passa por fora com folga
    'clear'; saliencia > 1,6 = degrau (espuma na quebra). land=True: para no primeiro topo de rocha que encontra."""

    def __init__(self, F, c, o, z_bot, wprof, lip=1.4, clear=1.0, dz=1.0, drift=0.0, land=False, name="",
                 max_jump=8.0, face_stop=-1e9):
        self.c = Vector(c)
        self.o = Vector((o[0], o[1], 0.0)).normalized()
        self.s = Vector((-self.o.y, self.o.x, 0.0))
        self.z_top, self.z_bot = self.c.z, z_bot
        self.wprof = wprof
        self.H = max(1.0, self.z_top - z_bot)
        self.name = name
        self.crest_back = 0.7        # a espuma do labio comeca 0,7 antes da borda (0,3 no topo de uma rocha)
        self.breaks = []             # (z, adv_antes, adv_depois)
        self.landed = None
        keys = [(self.z_top, 0.0)]
        adv = 0.0
        z = self.z_top
        while z > z_bot + 1e-6:
            zp = z
            z = max(z_bot, z - dz)
            drop = self.z_top - z
            free = lip * math.sqrt(min(drop, 3.0) / 3.0) + drift * max(0.0, drop - 3.0)
            cur = max(adv, free)
            w = self.width(z)
            fs = []
            if F is not None and z > face_stop:
                for u in (-0.5, -0.3, -0.1, 0.1, 0.3, 0.5):
                    f = F.out(self.c, self.o, self.s, u * w, z)
                    if f is not None and -30.0 < f < cur + max_jump:
                        fs.append(f)
            face = max(fs) if fs else None
            need = face + clear if face is not None else -1e9
            if land and F is not None and drop > 1.5:
                q = self.c + self.o * cur
                zt = F.down(q.x, q.y, zp + 0.5, dz + 3.0)
                if zt is not None and zt > z - 0.05:
                    self.landed = (Vector((q.x, q.y, zt)), cur)
                    keys.append((zt + 0.15, cur))
                    break
            if need > cur + 1.6:
                q = self.c + self.o * cur
                zt = F.down(q.x, q.y, zp + 0.2, dz + 2.0)
                zl = zt if (zt is not None and z - 0.5 < zt <= zp + 0.2) else zp - 0.3
                self.breaks.append((zl, cur, need))
                keys.append((zl + 0.35, cur))
                keys.append((zl + 0.15, cur + (need - cur) * 0.55))
                cur = need
            elif need > cur:
                cur = need
            adv = cur
            keys.append((z, adv))
        self.keys = self._simplify(keys)
        if self.landed is not None:
            self.z_bot = self.keys[-1][0]

    @staticmethod
    def _simplify(keys, tol=0.12):
        """Douglas-Peucker no perfil (avanco em funcao da cota): poucos pontos nos trechos retos"""
        if len(keys) < 3:
            return keys

        def rec(a, b):
            (za, xa), (zb, xb) = keys[a], keys[b]
            best, bi = 0.0, None
            for i in range(a + 1, b):
                zi, xi = keys[i]
                t = (za - zi) / (za - zb) if za != zb else 0.0
                d = abs(xi - (xa + (xb - xa) * t))
                if d > best:
                    best, bi = d, i
            if bi is not None and best > tol:
                return rec(a, bi)[:-1] + rec(bi, b)
            return [keys[a], keys[b]]
        out = rec(0, len(keys) - 1)
        # no maximo 8 de cota entre pontos (a largura muda ao longo da queda)
        res = [out[0]]
        for k1 in out[1:]:
            k0 = res[-1]
            n = int((k0[0] - k1[0]) / 8.0)
            for i in range(1, n + 1):
                t = i / (n + 1)
                res.append((k0[0] + (k1[0] - k0[0]) * t, k0[1] + (k1[1] - k0[1]) * t))
            res.append(k1)
        return res

    def width(self, z):
        w0, w1, fh, w2 = self.wprof
        drop = max(0.0, self.z_top - z)
        if drop <= fh:
            t = drop / max(0.1, fh)
            return w0 + (w1 - w0) * (1.0 - (1.0 - t) ** 2)
        t = min(1.0, (drop - fh) / max(1.0, self.H - fh))
        return w1 + (w2 - w1) * t

    def wob(self, z):
        """meandro lateral suave (a cortina nao desce como regua); zero no labio"""
        k = min(1.0, (self.z_top - z) / 6.0)
        ph = (sum(map(ord, self.name)) % 97) * 0.37
        return 0.05 * self.width(z) * k * math.sin(z * 0.17 + ph)

    def path(self, u=0.0):
        """pontos (Vector) e larguras do eixo da lamina na fracao lateral u"""
        pts = [self.c + self.o * a + self.s * (u * self.width(z) + self.wob(z)) + Vector((0, 0, z - self.c.z))
               for z, a in self.keys]
        return pts, [self.width(z) for z, a in self.keys]

    def build(self, mb, rng, nb=None, ns=None, crest=True, k=ARC_K):
        """corpo azul (Water_DB, secao em ARCO: de frente sombreia macio, de lado ainda tem volume) + 3-5 fios claros
        (Water_Fall) que comecam e terminam em alturas diferentes, com o azul aparecendo entre eles + riscos finos de
        espuma (Foam) + crista em tufos de espuma e espuma nas quebras. Camadas separadas >= 0,1 (Roblox)."""
        pts, ws = self.path()
        if len(pts) < 2:
            return
        self.k = k
        b = k * self.wprof[0]
        self.b = b
        sheet(mb, pts, ws, self.s, WATER, k=k, thick=0.4)
        H = self.z_top - self.z_bot

        def spread(k, lo, hi):
            """k posicoes laterais em ordem, com sorteio grande dentro de cada vao (nada de listra de toldo)"""
            sp = (hi - lo) / k
            return [lo + sp * (i + 0.5) + rng.uniform(-0.38, 0.38) * sp for i in range(k)]
        # fios claros (Water_Fall): larguras diferentes, derivam de lado ao descer, afinam nas pontas, comecam e
        # terminam em alturas diferentes (o azul do corpo aparece entre eles)
        nb = nb or max(3, min(5, int(self.wprof[1] / 2.3)))
        for u in spread(nb, -0.42, 0.42):
            z0 = self.z_top - (0.3 if rng.random() < 0.5 else rng.uniform(0.8, 0.2 * H + 0.8))
            z1 = self.z_bot + (0.15 if rng.random() < 0.55 else rng.uniform(0.1, 0.3) * H)
            if z0 - z1 < 1.0:
                continue
            fw = rng.choice((rng.uniform(0.06, 0.09), rng.uniform(0.11, 0.17)))
            u1 = max(-0.44, min(0.44, u + rng.uniform(-0.07, 0.07)))
            self._strip(mb, u, fw, z0, z1, 0.1, FALL, 0.12, u1=u1)
        # riscos de espuma: finos, curtos e soltos (brilho da agua que acelera)
        ns = ns if ns is not None else max(3, int(self.wprof[1] / 2.2))
        for u in spread(ns, -0.44, 0.44):
            z0 = self.z_top - rng.uniform(0.6, 0.55 * H + 0.6)
            z1 = max(self.z_bot + 0.3, z0 - rng.uniform(0.15, 0.45) * (z0 - self.z_bot))
            if z0 - z1 < 0.8:
                continue
            self._strip(mb, u, None, z0, z1, 0.26, FOAM, 0.1, wabs=rng.uniform(0.18, 0.34),
                        u1=u + rng.uniform(-0.04, 0.04))
        if crest:
            self.crest_foam(mb, rng, b)
        for zl, a0, a1 in self.breaks:
            self.break_foam(mb, rng, zl, a0, a1, b)

    def _strip(self, mb, u, fw, z0, z1, off, m, thick, wabs=None, u1=None):
        """fita chata na frente da lamina de z0 a z1 (acompanha o arco: 'off' acima da frente dele, inclinada como
        ele): fracao lateral u -> u1, largura fw * largura da queda (ou wabs), afinada nas duas pontas"""
        u1 = u if u1 is None else u1
        kk = getattr(self, "k", ARC_K)
        um = 0.5 * (u + u1)
        side = (self.s - self.o * (8.0 * kk * um)).normalized()
        span = z0 - z1
        zz = sorted({z for z, a in self.keys if z1 + 1e-6 < z < z0 - 1e-6} |
                    {z0, z1, z0 - 0.12 * span, z1 + 0.15 * span}, reverse=True)
        ks = [(z, self.adv(z)) for z in zz]
        if len(ks) < 2:
            return
        pts, ws = [], []
        full = [self.c + self.o * a + Vector((0, 0, z - self.c.z)) for z, a in ks]
        for i, (z, a) in enumerate(ks):
            p0, p1 = full[max(0, i - 1)], full[min(len(full) - 1, i + 1)]
            t = (p1 - p0)
            t = t.normalized() if t.length > 1e-6 else Vector((0, 0, -1))
            f = t.cross(self.s)
            f = f.normalized() if f.length > 1e-6 else self.o
            w = self.width(z)
            tt = (z0 - z) / max(1e-6, span)
            uu = u + (u1 - u) * tt
            k = min(1.0, 0.55 + tt / 0.12 * 0.45) * (1.0 - 0.45 * max(0.0, (tt - 0.85) / 0.15))
            pts.append(full[i] + self.s * (uu * w + self.wob(z)) + f * (arc_off(uu, kk) * w + off))
            base = wabs * (1.0 + 0.6 * tt) if wabs else max(0.3, fw * w)
            ws.append(max(0.12, base * k))
        WK.ribbon(mb, pts, ws, m, side, thick=thick, flat=True)

    def adv(self, z):
        K = self.keys
        if z >= K[0][0]:
            return K[0][1]
        for (z0, a0), (z1, a1) in zip(K, K[1:]):
            if z1 <= z <= z0:
                return a0 + (a1 - a0) * ((z0 - z) / (z0 - z1) if z0 > z1 else 0.0)
        return K[-1][1]

    def crest_foam(self, mb, rng, b):
        """crista: a agua rola por cima da borda em 2-3 linguas de espuma de larguras diferentes (com vao entre elas)
        + tufos de espuma de tamanhos diferentes ao longo do labio (nada de barra reta)"""
        c, o, s = self.c, self.o, self.s
        w = self.wprof[0]
        k = 2 if w < 6.0 else 3
        cuts = sorted(rng.uniform(-0.5, 0.5) * 0.5 + (-0.5 + (i + 1) / k) * 0.5 for i in range(k - 1))
        edges = [-0.5] + cuts + [0.5]
        for i in range(k):
            ua, ub = edges[i] + 0.04, edges[i + 1] - 0.04
            if ub - ua < 0.12:
                continue
            u = (ua + ub) / 2
            wi = (ub - ua) * w
            z1 = self.z_top - rng.uniform(0.8, 1.4)
            pts = [c - o * self.crest_back + s * (u * w) + Vector((0, 0, 0.12)),
                   c + o * (b * 0.4 + 0.3) + s * (u * w) + Vector((0, 0, -0.12)),
                   c + o * (self.adv(z1) + b + 0.45) + s * (u * self.width(z1) + self.wob(z1)) +
                   Vector((0, 0, z1 - c.z))]
            WK.ribbon(mb, pts, [wi * 0.95, wi, wi * rng.uniform(0.6, 0.8)], FOAM, s, thick=0.2, bulge=0.22)
        n = 3 + int(w / 2.2)
        sc = max(0.6, (w / 5.0) ** 0.5)
        for i in range(n):
            u = -0.5 + (i + 0.5) / n + rng.uniform(-0.06, 0.06)
            r = rng.uniform(0.32, 0.72) * sc
            q = c + o * rng.uniform(0.0, 0.5) + s * (u * w)
            mb.ico(r, (q.x, q.y, c.z + r * 0.15), FOAM, 1, (rng.uniform(1.3, 1.8), rng.uniform(1.0, 1.3), 0.7),
                   (0, 0, rng.uniform(0, 3)), jitter=0.25)

    def break_foam(self, mb, rng, zl, a0, a1, b):
        """a agua bate na saliencia: espuma que rola do pe da queda de cima ate a borda do degrau e desce um pouco,
        com tufos soltos de tamanhos diferentes"""
        c, o, s = self.c, self.o, self.s
        w = self.width(zl)
        # lingua de espuma mais estreita que a lamina (rola por cima do degrau) + tufos de tamanhos bem diferentes que
        # passam das bordas (respingo), alguns logo abaixo da quina
        pts = [c + o * (a0 - 0.2) + Vector((0, 0, zl + 1.0 - c.z)), c + o * (a0 + 0.3) + Vector((0, 0, zl + 0.3 - c.z)),
               c + o * ((a0 + a1) * 0.5 + 0.4) + Vector((0, 0, zl + 0.25 - c.z)),
               c + o * (a1 + b + 0.45) + Vector((0, 0, zl - 1.4 - c.z))]
        WK.ribbon(mb, pts, [w * 0.7, w * 0.82, w * 0.8, w * 0.62], FOAM, s, thick=0.3, bulge=0.4)
        n = 5 + int(w / 2.5)
        for k in range(n):
            u = -0.56 + 1.12 * (k + 0.5) / n + rng.uniform(-0.05, 0.05)
            big = rng.random() < 0.4
            r = max(0.45, w * (rng.uniform(0.09, 0.14) if big else rng.uniform(0.04, 0.08)))
            q = c + o * (a0 + rng.uniform(0.0, max(0.4, a1 - a0) + 0.6)) + s * (u * w)
            mb.ico(r, (q.x, q.y, zl + r * rng.uniform(0.2, 0.6)), FOAM, 1, (1.4, 1.2, rng.uniform(0.7, 1.0)),
                   (0, 0, rng.uniform(0, 3)), jitter=0.24)
        for k in range(3):
            u = rng.uniform(-0.35, 0.35)
            r = max(0.5, w * rng.uniform(0.06, 0.1))
            q = c + o * (a1 + b + rng.uniform(0.6, 1.2)) + s * (u * w)
            mb.ico(r, (q.x, q.y, zl - rng.uniform(1.5, 3.0)), FOAM, 1, (1.2, 1.0, 1.3), (0, 0, rng.uniform(0, 3)),
                   jitter=0.24)

    def foot(self):
        a = self.keys[-1][1]
        return self.c + self.o * a + Vector((0, 0, self.z_bot - self.c.z))


def foot_skirt(mb, rng, cur, n=13):
    """pe de uma queda no vazio: saia de espuma/nevoa ~1,3x a largura do pe, empilhada alguns studs (a lamina termina
    dentro dela: sem borda cortada mesmo sem as nuvens do render)"""
    ft = cur.foot()
    W = cur.width(cur.z_bot)
    sc = (W / 18.0) ** 0.5
    for i in range(n):
        u = -0.66 + 1.32 * (i + 0.5) / n + rng.uniform(-0.03, 0.03)
        r = rng.uniform(2.6, 4.2) * sc * (1.0 - 0.35 * abs(u))
        q = ft + cur.s * (u * W) + cur.o * rng.uniform(-1.0, 2.2)
        zc = cur.z_bot + rng.uniform(-2.0, 1.2) - abs(u) * 2.5
        mb.ico(r, (q.x, q.y, zc), FOAM, 1, (1.35, 1.15, 0.85), (0, 0, rng.uniform(0, 3)), jitter=0.22)
    for i in range(5):
        u = -0.32 + 0.64 * (i + 0.5) / 5 + rng.uniform(-0.04, 0.04)
        r = rng.uniform(2.0, 2.9) * sc
        q = ft + cur.s * (u * W) + cur.o * rng.uniform(0.3, 1.6)
        mb.ico(r, (q.x, q.y, cur.z_bot + rng.uniform(3.0, 5.5)), FOAM, 1, (1.25, 1.0, 1.05),
               (0, 0, rng.uniform(0, 3)), jitter=0.22)


def foam_patch(mb, rng, c, r, z, n=6, s=0.9, disc=True):
    """pe de uma queda num poco / na laje: disco de espuma + bolhas achatadas + borrifo em pe"""
    if disc:
        mb.cyl(r * 0.85, 0.3, (c.x, c.y, z + 0.08), (0, 0, rng.uniform(0, 1)), FOAM, 10, bevel=0.0)
    a0 = rng.uniform(0, math.tau)
    for i in range(n):
        a = a0 + i * math.tau / n + rng.uniform(-0.3, 0.3)
        rr = r * rng.uniform(0.75, 1.1)
        k = s * rng.uniform(0.6, 1.2)
        mb.ico(k, (c.x + math.cos(a) * rr, c.y + math.sin(a) * rr, z + k * 0.1), FOAM, 1,
               (rng.uniform(1.2, 1.7), rng.uniform(1.0, 1.4), 0.34), (0, 0, rng.uniform(0, 3)), jitter=0.2)
    for k in range(2):
        rr = max(0.6, r * rng.uniform(0.26, 0.36))
        mb.ico(rr, (c.x + rng.uniform(-0.3, 0.3) * r, c.y + rng.uniform(-0.3, 0.3) * r, z + rr * 0.35), FOAM, 1,
               (1.3, 1.15, 0.8), (0, 0, rng.uniform(0, 3)), jitter=0.2)


def flecks(mb, rng, c, z, n, r0, r1, a_mid, spread, lengths=(1.4, 2.4)):
    """riscos de espuma DEITADOS na lamina (fita chata afilada, 0,06 de espessura, topo <= lamina + 0,08)"""
    for k in range(n):
        a = a_mid + rng.uniform(-spread, spread)
        r = rng.uniform(r0, r1)
        q = Vector((c.x + math.cos(a) * r, c.y + math.sin(a) * r, z + 0.07))
        t = Vector((-math.sin(a), math.cos(a), 0.0)) * (rng.uniform(*lengths) * 0.5)
        side = Vector((math.cos(a), math.sin(a), 0.0))
        w = rng.uniform(0.26, 0.4)
        WK.ribbon(mb, [q - t, q, q + t], [0.06, w, 0.06], FOAM, side, thick=0.06, flat=True, fwd=(0, 0, 1))


def streaks(mb, rng, a, b, z, n, lat):
    """correnteza: fitas finas afiladas deitadas na lamina ao longo do fluxo de a para b (topo <= lamina + 0,08)"""
    d = (b - a)
    d.z = 0.0
    L_ = d.length
    d.normalize()
    s = Vector((-d.y, d.x, 0.0))
    for k in range(n):
        t = L_ * (0.2 + 0.65 * (k + 0.5) / n) + rng.uniform(-0.6, 0.6)
        q = a + d * t + s * (lat[k % len(lat)] + rng.uniform(-0.25, 0.25))
        q.z = z + 0.07
        h = d * (rng.uniform(2.4, 3.6) * 0.5)
        WK.ribbon(mb, [q - h, q - h * 0.3, q + h], [0.04, rng.uniform(0.14, 0.2), 0.04], FOAM, s, thick=0.06,
                  flat=True, fwd=(0, 0, 1))


# ------------------------------------------------------------------ rocha + colisao ajustada ao visual
def rpoly(rng, a, b, rot, n=8, ex=2.4, jit=0.08):
    """contorno de rocha (superelipse facetada de fm_parts) girado 'rot' (coords relativas ao centro)"""
    ca, sa = math.cos(rot), math.sin(rot)
    return [(x * ca - y * sa, x * sa + y * ca) for x, y in FP._rock_poly(a, b, n, rng, ex=ex, jit=jit)]


def column(mb, rng, c, poly, z0, z1, m=ROCK, taper=0.92, band=1.0, lean=None, slope=None, rings=None,
           jitter=0.04, bottom=False, top_m=None, chamfer=0.3):
    """coluna de rocha facetada (fm_parts.rock_column: a mesma linguagem das rochas do terreno)"""
    FP.rock_column(mb, Vector((c[0], c[1], 0.0)), poly, z0, z1, rng, m, taper=taper,
                   rings=rings or (2 if z1 - z0 > 6 else 1), jitter=jitter, tilt=0.04, lean=lean, chamfer=chamfer,
                   rim=False, band=(band, TOP) if band else None, bottom=bottom, slope=slope, top_m=top_m, lip=0.5)


class Piece:
    """marca as faces que uma peca acrescenta ao bmesh do MB (para medir a secao so dela)"""

    def __init__(self, mb):
        self.mb = mb
        self.f0 = len(mb.bm.faces)
        self.f1 = None

    def close(self):
        self.f1 = len(self.mb.bm.faces)
        return self

    def bvh(self):
        bm = self.mb.bm
        bm.faces.ensure_lookup_table()
        vs, ps = [], []
        for i in range(self.f0, self.f1 if self.f1 is not None else len(bm.faces)):
            f = bm.faces[i]
            b = len(vs)
            vs.extend(v.co.copy() for v in f.verts)
            ps.append(list(range(b, b + len(f.verts))))
        return BVHTree.FromPolygons(vs, ps)


NA = 72


def _r_at(rs, th):
    x = (th % math.tau) / math.tau * NA
    i = int(x) % NA
    f = x - int(x)
    return rs[i] * (1.0 - f) + rs[(i + 1) % NA] * f


def _rect_pts(cx, cy, hx, hy, ca, sa, k=5):
    pts = []
    for i in range(k + 1):
        t = -1.0 + 2.0 * i / k
        for lx, ly in ((t * hx, hy), (t * hx, -hy), (hx, t * hy), (-hx, t * hy)):
            pts.append((cx + lx * ca - ly * sa, cy + lx * sa + ly * ca))
    return pts


def _fits(rs, c, pts, tol):
    for x, y in pts:
        dx, dy = x - c[0], y - c[1]
        r = math.hypot(dx, dy)
        if r > 1e-6 and r > _r_at(rs, math.atan2(dy, dx)) - tol:
            return False
    return True


def _exit_t(cx, cy, hx, hy, ca, sa, ox, oy, dx, dy):
    """distancia do ponto (ox, oy) ate a saida da caixa na direcao (dx, dy) (0 se o ponto esta fora dela)"""
    lx0 = (ox - cx) * ca + (oy - cy) * sa
    ly0 = -(ox - cx) * sa + (oy - cy) * ca
    if abs(lx0) > hx + 1e-6 or abs(ly0) > hy + 1e-6:
        return 0.0
    ldx = dx * ca + dy * sa
    ldy = -dx * sa + dy * ca
    t = 1e9
    if abs(ldx) > 1e-9:
        t = min(t, ((hx if ldx > 0 else -hx) - lx0) / ldx)
    if abs(ldy) > 1e-9:
        t = min(t, ((hy if ldy > 0 else -hy) - ly0) / ldy)
    return t


def fit_col(mb, piece, c, rot, zb, zt, band=None, nbox=2, top="vis", name="", tol=0.06, offs=0.35):
    """colisao da peca (faces desde piece.f0): mede a secao por raios a partir de c (72 angulos, 6 cotas da faixa
    'band' onde o jogador encosta; padrao zb..zt), encaixa 1-2 caixas (cruz) DENTRO da menor secao e poe o topo no
    topo medido da rocha (top='vis') ou na cota dada. Retorna as caixas [(cx, cy, hx, hy)]."""
    pieces = piece if isinstance(piece, (list, tuple)) else [piece]
    bvhs = [p.bvh() for p in pieces]
    lo, hi = band if band else (zb + 0.2, zt - 0.4)
    zs = [lo + (hi - lo) * k / 5.0 for k in range(6)]
    rmin = [1e9] * NA
    rmax = [0.0] * NA

    def exit_r(bv, o_, d_):
        """distancia ate SAIR da peca ao longo do raio (pula entradas: faces com normal contra o raio)"""
        acc = 0.0
        org = o_.copy()
        for _ in range(4):
            h = bv.ray_cast(org, d_, 80.0)
            if h[0] is None:
                return None
            acc += h[3]
            if h[1].dot(d_) > 0.0:
                return acc
            org = h[0] + d_ * 0.01
            acc += 0.01
        return None
    for z in zs:
        rr = []
        for i in range(NA):
            th = i * math.tau / NA
            d_ = Vector((math.cos(th), math.sin(th), 0.0))
            best_r = None
            for bv in bvhs:
                r_ = exit_r(bv, Vector((c[0], c[1], z)), d_)
                if r_ is not None and (best_r is None or r_ > best_r):
                    best_r = r_
            rr.append(best_r)
        if sum(1 for r in rr if r is not None) < NA * 0.8:
            continue
        for i, r in enumerate(rr):
            r = 0.0 if r is None else r
            rmin[i] = min(rmin[i], r)
            rmax[i] = max(rmax[i], r)
    if rmin[0] > 1e8:
        print("WATER AVISO: secao vazia em", name)
        return []
    ca, sa = math.cos(rot), math.sin(rot)
    amax = max(rmin)
    best = None
    cand_off = [(0.0, 0.0)] + [(dx, dy) for dx in (-offs, 0.0, offs) for dy in (-offs, 0.0, offs) if dx or dy]
    for dx, dy in cand_off:
        cx, cy = c[0] + dx * ca - dy * sa, c[1] + dx * sa + dy * ca
        if not _fits(rmin, c, [(cx, cy)], tol + 0.3):
            continue

        def maxh(fixed, along_x):
            a_, b_ = 0.0, amax
            for _ in range(13):
                mid = (a_ + b_) / 2
                hx, hy = (fixed, mid) if along_x else (mid, fixed)
                if _fits(rmin, c, _rect_pts(cx, cy, hx, hy, ca, sa), tol):
                    a_ = mid
                else:
                    b_ = mid
            return a_
        cx_, cy_ = [], []
        for i in range(12):
            h = amax * (0.2 + 0.8 * i / 11)
            k = maxh(h, True)
            if k > 0.3:
                cx_.append((h, k))
            k = maxh(h, False)
            if k > 0.3:
                cy_.append((k, h))
        if nbox == 1:
            for hx, hy in cx_ + cy_:
                if best is None or hx * hy > best[0]:
                    best = (hx * hy, [(cx, cy, hx, hy)])
        elif nbox == 3:
            # cruz + caixa "quadrada" de maior area: cobre as quinas da superelipse (objetivo: alcance radial medio)
            if not cx_ or not cy_:
                continue
            b3 = max(cx_ + cy_, key=lambda t: t[0] * t[1])
            dirs = [(math.cos(i * math.tau / 36), math.sin(i * math.tau / 36)) for i in range(36)]
            r3 = [_exit_t(cx, cy, b3[0], b3[1], ca, sa, c[0], c[1], dx_, dy_) for dx_, dy_ in dirs]
            for hx1, hy1 in cx_:
                r1 = [_exit_t(cx, cy, hx1, hy1, ca, sa, c[0], c[1], dx_, dy_) for dx_, dy_ in dirs]
                for hx2, hy2 in cy_:
                    tot = 0.0
                    for k_, (dx_, dy_) in enumerate(dirs):
                        tot += max(r1[k_], r3[k_], _exit_t(cx, cy, hx2, hy2, ca, sa, c[0], c[1], dx_, dy_))
                    if best is None or tot > best[0]:
                        best = (tot, [(cx, cy, hx1, hy1), (cx, cy, hx2, hy2), (cx, cy, b3[0], b3[1])])
        else:
            for hx1, hy1 in cx_:
                for hx2, hy2 in cy_:
                    ar = hx1 * hy1 + hx2 * hy2 - min(hx1, hx2) * min(hy1, hy2)
                    if best is None or ar > best[0]:
                        best = (ar, [(cx, cy, hx1, hy1), (cx, cy, hx2, hy2)])
    if best is None:
        print("WATER AVISO: nenhuma caixa cabe em", name)
        return []
    boxes = []
    for bx in best[1]:
        if not any(o_ is not bx and o_[2] >= bx[2] - 1e-6 and o_[3] >= bx[3] - 1e-6 for o_ in boxes):
            boxes = [o_ for o_ in boxes if not (bx[2] >= o_[2] - 1e-6 and bx[3] >= o_[3] - 1e-6)] + [bx]
    # topo: medido na rocha (raio de cima) dentro das caixas (recuado 0,45 da borda: o chanfro fica de fora)
    if top == "vis":
        tv = []
        for cx, cy, hx, hy in boxes:
            for fx in (-1.0, -0.5, 0.0, 0.5, 1.0):
                for fy in (-1.0, -0.5, 0.0, 0.5, 1.0):
                    lx, ly = fx * max(0.0, hx - 0.45), fy * max(0.0, hy - 0.45)
                    x, y = cx + lx * ca - ly * sa, cy + lx * sa + ly * ca
                    zz_ = [h[0].z for h in (bv.ray_cast(Vector((x, y, zt + 20.0)), Vector((0, 0, -1)), 60.0)
                                            for bv in bvhs) if h[0] is not None]
                    if zz_:
                        tv.append(max(zz_))
        z_col = (min(tv) - 0.05) if tv else zt
        tv_lo, tv_hi = (min(tv), max(tv)) if tv else (zt, zt)
    else:
        z_col = float(top)
        tv_lo = tv_hi = z_col
    for cx, cy, hx, hy in boxes:
        col_box(COL_AREA, (2.0 * hx, 2.0 * hy, z_col - zb), (cx, cy, (zb + z_col) / 2.0), (0, 0, rot))
    if DEBUG:
        gaps = []
        for i in range(NA):
            th = i * math.tau / NA
            dx, dy = math.cos(th), math.sin(th)
            rc = max(_exit_t(cx, cy, hx, hy, ca, sa, c[0], c[1], dx, dy) for cx, cy, hx, hy in boxes)
            gaps.append(rmax[i] - rc)
        STATS.append((name, max(gaps), sum(gaps) / len(gaps), z_col, tv_lo, tv_hi))
    return boxes


# ------------------------------------------------------------------ pecas de pedra
def coping_run(mb, rng, pts, z_top, w=1.3, h=1.25, step=2.4, skip=None, closed=False, gap=0.1, stones=0.35):
    """cantaria da borda: blocos de arenito de comprimento/largura/giro variados ao longo da linha, com FALHAS
    (a grama do terreno aparece) e pedras baixas irregulares no lugar de alguns blocos (a borda nao vira anel de
    fonte). Topo z_top (piso + COPE)."""
    line = [Vector((p[0], p[1], 0.0)) for p in pts]
    if closed:
        line.append(line[0].copy())
    total = fm_lib.path_len(line)
    marks = [0.0]
    while marks[-1] < total - 0.8:
        marks.append(min(total, marks[-1] + step * rng.uniform(0.7, 1.3)))
    dense = fm_lib.resample(line, 0.25)
    cum = [0.0]
    for a, b in zip(dense, dense[1:]):
        cum.append(cum[-1] + (b - a).length)

    def at(s):
        for i in range(1, len(cum)):
            if cum[i] >= s:
                t = (s - cum[i - 1]) / max(1e-6, cum[i] - cum[i - 1])
                return dense[i - 1].lerp(dense[i], t)
        return dense[-1]
    n = 0
    for s0, s1 in zip(marks, marks[1:]):
        a, b = at(s0), at(s1)
        d = b - a
        if d.length < 0.6:
            continue
        cc = (a + b) / 2
        if skip and skip(cc):
            continue
        r = rng.random()
        if r < gap:
            continue
        ang = math.atan2(d.y, d.x)
        if r < gap + stones * 0.3:
            # pedra baixa irregular (rocha escura) no lugar do bloco
            mb.rock((cc.x, cc.y, z_top - 0.33), (d.length * rng.uniform(0.8, 1.05), w * rng.uniform(0.9, 1.25), 0.62),
                    DARK if rng.random() < 0.6 else ROCK, 1, (0, 0, ang + rng.uniform(-0.3, 0.3)), jitter=0.22)
            continue
        hh = h + rng.uniform(-0.1, 0.1)
        zt = z_top + rng.uniform(-0.03, 0.02)
        mb.box((d.length - rng.uniform(0.1, 0.3), w * rng.uniform(0.82, 1.15), hh),
               (cc.x, cc.y, zt - hh / 2), (0, 0, ang + rng.uniform(-0.1, 0.1)), BLOCK, 0.1)
        n += 1
    return n


def offset_circle(cx, cy, r, a0, a1, n):
    return [(cx + r * math.cos(a0 + (a1 - a0) * i / n), cy + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def rock_mass(mb, rng, c, a, b, zb, zt, rot, floor, out, name=""):
    """massa de rocha na borda de um poco: corpo principal facetado e afunilado (colisao ajustada, 2 caixas; topo
    quase plano, inclinacao <= 0,1) + laje escura RENTE ao chao encostada por fora (topo <= piso + 0,25: anda por
    cima, sem colisao propria) + seixo rente"""
    pc = Piece(mb)
    poly = rpoly(rng, a, b, rot, n=7, ex=2.2, jit=0.12)
    sl = (rng.uniform(-0.04, 0.04), rng.uniform(-0.04, 0.04))
    column(mb, rng, c, poly, zb, zt, m=ROCK, taper=0.88, band=0.9, slope=sl, rings=2, jitter=0.06, chamfer=0.32)
    fit_col(mb, pc, c, rot, zb, zt, band=(floor - 1.0, zt - 0.2), nbox=2, name=name)
    # laje rente ao chao (massa secundaria baixa) e seixo pequeno rente, os dois do lado de fora (grama)
    ox, oy = out
    q = (c[0] + ox * (a + 0.7) - oy * b * 0.7, c[1] + oy * (a + 0.7) + ox * b * 0.7)
    mb.rock((q[0], q[1], floor - 0.1), (a * 1.1, b * 1.0, 0.62), DARK, 1, (0, 0, rot + rng.uniform(0.3, 0.9)),
            jitter=0.2)
    q = (c[0] + ox * (a + 0.4) + oy * (b + 0.9), c[1] + oy * (a + 0.4) - ox * (b + 0.9))
    mb.rock((q[0], q[1], floor - 0.08), (1.2, 0.9, 0.55), ROCK, 1, (0, 0, rng.uniform(0, 3)), jitter=0.22)


def ledge(mb, rng, lip, o, s, z_top, a_back, a_front, hw):
    """laje saliente sob o labio (a queda bate nela: degrau com espuma). Visual, sem colisao: fica ~30 abaixo do
    labio, fora de qualquer alcance. Tampo largo + corpo pendurado que afina para baixo, encaixado na rocha molhada
    do entalhe"""
    ang = math.atan2(o.y, o.x)
    hl = (a_front - a_back) / 2.0
    ac = (a_front + a_back) / 2.0
    c = lip + o * ac
    column(mb, rng, (c.x, c.y), rpoly(rng, hl, hw, ang, n=9, ex=2.3, jit=0.08), z_top - 3.4, z_top, m=ROCK,
           taper=0.94, band=0.9, slope=(-o.x * 0.05, -o.y * 0.05), jitter=0.06, bottom=True, chamfer=0.4)
    c2 = lip + o * (ac - 2.2)
    column(mb, rng, (c2.x, c2.y), rpoly(rng, hl * 0.42, hw * 0.5, ang + 0.2, n=7, ex=2.2, jit=0.1), z_top - 14.0,
           z_top - 3.0, m=DARK, taper=1.75, band=0.0, lean=(o.x * 1.6, o.y * 1.6), jitter=0.08, bottom=True,
           chamfer=0.0)
    # pingo menor ao lado (a silhueta de baixo nao fica simetrica)
    c3 = lip + o * (ac - 1.0) + s * (hw * 0.55)
    column(mb, rng, (c3.x, c3.y), rpoly(rng, hl * 0.3, hw * 0.28, ang - 0.3, n=6, ex=2.2, jit=0.1), z_top - 8.5,
           z_top - 2.8, m=ROCK, taper=1.9, band=0.0, lean=(o.x * 0.8, o.y * 0.8), jitter=0.08, bottom=True,
           chamfer=0.0)


# ------------------------------------------------------------------ pocos do chao + quedas pela borda
LEDGE = {"SW": (-4.5, 4.6, 9.4), "SE": (-6.0, 4.2, 9.0)}     # (topo da laje, avanco da frente, meia-largura)


def ground_site(tag, pool, fall, seed):
    px, py, pr = pool
    fx, fy = fall
    d = math.hypot(fx - px, fy - py)
    ux, uy = (fx - px) / d, (fy - py) / d
    o = Vector((ux, uy, 0.0))
    s = Vector((-uy, ux, 0.0))
    t_lip = max(d, lip_t(px, py, ux, uy))
    rng = random.Random(seed)
    mb = MB("DB_Water_%s" % tag, C, rng, detail="near", floor=-999)
    P = Vector((px, py, 0.0))
    # leito (piso de colisao do db_col em G-1,6) e lamina (G-0,8), que entra 0,6 por baixo do chao
    mb.prism(DL.ccw(pool_poly(px, py, pr, ux, uy, CH_HW, t_lip - 0.2, 0.3)), G - BED - 0.6, G - BED, BLOCK)
    mb.prism(DL.ccw(pool_poly(px, py, pr, ux, uy, CH_HW, t_lip, 0.6)), ZW_G - 0.45, ZW_G, WATER)
    ang = math.atan2(uy, ux)
    # duas massas de rocha na boca do canal, meio dentro d'agua (2 caixas ajustadas cada) + lajes rentes por fora
    rocks = []
    for sd, k in ((-1, 0), (1, 1)):
        aa = ang + sd * rng.uniform(0.95, 1.2)
        rr = pr + rng.uniform(0.3, 0.8)
        c = (px + math.cos(aa) * rr, py + math.sin(aa) * rr)
        ra, rb = rng.uniform(2.3, 2.7), rng.uniform(1.8, 2.1)
        zt = G + rng.uniform(2.6, 3.4) - k * 0.8
        rock_mass(mb, rng, c, rb, ra, G - BED - 0.4, zt, aa, G, (math.cos(aa), math.sin(aa)),
                  name="%s_rocha%d" % (tag, k))
        rocks.append((c, ra + 1.6))

    def skip(q):
        return any(math.hypot(q.x - c[0], q.y - c[1]) < r for c, r in rocks)
    # cantaria da borda (poco + margens do canal ate perto do labio)
    t_mouth = math.sqrt(max(0.0, (pr + 0.45) ** 2 - (CH_HW + 0.45) ** 2))
    dd = math.asin(min(0.98, (CH_HW + 0.7) / (pr + 0.45)))
    coping_run(mb, rng, offset_circle(px, py, pr + 0.45, ang + dd, ang - dd + math.tau, 48), G + COPE, skip=skip,
               gap=0.14, stones=0.5)
    for sd in (-1, 1):
        a = P + o * (t_mouth - 0.3) + s * (sd * (CH_HW + 0.45))
        b = P + o * (t_lip - 3.2) + s * (sd * (CH_HW + 0.45))
        coping_run(mb, rng, [(a.x, a.y), (b.x, b.y)], G + COPE, skip=skip, gap=0.06, stones=0.25)
    # labio: soleira de pedra sob a lamina + rochas-bochecha dos dois lados, TODAS dentro da faixa da guarda da borda
    lip = P + o * t_lip
    mb.box((1.6, 2 * (CH_HW + 0.6), 1.6), (lip.x - o.x * 0.55, lip.y - o.y * 0.55, ZW_G - 0.15 - 0.8),
           (0, 0, ang), BLOCK, 0.1)
    for sd in (-1, 1):
        q = lip - o * rng.uniform(0.5, 0.9) + s * (sd * (CH_HW + 2.2))
        for _ in range(20):
            if rim_depth(q.x, q.y) >= 0.6:
                break
            q = q - o * 0.2
        # inteira dentro da faixa da guarda da borda (4,6): raio + inclinacao + folga
        ra = min(rng.uniform(2.1, 2.5), RIM_GUARD - 0.3 - 0.8 - rim_depth(q.x, q.y))
        rb = min(rng.uniform(1.5, 1.8), ra * 0.8)
        column(mb, rng, (q.x, q.y), rpoly(rng, ra, rb, ang + rng.uniform(-0.3, 0.3), n=8, ex=2.1, jit=0.14),
               G - 3.0, G + rng.uniform(0.8, 1.3), m=ROCK, taper=0.74, band=0.5, jitter=0.1,
               lean=(o.x * 0.6 + s.x * sd * 0.3, o.y * 0.6 + s.y * sd * 0.3))
        # seixo companheiro: no chao (>= 1,3 para dentro da borda) e dentro da faixa da guarda da borda
        q2 = lip - o * 0.4 + s * (sd * (CH_HW + 5.2))
        for _ in range(30):
            if rim_depth(q2.x, q2.y) >= 1.3:
                break
            q2 = q2 - o * 0.25
        mb.rock((q2.x, q2.y, G + 0.05), (1.8, 1.4, 1.0), ROCK, 1, (0, 0, rng.uniform(0, 3)), jitter=0.25)
        if DEBUG:
            for nm_, qq, rad in (("bochecha", q, ra + 0.8), ("seixo", q2, 1.1)):
                dep = rim_depth(qq.x, qq.y) + rad
                if dep > RIM_GUARD - 0.3:
                    print("WATER AVISO %s %s passa da guarda da borda: %.2f" % (tag, nm_, dep))
    # correnteza: fitas finas deitadas no canal (a agua acelera para o labio)
    streaks(mb, rng, P + o * t_mouth, P + o * (t_lip - 1.0), ZW_G, 4, (-1.2, 0.9, -0.3, 1.4))
    # laje saliente sob o labio (o degrau da queda)
    zl, af, hw = LEDGE[tag]
    ledge(mb, rng, lip, o, s, zl, -6.5, af, hw)
    # queda: sai do labio e cai livre (raios no terreno + nas pecas desta zona)
    F = Face(lip.x, lip.y, 60.0)
    F.add_bmesh(mb.bm)
    crest = Vector((lip.x, lip.y, ZW_G))
    cur = Curtain(F, crest, (ux, uy), Z_END, (2 * CH_HW + 0.6, 11.0, 14.0, 19.0), lip=1.6, clear=1.0,
                  drift=0.015, name=tag)
    cur.build(mb, rng)
    foot_skirt(mb, rng, cur)
    ft = cur.foot()
    FEET["FX_Fall_%s_Base" % tag] = (round(ft.x, 1), round(ft.y, 1), round(ft.z, 1))
    if DEBUG:
        print("WATER %s lip t=%.2f (%.1f, %.1f) polys=%d breaks=%s" % (tag, t_lip, lip.x, lip.y, F.npolys,
                                                                     [(round(z, 1), round(a0, 1), round(a1, 1))
                                                                      for z, a0, a1 in cur.breaks]))
        print("WATER %s perfil:" % tag, [(round(z, 1), round(a, 2)) for z, a in cur.keys], "pe=(%.1f, %.1f, %.1f)" % (
            ft.x, ft.y, ft.z), "larg: labio %.1f z10 %.1f pe %.1f" % (cur.width(ZW_G), cur.width(10.0),
                                                                     cur.width(cur.z_bot)))
    return mb.finish()


# ------------------------------------------------------------------ poco NW + cascata da mesa
NW_ZA = 47.5                   # topo da rocha A (1o degrau: 70 -> 47,5)
NW_ZB = 36.4                   # topo PLANO da rocha B: acima do pulo (7,2) desde o piso do terraco
EDGE_CLEAR = 0.8               # A fica >= 0,8 para fora da linha da borda; B >= 1,4 para dentro (guarda-corpo,
B_CLEAR = 1.4                  # coroamento e guarda invisivel ocupam +-0,6 e o coroamento vai ate -1,25)


def edge_frame():
    """borda NW do terraco da vila: canto HUB_POLY[0] -> HUB_POLY[-1]; e = ao longo, n = normal para FORA"""
    a = Vector((L.HUB_POLY[0][0], L.HUB_POLY[0][1], 0.0))
    b = Vector((L.HUB_POLY[-1][0], L.HUB_POLY[-1][1], 0.0))
    e = (b - a).normalized()
    n = Vector((e.y, -e.x, 0.0))
    px, py, pr = L.POOL_NW
    if (Vector((px, py, 0.0)) - a).dot(n) > 0:
        n = -n
    return a, e, n


def nw_frame():
    """bica (T, cota) e direcao da bica o1 (sai da mesa)"""
    tx, ty, tz = L.CASCADE_NW_TOP
    mx, my = L.MESAS[0][0], L.MESAS[0][1]
    o1 = Vector((tx - mx, ty - my, 0.0)).normalized()          # para onde a bica aponta (terreno: MesaSpring)
    return Vector((tx, ty, 0.0)), tz, o1


def _hub_dist(x, y):
    """distancia assinada ate o contorno da vila (positivo = dentro do terraco)"""
    d = L.polyline_dist(x, y, list(L.HUB_POLY) + [L.HUB_POLY[0]])
    return d if L.point_in_poly(x, y, L.HUB_POLY) else -d


def nw_site(seed=707):
    rng = random.Random(seed)
    mb = MB("DB_Water_NW", C, rng, detail="near", floor=-999)
    px, py, pr = L.POOL_NW
    P = Vector((px, py, 0.0))
    E0c, e, n = edge_frame()

    def W2(u, v):
        return E0c + n * u + e * v

    def UV(p):
        q = Vector((p[0], p[1], 0.0)) - E0c
        return q.dot(n), q.dot(e)
    T, tz, o1 = nw_frame()
    F = Face(T.x, T.y, 45.0)
    # topo real da bica e a frente dela
    zs = F.down(T.x - o1.x * 1.2, T.y - o1.y * 1.2, tz + 12.0, 30.0)
    zs = zs if zs is not None and abs(zs - tz) < 3.0 else tz - 0.4
    fs = F.out(T, o1, Vector((-o1.y, o1.x, 0)), 0.0, zs - 0.4)
    fs = fs if fs is not None and abs(fs) < 4.0 else 0.0
    E0 = T + o1 * (fs + 0.1)
    uT, vT = UV(E0)
    rot_n = math.atan2(n.y, n.x)
    z0 = G - 1.5
    # ---- A: coluna no bolsao entre a mesa e o muro do terraco (face da frente paralela a borda, >= EDGE_CLEAR para
    #      fora), fundo entrando na mesa; bloco de topo em balanco sobre o guarda-corpo (a agua do 2o degrau passa
    #      por cima da borda). Base escura + corpo de arenito + faixa clara no topo.
    zA = NW_ZA
    zAb = 40.5
    a_u, a_v = 4.1, 5.6                               # meia-largura ao longo de n (u) e de e (v)
    polyA = rpoly(rng, a_u, a_v, rot_n, n=10, ex=2.6, jit=0.05)
    umin = min(p[0] * n.x + p[1] * n.y for p in polyA) * 1.05
    cA = W2(EDGE_CLEAR - umin, vT - 1.0)
    uA, vA = UV(cA)
    pa = Piece(mb)
    column(mb, rng, (cA.x, cA.y), polyA, z0, G + 7.0, m=DARK, taper=0.99, band=0.0, rings=1,
           slope=(-e.x * 0.16, -e.y * 0.16), jitter=0.03, chamfer=0.0)
    pa.close()
    pa1 = Piece(mb)
    column(mb, rng, (cA.x, cA.y), [(x * 0.985, y * 0.985) for x, y in polyA], G + 6.8, zAb, m=ROCK, taper=0.96,
           band=0.0, rings=2, slope=(0.0, 0.0), jitter=0.03, chamfer=0.25)
    pa1.close()
    # bloco de topo: CONTEM a coluna (a colisao dela sobe ate o topo de A por dentro dele) e avanca para -n (sobre a
    # borda) ate u = -1,7; embaixo do balanco o guarda-corpo fica livre (>= 8 acima)
    au2 = (uA + a_u * 1.05 + 0.6 + 1.7) / 2.0
    av2 = a_v + 0.7
    polyA2 = rpoly(rng, au2, av2, rot_n, n=10, ex=2.5, jit=0.04)
    umin2 = min(p[0] * n.x + p[1] * n.y for p in polyA2) * 1.04
    cA2 = W2(-1.7 - umin2, vA)
    pa2 = Piece(mb)
    column(mb, rng, (cA2.x, cA2.y), polyA2, zAb - 0.6, zA, m=ROCK, taper=0.985, band=1.6, rings=2,
           slope=(0.0, 0.0), jitter=0.03, bottom=True, chamfer=0.35)
    pa2.close()
    # colisao de A: coluna ajustada a MENOR secao (base e bloco) do pe ate o topo medido + caixa do balanco
    fit_col(mb, [pa, pa1, pa2], (cA.x, cA.y), rot_n, z0, zA, band=(G - 1.0, zA - 0.5), nbox=3, top="vis",
            name="NW_A")
    fit_col(mb, pa2, (cA2.x, cA2.y), rot_n, zAb - 0.6, zA, band=(zAb - 0.3, zA - 0.5), nbox=1, top="vis",
            name="NW_A_topo")
    # tampao: fecha a fresta entre a frente de A e o muro/guarda do terraco (so onde a face de A esta a <= 1,6 da
    # borda: a caixa fica dentro do muro, da guarda e da rocha; topo na altura do corrimao, sem piso novo na fresta).
    # Com ele a fresta ao pe da mesa ao norte de A fica fechada (ninguem do bolsao entra)
    bv = pa.bvh()
    vs_ok = []
    for k in range(-28, 29):
        v = vA + k * 0.5
        o_ = W2(-0.2, v)
        h = bv.ray_cast(Vector((o_.x, o_.y, G + 1.5)), n, 14.0)
        if h[0] is not None and -0.2 + h[3] <= 1.6:
            vs_ok.append(v)
    if len(vs_ok) > 1:
        v0, v1 = min(vs_ok), max(vs_ok)
        cf = W2(0.75, (v0 + v1) / 2.0)
        col_box(COL_AREA, (2.1, v1 - v0, HB + 1.8 - z0), (cf.x, cf.y, (z0 + HB + 1.8) / 2.0), (0, 0, rot_n))
    # ---- B: rocha dentro do terraco, da borda (>= B_CLEAR para dentro) ate 1 dentro do poco; topo PLANO
    zB = NW_ZB
    lipA = W2(-1.7, vA)                                 # onde a agua deixa A (frente do bloco de topo)
    dir_pool = (P - lipA)
    dist_pool = dir_pool.length
    dB = dir_pool.normalized()
    rotB = math.atan2(dB.y, dB.x)
    b_len = (dist_pool - pr + 1.2 + 1.0) / 2.0          # de ~1 antes do pouso do 2o degrau ate 1,2 dentro do poco
    b_w = 3.9
    polyB = rpoly(rng, b_len, b_w, rotB, n=9, ex=2.3, jit=0.1)
    cB = lipA + dB * (b_len + 0.2)
    umaxB = UV(cB)[0] + max(p[0] * n.x + p[1] * n.y for p in polyB) * 1.06
    if umaxB > -B_CLEAR:
        cB = cB - n * (umaxB + B_CLEAR)
    # base escura com o topo INCLINADO (estrato em diagonal, nada de aro de barril) + corpo de arenito facetado
    pb = Piece(mb)
    column(mb, rng, (cB.x, cB.y), [(x * 1.01, y * 1.01) for x, y in polyB], HB - BED - 0.6, HB + 1.9, m=DARK,
           taper=1.0, band=0.0, rings=1, slope=(dB.x * 0.28, dB.y * 0.28), jitter=0.03, chamfer=0.0)
    pb.close()
    pb1 = Piece(mb)
    column(mb, rng, (cB.x, cB.y), polyB, HB - 0.2, zB, m=ROCK, taper=0.955, band=0.8, rings=3, slope=(0.0, 0.0),
           jitter=0.05, chamfer=0.3)
    pb1.close()
    fit_col(mb, [pb, pb1], (cB.x, cB.y), rotB, HB - BED - 0.6, zB, band=(HB - BED - 0.3, zB - 0.35), nbox=3,
            top="vis", name="NW_B")
    # tampao: fecha a fresta entre B e a guarda do terraco (so se a face de B chegar a <= 1,7 da borda)
    bvs = (pb.bvh(), pb1.bvh())
    vs_ok = []
    uB, vB = UV(cB)
    for k in range(-30, 31):
        v = vB + k * 0.5
        o_ = W2(-0.2, v)
        hs = [bv.ray_cast(Vector((o_.x, o_.y, HB + 1.5)), -n, 14.0) for bv in bvs]
        ds = [h[3] for h in hs if h[0] is not None]
        if ds and -0.2 - min(ds) >= -1.7:
            vs_ok.append(v)
    if len(vs_ok) > 1:
        v0, v1 = min(vs_ok), max(vs_ok)
        cf = W2(-1.1, (v0 + v1) / 2.0)
        col_box(COL_AREA, (1.6, v1 - v0, HB + 1.8 - (HB - 0.5)), (cf.x, cf.y, (HB - 0.5 + HB + 1.8) / 2.0),
                (0, 0, rot_n))
    # pedras da borda sul do poco (pequenas, meio na agua, dentro do guarda-corpo): fecham a faixa estreita
    south = []
    for ang_deg, ra, rb, h in ((230.0, 1.45, 1.2, 1.9), (254.0, 1.35, 1.15, 1.4)):
        aa = math.radians(ang_deg)
        rr = pr + 0.5
        for _ in range(12):
            c = (px + math.cos(aa) * rr, py + math.sin(aa) * rr)
            if _hub_dist(c[0], c[1]) - max(ra, rb) * 1.08 >= 0.75:
                break
            rr -= 0.1
        ps = Piece(mb)
        column(mb, rng, c, rpoly(rng, ra, rb, aa + math.pi / 2, n=8, ex=2.3, jit=0.06), HB - BED - 0.4, HB + h,
               m=ROCK, taper=0.9, band=0.7, slope=(0.0, 0.0), jitter=0.04, chamfer=0.3)
        fit_col(mb, ps, c, aa + math.pi / 2, HB - BED - 0.4, HB + h, band=(HB - 1.0, HB + h - 0.35), nbox=1,
                name="NW_sul%d" % len(south))
        south.append((c, max(ra, rb) + 0.7))

    def in_B(q, pad):
        v = Vector((q.x - cB.x, q.y - cB.y, 0.0))
        along = v.dot(dB)
        acr = v.dot(Vector((-dB.y, dB.x, 0.0)))
        return (along / (b_len + pad)) ** 2 + (acr / (b_w + pad)) ** 2 < 1.0

    def skip(q):
        return in_B(q, 1.0) or any(math.hypot(q.x - c[0], q.y - c[1]) < r for c, r in south)
    # ---- os raios da cascata enxergam as rochas A e B (bmesh desta zona, antes da agua) + a mesa
    F.add_bmesh(mb.bm)
    coping_run(mb, rng, offset_circle(px, py, pr + 0.45, 0.0, math.tau, 52)[:-1], HB + COPE, skip=skip, closed=True,
               gap=0.14, stones=0.5)
    circ = [(px + (pr + 0.3) * math.cos(t * math.tau / 32), py + (pr + 0.3) * math.sin(t * math.tau / 32))
            for t in range(32)]
    mb.prism(circ, HB - BED - 0.6, HB - BED, BLOCK)
    circ = [(px + (pr + 0.6) * math.cos(t * math.tau / 32), py + (pr + 0.6) * math.sin(t * math.tau / 32))
            for t in range(32)]
    mb.prism(circ, ZW_H - 0.45, ZW_H, WATER)
    # 1o degrau: bica (70) -> rocha A (rumo o1: sai da mesa)
    c1 = Vector((E0.x, E0.y, zs + 0.25))
    cur1 = Curtain(F, c1, (o1.x, o1.y), zA - 2.0, (4.2, 6.8, 7.0, 8.4), lip=1.5, clear=1.0, land=True, name="NW1")
    cur1.crest_back = 0.3
    cur1.build(mb, rng)
    # corrego na bica (sai da fenda da mesa e corre ate o bocal)
    q0 = c1 - o1 * 3.0
    WK.ribbon(mb, [q0 + Vector((0, 0, 0.02)), c1 - o1 * 1.0, c1 + Vector((0, 0, 0.0))], [2.6, 3.6, 4.2], WATER,
              Vector((-o1.y, o1.x, 0)), thick=0.3, bulge=0.12, fwd=(0, 0, 1))
    land1 = cur1.landed[0] if cur1.landed else cur1.foot()
    foam_patch(mb, rng, land1, 2.6, land1.z, n=6, s=0.8)
    # 2o degrau: da frente do bloco de topo de A (em balanco) -> B, rumo -n (cruza a borda por cima)
    uL, vL = UV(land1)
    v2 = vL - 1.2
    o2 = -n
    s2 = Vector((-o2.y, o2.x, 0.0))
    fa = F.out(W2(0.0, v2), o2, s2, 0.0, zA - 0.8)
    a_lip = (fa if fa is not None else 1.7) + 0.05
    q = W2(-a_lip + 0.8, v2)
    zA_top = F.down(q.x, q.y, zA + 6.0, 10.0) or zA
    c2 = W2(-a_lip, v2) + Vector((0, 0, zA_top + 0.22))
    film(mb, F, [land1, c2 + n * 0.4], 5.4, 0.22)
    # jato: tem que passar a borda e pousar em B (>= 1,2 alem da face de tras de B)
    org = W2(0.0, v2)
    fb_back = F.ray(Vector((org.x, org.y, zB - 0.5)), o2, 30.0)
    need_adv = ((fb_back if fb_back is not None else a_lip + 2.0) - a_lip) + 1.4
    cur2 = Curtain(F, c2, (o2.x, o2.y), zB - 3.0, (4.8, 7.4, 5.0, 8.6), lip=max(1.0, need_adv), clear=0.9,
                   land=True, name="NW2")
    cur2.crest_back = 0.3
    cur2.build(mb, rng)
    land2 = cur2.landed[0] if cur2.landed else cur2.foot()
    foam_patch(mb, rng, land2, 2.8, land2.z, n=6, s=0.8)
    # 3o degrau: da frente de B -> poco (rumo dB, deslocado de lado: zigue-zague)
    sB = Vector((-dB.y, dB.x, 0.0))
    lat3 = -1.8
    fbb = F.out(cB, dB, sB, lat3, zB - 1.0)
    b_lip = (fbb if fbb is not None else b_len) + 0.05
    q = cB + dB * (b_lip - 0.9) + sB * lat3
    zB_top = F.down(q.x, q.y, zB + 6.0, 12.0) or zB
    c3 = cB + dB * b_lip + sB * lat3 + Vector((0, 0, zB_top + 0.22))
    film(mb, F, [land2, c3 - dB * 0.4], 6.4, 0.22)
    cur3 = Curtain(F, c3, (dB.x, dB.y), ZW_H, (5.0, 8.4, 4.0, 10.2), lip=1.2, clear=0.9, land=False, name="NW3")
    cur3.crest_back = 0.3
    cur3.build(mb, rng)
    ft = cur3.foot()
    foam_patch(mb, rng, Vector((ft.x + dB.x * 0.6, ft.y + dB.y * 0.6, 0.0)), 4.2, ZW_H, n=8, s=1.1)
    FEET["FX_Fall_NW_Pool"] = (round(ft.x + dB.x * 0.6, 1), round(ft.y + dB.y * 0.6, 1), round(ZW_H + 0.5, 1))
    # riscos de espuma soltos na lamina (a agua do pe se espalha pelo poco)
    flecks(mb, rng, Vector((ft.x, ft.y, 0.0)), ZW_H, 6, 4.0, 6.8, rotB, 1.1)
    if DEBUG:
        for cu in (cur1, cur2, cur3):
            print("WATER %s perfil:" % cu.name, [(round(z, 1), round(a, 2)) for z, a in cu.keys],
                  "pouso:", None if not cu.landed else tuple(round(v, 1) for v in cu.landed[0]))
        print("WATER NW E0=(%.1f, %.1f) uT=%.2f vT=%.2f cA=(%.1f, %.1f) cA2=(%.1f, %.1f) cB=(%.1f, %.1f) umaxB=%.2f "
              "a_lip=%.2f lip2=%.2f b_lip=%.2f zA_top=%.2f zB_top=%.2f pe=(%.1f, %.1f, %.1f)" % (
                  E0.x, E0.y, uT, vT, cA.x, cA.y, cA2.x, cA2.y, cB.x, cB.y, umaxB, a_lip, max(1.0, need_adv), b_lip,
                  zA_top, zB_top, ft.x, ft.y, ft.z))
    return mb.finish()


def film(mb, F, pts, w, th):
    """lamina fina correndo sobre o topo de uma rocha (segue a superficie por raios de cima)"""
    a, b = Vector(pts[0]), Vector(pts[1])
    n = max(2, int((b - a).length / 1.2))
    P = []
    for i in range(n + 1):
        q = a.lerp(b, i / n)
        z = F.down(q.x, q.y, q.z + 6.0, 14.0)
        P.append(Vector((q.x, q.y, (z if z is not None else q.z) + th)))
    dv = (b - a)
    dv.z = 0.0
    dv = dv.normalized() if dv.length > 1e-6 else Vector((1, 0, 0))
    side = Vector((-dv.y, dv.x, 0.0))
    WK.ribbon(mb, P, [w * (0.85 + 0.15 * i / n) for i in range(n + 1)], WATER, side, thick=0.25, bulge=0.1,
              fwd=(0, 0, 1))


# ------------------------------------------------------------------ build
def build():
    STATS.clear()
    FEET.clear()
    ground_site("SW", L.POOL_SW, L.FALL_SW, 811)
    ground_site("SE", L.POOL_SE, L.FALL_SE, 823)
    nw_site(707)
    if DEBUG:
        for st in STATS:
            print("WATER COL %-16s gap_max=%.2f gap_med=%.2f topo_col=%.2f topo_vis=[%.2f, %.2f]" % st)
        print("WATER PES", FEET)


EXTRA_PROBES = _probe_list()
