# il_mining - PASS 3: fosso de mineracao em arte final (zona "mining", prefixo MINE_, colecao 03_MINING).
# Substitui il_blockout.mining(). Piso do fosso, muro e calcamento do anel sao do TERRENO; aqui fica tudo DENTRO do
# fosso e na borda dele:
#   escadas N/S (colisao identica a do blockout), rampas de madeira L/O (il_col.ramp_ends), cerca da borda (r FENCE_R,
#   mesmos vaos), toros de pedra na borda externa do anel, 4 torres de mineracao (L.DERRICKS), formacao central de
#   minerio (peca-heroi), minerio visivel em cada ponto de il_layout.ore_points() (1 objeto por raridade) e poucos
#   props de borda junto ao pe do muro. O centro fica amplo e livre (corredores de il_layout.lane_ends()).
import math, random, zlib
from mathutils import Vector
import il_lib as IL
from il_lib import MB, D, S, col_box, light
import il_layout as L
import fm_lib
import fm_parts as FP
from fm_parts import Frame
import fm_props_kit as PK
from il_col import ramp_ends

COLL = "03_MINING"
V = Vector

# ------------------------------------------------------------------ cameras de revisao (360 + altura do jogador)
CAMS = {
    "CAM_Mining_Player": ((0.0, -70.0, L.RING + 6.8), (0.0, -6.0, L.PIT + 2.0), 22),     # jogador no topo da escada S
    "CAM_Mining_Core": ((17.0, -23.0, L.PIT + 7.5), (0.0, 0.0, L.PIT + 7.0), 24),
    "CAM_Mining_Ramp": ((26.0, -30.0, L.PIT + 6.5), (54.0, 2.0, L.PIT + 4.0), 20),
    "CAM_Mining_Top": ((0.0, -38.0, 200.0), (0.0, 0.0, 0.0), 28),
    "CAM_Mining_S": ((0.0, -112.0, 46.0), (0.0, 0.0, L.PIT), 24),
    "CAM_Mining_N": ((0.0, 112.0, 46.0), (0.0, 0.0, L.PIT), 24),
    "CAM_Mining_E": ((112.0, 0.0, 46.0), (0.0, 0.0, L.PIT), 24),
    "CAM_Mining_W": ((-112.0, 0.0, 46.0), (0.0, 0.0, L.PIT), 24),
    "CAM_Mining_Floor": ((-12.0, -20.0, L.PIT + 4.6), (-40.0, -34.0, L.PIT + 5.0), 20),
    "CAM_Mining_CoreN": ((-14.0, 24.0, L.PIT + 6.0), (0.0, 0.0, L.PIT + 6.5), 24),
    "CAM_Mining_Ores": ((32.0, -9.0, L.PIT + 5.2), (14.0, 11.0, L.PIT + 1.5), 24),
}

# ------------------------------------------------------------------ materiais novos (4 de 5)
# cristal verde-agua (UNCOMMON) e dourado-laranja (SUPERLEGENDARY): casca + ponta brilhante (*_Glow)
_M = fm_lib.MATS.setdefault
# (emissao baixa na casca: com AgX a emissao alta lavava a cor para pastel; a ponta e que brilha)
_M("Crystal_MineTeal", (S(0, 178, 150), 0.15, 0.0, 0.35, S(0, 178, 150), 0.0))
_M("Crystal_MineTeal_Glow", (S(70, 255, 212), 0.15, 0.0, 1.6, S(60, 255, 205), 0.0))
_M("Crystal_MineGold", (S(255, 136, 0), 0.2, 0.0, 0.4, S(255, 128, 0), 0.0))
_M("Crystal_MineGold_Glow", (S(255, 212, 50), 0.2, 0.0, 1.8, S(255, 196, 40), 0.0))


class MMB(MB):
    """MB da zona: colecao fixa, detalhe 'near' e teto de variantes tonais por familia (orcamento de MeshParts)"""

    def __init__(self, name, rng=None, detail="near", vcap=2, remap=None):
        super().__init__(name, COLL, rng or random.Random(zlib.crc32(name.encode("utf-8")) & 0xffff),
                         detail=detail)
        self.vcap = vcap
        self.remap = remap or {}

    def _mi_for(self, m):
        return super()._mi_for(self.remap.get(m, m))

    def _variant_names(self, m):
        old = fm_lib.VARIANT_T2, fm_lib.VARIANT_T3
        try:
            if self.vcap <= 2:
                fm_lib.VARIANT_T3 = 10 ** 9
            if self.vcap <= 1:
                fm_lib.VARIANT_T2 = 10 ** 9
            return super()._variant_names(m)
        finally:
            fm_lib.VARIANT_T2, fm_lib.VARIANT_T3 = old


# ------------------------------------------------------------------ primitivas proprias (baixo poligono, facetadas)
def _basis(up):
    up = V(up).normalized()
    t1 = up.orthogonal().normalized()
    t2 = up.cross(t1).normalized()
    return up, t1, t2


def _solid(mb, rings, m, apex=None, cap_bottom=True, cap_top=True):
    """solido por aneis (mesmo numero de vertices, anti-horario em volta do eixo), com ponta opcional"""
    bm = mb.bm
    vr = [[bm.verts.new(p) for p in ring] for ring in rings]
    k = len(rings[0])
    for r0, r1 in zip(vr, vr[1:]):
        for j in range(k):
            j2 = (j + 1) % k
            bm.faces.new((r0[j], r0[j2], r1[j2], r1[j]))
    if cap_bottom:
        bm.faces.new(list(reversed(vr[0])))
    allv = [v for r in vr for v in r]
    if apex is not None:
        va = bm.verts.new(apex)
        allv.append(va)
        top = vr[-1]
        for j in range(k):
            bm.faces.new((top[j], top[(j + 1) % k], va))
    elif cap_top and len(vr) > 1:
        bm.faces.new(vr[-1])
    mb._post(allv, m, None, 0, 1)


def shard(mb, base, h, r, m, rng, up=(0, 0, 1), n=5, top=0.38, jit=0.16, sink=0.5, blunt=False, squash=1.0):
    """pedra facetada: prisma afunilado com ponta (ou topo cortado), base afundada 'sink' no chao"""
    up, t1, t2 = _basis(up)
    base = V(base)
    a0 = rng.uniform(0, math.tau)

    def ring(z, rr):
        pts = []
        for i in range(n):
            a = a0 + math.tau * i / n + rng.uniform(-0.14, 0.14)
            k = rr * rng.uniform(1 - jit, 1 + jit)
            pts.append(base + up * z + (t1 * math.cos(a) + t2 * math.sin(a) * squash) * k)
        return pts
    hh = h + sink
    rings = [ring(-sink, r), ring(hh * 0.5 - sink, r * 0.84), ring(hh * 0.86 - sink, r * top)]
    apex = None
    if not blunt:
        off = (t1 * rng.uniform(-0.25, 0.25) + t2 * rng.uniform(-0.25, 0.25)) * r
        apex = base + up * h + off
    _solid(mb, rings, m, apex)


def crystal(mb, base, h, r, up, m, m_tip, rng, n=6, tip=0.3, sink=0.4):
    """cristal hexagonal: corpo (m) + ponta (m_tip), pontudo de verdade (sem tampa microscopica)"""
    up, t1, t2 = _basis(up)
    base = V(base) - up * sink
    h = h + sink
    a0 = rng.uniform(0, math.tau)

    def ring(z, rr):
        return [base + up * z + (t1 * math.cos(a0 + math.tau * i / n) + t2 * math.sin(a0 + math.tau * i / n)) * rr
                for i in range(n)]
    hb = h * (1 - tip)
    _solid(mb, [ring(0.0, r), ring(hb, r * 0.93)], m, None, True, False)
    _solid(mb, [ring(hb, r * 0.93)], m_tip, base + up * h, False)


def lean(a, t):
    """eixo inclinado 't' rad na direcao de azimute 'a'"""
    return (math.cos(a) * math.sin(t), math.sin(a) * math.sin(t), math.cos(t))


def pyramid(mb, c, half, h, m, yaw=0.0, top=0.25):
    """telhadinho de 4 aguas (tronco de piramide quadrada; topo 'top' de meia-largura)"""
    r = half * math.sqrt(2.0)
    mb.cyl(r, h, (c[0], c[1], c[2] + h / 2), (0, 0, yaw + math.pi / 4), m, 4, r2=max(top, 0.2) * math.sqrt(2.0),
           bevel=0.0)


def pitched_box(area, a, b, w, h, below=0.0):
    """caixa de colisao inclinada de a ate b (secao w x h), com o topo 'h - below' acima da linha a-b"""
    a, b = V(a), V(b)
    d = b - a
    yaw = math.atan2(d.y, d.x)
    pitch = math.atan2(d.z, math.hypot(d.x, d.y))
    c = (a + b) / 2 + V((0, 0, h / 2 - below))
    return col_box(area, (d.length, w, h), c, (0, -pitch, yaw))


# ------------------------------------------------------------------ 1. escadas N e S (colisao identica ao blockout)
def pit_stairs(ore_pts):
    mb = MMB("MINE_Pit_Stairs", random.Random(2101), detail="near", vcap=2)
    n = L.PIT_STAIR_N
    rise = (L.RING - L.PIT) / n
    tread = 1.6
    W = L.PIT_STAIR_W
    for ang in (-90.0, 90.0):
        a = D(ang)
        base = (math.cos(a) * (L.PIT_R - n * tread), math.sin(a) * (L.PIT_R - n * tread), L.PIT)
        FP.stairs(mb, "MiningStairs", base, a, W, n, rise, tread, "Stone_Wall_Light", "Stone_Wall_Dark")
        F = Frame(base[0], base[1], base[2], a)
        # capa inclinada de pedra clara sobre os banzos (esconde o serrilhado dos blocos) + tampa plana no topo
        for s in (-1, 1):
            y = s * (W / 2 + 0.6)
            z0 = 1.2 + rise
            x1 = tread * (n - 1)
            mb.beam(F.p(-0.1, y, z0 - 0.3), F.p(x1, y, z0 + rise / tread * x1 - 0.3), 1.5, 1.1, "Stone_Wall_Light", 0.1)
            mb.box((tread + 0.3, 1.5, 0.4), F.p(x1 + tread / 2 + 0.1, y, rise * n + 1.2 + 0.05), F.r(),
                   "Stone_Wall_Light", 0.1)
        # pilaretes de pedra no pe (arremate dos banzos), exceto onde um minerio encosta no pe da escada
        for s in (-1, 1):
            y = s * (W / 2 + 0.6)
            q = F.p(0.75, y)
            if any(math.hypot(q.x - ox, q.y - oy) < orr + 0.9 for _, _, ox, oy, orr in ore_pts):
                continue
            mb.box((1.5, 1.5, 2.5), F.p(0.75, y, 1.25), F.r(), "Stone_Wall_Dark", 0.14)
            mb.box((1.8, 1.8, 0.35), F.p(0.75, y, 2.62), F.r(), "Stone_Wall_Light", 0.1)
    mb.finish()


# ------------------------------------------------------------------ 2. rampas de madeira L e O
def _ramp_geo(side):
    top, bot, a_top = ramp_ends(side)
    at = V((top[0], top[1], L.RING))
    ab = V((bot[0], bot[1], L.PIT))
    dh = V((ab.x - at.x, ab.y - at.y, 0.0))
    Lh = dh.length
    u = dh / Lh
    n1 = V((-u.y, u.x, 0.0))
    out = n1 if n1.dot(V((at.x, at.y, 0.0))) > 0 else -n1
    slope = (L.RING - L.PIT) / Lh

    def P(s, v, dz=0.0):
        z = L.RING - max(0.0, min(Lh, s)) * slope
        return V((at.x + u.x * s + out.x * v, at.y + u.y * s + out.y * v, z + dz))

    def v_wall(s):
        """lateral (v) onde o raio chega a PIT_R, na estacao s"""
        p = V((at.x + u.x * s, at.y + u.y * s, 0.0))
        # |p + out*v| = PIT_R -> v^2 + 2 (p.out) v + |p|^2 - R^2 = 0
        b = p.dot(out)
        c = p.length_squared - L.PIT_R ** 2
        return -b + math.sqrt(max(0.0, b * b - c))
    return dict(at=at, ab=ab, u=u, out=out, Lh=Lh, slope=slope, P=P, v_wall=v_wall, a_top=a_top)


RAMP_LAND = (-4.6, 0.4)       # estacoes (s) do patamar do topo (s < 0 = alem do topo da rampa)
RAMP_OUT_RAIL0 = 1.5          # o corrimao de fora comeca aqui (topo aberto do lado de fora)
RAMP_FOOT_FREE = 2.0          # os 2 ultimos studs do pe sem corrimao (as rotas dependem disso)


def ramps(ore_pts):
    rng = random.Random(3101)
    mb = MMB("MINE_Pit_Ramps", rng, detail="near", vcap=2)
    W = L.PIT_RAMP_W
    hw = W / 2
    for side in (1, -1):
        g = _ramp_geo(side)
        at, ab, u, out, Lh, slope, P, v_wall = (g[k] for k in ("at", "ab", "u", "out", "Lh", "slope", "P", "v_wall"))
        yaw = math.atan2(u.y, u.x)
        pitch = math.atan(slope)
        s0, s1 = RAMP_LAND
        # ---- colisao: rampa (identica ao blockout) + patamar macico + corrimaos + saia sob o trecho alto
        IL.col_ramp("MiningRamp", ab, at, W, 1.0)
        vo = max(v_wall(s0), v_wall(s1)) + 0.9
        c = P((s0 + s1) / 2, (vo - hw) / 2, 0.0)
        col_box("MiningRamp", (s1 - s0, vo + hw, L.RING - L.PIT + 0.5), (c.x, c.y, (L.RING + L.PIT - 0.5) / 2),
                (0, 0, yaw))
        vi = -hw - 0.15
        a_in = P(s0, vi)
        col_box("MiningRamp", ((P(0.0, vi) - a_in).length, 0.6, 4.4), (P(s0 / 2, vi, 2.2)), (0, 0, yaw))
        a_end0, a_end1 = P(s0, vi), P(s0, v_wall(s0) - 0.1)
        col_box("MiningRamp", ((a_end1 - a_end0).length, 0.6, 4.4), ((a_end0 + a_end1) / 2 + V((0, 0, 2.2))),
                (0, 0, yaw + math.pi / 2))
        pitched_box("MiningRamp", P(0.0, vi), P(Lh - RAMP_FOOT_FREE, vi), 0.6, 4.4)
        pitched_box("MiningRamp", P(RAMP_OUT_RAIL0, hw + 0.15), P(Lh - RAMP_FOOT_FREE, hw + 0.15), 0.6, 4.4)
        pitched_box("MiningRamp", P(s1 - 0.2, -hw + 0.4), P(4.6, -hw + 0.4), 0.6, 9.0, below=10.0)
        # ---- tablado: pranchas atravessadas + sarrafos antiderrapantes + longarinas laterais
        pw = 1.1
        k = 0
        s = 0.05
        while s < Lh - 0.3:
            s_mid = s + pw / 2
            p = P(s_mid, 0.0)
            ln = W + rng.uniform(-0.1, 0.25)
            mb.box((pw - 0.12, ln, 0.3), p - V((0, 0, 0.15 + rng.uniform(0.0, 0.04))), (0, pitch, yaw),
                   "Wood_Plank", 0.0)
            if k % 2 == 1:
                mb.box((0.28, W - 1.2, 0.16), p + V((0, 0, 0.06)), (0, pitch, yaw), "Wood_Dark", 0.0)
            s += pw
            k += 1
        for v in (-hw + 0.25, hw - 0.25):
            mb.beam(P(-0.1, v, -0.75), P(Lh + 0.1, v, -0.75), 0.5, 0.9, "Wood_Dark", 0.06)
        # ---- patamar do topo (pranchas ate o muro, sem sobrepor o calcamento do anel)
        s = s0
        while s < s1 - 0.1:
            sm = s + 0.5
            vw = v_wall(sm) - 0.08
            a = P(sm, -hw)
            b = P(sm, vw)
            c = (a + b) / 2
            mb.box((0.9, (b - a).length, 0.3), (c.x, c.y, L.RING - 0.15 - rng.uniform(0, 0.03)), (0, 0, yaw),
                   "Wood_Plank", 0.0)
            s += 1.0
        for v in (-hw + 0.25,):
            mb.beam(P(s0, v, -0.7), P(s1, v, -0.7), 0.5, 0.8, "Wood_Dark", 0.06)
        mb.beam(P(s0 + 0.25, -hw, -0.7), P(s0 + 0.25, v_wall(s0) - 0.1, -0.7), 0.5, 0.8, "Wood_Dark", 0.06)
        # ---- caixa do patamar (tabuas verticais do chao do fosso ate o patamar) e saia do trecho alto
        def boards(pa, pb, z_top_a, z_top_b, step=1.05):
            d = pb - pa
            ln = d.length
            nb = max(1, int(ln / step))
            ang = math.atan2(d.y, d.x)
            for i in range(nb):
                f = (i + 0.5) / nb
                q = pa + d * f
                zt = z_top_a + (z_top_b - z_top_a) * f
                hgt = zt - L.PIT
                if hgt < 0.6:
                    continue
                mb.box((ln / nb - 0.1, 0.3, hgt + 0.3), (q.x, q.y, L.PIT - 0.3 + (hgt + 0.3) / 2),
                       (0, 0, ang), "Wood_Plank", 0.0, tint=rng.uniform(-1, 1))
        z_under = L.RING - 0.95
        pa, pb = P(s0, -hw + 0.1), P(s1, -hw + 0.1)
        boards(V((pa.x, pa.y, 0)), V((pb.x, pb.y, 0)), z_under, z_under)
        pa, pb = P(s0 + 0.1, -hw), P(s0 + 0.1, v_wall(s0) - 0.2)
        boards(V((pa.x, pa.y, 0)), V((pb.x, pb.y, 0)), z_under, z_under)
        s_skirt = 5.0
        pa, pb = P(s1, -hw + 0.1), P(s_skirt, -hw + 0.1)
        boards(V((pa.x, pa.y, 0)), V((pb.x, pb.y, 0)), P(s1, 0, -0.95).z, P(s_skirt, 0, -0.95).z)
        # esteios de canto + travessa no meio da caixa do patamar (a caixa le como torre de madeira, nao caixote)
        zc = L.RING - 0.4
        for s_c, v_c in ((s0 + 0.1, -hw + 0.1), (s1, -hw + 0.1), (s0 + 0.1, v_wall(s0) - 0.45)):
            q = P(s_c, v_c)
            mb.box((0.8, 0.8, zc - L.PIT + 0.3), (q.x, q.y, (zc + L.PIT - 0.3) / 2), (0, 0, yaw), "Wood_Dark", 0.06)
        zm = (L.PIT + L.RING) / 2 - 0.4
        for pa, pb in ((P(s0 + 0.1, -hw - 0.1), P(s_skirt, -hw - 0.1)),
                       (P(s0 - 0.1, -hw + 0.1), P(s0 - 0.1, v_wall(s0) - 0.45))):
            mb.beam(V((pa.x, pa.y, zm)), V((pb.x, pb.y, zm)), 0.4, 0.5, "Wood_Dark", 0.0)
        for pa, pb in ((P(s0 + 0.1, -hw - 0.1), P(s1, -hw - 0.1)),
                       (P(s0 - 0.1, -hw + 0.1), P(s0 - 0.1, v_wall(s0) - 0.45))):
            mb.beam(V((pa.x, pa.y, L.PIT + 0.4)), V((pb.x, pb.y, zm - 0.2)), 0.3, 0.3, "Wood_Dark", 0.0)
        # ---- pilares de apoio (cavaletes) sob a rampa: evitam o minerio encostado
        for s_b in (8.5, 15.0, 21.5, 27.5):
            hz = P(s_b, 0, -1.2).z - L.PIT
            if hz < 1.0:
                continue
            ok = True
            for kind, i, x, y, r in ore_pts:
                q = P(s_b, -hw + 0.4)
                if math.hypot(q.x - x, q.y - y) < r + 0.8:
                    ok = False
            vs = (-hw + 0.45, hw - 0.45) if ok else (hw - 0.45,)
            for v in vs:
                q = P(s_b, v)
                mb.box((0.75, 0.75, hz + 0.3), (q.x, q.y, L.PIT - 0.3 + (hz + 0.3) / 2), (0, 0, yaw), "Wood_Dark",
                       0.05)
            a2, b2 = P(s_b, -hw + 0.45, -1.3), P(s_b, hw - 0.45, -1.3)
            mb.beam(a2, b2, 0.5, 0.55, "Wood_Dark", 0.0)
            if ok and hz > 2.4:
                mb.beam(P(s_b, -hw + 0.45, -1.3 - hz * 0.7), P(s_b, hw - 0.45, -1.4), 0.35, 0.35, "Wood_Dark", 0.0)
        # ---- corrimaos (postes + 2 travessas): dentro do patamar ao pe-2, fora de RAMP_OUT_RAIL0 ao pe-2
        def rail(pts3, post_step=3.2):
            posts = list(pts3) + [q for q in fm_lib.resample(pts3, post_step)
                                  if min((q - c).length for c in pts3) > 1.4]
            for p in posts:
                mb.box((0.5, 0.5, 3.2), p + V((0, 0, 1.6)), (0, 0, yaw), "Wood_Dark", 0.0)
                mb.box((0.62, 0.62, 0.2), p + V((0, 0, 3.3)), (0, 0, yaw), "Wood_Dark", 0.0)
            for a, b in zip(pts3, pts3[1:]):
                for hz in (1.45, 2.85):
                    mb.beam(a + V((0, 0, hz)), b + V((0, 0, hz)), 0.36, 0.4, "Wood_Plank", 0.0)
        vi = -hw - 0.15
        rail([P(s0, v_wall(s0) - 0.35), P(s0, vi), P(0.0, vi), P(Lh - RAMP_FOOT_FREE, vi)])
        rail([P(RAMP_OUT_RAIL0, hw + 0.15), P(Lh - RAMP_FOOT_FREE, hw + 0.15)])
    mb.finish()


# ------------------------------------------------------------------ 3. cerca da borda + toros do anel
def _spans(r, a0, a1, gaps):
    spans = [(a0, a1)]
    for ang, hw in gaps:
        da = math.degrees(hw / r)
        new = []
        for s0, s1 in spans:
            g0, g1 = ang - da, ang + da
            if g1 <= s0 or g0 >= s1:
                new.append((s0, s1))
                continue
            if g0 > s0:
                new.append((s0, g0))
            if g1 < s1:
                new.append((g1, s1))
        spans = new
    # junta o trecho que cruza 0/360
    if len(spans) > 1 and abs(spans[0][0] - a0) < 1e-6 and abs(spans[-1][1] - a1) < 1e-6:
        first = spans.pop(0)
        last = spans.pop()
        spans.append((last[0], first[1] + 360.0))
    return spans


def fence_gaps():
    gaps = [(90.0, L.PIT_STAIR_W / 2 + 0.8), (270.0, L.PIT_STAIR_W / 2 + 0.8)]
    for side in (1, -1):
        _, _, a_top = ramp_ends(side)
        gaps.append((a_top % 360.0, L.PIT_RAMP_W / 2 + 1.0))
    return gaps


def box_lantern(mb, c, s=1.0, frame="Metal_Dark", roof="Wood_Dark"):
    """lanterna de caixa (c = centro do vidro): base, vidro emissivo, 4 montantes, telhadinho"""
    c = V(c)
    mb.box((1.3 * s, 1.3 * s, 0.22), c + V((0, 0, -0.66 * s)), (0, 0, 0), frame, 0.0)
    mb.box((0.86 * s, 0.86 * s, 1.1 * s), c, (0, 0, 0), "Lantern_Glow", 0.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.box((0.22, 0.22, 1.2 * s), c + V((sx * 0.5 * s, sy * 0.5 * s, 0)), (0, 0, 0), frame, 0.0)
    pyramid(mb, c + V((0, 0, 0.58 * s)), 0.82 * s, 0.6 * s, roof, 0.0, 0.2)


def fence():
    rng = random.Random(4101)
    mb = MMB("MINE_Pit_Fence", rng, detail="near", vcap=2)
    R = L.FENCE_R
    z = L.RING
    spans = _spans(R, 0.0, 360.0, fence_gaps())
    gate_posts = []
    for s0, s1 in spans:
        arc_len = R * math.radians(s1 - s0)
        n = max(1, int(round(arc_len / 4.2)))
        angs = [s0 + (s1 - s0) * k / n for k in range(n + 1)]
        pts = [V((R * math.cos(D(a)), R * math.sin(D(a)), z)) for a in angs]
        for k, (a, p) in enumerate(zip(angs, pts)):
            if k in (0, n):
                gate_posts.append((a, p))
                continue
            mb.box((0.75, 0.75, 3.4), p + V((0, 0, 1.7)), (0, 0, D(a) + rng.uniform(-0.06, 0.06)), "Wood_Dark", 0.0)
            mb.box((0.95, 0.95, 0.24), p + V((0, 0, 3.5)), (0, 0, D(a)), "Wood_Dark", 0.0)
        for a, b in zip(pts, pts[1:]):
            for hz in (1.35, 2.8):
                mb.beam(a + V((0, 0, hz)), b + V((0, 0, hz)), 0.42, 0.38, "Wood_Plank", 0.0)
        # colisao em cordas de ate 16 graus (poucas caixas), deslocadas meia flecha para fora
        nseg = max(1, int(math.ceil((s1 - s0) / 16.0)))
        for i in range(nseg):
            b0 = s0 + (s1 - s0) * i / nseg
            b1 = s0 + (s1 - s0) * (i + 1) / nseg
            half = math.radians(b1 - b0) / 2
            chord = 2 * R * math.sin(half)
            sag = R * (1 - math.cos(half))
            am = D((b0 + b1) / 2)
            rm = R * math.cos(half) + sag / 2
            col_box("MiningFence", (0.9, chord + 0.5, 5.0), (rm * math.cos(am), rm * math.sin(am), z + 2.5),
                    (0, 0, am))
    # postes-lanterna nas pontas dos vaos (escadas e rampas)
    for a, p in gate_posts:
        mb.box((1.5, 1.5, 0.9), p + V((0, 0, 0.45)), (0, 0, D(a)), "Stone_Wall_Dark", 0.12)
        mb.box((1.0, 1.0, 3.8), p + V((0, 0, 0.9 + 1.9)), (0, 0, D(a)), "Wood_Dark", 0.08)
        box_lantern(mb, p + V((0, 0, 5.45)), 1.0, frame="Wood_Dark")
    mb.finish()
    return gate_posts


def _stair_axes():
    """(pe, direcao, meia-largura) das escadas que saem da borda externa do anel"""
    out = []
    import il_col
    for _, ang, w in il_col.RADIAL_STAIRS:
        a = D(ang)
        out.append((V((82.5 * math.cos(a), 82.5 * math.sin(a), 0)), V((math.cos(a), math.sin(a), 0)), w / 2 + 0.6))
    out.append((V((0.0, -82.5, 0)), V((0, -1, 0)), L.ENTRY_STAIR_W / 2 + 1.2))
    x0 = math.sqrt(82.0 ** 2 - L.MILL_STAIR[1] ** 2) - 0.4
    out.append((V((x0, L.MILL_STAIR[1], 0)), V((1, 0, 0)), 4.0 + 1.2))
    return out


def lantern_angles(r=79.5):
    """a cada 22,5 graus (11,25 + k 22,5); o toro que cai na frente de uma escada escorrega para o lado dela"""
    axes = _stair_axes()
    out = []
    for i in range(16):
        a = 11.25 + i * 22.5
        for _ in range(80):
            p = V((r * math.cos(D(a)), r * math.sin(D(a)), 0))
            bad = None
            for foot, d, hw in axes:
                q = p - foot
                along = q.dot(d)
                lat = q.x * d.y - q.y * d.x
                if along > -7.0 and abs(lat) < hw + 2.6:
                    bad = lat
                    break
            if bad is None:
                break
            # escorrega para longe do eixo da escada (lat > 0 -> lado horario)
            a += -0.25 if bad > 0 else 0.25
        out.append(a)
    return out


def ring_toros():
    rng = random.Random(5101)
    mb = MMB("MINE_Ring_Toros", rng, detail="near", vcap=1)
    r = 79.5
    z = L.RING
    for a in lantern_angles(r):
        x, y = r * math.cos(D(a)), r * math.sin(D(a))
        F = Frame(x, y, z, D(a))
        sq = F.r()
        mb.box((2.1, 2.1, 0.5), F.p(0, 0, 0.25), sq, "Stone_Wall_Dark", 0.1)
        mb.box((1.55, 1.55, 0.7), F.p(0, 0, 0.85), sq, "Stone_Wall_Light", 0.12)
        mb.box((0.95, 0.95, 2.2), F.p(0, 0, 2.3), sq, "Stone_Wall_Light", 0.08)
        mb.box((1.9, 1.9, 0.38), F.p(0, 0, 3.59), sq, "Stone_Wall_Dark", 0.08)
        mb.box((1.16, 1.16, 1.25), F.p(0, 0, 4.4), sq, "Lantern_Glow", 0.0)
        for sx in (-1, 1):
            for sy in (-1, 1):
                mb.box((0.34, 0.34, 1.25), F.p(sx * 0.62, sy * 0.62, 4.4), sq, "Stone_Wall_Light", 0.0)
        mb.box((2.2, 2.2, 0.3), F.p(0, 0, 5.17), sq, "Stone_Wall_Dark", 0.06)
        pyramid(mb, F.p(0, 0, 5.3), 1.1, 0.75, "Stone_Wall_Dark", D(a), 0.22)
        mb.box((0.42, 0.42, 0.45), F.p(0, 0, 6.28), sq, "Stone_Wall_Light", 0.0)
        col_box("MiningLantern", (1.7, 1.7, 6.4), F.p(0, 0, 3.2), sq)
    mb.finish()


# ------------------------------------------------------------------ 4. torres de mineracao
def derrick(mb, F, rng):
    b, t, ztop = 2.7, 2.15, 12.4

    def leg(sx, sy, z):
        s = b + (t - b) * (z / ztop)
        return F.p(sx * s, sy * s, z)

    corners = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    for sx, sy in corners:
        mb.box((1.5, 1.5, 0.7), F.p(sx * b, sy * b, 0.25), F.r(), "Stone_Wall_Dark", 0.12)
        mb.beam(leg(sx, sy, 0.4), leg(sx, sy, ztop + 0.35), 0.8, 0.8, "Wood_Dark", 0.06)
    for i in range(4):
        p, q = corners[i], corners[(i + 1) % 4]
        nx, ny = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2          # normal do lado (local)
        o = F.p(nx * 0.4, ny * 0.4) - F.p(0, 0)
        for z in (4.8, 8.75):
            mb.beam(leg(*p, z) + o * 0.3, leg(*q, z) + o * 0.3, 0.45, 0.5, "Wood_Dark", 0.0)
        for z0, z1 in ((1.0, 4.8), (4.8, 8.75)):
            mb.beam(leg(*p, z0) + o, leg(*q, z1) + o, 0.34, 0.34, "Wood_Dark", 0.0)
            mb.beam(leg(*q, z0) + o, leg(*p, z1) + o, 0.34, 0.34, "Wood_Dark", 0.0)
        mb.beam(leg(*p, ztop), leg(*q, ztop), 0.5, 0.55, "Wood_Dark", 0.0)
    # plataforma a +9 (tabuas) com guarda-corpo em 3 lados (a frente e da lanca)
    zp = 9.3
    for sy in (-1, 1):
        mb.beam(F.p(-3.4, sy * 2.4, zp - 0.55), F.p(3.4, sy * 2.4, zp - 0.55), 0.5, 0.5, "Wood_Dark", 0.0)
    for i in range(7):
        x = -3.0 + i * 1.0
        mb.box((0.9, 7.0, 0.3), F.p(x, 0, zp - 0.15 - rng.uniform(0, 0.04)), F.r(0, 0, rng.uniform(-0.01, 0.01)),
               "Wood_Plank", 0.0)
    rail = [F.p(3.3, -3.3, zp), F.p(-3.3, -3.3, zp), F.p(-3.3, 3.3, zp), F.p(3.3, 3.3, zp)]
    for p in rail + [F.p(0.0, -3.3, zp), F.p(0.0, 3.3, zp), F.p(-3.3, 0.0, zp)]:
        mb.box((0.4, 0.4, 2.4), p + V((0, 0, 1.2)), F.r(), "Wood_Dark", 0.0)
    for a, c in zip(rail, rail[1:]):
        for hz in (1.2, 2.3):
            mb.beam(a + V((0, 0, hz)), c + V((0, 0, hz)), 0.3, 0.3, "Wood_Plank", 0.0)
    # guincho no fundo da plataforma
    mb.cyl(0.62, 2.3, F.p(-1.6, 0, zp + 1.0), F.r(math.pi / 2, 0, 0), "Metal_Dark", 8, bevel=0.0)
    mb.cyl(0.72, 1.1, F.p(-1.6, 0, zp + 1.0), F.r(math.pi / 2, 0, 0), "Rope", 8, bevel=0.0)
    for sy in (-1, 1):
        mb.box((1.4, 0.3, 1.6), F.p(-1.6, sy * 1.3, zp + 0.8), F.r(), "Wood_Dark", 0.0)
    mb.beam(F.p(-1.6, 1.5, zp + 1.0), F.p(-1.6, 1.9, zp + 1.0), 0.25, 0.25, "Metal_Dark", 0.0)
    mb.beam(F.p(-1.6, 1.9, zp + 1.0), F.p(-1.0, 1.9, zp + 1.6), 0.25, 0.25, "Metal_Dark", 0.0)
    # montante central da frente + lanca com roldana
    mb.beam(F.p(2.2, 0, zp), F.p(2.2, 0, ztop), 0.5, 0.5, "Wood_Dark", 0.0)
    mb.beam(F.p(1.9, 0, ztop - 0.35), F.p(4.9, 0, ztop - 0.35), 0.5, 0.6, "Wood_Dark", 0.05)
    mb.beam(F.p(2.3, 0, ztop - 2.2), F.p(3.9, 0, ztop - 0.6), 0.34, 0.34, "Wood_Dark", 0.0)
    pc = F.p(4.4, 0, ztop - 1.35)
    mb.cyl(0.8, 0.32, pc, F.r(math.pi / 2, 0, 0), "Metal_Dark", 10, bevel=0.0)
    mb.cyl(0.25, 0.7, pc, F.r(math.pi / 2, 0, 0), "Metal_Iron", 6, bevel=0.0)
    for sy in (-1, 1):
        mb.box((0.5, 0.2, 1.2), F.p(4.4, sy * 0.3, ztop - 0.95), F.r(), "Metal_Dark", 0.0)
    # telhadinho (4 aguas) com testeira
    mb.box((7.2, 7.2, 0.35), F.p(0, 0, ztop + 0.55), F.r(), "Wood_Dark", 0.04)
    pyramid(mb, F.p(0, 0, ztop + 0.72), 3.85, 2.1, "Roof_Blue", F.a, 0.35)
    mb.box((0.8, 0.8, 0.5), F.p(0, 0, ztop + 3.05), F.r(), "Wood_Dark", 0.0)
    # corda: roldana -> guincho e roldana -> balde
    zb = 6.3
    mb.tube([F.p(4.4 + 0.8, 0, ztop - 1.35), F.p(4.4 + 0.8, 0, zb + 2.0)], 0.12, "Rope", 5)
    mb.tube([F.p(4.4 - 0.2, 0, ztop - 0.6), F.p(-1.6, 0, zp + 1.7)], 0.12, "Rope", 5)
    # balde pendurado (fundo acima da cabeca do jogador)
    bc = F.p(4.4 + 0.8, 0, zb)
    mb.cyl(0.75, 1.5, bc + V((0, 0, 0.75)), F.r(), "Wood_Plank", 8, r2=0.98, bevel=0.0)
    for hz, rr in ((0.35, 0.86), (1.25, 1.0)):
        mb.cyl(rr, 0.2, bc + V((0, 0, hz)), F.r(), "Metal_Dark", 8, bevel=0.0)
    mb.cyl(0.88, 0.3, bc + V((0, 0, 1.5)), F.r(), "Stone_Wall_Dark", 6, r2=0.45, bevel=0.0)
    for sy in (-1, 1):
        mb.beam(F.p(5.2, sy * 0.98, zb + 1.5), F.p(5.2, 0, zb + 2.1), 0.2, 0.2, "Metal_Dark", 0.0)


def derricks():
    rng = random.Random(6101)
    mb = MMB("MINE_Derricks", rng, detail="near", vcap=1, remap={"Metal_Iron": "Metal_Dark"})
    for ang in L.DERRICKS:
        a = D(ang)
        cx, cy = L.DERRICK_R * math.cos(a), L.DERRICK_R * math.sin(a)
        F = Frame(cx, cy, L.PIT, a + math.pi)            # +x local = para o centro do fosso
        derrick(mb, F, rng)
        col_box("MiningDerrick", (7.0, 7.0, 9.3), F.p(0, 0, 4.65), F.r())
    mb.finish()


# ------------------------------------------------------------------ 5. formacao central (peca-heroi)
def core():
    rng = random.Random(7101)
    mb = MMB("MINE_Core_Formation", rng, detail="near", vcap=2)
    z = L.PIT
    R = L.CORE_R
    # monte baixo de terra sob as pedras (cone suave, sem borda de prato)
    a0 = rng.uniform(0, 1)
    rings = []
    for rr, zz in ((R - 0.4, -0.3), (R * 0.72, 0.45), (R * 0.4, 1.0)):
        rings.append([V((rr * math.cos(a0 + math.tau * i / 14) * rng.uniform(0.96, 1.04),
                         rr * math.sin(a0 + math.tau * i / 14) * rng.uniform(0.96, 1.04), z + zz)) for i in range(14)])
    _solid(mb, rings, "Dirt_Pit")
    # anel externo: pedras medias inclinadas para fora
    for i in range(11):
        a = math.tau * i / 11 + rng.uniform(-0.18, 0.18)
        rr = rng.uniform(1.4, 2.0)
        d = min(R - rr * 1.2 - 0.3, rng.uniform(6.4, 7.4))
        h = rng.uniform(2.8, 5.2)
        m = "Cliff_Rock_Dark" if i % 3 == 0 else "Cliff_Rock"
        shard(mb, (d * math.cos(a), d * math.sin(a), z), h, rr, m, rng, lean(a, rng.uniform(0.12, 0.28)), n=5)
    # anel do meio: pedras altas
    for i in range(7):
        a = math.tau * i / 7 + 0.35 + rng.uniform(-0.2, 0.2)
        d = rng.uniform(3.6, 4.8)
        rr = rng.uniform(1.8, 2.4)
        h = rng.uniform(5.8, 8.8)
        m = "Cliff_Rock" if i % 2 else "Cliff_Rock_Dark"
        shard(mb, (d * math.cos(a), d * math.sin(a), z), h, rr, m, rng, lean(a, rng.uniform(0.06, 0.18)), n=5)
    # miolo
    for i in range(3):
        a = math.tau * i / 3 + 1.0
        shard(mb, (1.6 * math.cos(a), 1.6 * math.sin(a), z), rng.uniform(5.0, 6.5), 2.2, "Cliff_Rock", rng,
              lean(a, 0.08), n=5)
    # cristal-mestre + secundarios inclinados + pequenos entre as pedras
    crystal(mb, (0.2, -0.3, z + 2.4), 13.3, 2.45, (0.03, -0.02, 1.0), "Crystal_Blue", "Crystal_Blue_Core", rng, 6,
            0.3, 1.2)
    for i in range(5):
        a = math.tau * i / 5 + 0.6 + rng.uniform(-0.15, 0.15)
        d = rng.uniform(1.6, 2.4)
        crystal(mb, (d * math.cos(a), d * math.sin(a), z + 2.6), rng.uniform(7.0, 9.6) if i % 2 == 0 else
                rng.uniform(5.6, 7.0), rng.uniform(1.15, 1.45), lean(a, rng.uniform(0.28, 0.42)), "Crystal_Blue",
                "Crystal_Blue_Core", rng, 6, 0.3, 1.0)
    for i in range(7):
        a = math.tau * i / 7 + 0.1 + rng.uniform(-0.2, 0.2)
        d = rng.uniform(4.6, 6.4)
        crystal(mb, (d * math.cos(a), d * math.sin(a), z + rng.uniform(0.6, 1.8)), rng.uniform(2.4, 4.0),
                rng.uniform(0.5, 0.72), lean(a, rng.uniform(0.35, 0.6)), "Crystal_Blue", "Crystal_Blue_Core", rng,
                6, 0.35, 0.5)
    # cascalho na borda
    for i in range(16):
        a = rng.uniform(0, math.tau)
        d = rng.uniform(8.3, 9.5)
        rr = rng.uniform(0.45, 0.8)
        shard(mb, (d * math.cos(a), d * math.sin(a), z), rr * 1.1, rr, "Cliff_Rock", rng, n=5, top=0.5,
              sink=0.3, blunt=True)
    mb.finish()
    # colisao simples: octogono baixo (2 caixas) + nucleo alto
    col_box("MiningCore", (15.0, 15.0, 7.0), (0, 0, z + 3.5))
    col_box("MiningCore", (15.0, 15.0, 7.0), (0, 0, z + 3.5), (0, 0, math.pi / 4))
    col_box("MiningCore", (7.0, 7.0, 16.0), (0, 0, z + 8.0), (0, 0, math.pi / 8))
    light("L_Mining_Core_Glow", "POINT", (0, 0, z + 10.0), 2200, (0.35, 0.62, 1.0), 2.5)


# ------------------------------------------------------------------ 6. minerio por raridade
def on_stairs(x, y, r):
    """ponto de minerio com o CENTRO dentro da pegada das escadas N/S (r 45,6..60, |x| < meia-largura + banzo)"""
    hw = L.PIT_STAIR_W / 2 + 1.2
    y0 = L.PIT_R - L.PIT_STAIR_N * 1.6
    return abs(x) < hw and abs(y) > y0 - 0.3


def _ore_common(mb, x, y, r, rng):
    z = L.PIT
    shard(mb, (x, y, z), rng.uniform(2.0, 2.4), 1.55, "Cliff_Rock", rng, n=6, top=0.52, blunt=True)
    b = rng.uniform(0, math.tau)
    shard(mb, (x + 1.35 * math.cos(b), y + 1.35 * math.sin(b), z), 1.2, 0.85, "Cliff_Rock", rng, n=5, top=0.5,
          blunt=True)
    for k in range(3):
        a = b + math.pi + (k - 1) * 1.1 + rng.uniform(-0.3, 0.3)
        d = rng.uniform(0.35, 0.8)
        crystal(mb, (x + d * math.cos(a), y + d * math.sin(a), z + rng.uniform(1.2, 1.6)), rng.uniform(0.9, 1.45),
                rng.uniform(0.24, 0.32), lean(a, rng.uniform(0.25, 0.55)), "Crystal_Blue", "Crystal_Blue_Core", rng,
                5, 0.42, 0.3)
    for k in range(3):
        a = rng.uniform(0, math.tau)
        d = rng.uniform(1.7, 2.1)
        shard(mb, (x + d * math.cos(a), y + d * math.sin(a), z), 0.45, 0.36, "Cliff_Rock", rng, n=5, top=0.5,
              sink=0.2, blunt=True)
    return 3.0, 2.5


def _ore_uncommon(mb, x, y, r, rng):
    z = L.PIT
    shard(mb, (x, y, z), rng.uniform(2.3, 2.7), 1.8, "Cliff_Rock", rng, n=6, top=0.5, blunt=True)
    b = rng.uniform(0, math.tau)
    shard(mb, (x + 1.6 * math.cos(b), y + 1.6 * math.sin(b), z), 1.4, 0.95, "Cliff_Rock", rng, n=5, top=0.5,
          blunt=True)
    for k in range(4):
        a = b + math.pi + (k - 1.5) * 0.9 + rng.uniform(-0.25, 0.25)
        d = 0.0 if k == 1 else rng.uniform(0.5, 0.9)
        crystal(mb, (x + d * math.cos(a), y + d * math.sin(a), z + rng.uniform(1.3, 1.8)),
                rng.uniform(2.2, 2.8) if k == 1 else rng.uniform(1.4, 2.1), rng.uniform(0.38, 0.48),
                lean(a, 0.1 if k == 1 else rng.uniform(0.3, 0.55)), "Crystal_MineTeal", "Crystal_MineTeal_Glow",
                rng, 6, 0.36, 0.4)
    for k in range(3):
        a = rng.uniform(0, math.tau)
        d = rng.uniform(2.0, 2.45)
        shard(mb, (x + d * math.cos(a), y + d * math.sin(a), z), 0.5, 0.4, "Cliff_Rock", rng, n=5, top=0.5,
              sink=0.2, blunt=True)
    return 3.4, 2.8


def _ore_epic(mb, x, y, r, rng):
    z = L.PIT
    shard(mb, (x, y, z), rng.uniform(2.4, 2.8), 2.0, "Cliff_Rock_Dark", rng, n=6, top=0.5, blunt=True)
    b = rng.uniform(0, math.tau)
    for k in range(2):
        a = b + k * 2.3
        shard(mb, (x + 1.8 * math.cos(a), y + 1.8 * math.sin(a), z), rng.uniform(1.3, 1.8), 0.95, "Cliff_Rock_Dark",
              rng, lean(a, 0.2), n=5, top=0.45)
    for k in range(5):
        a = b + math.pi * 0.6 + (k - 2) * 0.75 + rng.uniform(-0.2, 0.2)
        d = 0.0 if k == 2 else rng.uniform(0.6, 1.1)
        crystal(mb, (x + d * math.cos(a), y + d * math.sin(a), z + rng.uniform(1.4, 1.9)),
                rng.uniform(3.2, 3.8) if k == 2 else rng.uniform(1.8, 2.8), rng.uniform(0.46, 0.6),
                lean(a, 0.08 if k == 2 else rng.uniform(0.3, 0.6)), "Crystal_Purple", "Crystal_Purple_Core", rng, 6,
                0.34, 0.4)
    for k in range(4):
        a = rng.uniform(0, math.tau)
        d = rng.uniform(2.4, 2.9)
        shard(mb, (x + d * math.cos(a), y + d * math.sin(a), z), 0.55, 0.42, "Cliff_Rock_Dark", rng, n=5, top=0.5,
              sink=0.2, blunt=True)
    return 3.8, 3.0


def _ore_super(mb, x, y, r, rng):
    z = L.PIT
    shard(mb, (x, y, z), 1.9, 2.3, "Cliff_Rock_Dark", rng, n=7, top=0.6, blunt=True)
    b = rng.uniform(0, math.tau)
    for k in range(3):
        a = b + k * math.tau / 3
        shard(mb, (x + 2.1 * math.cos(a), y + 2.1 * math.sin(a), z), rng.uniform(1.4, 2.0), 1.15, "Cliff_Rock_Dark",
              rng, lean(a, 0.25), n=5, top=0.45)
    crystal(mb, (x, y, z + 1.4), 5.6, 1.05, (0.04, 0.03, 1.0), "Crystal_MineGold", "Crystal_MineGold_Glow", rng, 6,
            0.3, 0.6)
    for k in range(6):
        a = b + math.pi / 3 + k * math.tau / 6 + rng.uniform(-0.2, 0.2)
        d = rng.uniform(0.9, 1.5)
        crystal(mb, (x + d * math.cos(a), y + d * math.sin(a), z + rng.uniform(1.2, 1.7)), rng.uniform(2.6, 4.2),
                rng.uniform(0.55, 0.78), lean(a, rng.uniform(0.3, 0.5)), "Crystal_MineGold", "Crystal_MineGold_Glow",
                rng, 6, 0.32, 0.5)
    for k in range(5):
        a = b + k * math.tau / 5 + 0.4
        d = rng.uniform(3.0, 3.4)
        crystal(mb, (x + d * math.cos(a), y + d * math.sin(a), z), rng.uniform(0.9, 1.4), rng.uniform(0.28, 0.36),
                lean(a, 0.55), "Crystal_MineGold", "Crystal_MineGold_Glow", rng, 5, 0.4, 0.2)
    return 5.0, 3.2


ORE_BUILD = {"COMMON": _ore_common, "UNCOMMON": _ore_uncommon, "EPIC": _ore_epic, "SUPERLEGENDARY": _ore_super}


def ores(pts):
    mbs = {}
    skipped = []
    for kind, _ in L.ORE_KINDS:
        mbs[kind] = MMB("MINE_Ore_%s" % kind, random.Random(zlib.crc32(kind.encode()) & 0xffff), detail="near",
                        vcap=1)
    for kind, i, x, y, r in pts:
        if on_stairs(x, y, r):
            skipped.append("ORE_%s_%02d" % (kind, i))
            continue
        rng = random.Random(zlib.crc32(("%s_%d" % (kind, i)).encode()) & 0xffffff)
        w, hgt = ORE_BUILD[kind](mbs[kind], x, y, r, rng)
        col_box("MineOre", (w, w, hgt), (x, y, L.PIT + hgt / 2), (0, 0, math.atan2(y, x)))
    for mb in mbs.values():
        mb.finish()
    if skipped:
        print("MINE AVISO: pontos de minerio DENTRO das escadas N/S (sem visual/colisao): %s" % ", ".join(skipped))
    return skipped


# ------------------------------------------------------------------ 7. props de borda (junto ao pe do muro)
def _at(r, a_deg):
    a = D(a_deg)
    return r * math.cos(a), r * math.sin(a)


def props(ore_pts):
    rng = random.Random(8101)
    mb = MMB("MINE_Props", rng, detail="near", vcap=1,
             remap={"Wood_Light": "Wood_Plank", "Metal_Iron": "Metal_Dark", "Crystal_Purple": "Crystal_Blue",
                    "Crystal_Purple_Core": "Crystal_Blue_Core"})
    z = L.PIT
    # vagonetes em trilho curto perto do pe da rampa leste (vao livre entre o minerio e a torre NE)
    R = 56.4
    a0, a1 = 32.8, 44.2
    pts = [V((*_at(R, a0 + (a1 - a0) * k / 8), z)) for k in range(9)]
    PK.rail_stub(mb, pts, z=z, rng=rng)
    t_end = (pts[-1] - pts[-2]).normalized()
    PK.bumper(mb, pts[-1] + V((0, 0, 0.3)), t_end)
    for ac, load in ((35.6, "crystal"), (40.3, "ore")):
        x, y = _at(R, ac)
        yaw = D(ac) + math.pi / 2
        PK.cart(mb, (x, y, z + 0.3), yaw, rng, load="crystal" if load == "crystal" else None, m_body="Wood_Plank")
        if load == "ore":
            mb.cyl(1.9, 0.5, (x, y, z + 0.3 + 3.05), (0, 0, yaw + math.pi / 4), "Cliff_Rock_Dark", 4, r2=0.9,
                   bevel=0.0)
            crystal(mb, (x + 0.3, y, z + 3.4), 0.9, 0.3, lean(rng.uniform(0, 6), 0.3), "Crystal_Purple",
                    "Crystal_Purple_Core", rng, 5, 0.4, 0.3)
    m0, m1 = V((*_at(R, 34.0), z)), V((*_at(R, 42.0), z))
    c = (m0 + m1) / 2
    col_box("MiningProps", ((m1 - m0).length + 3.2, 2.6, 3.6), (c.x, c.y, z + 1.8),
            (0, 0, math.atan2(m1.y - m0.y, m1.x - m0.x)))
    # pilha de caixas NO (112 graus)
    x, y = _at(56.0, 112.0)
    yaw = D(112.0) + math.pi / 2
    F = Frame(x, y, z, yaw)
    PK.crate(mb, tuple(F.p(-1.3, 0.0)), 2.3, yaw + 0.08)
    PK.crate(mb, tuple(F.p(1.2, 0.2)), 2.1, yaw - 0.12)
    PK.crate(mb, tuple(F.p(-0.9, 0.1, 2.3)), 1.8, yaw + 0.3)
    PK.keg(mb, tuple(F.p(2.9, 0.9)), 0.8, 1.9)
    col_box("MiningProps", (7.0, 3.2, 3.0), tuple(F.p(0.6, 0.3, 1.5)), F.r())
    # suporte de ferramentas (146 graus), encostado no muro, de frente para o centro
    x, y = _at(57.2, 146.0)
    F = Frame(x, y, z, D(146.0) + math.pi / 2)
    PK.tool_rack(mb, F, rng, kinds=("pick", "shovel", "pick", "pick", "shovel"))
    col_box("MiningProps", (7.2, 1.8, 3.8), tuple(F.p(0, 0.3, 1.9)), F.r())
    # mesa de triagem (215 graus)
    x, y = _at(55.6, 215.0)
    F = Frame(x, y, z, D(215.0) + math.pi / 2)
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.box((0.4, 0.4, 2.6), F.p(sx * 1.9, sy * 0.95, 1.3), F.r(), "Wood_Dark", 0.0)
    mb.box((4.6, 2.5, 0.32), F.p(0, 0, 2.72), F.r(), "Wood_Plank", 0.04)
    mb.box((4.0, 0.3, 0.3), F.p(0, 0, 0.7), F.r(), "Wood_Dark", 0.0)
    mb.box((2.0, 1.7, 0.2), F.p(-1.0, 0.0, 3.08), F.r(0.14, 0, 0), "Metal_Dark", 0.0)
    for k in range(4):
        a = rng.uniform(0, math.tau)
        shard(mb, F.p(-1.0 + 0.5 * math.cos(a), 0.4 * math.sin(a), 3.15), 0.35, 0.3, "Cliff_Rock_Dark", rng, n=5,
              top=0.5, sink=0.1, blunt=True)
    for k, m, mt in ((0, "Crystal_Blue", "Crystal_Blue_Core"), (1, "Crystal_Purple", "Crystal_Purple_Core"),
                     (2, "Crystal_Blue", "Crystal_Blue_Core")):
        crystal(mb, F.p(0.9 + k * 0.45, -0.3 + (k % 2) * 0.6, 2.88), 0.8, 0.22, lean(rng.uniform(0, 6), 0.25), m, mt,
                rng, 5, 0.4, 0.1)
    PK.keg(mb, tuple(F.p(3.1, 0.9)), 0.62, 1.2)
    col_box("MiningProps", (5.4, 3.0, 3.2), tuple(F.p(0.3, 0.1, 1.6)), F.r())
    # caixas abertas com cristais (250 graus)
    x, y = _at(56.0, 250.0)
    yaw = D(250.0) + math.pi / 2
    F = Frame(x, y, z, yaw)
    PK.crate(mb, tuple(F.p(-1.2, 0.2)), 2.2, yaw - 0.1)
    PK.crate(mb, tuple(F.p(1.3, 0.0)), 2.2, yaw + 0.15, lid=False)
    q = F.p(1.3, 0.0, 1.55)
    mb.box((1.9, 1.9, 0.3), q, (0, 0, yaw + 0.15), "Cliff_Rock_Dark", 0.0)
    for k in range(3):
        a = rng.uniform(0, math.tau)
        crystal(mb, q + V((0.45 * math.cos(a), 0.45 * math.sin(a), 0.1)), rng.uniform(0.9, 1.4), 0.3,
                lean(a, 0.3), "Crystal_Blue", "Crystal_Blue_Core", rng, 5, 0.4, 0.2)
    PK.crate(mb, tuple(F.p(-1.0, 0.1, 2.2)), 1.7, yaw + 0.35)
    col_box("MiningProps", (5.6, 3.0, 3.0), tuple(F.p(0.0, 0.1, 1.5)), F.r())
    shoring(mb, ore_pts, rng)
    mb.finish()


# arcos (graus) ja ocupados pelos props de borda
PROP_ARCS = [(32.8, 44.2), (108.0, 117.0), (141.0, 151.0), (210.0, 220.0), (245.0, 255.0)]


def _ramp_arc(aa):
    """angulo (graus, 0..360) na faixa das rampas L/O + patamares"""
    return aa >= 330.0 or aa <= 18.0 or 162.0 <= aa <= 210.0


def _wall_free(a_deg, half_w, ore_pts, r=59.5):
    x, y = _at(r, a_deg)
    aa = a_deg % 360.0
    if _ramp_arc(aa) or abs(x) < L.PIT_STAIR_W / 2 + 1.2 + half_w + 1.0:
        return False
    if any(a0 - 4.0 <= aa <= a1 + 4.0 for a0, a1 in PROP_ARCS):
        return False
    if any(math.hypot(x - ox, y - oy) < orr + half_w + 0.8 for _, _, ox, oy, orr in ore_pts):
        return False
    for d in L.DERRICKS:
        if math.hypot(x - L.DERRICK_R * math.cos(D(d)), y - L.DERRICK_R * math.sin(D(d))) < 5.5:
            return False
    return True


def shoring(mb, ore_pts, rng):
    """escoramento de madeira (portico com X) encostado no muro do fosso, onde o pe do muro esta livre"""
    picked = []
    for a10 in range(0, 3600, 10):
        a = a10 / 10.0
        if len(picked) >= 10:
            break
        if any(abs(((a - b + 180.0) % 360.0) - 180.0) < 22.0 for b in picked):
            continue
        if _wall_free(a, 2.9, ore_pts) and _wall_free(a - 2.5, 1.0, ore_pts) and _wall_free(a + 2.5, 1.0, ore_pts):
            picked.append(a)
    for k, a in enumerate(picked):
        x, y = _at(59.45, a)
        F = Frame(x, y, L.PIT, D(a) + math.pi / 2)        # +y local = para o centro
        for sx in (-1, 1):
            mb.box((0.62, 0.62, 6.1), F.p(sx * 2.3, 0, 3.0), F.r(), "Wood_Dark", 0.05)
        mb.box((5.8, 0.72, 0.6), F.p(0, 0.02, 6.1), F.r(), "Wood_Dark", 0.05)
        mb.box((5.2, 0.6, 0.4), F.p(0, 0, 0.2), F.r(), "Wood_Dark", 0.0)
        for sx in (-1, 1):
            mb.beam(F.p(-sx * 2.0, 0.18, 0.5), F.p(sx * 2.0, 0.18, 5.75), 0.34, 0.34, "Wood_Dark", 0.0)
        if k % 2 == 0:
            top = F.p(0, 0.75, 6.1)
            mb.box((0.3, 1.1, 0.3), F.p(0, 0.45, 5.95), F.r(), "Metal_Dark", 0.0)
            mb.rod(top, top - V((0, 0, 0.5)), 0.1, "Metal_Dark", 4)
            box_lantern(mb, top - V((0, 0, 1.3)), 0.8)
    return picked


def pebble(mb, x, y, s, rng, m="Cliff_Rock"):
    """seixo baixo de 2 aneis (16 tris)"""
    a0 = rng.uniform(0, math.tau)
    rings = []
    for rr, zz in ((s, -0.12), (s * 0.55, s * 0.62)):
        rings.append([V((x + rr * rng.uniform(0.85, 1.15) * math.cos(a0 + math.tau * i / 5),
                         y + rr * rng.uniform(0.85, 1.15) * math.sin(a0 + math.tau * i / 5), L.PIT + zz))
                      for i in range(5)])
    _solid(mb, rings, m)


def rubble(ore_pts):
    """cascalho solto no piso do fosso (a textura das referencias) + lascas de cristal; sem colisao"""
    rng = random.Random(9901)
    mb = MMB("MINE_Pit_Rubble", rng, detail="near", vcap=1)
    z = L.PIT
    n = 0
    shards = 0
    for _ in range(3000):
        if n >= 84:
            break
        rr = math.sqrt(rng.uniform(12.5 ** 2, 57.0 ** 2))
        a = rng.uniform(0, math.tau)
        x, y = rr * math.cos(a), rr * math.sin(a)
        aa = math.degrees(a) % 360.0
        if any(math.hypot(x - ox, y - oy) < orr + 0.3 for _, _, ox, oy, orr in ore_pts):
            continue
        if abs(x) < L.PIT_STAIR_W / 2 + 1.6 and abs(y) > 44.5:
            continue
        if rr > 48.0 and _ramp_arc(aa):
            continue
        if rr > 51.0 and any(a0 - 3.0 <= aa <= a1 + 3.0 for a0, a1 in PROP_ARCS):
            continue
        if any(math.hypot(x - L.DERRICK_R * math.cos(D(d)), y - L.DERRICK_R * math.sin(D(d))) < 4.6
               for d in L.DERRICKS):
            continue
        k = 1 + (rng.random() < 0.45) + (rng.random() < 0.2)
        for j in range(k):
            ox, oy = (rng.uniform(-0.9, 0.9), rng.uniform(-0.9, 0.9)) if j else (0.0, 0.0)
            s = rng.uniform(0.24, 0.5)
            pebble(mb, x + ox, y + oy, s, rng)
        if shards < 16 and rng.random() < 0.3:
            crystal(mb, (x + 0.5, y - 0.3, z), rng.uniform(0.5, 0.8), 0.22, lean(a, rng.uniform(0.3, 0.7)),
                    "Crystal_Blue", "Crystal_Blue_Core", rng, 5, 0.45, 0.1)
            shards += 1
        n += 1
    mb.finish()


# ------------------------------------------------------------------ build
def build():
    pts = L.ore_points()
    pit_stairs(pts)
    ramps(pts)
    gate_posts = fence()
    ring_toros()
    derricks()
    core()
    ores(pts)
    props(pts)
    rubble(pts)
    # 2 luzes quentes nos postes-lanterna das escadas N e S (o resto e Lantern_Glow)
    for tag, ang in (("S", 270.0), ("N", 90.0)):
        a, p = min(gate_posts, key=lambda g: abs(((g[0] - ang + 180.0) % 360.0) - 180.0))
        light("L_Mining_Gate_%s" % tag, "POINT", p + V((0, 0, 5.45)), 160, (1.0, 0.62, 0.28), 0.4)
