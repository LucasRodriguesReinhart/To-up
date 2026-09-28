# sg_water - ZONA WATER da Ilha 3 (Shadow Garden): as 4 cachoeiras FRIAS da borda (sg_layout.WATERFALLS).
# build() substitui sg_blockout.water. Prefixo SG_Water_, colecao 07_WATER. Sem luz, sem colisao (nada andavel aqui:
# o piso, a bancada do labio e as guardas sao do sg_col/sg_terrain; a fonte da praca e da vila).
#   Cada queda (1 objeto MB por queda -> 1 MeshPart por material):
#   1. NASCENTE curta: a agua brota de uma FENDA escura na bancada de pedra do terreno (cota do labio -0,1) poucos
#      studs antes do labio, com borbulho de espuma, e corre rasa (lamina Water_SG 0,08 acima da pedra) ate a borda;
#      a do SUL (sem bancada) sai de uma fenda na face do penhasco (fundo escuro, ombreiras e soleira em colunas de
#      basalto, sobrancelha em balanco);
#   2. CORTINA que cai colada a face REAL do penhasco: raios BVH nas malhas SG_Ter_* da cena (a mesma tecnica da
#      Ilha 2, db_water): o avanco nunca diminui, onde a rocha avanca a agua passa por fora com folga e ganha espuma na
#      quebra; corpo azul frio (Water_SG, secao em arco) + fios claros (Water_Fall: o jogo anima a textura
#      FluxoCachoeira nessas pecas) + riscos de espuma;
#   3. ESPUMA na crista do labio e onde bate nas saliencias; SAIA de espuma/nevoa no pe (~-60, dentro das nuvens: o
#      export nao leva as nuvens, entao o pe nunca fica cortado no ar).
# Marcadores FX_Fall_*/AUDIO_Waterfall_* sao do sg_core (nao cria). Materiais: Water_SG, Water_Fall, Foam + rocha da
# paleta (nenhum material novo).
import math, random
import numpy as np
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import sg_lib as SL
from sg_lib import MB
import sg_layout as L
import fm_water_kit as WK

C = "07_WATER"
WATER, FALL, FOAM = "Water_SG", "Water_Fall", "Foam"
ROCK, DARK, TOP = "Cliff_Rock_SG", "Cliff_Rock_SG_Dark", "Cliff_Rock_SG_Top"
Z_END = -60.0                    # pe das quedas (mar de nuvens / nevoa do jogo nos FX_Fall_*_Base)
TAGS = ("West", "East", "North", "South")
DEBUG = True
INFO = {}                        # tag -> dados medidos (labio, perfil, quebras)

# (tag, ponto do mirante (x, y, piso)) - onde o jogador para e olha o labio
MIRANTES = {
    "West": (-112.0, -49.0, L.P2),
    "East": (131.0, -109.0, L.P1),
    "North": (-42.5, 167.5, L.P3),
    "South": (-57.0, -160.5, L.P1),            # canto sudoeste do P1 (a queda sul sai de uma fenda abaixo da calcada)
}


def _cams():
    cams = {}
    for (x, y, z, deg), tag in zip(L.WATERFALLS, TAGS):
        a = math.radians(deg)
        ux, uy = math.cos(a), math.sin(a)
        sx, sy = -uy, ux
        # de perto (fora da ilha, um pouco abaixo do labio, de lado)
        cams["CAM_SGWater_%s_Near" % tag] = ((x + ux * 46.0 + sx * 20.0, y + uy * 46.0 + sy * 20.0, z + 2.0),
                                             (x + ux * 2.0, y + uy * 2.0, z - 16.0), 24)
        # de baixo (acima do mar de nuvens, olhando a cortina subir ate o labio)
        cams["CAM_SGWater_%s_Below" % tag] = ((x + ux * 34.0 - sx * 16.0, y + uy * 34.0 - sy * 16.0, -24.0),
                                              (x + ux * 1.0, y + uy * 1.0, z - 18.0), 22)
        # altura do jogador no mirante do labio (olho 5,2 acima do piso)
        mx, my, mz = MIRANTES[tag]
        cams["CAM_SGWater_%s_PlayerHeight" % tag] = ((mx, my, mz + 5.2), (x + ux * 5.0, y + uy * 5.0, z - 7.0), 22)
    return cams


CAMS = _cams()

# rotas extras: o jogador chega a pe em cada mirante (a agua nao pode bloquear nada)
EXTRA_ROUTES = {
    "WATER_mirante_oeste": ([(-60.0, -45.0), (-100.0, -46.0), MIRANTES["West"][:2]], L.P2),
    "WATER_mirante_leste": ([(108.0, -116.0), (120.0, -112.0), MIRANTES["East"][:2]], L.P1),
    "WATER_mirante_norte": ([(-20.0, 150.0), (-34.0, 160.0), MIRANTES["North"][:2]], L.P3),
    "WATER_mirante_sul": ([(-30.0, -126.0), (-33.0, -152.0), (-50.0, -156.0), MIRANTES["South"][:2]], L.P1),
}
EXTRA_PROBES = []


# ------------------------------------------------------------------ raios contra o terreno (tecnica da Ilha 2)
class Face:
    """BVH das malhas SG_Ter_* (poligonos a menos de R de (cx, cy)) + BVHs extras (as rochas desta zona)"""

    def __init__(self, cx, cy, R, prefix=("SG_Ter_",)):
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
    """lamina varrida por pts com secao em ARCO (flecha k * largura para fora, espessura 'thick')"""
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
    u = max(-0.5, min(0.5, u))
    return k * (1.0 - 4.0 * u * u)


class Curtain:
    """cortina que sai de uma crista c (Vector 3D) para fora (o, horizontal) e cai ate z_bot.
    wprof = (largura no labio, depois de abrir, altura da abertura, no pe). Perfil (avanco x cota): parabola curta no
    labio + deriva; o avanco NUNCA diminui; onde a rocha (raios) avanca alem do jato, a agua passa por fora com folga
    'clear'; saliencia > 1,6 = degrau (espuma na quebra)."""

    def __init__(self, F, c, o, z_bot, wprof, lip=1.4, clear=0.8, dz=1.0, drift=0.0, name="", max_jump=8.0,
                 throw=3.0):
        self.c = Vector(c)
        self.o = Vector((o[0], o[1], 0.0)).normalized()
        self.s = Vector((-self.o.y, self.o.x, 0.0))
        self.z_top, self.z_bot = self.c.z, z_bot
        self.wprof = wprof
        self.H = max(1.0, self.z_top - z_bot)
        self.name = name
        self.crest_back = 0.7
        self.breaks = []             # (z, adv_antes, adv_depois)
        keys = [(self.z_top, 0.0)]
        adv = 0.0
        z = self.z_top
        while z > z_bot + 1e-6:
            zp = z
            z = max(z_bot, z - dz)
            drop = self.z_top - z
            free = lip * math.sqrt(min(drop, throw) / throw) + drift * max(0.0, drop - throw)
            cur = max(adv, free)
            w = self.width(z)
            fs = []
            if F is not None:
                for u in (-0.5, -0.3, -0.1, 0.1, 0.3, 0.5):
                    f = F.out(self.c, self.o, self.s, u * w, z)
                    if f is not None and -30.0 < f < cur + max_jump:
                        fs.append(f)
            face = max(fs) if fs else None
            need = face + clear if face is not None else -1e9
            if need > cur + 1.2:
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

    @staticmethod
    def _simplify(keys, tol=0.12):
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
        res = [out[0]]
        for k1 in out[1:]:
            k0 = res[-1]
            n = int((k0[0] - k1[0]) / 9.0)
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
        k = min(1.0, (self.z_top - z) / 6.0)
        ph = (sum(map(ord, self.name)) % 97) * 0.37
        return 0.05 * self.width(z) * k * math.sin(z * 0.17 + ph)

    def path(self, u=0.0):
        pts = [self.c + self.o * a + self.s * (u * self.width(z) + self.wob(z)) + Vector((0, 0, z - self.c.z))
               for z, a in self.keys]
        return pts, [self.width(z) for z, a in self.keys]

    def adv(self, z):
        K = self.keys
        if z >= K[0][0]:
            return K[0][1]
        for (z0, a0), (z1, a1) in zip(K, K[1:]):
            if z1 <= z <= z0:
                return a0 + (a1 - a0) * ((z0 - z) / (z0 - z1) if z0 > z1 else 0.0)
        return K[-1][1]

    def build(self, mb, rng, nb=None, ns=None, k=ARC_K):
        pts, ws = self.path()
        if len(pts) < 2:
            return
        self.k = k
        b = k * self.wprof[0]
        sheet(mb, pts, ws, self.s, WATER, k=k, thick=0.4)
        H = self.z_top - self.z_bot

        def spread(n, lo, hi):
            sp = (hi - lo) / n
            return [lo + sp * (i + 0.5) + rng.uniform(-0.38, 0.38) * sp for i in range(n)]
        # fios claros (Water_Fall, a textura animada do jogo): larguras diferentes, derivam de lado, comecam e
        # terminam em alturas diferentes (o azul do corpo aparece entre eles)
        nb = nb or max(4, min(6, int(self.wprof[1] / 1.8)))
        for u in spread(nb, -0.42, 0.42):
            z0 = self.z_top - (0.3 if rng.random() < 0.5 else rng.uniform(0.8, 0.2 * H + 0.8))
            z1 = self.z_bot + (0.15 if rng.random() < 0.6 else rng.uniform(0.1, 0.3) * H)
            if z0 - z1 < 1.0:
                continue
            fw = rng.choice((rng.uniform(0.04, 0.06), rng.uniform(0.08, 0.12), rng.uniform(0.13, 0.17)))
            u1 = max(-0.44, min(0.44, u + rng.uniform(-0.07, 0.07)))
            self._strip(mb, u, fw, z0, z1, 0.1, FALL, 0.12, u1=u1)
        # riscos de espuma: finos, curtos e soltos (brilho da agua que acelera)
        ns = ns if ns is not None else max(3, int(self.wprof[1] / 2.4))
        for u in spread(ns, -0.44, 0.44):
            z0 = self.z_top - rng.uniform(0.6, 0.5 * H + 0.6)
            z1 = max(self.z_bot + 0.3, z0 - rng.uniform(0.12, 0.35) * (z0 - self.z_bot))
            if z0 - z1 < 0.8:
                continue
            self._strip(mb, u, None, z0, z1, 0.24, FOAM, 0.1, wabs=rng.uniform(0.2, 0.36),
                        u1=u + rng.uniform(-0.04, 0.04))
        self.crest_foam(mb, rng, b)
        for zl, a0, a1 in self.breaks:
            self.break_foam(mb, rng, zl, a0, a1, b)

    def _strip(self, mb, u, fw, z0, z1, off, m, thick, wabs=None, u1=None):
        """fita chata na frente da lamina de z0 a z1 (off acima da frente do arco), afinada nas duas pontas"""
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
            base = wabs * (1.0 + 0.6 * tt) if wabs else max(0.24, fw * w)
            ws.append(max(0.2, base * k))
        WK.ribbon(mb, pts, ws, m, side, thick=thick, flat=True)

    def crest_foam(self, mb, rng, b):
        """crista: a agua rola por cima da borda em 2-3 linguas de espuma de larguras diferentes + poucos tufos"""
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
            z1 = self.z_top - rng.uniform(0.9, 1.6)
            pts = [c - o * self.crest_back + s * (u * w) + Vector((0, 0, 0.1)),
                   c + o * (b * 0.4 + 0.3) + s * (u * w) + Vector((0, 0, -0.12)),
                   c + o * (self.adv(z1) + b + 0.45) + s * (u * self.width(z1) + self.wob(z1)) +
                   Vector((0, 0, z1 - c.z))]
            WK.ribbon(mb, pts, [wi * 0.95, wi, wi * rng.uniform(0.6, 0.8)], FOAM, s, thick=0.2, bulge=0.22)
        for sd in (-1, 1):
            r = rng.uniform(0.34, 0.48)
            q = c + o * rng.uniform(0.1, 0.4) + s * (sd * (0.5 * w - 0.25))
            mb.ico(r, (q.x, q.y, c.z + 0.02), FOAM, 1, (1.6, 1.2, 0.45), (0, 0, rng.uniform(0, 3)), jitter=0.2)

    def break_foam(self, mb, rng, zl, a0, a1, b):
        """a agua bate na saliencia: 2 faixas de espuma de larguras diferentes na FRENTE da cortina, do degrau ate uns
        3 abaixo (afinando) + um tufo pequeno em cada borda (respingo)"""
        c, o, s = self.c, self.o, self.s
        w = self.width(zl)
        for u, wf in ((rng.uniform(-0.2, -0.1), rng.uniform(0.26, 0.32)), (rng.uniform(0.1, 0.2), rng.uniform(0.18, 0.24))):
            self._strip(mb, u, None, zl + rng.uniform(0.0, 0.4), zl - rng.uniform(2.2, 3.4), 0.3, FOAM, 0.15,
                        wabs=w * wf, u1=u + rng.uniform(-0.05, 0.05))
        for sd in (-1, 1):
            r = max(0.45, w * rng.uniform(0.035, 0.055))
            q = c + o * (a1 + b + rng.uniform(0.2, 0.6)) + s * (sd * w * rng.uniform(0.42, 0.5))
            mb.ico(r, (q.x, q.y, zl - rng.uniform(0.3, 1.2)), FOAM, 1, (1.3, 1.1, 0.9), (0, 0, rng.uniform(0, 3)),
                   jitter=0.24)

    def foot(self):
        a = self.keys[-1][1]
        return self.c + self.o * a + Vector((0, 0, self.z_bot - self.c.z))


def foot_skirt(mb, rng, cur, n=9):
    """pe da queda no vazio: saia de espuma/nevoa ~1,3x a largura do pe (a lamina termina dentro dela)"""
    ft = cur.foot()
    W = cur.width(cur.z_bot)
    sc = (W / 18.0) ** 0.5
    for i in range(n):
        u = -0.62 + 1.24 * (i + 0.5) / n + rng.uniform(-0.03, 0.03)
        r = rng.uniform(2.8, 4.4) * sc * (1.0 - 0.35 * abs(u))
        q = ft + cur.s * (u * W) + cur.o * rng.uniform(-1.0, 2.2)
        zc = cur.z_bot + rng.uniform(-2.0, 1.2) - abs(u) * 2.5
        mb.ico(r, (q.x, q.y, zc), FOAM, 1, (1.35, 1.15, 0.85), (0, 0, rng.uniform(0, 3)), jitter=0.22)
    for i in range(3):
        u = -0.3 + 0.6 * (i + 0.5) / 3 + rng.uniform(-0.04, 0.04)
        r = rng.uniform(2.2, 3.0) * sc
        q = ft + cur.s * (u * W) + cur.o * rng.uniform(0.3, 1.6)
        mb.ico(r, (q.x, q.y, cur.z_bot + rng.uniform(3.0, 5.0)), FOAM, 1, (1.25, 1.0, 1.05),
               (0, 0, rng.uniform(0, 3)), jitter=0.22)


# ------------------------------------------------------------------ nascente
def hexp(cx, cy, r, rot=0.0, n=6, sx=1.0):
    return [(cx + r * sx * math.cos(rot + 2 * math.pi * k / n), cy + r * math.sin(rot + 2 * math.pi * k / n))
            for k in range(n)]


def poly_frame(c, o, s, pts):
    """pontos (avanco, lateral) no referencial da queda -> XY"""
    return [(c.x + o.x * a + s.x * l, c.y + o.y * a + s.y * l) for a, l in pts]


def spring_bench(mb, rng, F, c, o, s, t_back):
    """nascente na BANCADA do terreno: fenda escura atravessada t_back antes do labio, borbulho de espuma sobre ela e
    lamina rasa ate a crista (larga 2,8 na fenda -> 6,2 na borda). Topo da lamina = crista (0,05 acima da pedra)."""
    z = c.z + 0.05                   # cota do labio (a pedra da bancada fica em z - 0,1)
    w0, w1 = 2.8, 6.2
    n = 6
    left, right = [], []
    for i in range(n + 1):
        t = i / n
        a = -t_back + t_back * t
        w = w0 + (w1 - w0) * (t ** 0.8)
        jl = rng.uniform(-0.3, 0.3) if 0 < i < n else 0.0
        jr = rng.uniform(-0.3, 0.3) if 0 < i < n else 0.0
        left.append((a, -w / 2 + jl))
        right.append((a, w / 2 + jr))
    # fecho de tras arredondado (a agua sai da fenda)
    back = [(-t_back - 0.45, -w0 * 0.32), (-t_back - 0.65, 0.0), (-t_back - 0.45, w0 * 0.32)]
    outline = poly_frame(c, o, s, [right[-1]] + right[-2::-1] + back[::-1] + left)
    mb.prism(SL.ccw(outline), z - 0.35, z - 0.05, WATER)
    # fenda escura atravessada (a boca da nascente) com labios de pedra clara de cada lado
    fq = c - o * (t_back + 0.2)
    ang = math.atan2(o.y, o.x)
    mb.box((0.55, w0 + 0.4, 0.3), (fq.x, fq.y, z - 0.12), (0, 0, ang), DARK, 0.0)
    # borbulho: 2 tufos baixos de espuma saindo da fenda
    for k in range(2):
        u = -0.18 + 0.36 * k + rng.uniform(-0.05, 0.05)
        q = fq + s * (u * w0) + o * rng.uniform(0.3, 0.6)
        r = rng.uniform(0.42, 0.55)
        mb.ico(r, (q.x, q.y, z - 0.02), FOAM, 1, (1.6, 1.2, 0.3), (0, 0, rng.uniform(0, 3)), jitter=0.2)


def spring_cleft(mb, rng, F, P0, o, s, zm):
    """fenda na FACE do penhasco (queda sul, sem bancada): fundo escuro recuado, sobrancelha, ombreiras de colunas de
    basalto de alturas diferentes e soleira; a agua sai do fundo escuro, corre pela soleira e cai. Devolve a crista."""
    ang = math.atan2(o.y, o.x)
    fs = [F.out(P0, o, s, lat, z) for lat in (-3.0, -1.5, 0.0, 1.5, 3.0) for z in (zm - 1.0, zm + 1.0, zm + 3.0)]
    fs = [f for f in fs if f is not None and -8.0 < f < 12.0]
    face = max(fs) if fs else 0.0

    def A(a, lat, z=0.0):
        return P0 + o * a + s * lat + Vector((0.0, 0.0, z))
    # fundo escuro (a agua sai de dentro dele)
    q = A(face - 1.0, 0.0)
    mb.prism(SL.ccw(poly_frame(q, o, s, [(-1.6, -2.6), (1.0, -2.2), (1.0, 2.2), (-1.6, 2.6)])), zm - 0.6, zm + 3.2,
             DARK)
    # soleira: laje de basalto em balanco sob a agua (bica natural)
    q = A(face, 0.0)
    sill = poly_frame(q, o, s, [(-1.0, -3.0), (1.9, -2.6), (2.5, -1.0), (2.6, 1.2), (1.8, 2.8), (-1.0, 3.1)])
    mb.prism(SL.ccw(sill), zm - 1.6, zm - 0.3, ROCK, bevel=0.15)
    # ombreiras: colunas hexagonais de alturas diferentes
    for sd, (h0, h1) in ((-1, (6.5, 4.2)), (1, (8.0, 3.0))):
        for j in range(2):
            q = A(face + 0.3 - j * 1.4, sd * (3.9 + j * 1.6 + rng.uniform(-0.2, 0.2)))
            r = rng.uniform(1.25, 1.6)
            zt = zm + (h1 if j == 0 else h1 + rng.uniform(1.0, 2.2))
            mb.prism(SL.ccw(hexp(q.x, q.y, r, ang + rng.uniform(0, 1))), zm - h0 - j * 2.0, zt, ROCK, bevel=0.15)
            mb.prism(SL.ccw(hexp(q.x, q.y, r * 0.92, ang + rng.uniform(0, 1))), zt, zt + 0.25, TOP)
    # sobrancelha: bloco de colunas deitado por cima da boca
    q = A(face + 0.2, rng.uniform(-0.3, 0.3))
    brow = poly_frame(q, o, s, [(-1.8, -3.6), (1.2, -3.2), (1.5, 0.0), (1.1, 3.4), (-1.8, 3.8)])
    mb.prism(SL.ccw(brow), zm + 3.0, zm + 4.6, ROCK, bevel=0.15)
    mb.prism(SL.ccw(poly_frame(q, o, s, [(-1.6, -3.3), (0.9, -2.9), (1.2, 0.0), (0.8, 3.1), (-1.6, 3.5)])),
             zm + 4.6, zm + 4.85, TOP)
    # agua: sai do fundo escuro, corre pela soleira e cai (os raios enxergam a fenda + o penhasco)
    F.add_bmesh(mb.bm)
    lipx = face + 2.5
    WK.ribbon(mb, [A(face - 0.8, 0.0, zm - 0.12), A(face + 1.0, 0.0, zm - 0.2), A(lipx - 0.05, 0.0, zm - 0.24)],
              [3.4, 4.4, 5.0], WATER, s, thick=0.3, bulge=0.08, fwd=(0, 0, 1))
    return A(lipx, 0.0, zm - 0.22), face


# ------------------------------------------------------------------ uma queda
WPROF = {"West": (6.0, 11.0, 12.0, 26.0), "East": (6.0, 10.5, 12.0, 24.0), "North": (6.0, 11.5, 12.0, 28.0),
         "South": (5.0, 9.0, 12.0, 20.0)}


def fall(i, x, y, z, deg, tag, seed):
    rng = random.Random(seed)
    a = math.radians(deg)
    o = Vector((math.cos(a), math.sin(a), 0.0))
    s = Vector((-o.y, o.x, 0.0))
    F = Face(x, y, 45.0)
    mb = MB("SG_Water_Fall_%s" % tag, C, rng, detail="near", floor=-999)
    # bancada do terreno: trecho continuo do eixo com topo na cota do labio -0,1
    hits = []
    t = -24.0
    while t <= 5.0:
        zt = F.down(x + o.x * t, y + o.y * t, z + 3.0, 6.0)
        hits.append((t, zt is not None and abs(zt - (z - 0.1)) < 0.2))
        t += 0.2
    t_edge = None
    for tt, ok in hits:
        if ok:
            t_edge = tt
    if t_edge is not None:
        t_back = t_edge
        for tt, ok in reversed(hits):
            if tt > t_edge:
                continue
            if not ok:
                break
            t_back = tt
        t_edge += 0.1
        c = Vector((x + o.x * t_edge, y + o.y * t_edge, z - 0.05))
        run = t_edge - t_back
        spring_bench(mb, rng, F, c, o, s, min(8.0, max(2.5, run - 1.2)))
        kind = "bancada"
    else:
        P0 = Vector((x, y, 0.0))
        c, face = spring_cleft(mb, rng, F, P0, o, s, z)
        run = face
        kind = "fenda"
    cur = Curtain(F, c, (o.x, o.y), Z_END, WPROF[tag], lip=1.3, clear=0.8, drift=0.015, name=tag)
    cur.crest_back = 0.6 if kind == "bancada" else 0.3
    cur.build(mb, rng, k=ARC_K * (1.0 if kind == "bancada" else 0.8))
    foot_skirt(mb, rng, cur)
    INFO[tag] = dict(kind=kind, crest=tuple(round(v, 2) for v in c), run=round(run, 2),
                     keys=[(round(zz, 1), round(aa, 2)) for zz, aa in cur.keys],
                     breaks=[(round(zz, 1), round(a0, 1), round(a1, 1)) for zz, a0, a1 in cur.breaks],
                     foot=tuple(round(v, 1) for v in cur.foot()), polys=F.npolys)
    ob = mb.finish()
    return ob


# ------------------------------------------------------------------ build
def build():
    INFO.clear()
    for i, ((x, y, z, deg), tag) in enumerate(zip(L.WATERFALLS, TAGS)):
        fall(i, x, y, z, deg, tag, 7301 + 97 * i)
    if DEBUG:
        for tag in TAGS:
            d = INFO.get(tag, {})
            print("WATER %s %s crista=%s corrida=%s pe=%s polys=%s quebras=%s" % (
                tag, d.get("kind"), d.get("crest"), d.get("run"), d.get("foot"), d.get("polys"), d.get("breaks")))
