# sg_water - ZONA WATER da Ilha 3 (Shadow Garden): a PEDRA das 4 cachoeiras frias da borda (sg_layout.WATERFALLS).
# build() substitui sg_blockout.water. Prefixo SG_Water_, colecao 07_WATER. Sem luz, sem colisao (nada andavel aqui:
# o piso, a bancada do labio e as guardas sao do sg_col/sg_terrain; a fonte da praca e da vila).
# ACABAMENTO 2 / AGUA NO ROBLOX (2026-09-30, pedido do usuario: "a agua voce deve fazer no Roblox, porque isso aqui e
# lixo"): a AGUA SAIU DO EXPORT - sem lamina, filetes, espuma de crista/quebra, veu do pe e lamina da nascente. O jogo
# faz a agua (Terrain Water / partes com textura e particulas) lendo os MARCADORES. Aqui fica so a rocha:
#   Cada queda (1 objeto MB por queda -> 1 MeshPart por material de rocha):
#   1. NASCENTE da bancada (Oeste/Leste/Norte): boca de pedra no fundo da corrida (2 ombreiras + verga + fundo escuro),
#      CALHA de 2 margens de pedra em blocos (largura 2,4 na boca -> W_LIP no labio) sobre a bancada do terreno e BICA
#      de pedra em balanco (SPOUT alem da crista, 0,12 abaixo da bancada) de onde a agua cai;
#      a do SUL (sem bancada) sai de uma fenda na face do penhasco (fundo escuro, ombreiras e soleira em colunas de
#      basalto, sobrancelha em balanco); a soleira virou bica com 2 bochechas convergentes (calha);
#   2. a CORTINA nao e mais modelada, mas o PERFIL continua medido (raios BVH nas malhas SG_Ter_* + a pedra desta zona,
#      a tecnica da Ilha 2): o avanco nunca diminui e passa por fora da rocha com folga; saliencia = degrau (quebra).
# Marcadores (criados pelo sg_core.fx_markers a partir da tabela FALL_FX; AQUI so sao conferidos e ATUALIZADOS com o
# medido, nunca criados):
#   FX_Fall_<n>_Lip   borda da bica no nivel da PEDRA (a agua corre por cima); frente local +Y = para fora da rocha
#                     (fwd_x/fwd_z no export). width (largura da calha na bica), kind (bancada|fenda), src_pos (boca da
#                     nascente, convertido para o Roblox), channel_w0, drop, depth_hint, waypoints (eixo da cortina medido,
#                     do labio ao pe, convertido para o Roblox) e widths (largura em cada waypoint);
#   FX_Fall_<n>_Step  onde a cortina bate no degrau de basalto (sg_terrain.fall_steps): width, jump (quanto a lamina
#                     passa mais para fora); FX_Fall_<n>_Step_Upper = saliencia de cima do estrato (so onde existe);
#   FX_Fall_<n>_Base  pe da cortina (cota Z_END): width.
import math, random
import numpy as np
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import sg_lib as SL
from sg_lib import MB, yaw_to
import sg_layout as L

C = "07_WATER"
ROCK, DARK, TOP = "Cliff_Rock_SG", "Cliff_Rock_SG_Dark", "Cliff_Rock_SG_Top"
Z_END = -53.0                    # pe das quedas (cota do veu antigo, meio encoberto pelo mar de nuvens/nevoa do jogo)
TAGS = ("West", "East", "North", "South")
DEBUG = True
INFO = {}                        # tag -> dados medidos (labio, perfil, quebras)
W_LIP = {"West": 5.4, "East": 5.4, "North": 5.4, "South": 3.8}    # largura da calha na bica (= width do FX_Fall_n_Lip)
W_SRC = 2.4                      # largura da boca da nascente (bancada)
SPOUT = 1.1                      # bica: avanco alem da crista da bancada
SPOUT_DROP = 0.12                # bica: topo abaixo da bancada (a agua desce um dedo antes de cair)

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


# ------------------------------------------------------------------ perfil da cortina (medido; a agua e do Roblox)
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
                keys.append((zl + 0.15, need))          # revisao 13b: salta por cima da quina (sem lasca)
                cur = need
            elif need > cur:
                cur = need
            adv = cur
            keys.append((z, adv))
        self.keys = self._simplify(keys)
        self.opened = True

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
            w = w0 + (w1 - w0) * (1.0 - (1.0 - t) ** 2)
        else:
            t = min(1.0, (drop - fh) / max(1.0, self.H - fh))
            w = w1 + (w2 - w1) * t
        if getattr(self, "opened", False):          # overhaul 13: abre 16% em 3 studs abaixo de cada quebra
            for zl, a0, a1 in self.breaks:
                w *= 1.0 + 0.12 * max(0.0, min(1.0, (zl - z) / 4.0))
        return w

    def wob(self, z):
        """revisao 13: sem ondulacao lateral (a lamina cai reta; a ondulacao lia cobra)"""
        return 0.0

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

    def foot(self):
        a = self.keys[-1][1]
        return self.c + self.o * a + Vector((0, 0, self.z_bot - self.c.z))


# ------------------------------------------------------------------ nascente (so pedra)
def hexp(cx, cy, r, rot=0.0, n=6, sx=1.0):
    return [(cx + r * sx * math.cos(rot + 2 * math.pi * k / n), cy + r * math.sin(rot + 2 * math.pi * k / n))
            for k in range(n)]


def poly_frame(c, o, s, pts):
    """pontos (avanco, lateral) no referencial da queda -> XY"""
    return [(c.x + o.x * a + s.x * l, c.y + o.y * a + s.y * l) for a, l in pts]


def _shrink(poly, f):
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    return [(cx + (x - cx) * f, cy + (y - cy) * f) for x, y in poly]


def stone(mb, c, o, s, pts, z0, z1, cap=True):
    """bloco de pedra (contorno no referencial da queda) com chanfro; cap = tampo claro ao luar (Cliff_Rock_SG_Top)"""
    poly = SL.ccw(poly_frame(c, o, s, pts))
    mb.prism(poly, z0, z1, ROCK, bevel=0.1)
    if cap:
        mb.prism(SL.ccw(_shrink(poly, 0.86)), z1 - 0.02, z1 + 0.1, TOP)


def banks(mb, c, o, s, a0, a1, lin, zb, h0, h1, w=1.25, ph=0.0, zbot=None):
    """as 2 MARGENS da calha: blocos ao longo de a0..a1 (junta 0,08), face de dentro na lateral +-lin(a), largura ~w,
    topo zb + h (h0 -> h1) com variacao DIRIGIDA (senoide por bloco, sem sorteio); contorno de 6 lados (pedra, nao caixa)"""
    n = max(2, int(round((a1 - a0) / 2.2)))
    zbot = zb - 0.45 if zbot is None else zbot
    for sd in (-1, 1):
        for k in range(n):
            t0, t1 = k / n, (k + 1) / n
            aa0 = a0 + (a1 - a0) * t0 + (0.04 if k else 0.0)
            aa1 = a0 + (a1 - a0) * t1 - (0.04 if k < n - 1 else 0.0)
            li0, li1 = lin(aa0), lin(aa1)
            wk = w * (1.0 + 0.14 * math.sin(2.3 * k + ph + sd))
            hk = h0 + (h1 - h0) * (t0 + t1) / 2 + 0.08 * math.sin(1.9 * k + ph + 2 * sd)
            pts = [(aa0 + 0.08, li0), (aa1 - 0.08, li1), (aa1, li1 + wk * 0.35), (aa1 - 0.22, li1 + wk),
                   (aa0 + 0.22, li0 + wk * 0.92), (aa0, li0 + wk * 0.4)]
            pts = [(a, sd * l) for a, l in pts]
            if sd < 0:
                pts = pts[::-1]
            stone(mb, c, o, s, pts, zbot, zb + hk)


def spring_bench(mb, F, c, o, s, t_back, w_lip, ph):
    """nascente na BANCADA do terreno (topo zb = crista - 0,05): boca de pedra no fundo da corrida (ombreiras + verga +
    fundo escuro: a agua sai por baixo da verga), CALHA com 2 margens de blocos (largura W_SRC na boca -> w_lip na
    crista) e BICA em balanco (SPOUT alem da crista, topo SPOUT_DROP abaixo da bancada). Devolve (labio, boca):
    labio = borda da bica no nivel da pedra, boca = saida da nascente no piso da calha."""
    zb = c.z - 0.05
    tb = t_back
    # teto da boca: nunca acima do piso do patamar atras dela (a verga nao pode virar calombo na calcada)
    top = 1.18
    for lat in (-2.8, 0.0, 2.8):
        q = c - o * (tb + 2.6) + s * lat
        zp = F.down(q.x, q.y, zb + 6.0, 9.0)
        if zp is not None and zp > zb + 0.3:
            top = min(top, zp - zb - 0.14)
    top = max(0.7, top)
    # boca: 2 ombreiras, verga por cima, fundo escuro recuado (a abertura fica 2,2 x ~0,6)
    for sd, h in ((-1, 1.0), (1, 0.82)):
        pts = [(-tb + 0.05, sd * 1.1), (-tb - 0.1, sd * 3.0), (-tb - 1.2, sd * 3.3), (-tb - 2.2, sd * 2.6),
               (-tb - 2.3, sd * 1.1)]
        stone(mb, c, o, s, pts[::-1] if sd < 0 else pts, zb - 0.45, zb + min(h, top - 0.1))
    stone(mb, c, o, s, [(-tb + 0.18, -2.1), (-tb + 0.02, 2.2), (-tb - 1.9, 2.0), (-tb - 2.1, -1.9)],
          zb + top - 0.58, zb + top - 0.1)
    q = poly_frame(c, o, s, [(-tb - 1.3, -1.3), (-tb - 2.1, -1.3), (-tb - 2.1, 1.3), (-tb - 1.3, 1.3)])
    mb.prism(SL.ccw(q), zb - 0.2, zb + top - 0.5, DARK)
    # calha: margens da boca ate a ponta da bica (a face de dentro abre de W_SRC para w_lip ate a crista)

    def lin(a):
        t = max(0.0, min(1.0, (a + tb) / max(0.1, tb)))
        return W_SRC / 2 + (w_lip / 2 - W_SRC / 2) * (t ** 0.8)
    banks(mb, c, o, s, -tb + 0.02, SPOUT - 0.2, lin, zb, 0.72, 0.36, ph=ph)
    # bica: laje em balanco sob a ponta da calha (entra 0,8 na bancada) + misula por baixo (le como pedra encaixada)
    hw = w_lip / 2 + 1.5
    spout = [(-0.8, -hw), (SPOUT - 0.4, -hw + 0.25), (SPOUT, -hw + 0.9), (SPOUT + 0.06, 0.0), (SPOUT, hw - 0.9),
             (SPOUT - 0.4, hw - 0.25), (-0.8, hw)]
    zt = zb - SPOUT_DROP
    mb.prism(SL.ccw(poly_frame(c, o, s, spout)), zt - 0.8, zt, ROCK, bevel=0.1)
    corb = [(-0.8, -hw + 0.6), (SPOUT - 0.7, -hw + 1.0), (SPOUT - 0.5, 0.0), (SPOUT - 0.7, hw - 1.0), (-0.8, hw - 0.6)]
    mb.prism(SL.ccw(poly_frame(c, o, s, corb)), zt - 1.9, zt - 0.8, DARK, bevel=0.1)
    lip = c + o * SPOUT + Vector((0.0, 0.0, zt - c.z))
    src = c - o * (tb - 0.3) + Vector((0.0, 0.0, zb - c.z))
    return lip, src


def spring_cleft(mb, rng, F, P0, o, s, zm, w_lip):
    """fenda na FACE do penhasco (queda sul, sem bancada): fundo escuro recuado, sobrancelha, ombreiras de colunas de
    basalto de alturas diferentes e SOLEIRA-BICA com 2 bochechas convergentes (calha). Devolve (labio, boca, face)."""
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
    # soleira: laje de basalto em balanco (bica natural), frente larga o bastante para a calha
    q = A(face, 0.0)
    sill = poly_frame(q, o, s, [(-1.0, -3.0), (2.0, -2.9), (2.6, -2.1), (2.7, 0.0), (2.6, 2.1), (2.0, 3.0), (-1.0, 3.1)])
    mb.prism(SL.ccw(sill), zm - 1.6, zm - 0.3, ROCK, bevel=0.15)
    # bochechas da calha: convergem de +-2,2 (fundo) para +-w_lip/2 (ponta)
    lipx = 2.62

    def lin(a):
        t = max(0.0, min(1.0, (a + 1.0) / (lipx + 1.0)))
        return 2.2 + (w_lip / 2 - 2.2) * t
    banks(mb, q, o, s, -1.0, lipx - 0.2, lin, zm - 0.3, 0.6, 0.34, w=0.8, ph=1.3, zbot=zm - 0.7)
    # ombreiras: colunas hexagonais de alturas diferentes
    for sd, (h0, h1) in ((-1, (6.5, 4.2)), (1, (8.0, 3.0))):
        for j in range(2):
            q2 = A(face + 0.3 - j * 1.4, sd * (3.9 + j * 1.6 + rng.uniform(-0.2, 0.2)))
            r = rng.uniform(1.25, 1.6)
            zt = zm + (h1 if j == 0 else h1 + rng.uniform(1.0, 2.2))
            mb.prism(SL.ccw(hexp(q2.x, q2.y, r, ang + rng.uniform(0, 1))), zm - h0 - j * 2.0, zt, ROCK, bevel=0.15)
            mb.prism(SL.ccw(hexp(q2.x, q2.y, r * 0.92, ang + rng.uniform(0, 1))), zt, zt + 0.25, TOP)
    # sobrancelha: bloco de colunas deitado por cima da boca
    q2 = A(face + 0.2, rng.uniform(-0.3, 0.3))
    brow = poly_frame(q2, o, s, [(-1.8, -3.6), (1.2, -3.2), (1.5, 0.0), (1.1, 3.4), (-1.8, 3.8)])
    mb.prism(SL.ccw(brow), zm + 3.0, zm + 4.6, ROCK, bevel=0.15)
    mb.prism(SL.ccw(poly_frame(q2, o, s, [(-1.6, -3.3), (0.9, -2.9), (1.2, 0.0), (0.8, 3.1), (-1.6, 3.5)])),
             zm + 4.6, zm + 4.85, TOP)
    return A(face + lipx, 0.0, zm - 0.3), A(face - 0.7, 0.0, zm - 0.3), face


# ------------------------------------------------------------------ uma queda
# largura da cortina medida (so para os marcadores: labio = W_LIP, abre, altura da abertura, pe)
WPROF = {"West": (5.4, 6.3, 12.0, 6.8), "East": (5.4, 6.2, 12.0, 6.6), "North": (5.4, 6.5, 12.0, 7.0),
         "South": (3.8, 4.4, 12.0, 4.7)}


def _set_marker(name, loc, yaw, props):
    """ATUALIZA um marcador do sg_core com o medido (nunca cria); avisa se a tabela do sg_core ficou velha"""
    ob = bpy.data.objects.get(name)
    if ob is None:
        print("WATER AVISO marcador %s nao existe (sg_core.fx_markers / FALL_FX)" % name)
        return
    d = (Vector(loc) - ob.location).length
    if d > 0.3:
        print("WATER AVISO %s: sg_core.FALL_FX difere %.2f do medido (corrigido aqui; atualize a tabela)" % (name, d))
    ob.location = Vector(loc)
    ob.rotation_euler = (0.0, 0.0, yaw)
    for k, v in props.items():
        ob[k] = v


def markers(n, tag, cur, lip, src, o, kind):
    yaw = yaw_to(o.x, o.y)
    pts, ws = cur.path()
    _set_marker("FX_Fall_%d_Lip" % n, lip, yaw, {
        "fx": "nevoa_borda", "kind": kind, "width": W_LIP[tag], "channel_w0": W_SRC if kind == "bancada" else 4.4,
        "src_pos": tuple(round(v, 3) for v in src), "drop": round(lip.z - cur.z_bot, 2), "depth_hint": 0.25,
        "waypoints": ";".join("%.2f,%.2f,%.2f" % tuple(p) for p in pts),
        "widths": ";".join("%.2f" % w for w in ws)})
    brk = sorted(cur.breaks, key=lambda b: -b[0])          # de cima para baixo
    names = ["FX_Fall_%d_Step" % n] if len(brk) == 1 else ["FX_Fall_%d_Step_Upper" % n, "FX_Fall_%d_Step" % n]
    if len(brk) > 2:
        print("WATER AVISO %s: %d quebras (marcadores so para as 2 de baixo)" % (tag, len(brk)))
        brk = brk[-2:]
    for nm, (zl, a0, a1) in zip(names, brk):
        q = cur.c + cur.o * ((a0 + a1) / 2.0) + Vector((0.0, 0.0, zl - cur.c.z))
        _set_marker(nm, q, yaw, {"fx": "espuma_degrau", "width": round(cur.width(zl), 2), "jump": round(a1 - a0, 2)})
    _set_marker("FX_Fall_%d_Base" % n, cur.foot(), yaw, {"fx": "nevoa_base", "width": round(cur.width(cur.z_bot), 2)})


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
        lip, src = spring_bench(mb, F, c, o, s, min(8.0, max(2.5, run - 1.2)), W_LIP[tag], ph=i * 1.1)
        kind = "bancada"
    else:
        P0 = Vector((x, y, 0.0))
        lip, src, face = spring_cleft(mb, rng, F, P0, o, s, z, W_LIP[tag])
        run = face
        kind = "fenda"
    F.add_bmesh(mb.bm)                      # a cortina (medida) passa por fora da bica e das margens
    cur = Curtain(F, lip, (o.x, o.y), Z_END, WPROF[tag], lip=1.0, clear=1.1, drift=0.008, name=tag)
    markers(i + 1, tag, cur, lip, src, o, kind)
    INFO[tag] = dict(kind=kind, lip=tuple(round(v, 2) for v in lip), src=tuple(round(v, 2) for v in src),
                     run=round(run, 2), breaks=[(round(zz, 1), round(a0, 1), round(a1, 1)) for zz, a0, a1 in cur.breaks],
                     foot=tuple(round(v, 1) for v in cur.foot()), polys=F.npolys)
    return mb.finish()


# ------------------------------------------------------------------ build
def build():
    INFO.clear()
    for i, ((x, y, z, deg), tag) in enumerate(zip(L.WATERFALLS, TAGS)):
        fall(i, x, y, z, deg, tag, 7301 + 97 * i)
    if DEBUG:
        for i, tag in enumerate(TAGS):
            d = INFO.get(tag, {})
            print("WATER %s %s labio=%s boca=%s corrida=%s pe=%s polys=%s quebras=%s" % (
                tag, d.get("kind"), d.get("lip"), d.get("src"), d.get("run"), d.get("foot"), d.get("polys"),
                d.get("breaks")))
            for nm in ("Lip", "Step_Upper", "Step", "Base"):
                ob = bpy.data.objects.get("FX_Fall_%d_%s" % (i + 1, nm))
                if ob is not None:
                    print("WATER FALL_FX %s (%.2f, %.2f, %.2f) width=%s" % (ob.name, *ob.location, ob.get("width")))
