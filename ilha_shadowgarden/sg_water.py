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
# ONDA 2 / o2b (2026-10-01, PLANTA v4): roda no build (build_sg.ZONE_MODULES water) e o blockout SG_Water_Lips sai.
#   - quedas: mesma pedra (bica, calha, boca/fenda) sobre a rocha NOVA do sg_terrain (onda 1f); os FX_Fall_* sao
#     MEDIDOS de novo (labio na borda real da bica, degrau no basalto, pe, waypoints/widths por raio). A cortina
#     desvia tambem da ponte de chegada e da saida (SG_Ent_ / SG_Exit_). Mirantes e rotas do QA na planta v4.
#   - so 2 materiais nas bicas de bancada (o fundo da boca e a misula em Cliff_Rock_SG recuado: 4 quedas = 9 MeshParts);
#   - ESPELHOS D'AGUA medidos na pedra que estiver na cena (o Blender so faz a pedra, a agua e do Roblox), todos no
#     mesmo idioma da fonte: marcador no CENTRO e no NIVEL da lamina, 'level', 'floor', 'depth', 'shape' e a medida
#     da lamina ('radius'/'apothem'/'sides' no poligono, 'sx'/'sy' no retangulo, sx no X local e sy no Y local = fwd):
#       WATER_Fountain_Basin / _Bowl_<n> (fonte da praca, sg_village), WATER_Fountain_Spout_<n> (land_pos conferido);
#       WATER_CavePool (rio do salao sombrio, sg_cave: + bridge_x0/x1 = corpo da ponte do eixo, que corta a lamina);
#       WATER_CaveFall_Lip / _Base (queda da fenda NE: labio na borda da bica de pedra, waypoints/widths ate o rio);
#       WATER_Court_L / _R (espelhos do patio; o sg_court, quando roda depois, sincroniza com a bacia dele).
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
POOLS = {}                       # marcador -> medida da lamina (espelhos d'agua)
W_LIP = {"West": 5.4, "East": 5.4, "North": 5.4, "South": 3.8}    # largura da calha na bica (= width do FX_Fall_n_Lip)
W_SRC = 2.4                      # largura da boca da nascente (bancada)
SPOUT = 1.1                      # bica: avanco alem da crista da bancada
SPOUT_DROP = 0.12                # bica: topo abaixo da bancada (a agua desce um dedo antes de cair)

# (tag, ponto do mirante (x, y, piso)) - onde o jogador para e olha o labio (planta v4)
MIRANTES = {
    "West": (-172.0, -62.0, L.P2),              # P2 oeste, atras da bica (rua do P2 em y -86; casa H6 a leste)
    "East": (156.0, -200.0, L.P1),              # atras da bica, ao fim da rua leste do P1 (praca -> leste)
    "North": (-74.0, 358.0, L.P3),              # terraco norte, entre a rota da saida e os pinheiros da borda
    "South": (0.0, -400.0, L.DECK),             # na PONTE DE CHEGADA: a fenda sul so se ve dela (a calcada a esconde)
}
# (linha de visada do olho 5,2 ate o labio conferida por raio na cena inteira)


def _cams():
    cams = {}
    for (x, y, z, deg), tag in zip(L.WATERFALLS, TAGS):
        a = math.radians(deg)
        ux, uy = math.cos(a), math.sin(a)
        sx, sy = -uy, ux
        # de perto (fora da ilha, um pouco abaixo do labio, de lado)
        cams["CAM_SGWater_%s_Near" % tag] = ((x + ux * 46.0 + sx * 20.0, y + uy * 46.0 + sy * 20.0, z + 2.0),
                                             (x + ux * 2.0, y + uy * 2.0, z - 16.0), 24)
        # bica de perto (o2b: com os marcadores Lip/Step/Base e os waypoints no render de conferencia)
        cams["CAM_SGWater_%s_Spout" % tag] = ((x + ux * 14.0 + sx * 9.0, y + uy * 14.0 + sy * 9.0, z + 5.0),
                                              (x, y, z - 1.0), 26)
        # de baixo (acima do mar de nuvens, olhando a cortina subir ate o labio)
        cams["CAM_SGWater_%s_Below" % tag] = ((x + ux * 34.0 - sx * 16.0, y + uy * 34.0 - sy * 16.0, -24.0),
                                              (x + ux * 1.0, y + uy * 1.0, z - 18.0), 22)
        # altura do jogador no mirante do labio (olho 5,2 acima do piso)
        mx, my, mz = MIRANTES[tag]
        cams["CAM_SGWater_%s_PlayerHeight" % tag] = ((mx, my, mz + 5.2), (x + ux * 3.0, y + uy * 3.0, z - 2.0), 22)
    # fonte da praca, rio e queda do salao sombrio, espelhos do patio
    fx, fy = L.PLAZA_C
    cams["CAM_SGWater_Fountain"] = ((fx + 16.0, fy - 17.0, L.P1 + 9.0), (fx, fy, L.P1 + 3.2), 26)
    cams["CAM_SGWater_FountainPH"] = ((fx - 2.0, fy - 22.0, L.P1 + 5.2), (fx, fy, L.P1 + 3.6), 24)
    cams["CAM_SGWater_CaveRiver"] = ((44.0, 236.0, L.CAVE_FLOOR + 9.0), (66.0, 206.0, L.CAVE_FLOOR + 6.0), 18)
    cams["CAM_SGWater_Court"] = ((0.0, 4.0, L.P3 + 9.0), (52.0, 40.0, L.P3), 22)
    return cams


CAMS = _cams()

# rotas extras: o jogador chega a pe em cada mirante (a agua nao pode bloquear nada)
EXTRA_ROUTES = {
    "WATER_mirante_oeste": ([(-140.0, -86.0), (-160.0, -80.0), MIRANTES["West"][:2]], L.P2),
    "WATER_mirante_leste": ([(96.0, -222.0), (138.0, -222.0), MIRANTES["East"][:2]], L.P1),
    "WATER_mirante_norte": ([(-132.0, 290.0), (-116.0, 330.0), (-96.0, 348.0), MIRANTES["North"][:2]], L.P3),
    "WATER_mirante_sul": ([(0.0, -336.0), (0.0, -370.0), MIRANTES["South"][:2]], L.DECK),
}
EXTRA_PROBES = []
PREFIX = ("SG_Ter_", "SG_Ent_", "SG_Exit_")      # o que a cortina tem de contornar (rocha, ponte de chegada, saida)


# ------------------------------------------------------------------ raios contra o terreno (tecnica da Ilha 2)
class Face:
    """BVH das malhas SG_Ter_* (poligonos a menos de R de (cx, cy)) + BVHs extras (as rochas desta zona)"""

    def __init__(self, cx, cy, R, prefix=PREFIX):
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
    mb.prism(SL.ccw(q), zb - 0.2, zb + top - 0.5, ROCK)      # o2b: rocha recuada na sombra da verga (era DARK)
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
    mb.prism(SL.ccw(poly_frame(c, o, s, corb)), zt - 1.9, zt - 0.8, ROCK, bevel=0.1)   # o2b: era DARK (1 MeshPart)
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
        print("WATER medido %s: %.2f da estimativa do sg_core (o marcador fica no MEDIDO)" % (name, d))
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


# ------------------------------------------------------------------ espelhos d'agua (fonte, rio da caverna, patio)
class Probe:
    """BVH das malhas com os prefixos dados cujo contorno passa perto de (cx, cy) (raio R)"""

    def __init__(self, cx, cy, R, prefix):
        verts, polys = [], []
        for o in bpy.data.objects:
            if o.type != "MESH" or not o.name.startswith(prefix) or o.name.startswith("COL_"):
                continue
            me = o.data
            if not me.polygons:
                continue
            M = o.matrix_world
            bb = [M @ Vector(c) for c in o.bound_box]
            if (max(v.x for v in bb) < cx - R or min(v.x for v in bb) > cx + R or
                    max(v.y for v in bb) < cy - R or min(v.y for v in bb) > cy + R):
                continue
            co = np.empty(len(me.vertices) * 3, dtype=np.float64)
            me.vertices.foreach_get("co", co)
            co = co.reshape(-1, 3)
            A = np.array(M)
            co = co @ A[:3, :3].T + A[:3, 3]
            base = len(verts)
            verts.extend(Vector(v) for v in co)
            polys.extend([base + i for i in p.vertices] for p in me.polygons)
        self.tree = BVHTree.FromPolygons(verts, polys) if polys else None

    def hit(self, org, d, dist):
        if self.tree is None:
            return None
        h = self.tree.ray_cast(Vector(org), Vector(d).normalized(), dist)
        return None if h[0] is None else h[3]

    def down(self, x, y, z0, dist):
        h = self.hit((x, y, z0), (0.0, 0.0, -1.0), dist)
        return None if h is None else z0 - h


def _median(v):
    v = sorted(x for x in v if x is not None)
    return v[len(v) // 2] if v else None


def _level_ok(ob, floor, rim):
    """mantem o nivel de projeto se ele fica entre o fundo e a borda; senao, 0,2 abaixo da borda"""
    lev = ob.location.z
    if floor is not None and rim is not None and not (floor + 0.08 < lev < rim - 0.02):
        lev = rim - 0.2
    return lev


def basin_poly(name, prefix, seek_hole=True):
    """lamina POLIGONAL (fonte): centro no marcador; mede o raio no vertice (fwd), o apotema (meio do lado), o fundo, a
    borda e o fuste que atravessa a agua. Atualiza o marcador (centro no NIVEL)."""
    ob = bpy.data.objects.get(name)
    if ob is None:
        return None
    c = ob.location.copy()
    P = Probe(c.x, c.y, 14.0, prefix)
    if P.tree is None:
        print("WATER AVISO %s: nenhuma pedra (%s) em volta" % (name, prefix))
        return None
    sides = int(ob.get("sides", 12))
    fw = ob.matrix_world.to_3x3() @ Vector((0.0, 1.0, 0.0))
    a0 = math.atan2(fw.y, fw.x)
    hole0 = float(ob.get("hole_r", 0.0))
    lev = c.z
    dz = Vector((0.0, 0.0, -0.03))
    rs, aps, holes = [], [], []
    for k in range(sides):
        for half, acc in ((0.0, rs), (0.5, aps)):
            a = a0 + 2 * math.pi * (k + half) / sides
            u = Vector((math.cos(a), math.sin(a), 0.0))
            r0 = hole0 + 0.25
            h = P.hit(c + u * r0 + dz, u, 12.0)
            if h is not None:
                acc.append(r0 + h)
                if seek_hole and half == 0.0 and hole0 > 0.0:
                    rr = r0 + h - 0.15
                    hh = P.hit(c + u * rr + dz, -u, rr)
                    if hh is not None:
                        holes.append(rr - hh)
    radius, apothem = _median(rs), _median(aps)
    if radius is None:
        print("WATER AVISO %s: borda nao encontrada no nivel %.2f" % (name, lev))
        return None
    hole = _median(holes) if holes else hole0
    rf = (hole + (apothem or radius)) / 2.0
    angs = (0.3, 1.9, 3.5, 5.1)
    floor = _median([P.down(c.x + rf * math.cos(a0 + t), c.y + rf * math.sin(a0 + t), lev + 0.02, 3.0) for t in angs])
    rr = radius + 0.3
    rim = _median([P.down(c.x + rr * math.cos(a0 + t), c.y + rr * math.sin(a0 + t), lev + 3.0, 4.0) for t in angs])
    nl = _level_ok(ob, floor, rim)
    ob.location.z = nl
    ob["radius"] = round(radius, 3)
    ob["apothem"] = round(apothem if apothem is not None else radius * math.cos(math.pi / sides), 3)
    if seek_hole:
        ob["hole_r"] = round(hole, 3)
    ob["level"] = round(nl, 3)
    if floor is not None:
        ob["floor"] = round(floor, 3)
        ob["depth"] = round(nl - floor, 3)
    if rim is not None:
        ob["rim"] = round(rim, 3)
    ob["shape"] = "poligono"
    return dict(radius=radius, apothem=apothem, hole=hole, floor=floor, rim=rim, level=nl)


def basin_rect(name, prefix, R=40.0, samples=None, cut=None):
    """lamina RETANGULAR (rio, espelhos): mede as faces de dentro no nivel a partir de pontos livres (samples, no
    referencial do marcador), o fundo e a borda; recentra o marcador e grava sx/sy (X/Y locais), level, floor, depth.
    cut = (u0, u1) pontos livres dos 2 lados de um corpo que atravessa a lamina (a ponte do rio): bridge_x0/x1 locais."""
    ob = bpy.data.objects.get(name)
    if ob is None:
        return None
    M3 = ob.matrix_world.to_3x3().normalized()
    ux, uy = M3 @ Vector((1.0, 0.0, 0.0)), M3 @ Vector((0.0, 1.0, 0.0))
    c = ob.location.copy()
    P = Probe(c.x, c.y, R + 10.0, prefix)
    if P.tree is None:
        print("WATER AVISO %s: nenhuma pedra (%s) em volta" % (name, prefix))
        return None
    lev = c.z - 0.03
    samples = samples or [(0.0, 0.0)]
    xs0, xs1, ys0, ys1, floors = [], [], [], [], []
    for su, sv in samples:
        o = c + ux * su + uy * sv
        o.z = lev
        for d, acc, base, sg in ((ux, xs1, su, 1), (-ux, xs0, su, -1), (uy, ys1, sv, 1), (-uy, ys0, sv, -1)):
            h = P.hit(o, d, R * 2.0)
            if h is not None:
                acc.append(base + sg * h)
        floors.append(P.down(o.x, o.y, lev + 0.02, 4.0))
    if not (xs0 and xs1 and ys0 and ys1):
        print("WATER AVISO %s: faces da bacia nao encontradas" % name)
        return None
    if cut is None:
        x0, x1 = max(xs0), min(xs1)
    else:                                              # o corpo da ponte nao conta como face da bacia
        x0, x1 = min(xs0), max(xs1)
    y0, y1 = max(ys0), min(ys1)
    floor = _median(floors)
    rims = []
    for pu, pv in (((x0 + x1) / 2 + (40.0 if cut else 0.0), y1 + 0.35), ((x0 + x1) / 2 + (40.0 if cut else 0.0), y0 - 0.35),
                   (x0 - 0.35, (y0 + y1) / 2), (x1 + 0.35, (y0 + y1) / 2)):
        p = c + ux * pu + uy * pv
        rims.append(P.down(p.x, p.y, lev + 3.0, 4.0))
    rims = [z for z in rims if z is not None]
    rim = min(rims) if rims else None
    nl = _level_ok(ob, floor, rim)
    mu, mv = (x0 + x1) / 2, (y0 + y1) / 2
    newc = c + ux * mu + uy * mv
    newc.z = nl
    out = dict(x0=x0 - mu, x1=x1 - mu, y0=y0 - mv, y1=y1 - mv, floor=floor, rim=rim, level=nl, c=newc.copy(),
               ux=ux.copy(), uy=uy.copy())
    if cut is not None:
        ha = P.hit(c + ux * cut[1] + Vector((0, 0, lev - c.z)), -ux, abs(cut[1] - cut[0]))
        hb = P.hit(c + ux * cut[0] + Vector((0, 0, lev - c.z)), ux, abs(cut[1] - cut[0]))
        if ha is not None and hb is not None:
            bx0, bx1 = cut[0] + hb - mu, cut[1] - ha - mu
            ob["bridge_x0"], ob["bridge_x1"] = round(bx0, 2), round(bx1, 2)
            out["bridge"] = (bx0, bx1)
    ob.location = newc
    ob["sx"], ob["sy"] = round(x1 - x0, 3), round(y1 - y0, 3)
    ob["level"] = round(nl, 3)
    if floor is not None:
        ob["floor"] = round(floor, 3)
        ob["depth"] = round(nl - floor, 3)
    if rim is not None:
        ob["rim"] = round(rim, 3)
    ob["shape"] = "retangulo"
    return out


def fountain():
    """fonte da praca (sg_village.plaza desenha com as cotas do sg_core): bacia + 2 tacas medidas; as bicas so sao
    conferidas (land_pos dentro da lamina de destino, no nivel dela)"""
    res = {}
    for nm in ("WATER_Fountain_Basin", "WATER_Fountain_Bowl_1", "WATER_Fountain_Bowl_2"):
        res[nm] = basin_poly(nm, ("SG_Vil_Fountain",))
    for ob in [o for o in bpy.data.objects if o.name.startswith("WATER_Fountain_Spout_")]:
        dst = bpy.data.objects.get("WATER_Fountain_" + str(ob.get("to", "")))
        lp = ob.get("land_pos")
        if dst is None or lp is None:
            continue
        lp = Vector(tuple(lp))
        r = math.hypot(lp.x - dst.location.x, lp.y - dst.location.y)
        ok = float(dst.get("hole_r", 0.0)) + 0.2 < r < float(dst.get("apothem", dst.get("radius", 99.0))) - 0.2
        lp.z = dst.location.z
        ob["land_pos"] = (round(lp.x, 3), round(lp.y, 3), round(lp.z, 3))
        ob["drop"] = round(ob.location.z - lp.z, 2)
        if not ok:
            print("WATER AVISO %s: o jato cai fora da lamina de %s (r %.2f)" % (ob.name, dst.name, r))
    return res


def _ray_enter(lu, lv, du, dv, x0, x1, y0, y1):
    """distancia ao longo de (du, dv) ate o raio que sai de (lu, lv) entrar no retangulo (slab)"""
    t0, t1 = -1e9, 1e9
    for p, d, a, b in ((lu, du, x0, x1), (lv, dv, y0, y1)):
        if abs(d) < 1e-9:
            if not (a <= p <= b):
                return None
            continue
        ta, tb = (a - p) / d, (b - p) / d
        t0, t1 = max(t0, min(ta, tb)), min(t1, max(ta, tb))
    return t0 if t0 <= t1 else None


def cave_water():
    """rio escuro do salao sombrio (sg_cave) e a queda da fenda NE (labio na borda REAL da bica de pedra; a cortina
    passa por fora do meio-fio e cai DENTRO do rio)"""
    if not any(o.name.startswith("SG_Cave_") for o in bpy.data.objects):
        print("WATER AVISO salao sombrio sem detalhe: WATER_Cave* ficam com a estimativa do sg_core")
        return None
    rv = bpy.data.objects.get("WATER_CavePool")
    if rv is not None:
        # o sg_core gravava sx = extensao em X do mundo com a frente em +X (sx caia no Y local): a frente passa a +Y,
        # o mesmo referencial dos espelhos do patio (sx = X local = X do mundo, sy = Y local = fwd)
        rv.rotation_euler = (0.0, 0.0, yaw_to(0.0, 1.0))
        bpy.context.view_layer.update()
    pool = basin_rect("WATER_CavePool", ("SG_Cave_",), R=95.0,
                      samples=[(-40.0, 0.0), (40.0, 0.0), (-70.0, 0.0), (70.0, 0.0)], cut=(-30.0, 30.0))
    lip_ob, base_ob = bpy.data.objects.get("WATER_CaveFall_Lip"), bpy.data.objects.get("WATER_CaveFall_Base")
    if lip_ob is None or base_ob is None or pool is None:
        return pool
    fw = lip_ob.matrix_world.to_3x3() @ Vector((0.0, 1.0, 0.0))
    o = Vector((fw.x, fw.y, 0.0)).normalized()
    s = Vector((-o.y, o.x, 0.0))
    p0 = lip_ob.location.copy()
    P = Probe(p0.x, p0.y, 30.0, ("SG_Cave_",))
    # borda da bica: o ultimo ponto (no eixo, andando para fora) com piso de pedra na cota do labio
    edge = None
    for k in range(-60, 61):
        q = p0 + o * (k * 0.05)
        z = P.down(q.x, q.y, p0.z + 0.6, 1.4)
        if z is not None and abs(z - p0.z) < 0.35:
            edge = (k * 0.05, z)
    if edge is None:
        print("WATER AVISO WATER_CaveFall_Lip: bica de pedra nao encontrada")
        return pool
    lip = p0 + o * edge[0]
    lip.z = edge[1]
    # largura do canal (faces de dentro das 2 bochechas, 1 atras da borda)
    wl = [P.hit(lip - o * 1.0 + Vector((0, 0, 0.3)), s * sg, 4.0) for sg in (-1, 1)]
    width = (wl[0] + wl[1]) if all(w is not None for w in wl) else float(lip_ob.get("width", 4.0))
    # a lamina tem de cair DENTRO do rio: avanco ate entrar no retangulo da lamina + 1,5
    c, ux, uy = pool["c"], pool["ux"], pool["uy"]
    rel = lip - c
    t_in = _ray_enter(rel.dot(ux), rel.dot(uy), o.dot(ux), o.dot(uy), pool["x0"], pool["x1"], pool["y0"], pool["y1"])
    need = max(1.0, (t_in if t_in is not None else 0.0) + 1.5)
    F = Face(lip.x, lip.y, 30.0, prefix=("SG_Cave_",))
    drift = 0.004
    H = lip.z - pool["level"]
    lip_throw = max(1.0, need - drift * max(0.0, H - 3.0))
    cur = Curtain(F, lip, (o.x, o.y), pool["level"], (width, width * 1.12, 10.0, width * 1.3), lip=lip_throw,
                  clear=0.8, drift=drift, name="CaveFall")
    pts, ws = cur.path()
    yaw = yaw_to(o.x, o.y)
    _set_marker("WATER_CaveFall_Lip", lip, yaw, {
        "width": round(width, 2), "drop": round(lip.z - cur.z_bot, 2), "to": "WATER_CavePool", "kind": "fenda",
        "waypoints": ";".join("%.2f,%.2f,%.2f" % tuple(p) for p in pts), "widths": ";".join("%.2f" % w for w in ws),
        "note": "queda da fenda NE do salao sombrio: borda da bica no nivel da pedra; agua do Roblox"})
    foot = cur.foot()
    _set_marker("WATER_CaveFall_Base", foot, yaw, {"fx": "nevoa_base", "width": round(cur.width(cur.z_bot), 2),
                                                   "level": round(pool["level"], 3)})
    INFO["CaveFall"] = dict(lip=tuple(round(v, 2) for v in lip), foot=tuple(round(v, 2) for v in foot),
                            width=round(width, 2), throw=round(lip_throw, 2), enter=t_in)
    return pool


def court_water():
    """espelhos do patio: mede a bacia que estiver na cena (blockout do vestir ou sg_court)"""
    res = {}
    for nm in ("L", "R"):
        res[nm] = basin_rect("WATER_Court_%s" % nm, ("SG_Prop_", "SG_Court", "SG_Veg_", "SG_Gar"), R=24.0,
                             samples=[(0.0, 0.0), (-4.0, -3.0), (4.0, 3.0)])
    return res



def _alias(n):
    import fm_lib
    return fm_lib.alias(n)


# ------------------------------------------------------------------ z-fight: alivio automatico (onda 2, o2b)
# REGRA do brief (z-fighting): nenhuma face visivel coplanar ou a menos de 0,05 de outra face paralela de material
# diferente; janela/brilho a >= 0,12. O desenho APROVADO da torre (codigo da Ilha 1), da base e da alquimia tinha ~270
# pares assim (relatorio 19_zfight: F12/F13). Em vez de redesenhar peca a peca, este passe roda DEPOIS do build da
# zona: acha os pares de tris (mesmo sentido, cos > 0,995, planos a < 0,05 - ou < 0,13 com janela/brilho - e
# sobreposicao no plano) e move SO os vertices da ilha (componente conexa) MENOR que estao naquele plano: a peca cresce
# ou recua 0,03 a 0,13 na normal, para o lado em que ja estava (coplanar exato: para fora); o resto da peca fica.
# Pecas de outros donos (terreno, vila) sao so referencia e nunca mudam.
def _is_glow(m):
    return "Glow" in m or m.startswith("Window_")


def _mesh_tris(o, oi):
    """tris do objeto no mundo (numpy): pontos (n,3,3), material, ilha (componente conexa) de cada tri"""
    import numpy as np
    me = o.data
    me.calc_loop_triangles()
    n = len(me.loop_triangles)
    nv = len(me.vertices)
    if not n or not nv:
        return None
    co = np.empty(nv * 3)
    me.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3)
    A = np.array(o.matrix_world)
    co = co @ A[:3, :3].T + A[:3, 3]
    vi = np.empty(n * 3, dtype=np.int64)
    me.loop_triangles.foreach_get("vertices", vi)
    vi = vi.reshape(-1, 3)
    mi = np.empty(n, dtype=np.int64)
    me.loop_triangles.foreach_get("material_index", mi)
    ed = np.empty(len(me.edges) * 2, dtype=np.int64)
    me.edges.foreach_get("vertices", ed)
    ed = ed.reshape(-1, 2)
    lab = np.arange(nv)
    while len(ed):                                   # rotulo minimo propagado pelas arestas (componentes conexas)
        m = np.minimum(lab[ed[:, 0]], lab[ed[:, 1]])
        chg = (lab[ed[:, 0]] != m) | (lab[ed[:, 1]] != m)
        if not chg.any():
            break
        np.minimum.at(lab, ed[:, 0], m)
        np.minimum.at(lab, ed[:, 1], m)
        lab = lab[lab]
    names = [_alias(mm.name) if mm else "-" for mm in me.materials] or ["-"]
    return dict(o=o, oi=oi, co=co, vi=vi, P=co[vi], mat=[names[min(k, len(names) - 1)] for k in mi], isl=lab[vi[:, 0]],
                lab=lab)


def zf_relief(mine, others=(), gap=0.08, glow_gap=0.13, passes=5, min_area=0.01, verbose=True):
    """mine: objetos MESH desta zona (editaveis); others: vizinhos (so referencia). Devolve o numero de ajustes."""
    import numpy as np
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    mine = [o for o in mine if o is not None and o.type == "MESH" and not o.name.startswith("COL_")]
    others = [o for o in others if o is not None and o.type == "MESH" and not o.name.startswith("COL_")]
    nmine = len(mine)
    total = 0
    moved_keys = set()
    for it in range(passes):
        data = [_mesh_tris(o, k) for k, o in enumerate(mine + others)]
        data = [d for d in data if d is not None]
        P = np.concatenate([d["P"] for d in data])
        owner = np.concatenate([np.full(len(d["P"]), d["oi"]) for d in data])
        isl = np.concatenate([d["isl"] for d in data])
        mats = [m for d in data for m in d["mat"]]
        mid = {m: k for k, m in enumerate(sorted(set(mats)))}
        matn = np.array([mid[m] for m in mats])
        glow = np.array([_is_glow(m) for m in sorted(set(mats))])[matn]
        cr = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0])
        ln = np.linalg.norm(cr, axis=1)
        area = ln / 2.0
        ok = area > 1e-5
        nrm = np.zeros_like(cr)
        nrm[ok] = cr[ok] / ln[ok, None]
        cen = P.mean(axis=1)
        rad = np.max(np.linalg.norm(P - cen[:, None, :], axis=2), axis=1)
        pd = np.einsum("ij,ij->i", nrm, cen)
        gkey = owner * 10000000 + isl
        ukey, ginv = np.unique(gkey, return_inverse=True)
        garea = np.bincount(ginv, weights=area)
        PT = [(Vector(t[0]), Vector(t[1]), Vector(t[2])) for t in P]
        CV = [Vector(c) for c in cen]
        NR = [Vector(v) for v in nrm]
        MT, GI, GL, AR, OW = matn.tolist(), ginv.reshape(-1).tolist(), glow.tolist(), area.tolist(), owner.tolist()
        GA = garea.tolist()

        def barycentric(p, tri):
            a, b, c = tri
            v0, v1, v2 = b - a, c - a, p - a
            d00, d01, d11 = v0.dot(v0), v0.dot(v1), v1.dot(v1)
            den = d00 * d11 - d01 * d01
            if abs(den) < 1e-12:
                return None
            d20, d21 = v2.dot(v0), v2.dot(v1)
            v = (d11 * d20 - d01 * d21) / den
            w = (d00 * d21 - d01 * d20) / den
            return (1.0 - v - w, v, w)
        tree = BVHTree.FromPolygons([Vector(v) for v in P.reshape(-1, 3)],
                                    [(3 * i, 3 * i + 1, 3 * i + 2) for i in range(len(P))])
        moves = {}
        # prefiltro: so consulta tris cujo PLANO (normal ~0,08 rad, offset 0,15; 2 grades defasadas) tem outro material
        cand = np.zeros(len(P), dtype=bool)
        for sh in (0.0, 0.5):
            keys = np.column_stack([np.floor(nrm * 12.0 + sh), np.floor(pd / 0.15 + sh)]).astype(np.int64)
            _, kinv = np.unique(keys, axis=0, return_inverse=True)
            kinv = kinv.reshape(-1)
            pm = np.unique(np.column_stack([kinv, matn]), axis=0)
            cnt = np.bincount(pm[:, 0], minlength=int(kinv.max()) + 1)
            cand |= cnt[kinv] >= 2
        sel = (owner < nmine) & (area > min_area) & cand
        if it > 0:                                   # passes seguintes: so as ilhas que andaram
            sel &= np.isin(gkey, np.array(sorted(moved_keys), dtype=np.int64))
        q = np.nonzero(sel)[0]
        for i in q.tolist():
            ci, ni, mi_, gi = CV[i], NR[i], MT[i], GI[i]
            for loc, nn, j, dist in tree.find_nearest_range(ci, float(rad[i]) + glow_gap):
                if j == i or MT[j] == mi_ or GI[j] == gi or AR[j] < 1e-4:
                    continue
                nj = NR[j]
                if ni.dot(nj) < 0.995:
                    continue
                d = nj.dot(ci - PT[j][0])                    # quanto o meu tri esta na frente do outro
                gl = GL[i] or GL[j]
                if abs(d) >= (glow_gap - 0.004 if gl else 0.06):
                    continue
                # sobreposicao no plano: amostras de cada tri dentro do outro (baricentrica)
                hit = False
                for a, b in ((i, j), (j, i)):
                    pb = PT[b]
                    ca = CV[a]
                    for pt in (ca, ca + (PT[a][0] - ca) * 0.7, ca + (PT[a][1] - ca) * 0.7, ca + (PT[a][2] - ca) * 0.7):
                        bc = barycentric(pt, pb)
                        if bc is not None and bc[1] > 0.02 and bc[2] > 0.02 and bc[1] + bc[2] < 0.98:
                            hit = True
                            break
                    if hit:
                        break
                if not hit:
                    continue
                if OW[j] >= nmine or GA[gi] <= GA[GI[j]]:
                    k, dm, pn, pp = i, d, nrm[i], pd[i]
                else:
                    k, dm, pn, pp = j, -d, nrm[j], pd[j]
                delta = (1.0 if dm >= 0.0 else -1.0) * ((glow_gap if gl else gap) - abs(d))
                key = (int(owner[k]), int(isl[k]))
                old = moves.get(key)
                if old is None or abs(delta) > abs(old[2]):
                    moves[key] = (pn.copy(), float(pp), delta)
        if not moves:
            break
        byobj = {}
        for (oi, il), mv in moves.items():
            byobj.setdefault(oi, []).append((il, mv))
        for d in data:
            if d["oi"] not in byobj:
                continue
            o = d["o"]
            co = d["co"].copy()
            for il, (pn, pp, delta) in byobj[d["oi"]]:
                isl_v = d["lab"] == il
                pj = co[isl_v] @ pn
                sel = isl_v & (np.abs(co @ pn - pp) < 0.012)
                # nunca achata nem inverte a peca: o plano nao pode passar por outro vertice da propria ilha
                lo, hi = (pp + delta - 0.03, pp - 0.012) if delta < 0 else (pp + 0.012, pp + delta + 0.03)
                if np.any((pj > lo) & (pj < hi)):
                    continue
                co[sel] += pn * delta
            Mi = np.array(o.matrix_world.inverted())
            loc = co @ Mi[:3, :3].T + Mi[:3, 3]
            o.data.vertices.foreach_set("co", loc.reshape(-1))
            o.data.update()
        total += len(moves)
        moved_keys = {oi * 10000000 + il for (oi, il) in moves}
        if verbose:
            print("ZF alivio passe %d: %d pecas ajustadas" % (it + 1, len(moves)))
    return total


def zone_relief(mine_prefix, near_prefix=("SG_Ter_", "SG_Vil_", "SG_Ent_", "SG_Prop_"), pad=2.0, **kw):
    """alivio de z-fight de uma zona: as malhas com mine_prefix (editaveis) contra elas mesmas e os vizinhos cujo
    contorno toca o delas (so referencia)"""
    import time
    from mathutils import Vector
    t = time.time()
    mine = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(mine_prefix)]
    if not mine:
        return 0
    bb = [o.matrix_world @ Vector(c) for o in mine for c in o.bound_box]
    x0, x1 = min(v.x for v in bb) - pad, max(v.x for v in bb) + pad
    y0, y1 = min(v.y for v in bb) - pad, max(v.y for v in bb) + pad
    others = []
    for o in bpy.data.objects:
        if o.type != "MESH" or not o.name.startswith(near_prefix) or o in mine:
            continue
        b2 = [o.matrix_world @ Vector(c) for c in o.bound_box]
        if max(v.x for v in b2) > x0 and min(v.x for v in b2) < x1 and max(v.y for v in b2) > y0 and                 min(v.y for v in b2) < y1:
            others.append(o)
    n = zf_relief(mine, others, **kw)
    print("ZF alivio %s: %d ajustes (%d vizinhos) %.1fs" % (mine_prefix, n, len(others), time.time() - t))
    return n


# ------------------------------------------------------------------ build
def build():
    INFO.clear()
    for i, ((x, y, z, deg), tag) in enumerate(zip(L.WATERFALLS, TAGS)):
        fall(i, x, y, z, deg, tag, 7301 + 97 * i)
    POOLS.clear()
    POOLS.update(fountain())
    POOLS["WATER_CavePool"] = cave_water()
    for k, v in court_water().items():
        POOLS["WATER_Court_" + k] = v
    zone_relief(("SG_Water_",))
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
        for ob in sorted([o for o in bpy.data.objects if o.name.startswith("WATER_")], key=lambda o: o.name):
            keys = [k for k in ("shape", "radius", "apothem", "hole_r", "sx", "sy", "level", "floor", "rim", "depth",
                                "bridge_x0", "bridge_x1", "width", "drop", "land_pos") if k in ob.keys()]
            print("WATER ESPELHO %s (%.2f, %.2f, %.2f) %s" % (ob.name, *ob.location, " ".join(
                "%s=%s" % (k, ob[k] if isinstance(ob[k], (str, int, float)) else tuple(round(v, 2) for v in ob[k]))
                for k in keys)))
        if "CaveFall" in INFO:
            print("WATER CAVEFALL", INFO["CaveFall"])
