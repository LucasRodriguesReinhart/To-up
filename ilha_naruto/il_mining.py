# il_mining - fosso de mineracao em arte final (zona "mining", prefixo MINE_, colecao 03_MINING). Rodada 2: nucleo
# baixo (monumento), minerio na paleta das refs, torres abertas com polia, regras de chanfro/micro/z-fighting (MMB) -
# auditoria em il_mining_qa.py; progresso em _studio/mining/PROGRESSO.md.
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
from il_col import ramp_ends

COLL = "03_MINING"
V = Vector

# ------------------------------------------------------------------ cameras de revisao (360 + altura do jogador)
CAMS = {
    "CAM_Mining_Player": ((0.0, -70.0, L.RING + 6.8), (0.0, -6.0, L.PIT + 2.0), 22),     # jogador no topo da escada S
    "CAM_Mining_Core": ((17.0, -23.0, L.PIT + 7.5), (0.0, 0.0, L.PIT + 4.5), 24),
    "CAM_Mining_Ramp": ((26.0, -30.0, L.PIT + 6.5), (54.0, 2.0, L.PIT + 4.0), 20),
    "CAM_Mining_Top": ((0.0, -38.0, 200.0), (0.0, 0.0, 0.0), 28),
    "CAM_Mining_S": ((14.0, -100.0, 50.0), (0.0, 0.0, L.PIT), 24),     # (fora do pinaculo do portao)
    "CAM_Mining_N": ((0.0, 112.0, 46.0), (0.0, 0.0, L.PIT), 24),
    "CAM_Mining_E": ((112.0, 0.0, 46.0), (0.0, 0.0, L.PIT), 24),
    "CAM_Mining_W": ((-112.0, 0.0, 46.0), (0.0, 0.0, L.PIT), 24),
    "CAM_Mining_Floor": ((-12.0, -20.0, L.PIT + 4.6), (-40.0, -34.0, L.PIT + 5.0), 20),
    "CAM_Mining_CoreN": ((-14.0, 24.0, L.PIT + 6.0), (0.0, 0.0, L.PIT + 4.5), 24),
    "CAM_Mining_Ores": ((32.0, -9.0, L.PIT + 5.2), (14.0, 11.0, L.PIT + 1.5), 24),
    # rodada 2: visada do anel sul (escada N + porta do salao por cima do nucleo), torre de perto, rampa L do anel
    "CAM_Mining_SightS": ((0.0, -70.0, L.RING + 6.8), (0.0, 0.0, L.PIT + 3.8), 22),
    "CAM_Mining_Derrick": ((8.0, -14.0, L.PIT + 6.8), (32.0, -38.0, L.PIT + 7.8), 22),
    "CAM_Mining_RampTop": ((60.0, -36.0, L.RING + 6.8), (50.0, -10.0, L.PIT + 4.8), 22),
}

# ------------------------------------------------------------------ materiais novos (4 de 5)
# Rodada 2 (paleta das refs, sem confete): COMMON usa o Crystal_Blue da paleta (sem Core); UNCOMMON azul-ciano
# (~70,160,255) SEM brilho (casca + ponta clara, ambas SmoothPlastic no Roblox); EPIC = Crystal_Purple + _Core (Neon);
# SUPERLEGENDARY dourado com ponta *_Glow (Neon). So os raros (EPIC, SUPERLEGENDARY) tem brilho.
_M = fm_lib.MATS.setdefault
_M("Crystal_MineCyan", (S(70, 160, 255), 0.15, 0.0, 0.12, S(70, 160, 255), 0.0))
_M("Crystal_MineCyan_Tip", (S(140, 205, 255), 0.15, 0.0, 0.2, S(140, 205, 255), 0.0))
_M("Crystal_MineGold", (S(240, 172, 28), 0.2, 0.0, 0.4, S(240, 168, 28), 0.0))
_M("Crystal_MineGold_Glow", (S(255, 224, 96), 0.2, 0.0, 1.8, S(255, 214, 80), 0.0))


MICRO = 0.35          # rodada 2: peca com TODAS as dimensoes abaixo disto nao e criada


def bev_rule(bevel, dmin):
    """rodada 2: chanfro 0 se a menor dimensao < 1,0; senao no maximo 5% dela"""
    if not bevel or bevel <= 0 or dmin < 1.0:
        return 0.0
    return min(bevel, 0.05 * dmin)


class MMB(MB):
    """MB da zona: colecao fixa, detalhe 'near' e teto de variantes tonais por familia (orcamento de MeshParts).
    Rodada 2: TODA primitiva (inclusive as dos kits do lobby chamadas com este MB) passa pela regra de chanfro
    (bev_rule) e as pecas microscopicas (todas as dimensoes < MICRO) sao descartadas."""

    def __init__(self, name, rng=None, detail="near", vcap=2, remap=None):
        super().__init__(name, COLL, rng or random.Random(zlib.crc32(name.encode("utf-8")) & 0xffff),
                         detail=detail)
        self.vcap = vcap
        self.remap = remap or {}
        self.n_micro = 0

    def box(self, size, loc, rot=(0, 0, 0), m="Stone_Light", bevel=0.12, seg=1, tint=None):
        if max(size) < MICRO:
            self.n_micro += 1
            return
        super().box(size, loc, rot, m, bev_rule(bevel, min(size)), seg, tint)

    def beam(self, a, b, w, h=None, m="Wood_Dark", bevel=0.08, roll=0.0, tint=None):
        h = h or w
        ln = (V(b) - V(a)).length
        if max(ln, w, h) < MICRO:
            self.n_micro += 1
            return
        super().beam(a, b, w, h, m, bev_rule(bevel, min(ln, w, h)), roll, tint)

    def cyl(self, r, h, loc, rot=(0, 0, 0), m="Metal_Iron", n=12, r2=None, bevel=0.08, seg=1, caps=True, tint=None,
            angle=0.5):
        rr = r if r2 is None else r2
        if max(2 * max(r, rr), h) < MICRO:
            self.n_micro += 1
            return
        super().cyl(r, h, loc, rot, m, n, r2, bev_rule(bevel, min(2 * min(r, rr), h)), seg, caps, tint, angle)

    def rod(self, a, b, r, m="Metal_Iron", n=8, bevel=0.0, tint=None, caps=True):
        ln = (V(b) - V(a)).length
        if max(ln, 2 * r) < MICRO:
            self.n_micro += 1
            return
        super().rod(a, b, r, m, n, bev_rule(bevel, min(ln, 2 * r)), tint, caps)

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
            # (tampa 0,1 mais larga que a capa de cada lado: faces laterais nao coincidem)
            mb.box((2.0, 1.7, 0.4), F.p(x1 + tread / 2, y, rise * n + 1.2 + 0.05), F.r(), "Stone_Wall_Light", 0.1)
        # pilaretes de pedra no pe (arremate dos banzos), exceto onde um minerio encosta no pe da escada
        for s in (-1, 1):
            y = s * (W / 2 + 0.6)
            q = F.p(0.75, y)
            if any(math.hypot(q.x - ox, q.y - oy) < orr + 0.9 for _, _, ox, oy, orr in ore_pts):
                continue
            # (1,8 de largura: sai 0,15 de cada lado da capa inclinada de 1,5 - sem face coincidente)
            mb.box((1.8, 1.8, 2.5), F.p(0.75, y, 1.25), F.r(), "Stone_Wall_Dark", 0.14)
            mb.box((2.0, 2.0, 0.4), F.p(0.75, y, 2.6), F.r(), "Stone_Wall_Light", 0.1)
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
                # sarrafo antiderrapante (secao >= 0,3 x 0,24: nada microscopico; topo 0,14 acima do tablado)
                mb.box((0.36, W - 1.6, 0.24), p + V((0, 0, 0.02)), (0, pitch, yaw), "Wood_Dark", 0.0)
            s += pw
            k += 1
        # longarinas recuadas 0,45 da borda (as pontas das pranchas nao coincidem com a face delas)
        for v in (-hw + 0.7, hw - 0.7):
            mb.beam(P(-0.1, v, -0.75), P(Lh + 0.1, v, -0.75), 0.5, 0.9, "Wood_Dark", 0.06)
        # ---- patamar do topo (pranchas ate o muro, sem sobrepor o calcamento do anel)
        for kk in range(5):
            sm = -0.5 - kk * 1.0            # pranchas de -4,95 a -0,05 (a 1a prancha da rampa comeca em 0,11)
            vw = v_wall(sm) - 0.08
            a = P(sm, -hw)
            b = P(sm, vw)
            c = (a + b) / 2
            mb.box((0.9, (b - a).length, 0.3), (c.x, c.y, L.RING - 0.15 - rng.uniform(0, 0.03)), (0, 0, yaw),
                   "Wood_Plank", 0.0)
        for v in (-hw + 0.45,):
            la, lb = P(s0 + 0.35, v), P(s1 + 0.2, v)          # horizontal (P() desce depois de s = 0)
            mb.beam(V((la.x, la.y, L.RING - 0.7)), V((lb.x, lb.y, L.RING - 0.7)), 0.5, 0.8, "Wood_Dark", 0.06)
        mb.beam(P(s0 + 0.25, -hw, -0.7), P(s0 + 0.25, v_wall(s0) - 0.3, -0.7), 0.5, 0.8, "Wood_Dark", 0.06)
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
                mb.box((ln / nb - 0.1, 0.3, hgt + 0.4), (q.x, q.y, L.PIT - 0.4 + (hgt + 0.4) / 2),
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
        zc = L.RING - 0.8                  # topo dos esteios longe das fiadas do muro do fosso (9,67 / 9,73)
        for s_c, v_c in ((s0 + 0.1, -hw + 0.1), (s1, -hw + 0.1), (s0 + 0.1, v_wall(s0) - 0.45)):
            q = P(s_c, v_c)
            mb.box((0.8, 0.8, zc - L.PIT + 0.55), (q.x, q.y, (zc + L.PIT - 0.55) / 2), (0, 0, yaw), "Wood_Dark", 0.06)
        zm = (L.PIT + L.RING) / 2 - 0.4
        for pa, pb in ((P(s0 + 0.35, -hw - 0.1), P(s_skirt + 0.25, -hw - 0.1)),
                       (P(s0 - 0.4, -hw - 0.15), P(s0 - 0.4, v_wall(s0) - 0.45))):
            mb.beam(V((pa.x, pa.y, zm)), V((pb.x, pb.y, zm)), 0.4, 0.5, "Wood_Dark", 0.0)
        for pa, pb in ((P(s0 + 0.1, -hw - 0.1), P(s1, -hw - 0.1)),
                       (P(s0 - 0.4, -hw + 0.1), P(s0 - 0.4, v_wall(s0) - 0.45))):
            # (mao-francesa termina abaixo da travessa: sem faces paralelas a < 0,1 onde as duas se cruzam)
            mb.beam(V((pa.x, pa.y, L.PIT + 0.4)), V((pb.x, pb.y, zm - 0.5)), 0.3, 0.3, "Wood_Dark", 0.0)
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
                mb.box((0.75, 0.75, hz + 0.55), (q.x, q.y, L.PIT - 0.55 + (hz + 0.55) / 2), (0, 0, yaw), "Wood_Dark",
                       0.05)
            a2, b2 = P(s_b, -hw + 0.2, -1.3), P(s_b, hw - 0.2, -1.3)     # pontas a 0,25 das longarinas
            mb.beam(a2, b2, 0.5, 0.55, "Wood_Dark", 0.0)
            if ok and hz > 2.4:
                mb.beam(P(s_b, -hw + 0.45, -1.3 - hz * 0.7), P(s_b, hw - 0.45, -1.4), 0.35, 0.35, "Wood_Dark", 0.0)
        # ---- corrimaos (postes + 2 travessas): dentro do patamar ao pe-2, fora de RAMP_OUT_RAIL0 ao pe-2
        def rail(pts3, post_step=3.2):
            posts = list(pts3) + [q for q in fm_lib.resample(pts3, post_step)
                                  if min((q - c).length for c in pts3) > 1.4]
            for p in posts:
                mb.box((0.6, 0.6, 3.2), p + V((0, 0, 1.6)), (0, 0, yaw), "Wood_Dark", 0.0)
                mb.box((0.8, 0.8, 0.24), p + V((0, 0, 3.3)), (0, 0, yaw), "Wood_Dark", 0.0)
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
    mb.box((1.3 * s, 1.3 * s, 0.24), c + V((0, 0, -0.55 * s - 0.12)), (0, 0, 0), frame, 0.0)
    # vidro: do meio da base (-0,55 s - 0,12) ate 0,45 s; montantes da base (-0,55 s) ao telhado (0,58 s): nenhuma
    # face horizontal de materiais diferentes a menos de 0,1
    zg0, zg1 = -0.55 * s - 0.12, 0.45 * s
    mb.box((0.86 * s, 0.86 * s, zg1 - zg0), c + V((0, 0, (zg0 + zg1) / 2)), (0, 0, 0), "Lantern_Glow", 0.0)
    zp0, zp1 = -0.55 * s, 0.58 * s
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.box((0.24, 0.24, zp1 - zp0), c + V((sx * 0.47 * s, sy * 0.47 * s, (zp0 + zp1) / 2)), (0, 0, 0),
                   frame, 0.0)
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
                # montantes entram nas lajes de cima e de baixo (topo/pe a 0,1 do vidro)
                mb.box((0.36, 0.36, 1.45), F.p(sx * 0.62, sy * 0.62, 4.4), sq, "Stone_Wall_Light", 0.0)
        mb.box((2.2, 2.2, 0.3), F.p(0, 0, 5.17), sq, "Stone_Wall_Dark", 0.06)
        pyramid(mb, F.p(0, 0, 5.3), 1.1, 0.75, "Stone_Wall_Dark", D(a), 0.22)
        mb.box((0.42, 0.42, 0.45), F.p(0, 0, 6.28), sq, "Stone_Wall_Light", 0.0)
        col_box("MiningLantern", (1.7, 1.7, 6.4), F.p(0, 0, 3.2), sq)
    mb.finish()


# ------------------------------------------------------------------ 4. torres de mineracao
# Rodada 2 (critica): sem o telhadinho azul. Cavalete ABERTO de madeira (4 pernas afuniladas, travessas e X) com um
# cavalete de cabeca e uma POLIA (r DERRICK_SHEAVE_R) de frente para o centro do fosso. O cabo (Rope) passa por cima
# da polia: uma ponta desce pelo meio da torre ate a caçamba de minerio, a outra desce e fica amarrada na travessa.
DERRICK_B, DERRICK_T, DERRICK_H = 2.6, 1.9, 11.0     # meia-largura na base / no topo, cota do quadro de topo
DERRICK_SHEAVE_R = 1.2


def derrick(mb, F, rng):
    b, t, ztop = DERRICK_B, DERRICK_T, DERRICK_H
    WD, WP, MD, RP = "Wood_Dark", "Wood_Plank", "Metal_Dark", "Rope"

    def half(z):
        return b + (t - b) * (z / ztop)

    def leg(sx, sy, z):
        s = half(z)
        return F.p(sx * s, sy * s, z)

    corners = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    for sx, sy in corners:
        # sapata de pedra (fundo 0,25 abaixo do piso: longe das manchas planas do terreno)
        mb.box((1.5, 1.5, 0.8), F.p(sx * b, sy * b, 0.15), F.r(), "Stone_Wall_Dark", 0.0)
        mb.beam(leg(sx, sy, 0.5), leg(sx, sy, ztop + 0.45), 0.8, 0.8, WD, 0.0)
    for i in range(4):
        p, q = corners[i], corners[(i + 1) % 4]
        nx, ny = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2          # normal do lado (local)
        o = F.p(nx * 0.45, ny * 0.45) - F.p(0, 0)
        for z in (3.8, 7.4):
            mb.beam(leg(*p, z) + o * 0.5, leg(*q, z) + o * 0.5, 0.45, 0.5, WD, 0.0)
        for z0, z1 in ((0.9, 3.8), (3.8, 7.4), (7.4, ztop - 0.2)):
            if i == 1 and z0 == 3.8:
                continue            # face do centro: painel do meio aberto (a caçamba aparece)
            mb.beam(leg(*p, z0) + o, leg(*q, z1) + o, 0.34, 0.34, WD, 0.0)
            mb.beam(leg(*q, z0) + o, leg(*p, z1) + o, 0.34, 0.34, WD, 0.0)
        mb.beam(leg(*p, ztop), leg(*q, ztop), 0.55, 0.6, WD, 0.0)        # quadro do topo
    # cavalete de cabeca: 2 barrotes (ao longo de y) sobre o quadro e, em cada um, um A (2 pernas) que termina no
    # mancal do eixo: de frente, o cubo e os raios da polia ficam a vista
    zc = ztop + 1.65
    for sx in (-1, 1):
        x = sx * 0.95
        mb.beam(F.p(x, -t - 0.3, ztop + 0.5), F.p(x, t + 0.3, ztop + 0.5), 0.5, 0.45, WD, 0.0)
        for sy in (-1, 1):
            mb.beam(F.p(x, sy * (t - 0.15), ztop + 0.6), F.p(x, sy * 0.2, zc - 0.1), 0.42, 0.42, WD, 0.0)
        mb.box((0.5, 0.8, 0.7), F.p(x, 0.0, zc), F.r(), WD, 0.0)
        mb.beam(F.p(x, -(t - 0.4), ztop + 1.0), F.p(x, t - 0.4, ztop + 1.0), 0.36, 0.36, WD, 0.0)
    # polia de frente para o centro: disco de madeira (plano y-z local), 2 raios de ferro, cubo e eixo
    C = F.p(0.0, 0.0, zc)
    R = DERRICK_SHEAVE_R
    mb.cyl(R, 0.3, C, F.r(0, math.pi / 2, 0), WP, 12, bevel=0.0)
    mb.box((0.52, 2 * R - 0.25, 0.3), C, F.r(), MD, 0.0)
    mb.box((0.52, 0.3, 2 * R - 0.25), C, F.r(), MD, 0.0)
    mb.cyl(0.42, 0.9, C, F.r(0, math.pi / 2, 0), MD, 8, bevel=0.0)
    mb.rod(F.p(-1.45, 0.0, zc), F.p(1.45, 0.0, zc), 0.18, MD, 6)        # pontas 0,25 alem dos mancais
    # cabo: amarrado na travessa do lado -y, sobe, passa por cima da polia e desce ate a caçamba (+y)
    rr = 0.14
    rho = R + rr
    zb = 4.3                                            # fundo da caçamba (acima da cabeca do jogador)
    tie = F.p(0.0, -(half(3.8) + 0.1), 3.8 + 0.35)
    arc = [F.p(0.0, rho * math.cos(a), zc + rho * math.sin(a)) for a in [math.pi * k / 10.0 for k in range(10, -1, -1)]]
    hook = F.p(0.0, rho, zb + 2.25)
    mb.tube([tie, F.p(0.0, -rho, 5.2)] + arc + [hook], rr, RP, 6)
    mb.tube([tie + V((0, 0, 0.05)), tie - V((0, 0, 1.4))], rr, RP, 6)       # ponta solta pendurada
    # caçamba de madeira com aros, alca e carga de minerio
    bc = F.p(0.0, rho, zb)
    mb.cyl(0.8, 1.3, bc + V((0, 0, 0.65)), F.r(), WP, 8, r2=0.95, bevel=0.0)
    for hz in (0.28, 1.0):
        rz = 0.8 + 0.15 * hz / 1.3
        mb.cyl(rz + 0.13, 0.24, bc + V((0, 0, hz)), F.r(), MD, 8, bevel=0.0)
    mb.cyl(0.84, 0.5, bc + V((0, 0, 1.3)), F.r(), "Cliff_Rock_Dark", 6, r2=0.38, bevel=0.0)
    for sx in (-1, 1):
        mb.beam(F.p(sx * 1.0, rho, zb + 1.15), F.p(0.0, rho, zb + 2.3), 0.22, 0.22, MD, 0.0)
    mb.box((0.4, 0.4, 0.4), F.p(0.0, rho, zb + 2.3), F.r(), MD, 0.0)
    # monte de minerio escuro no pe, sob a caçamba (dentro da torre)
    for k in range(3):
        a = rng.uniform(0, math.tau)
        shard(mb, F.p(0.6 * math.cos(a), rho - 0.3 + 0.6 * math.sin(a), 0.0), rng.uniform(0.6, 0.9),
              rng.uniform(0.6, 0.8), "Cliff_Rock_Dark", rng, n=5, top=0.5, sink=0.3, blunt=True)


def derricks():
    rng = random.Random(6101)
    mb = MMB("MINE_Derricks", rng, detail="near", vcap=1, remap={"Metal_Iron": "Metal_Dark"})
    for ang in L.DERRICKS:
        a = D(ang)
        cx, cy = L.DERRICK_R * math.cos(a), L.DERRICK_R * math.sin(a)
        F = Frame(cx, cy, L.PIT, a + math.pi)            # +x local = para o centro do fosso
        derrick(mb, F, rng)
        col_box("MiningDerrick", (2 * DERRICK_B + 1.4, 2 * DERRICK_B + 1.4, DERRICK_H + 0.5),
                F.p(0, 0, (DERRICK_H + 0.5) / 2), F.r())
    mb.finish()


# ------------------------------------------------------------------ 5. formacao central (peca-heroi, NAO se minera)
# Rodada 2 (critica): virou monumento. Agora e um monte BAIXO de rochas escuras (topo <= L.PIT + 8) com uma coroa de
# cristais azuis grossos inclinados para fora. O eixo N-S (|x| < CORE_SIGHT_HW) fica sem pontas altas: do anel sul o
# jogador ve a escada N e a porta do salao por cima/entre os cristais.
CORE_TOP = L.PIT + 8.0 - 0.15
CORE_SIGHT_HW = 2.6
CORE_SIGHT_Z = L.PIT + 5.4        # teto das pecas dentro da faixa de visada


def _sight_cap(x, r, want):
    """altura maxima (acima de L.PIT) de uma pedra cuja pegada cruza a faixa de visada N-S"""
    if abs(x) - r < CORE_SIGHT_HW:
        return min(want, CORE_SIGHT_Z - L.PIT)
    return want


def core():
    rng = random.Random(7101)
    mb = MMB("MINE_Core_Formation", rng, detail="near", vcap=1,
             remap={"Cliff_Rock_Dark": "Cliff_Rock_Dark_B", "Cliff_Rock": "Cliff_Rock_Dark"})
    z = L.PIT
    R = L.CORE_R
    top = CORE_TOP
    # monte baixo de terra sob as pedras (cone com ponta: sem tampa plana paralela a nada)
    a0 = rng.uniform(0, 1)
    rings = []
    for rr, zz in ((R - 0.2, -0.4), (R * 0.7, 0.5)):
        rings.append([V((rr * math.cos(a0 + math.tau * i / 14) * rng.uniform(0.96, 1.04),
                         rr * math.sin(a0 + math.tau * i / 14) * rng.uniform(0.96, 1.04), z + zz)) for i in range(14)])
    _solid(mb, rings, "Dirt_Pit", V((0.0, 0.0, z + 1.4)))
    DARK, MID = "Cliff_Rock_Dark", "Cliff_Rock"
    # anel externo: pedras largas e baixas inclinadas para fora (3 escuras : 1 cinza)
    for i in range(13):
        a = math.tau * i / 13 + rng.uniform(-0.14, 0.14)
        rr = rng.uniform(1.5, 2.0)
        d = min(R - rr * 1.15 - 0.2, rng.uniform(6.6, 7.4))
        x, y = d * math.cos(a), d * math.sin(a)
        h = _sight_cap(x, rr, rng.uniform(2.0, 3.4))
        shard(mb, (x, y, z), h, rr, MID if i % 4 == 1 else DARK, rng, lean(a, rng.uniform(0.15, 0.3)), n=5, top=0.45)
    # anel do meio: pedras mais altas (topo 6,6..8,4), mais baixas na faixa de visada
    for i in range(9):
        a = math.tau * i / 9 + 0.2 + rng.uniform(-0.15, 0.15)
        d = rng.uniform(4.4, 5.3)
        rr = rng.uniform(1.8, 2.3)
        x, y = d * math.cos(a), d * math.sin(a)
        h = _sight_cap(x, rr * 0.6, rng.uniform(3.4, 5.0))
        shard(mb, (x, y, z), h, rr, MID if i % 3 == 2 else DARK, rng, lean(a, rng.uniform(0.1, 0.22)), n=5,
              top=0.42)
    # miolo: 4 blocos escuros sob a coroa (a leste e a oeste, fora da faixa de visada)
    for a_deg in (15.0, 165.0, 200.0, 340.0):
        a = D(a_deg + rng.uniform(-8, 8))
        shard(mb, (2.3 * math.cos(a), 2.3 * math.sin(a), z), rng.uniform(4.2, 5.0), 2.0, DARK, rng, lean(a, 0.1),
              n=5, top=0.45)
    # coroa de cristais grossos inclinados para fora (os mais altos a L e O; nenhum no eixo N-S)
    CB, CT = "Crystal_Blue", "Crystal_Blue_Core"
    for k, a_deg in enumerate((0.0, 42.0, 138.0, 180.0, 222.0, 318.0)):
        a = D(a_deg + rng.uniform(-7, 7))
        t = rng.uniform(0.36, 0.48)
        d = 2.5
        bz = z + 1.5
        tip = top - (0.0 if k in (0, 3) else rng.uniform(0.4, 1.1))
        h = (tip - bz) / math.cos(t)
        crystal(mb, (d * math.cos(a), d * math.sin(a), bz), h, rng.uniform(1.3, 1.6), lean(a, t), CB, CT, rng, 6,
                0.2, 1.3)
    # cristal central: grosso e curto (topo ~ L.PIT + 5,6), levemente para o norte
    crystal(mb, (0.0, 0.3, z + 1.6), (CORE_SIGHT_Z + 0.3 - z - 1.6) / math.cos(0.12), 1.75, lean(D(90.0), 0.12),
            CB, CT, rng, 6, 0.22, 1.4)
    # cristais medios entre as pedras do meio (fora da faixa de visada)
    for a_deg in (20.0, 65.0, 115.0, 160.0, 200.0, 245.0, 295.0, 340.0):
        a = D(a_deg + rng.uniform(-6, 6))
        d = rng.uniform(3.6, 4.4)
        x, y = d * math.cos(a), d * math.sin(a)
        t = rng.uniform(0.45, 0.6)
        h = rng.uniform(3.0, 4.2)
        if abs(x) < CORE_SIGHT_HW + 0.8:
            h = min(h, (CORE_SIGHT_Z - z - 1.2) / math.cos(t))
        crystal(mb, (x, y, z + 1.4), h, rng.uniform(0.7, 0.95), lean(a, t), CB, CT, rng, 6, 0.25, 0.8)
    # cristais pequenos entre as pedras de fora
    for i in range(9):
        a = math.tau * i / 9 + 0.35 + rng.uniform(-0.15, 0.15)
        d = rng.uniform(6.0, 7.0)
        crystal(mb, (d * math.cos(a), d * math.sin(a), z + rng.uniform(0.5, 1.2)), rng.uniform(1.6, 2.4),
                rng.uniform(0.42, 0.55), lean(a, rng.uniform(0.5, 0.7)), CB, CT, rng, 6, 0.36, 0.4)
    # cascalho escuro na borda do monte
    for i in range(18):
        a = rng.uniform(0, math.tau)
        d = rng.uniform(8.6, 9.6)
        rr = rng.uniform(0.45, 0.8)
        shard(mb, (d * math.cos(a), d * math.sin(a), z), rr * 1.1, rr, DARK if i % 3 else MID, rng, n=5, top=0.5,
              sink=0.3, blunt=True)
    ob = mb.finish()
    zmax = max(v.co.z for v in ob.data.vertices)
    print("MINE nucleo: topo z=%.2f (limite %.2f) %s" % (zmax, L.PIT + 8.0, "OK" if zmax <= L.PIT + 8.0 else
                                                         "ESTOUROU"))
    # colisao: octogono largo e baixo (2 caixas) + octogono estreito ate o topo (2 caixas)
    col_box("MiningCore", (16.0, 16.0, 4.6), (0, 0, z + 2.3))
    col_box("MiningCore", (16.0, 16.0, 4.6), (0, 0, z + 2.3), (0, 0, math.pi / 4))
    col_box("MiningCore", (10.0, 10.0, top - z), (0, 0, (z + top) / 2), (0, 0, math.pi / 8))
    col_box("MiningCore", (10.0, 10.0, top - z), (0, 0, (z + top) / 2), (0, 0, 3 * math.pi / 8))
    light("L_Mining_Core_Glow", "POINT", (0, 0, z + 7.0), 600, (0.35, 0.62, 1.0), 2.5)


# ------------------------------------------------------------------ 6. minerio por raridade
def on_stairs(x, y, r):
    """ponto de minerio com o CENTRO dentro da pegada das escadas N/S (r 45,6..60, |x| < meia-largura + banzo)"""
    hw = L.PIT_STAIR_W / 2 + 1.2
    y0 = L.PIT_R - L.PIT_STAIR_N * 1.6
    return abs(x) < hw and abs(y) > y0 - 0.3


def _ore_common(mb, x, y, r, rng):
    """COMMON (rodada 2): rocha cinza baixa e larga (60% do tamanho da rodada 1), afundada no chao, com 1-2 pontas
    azuis pequenas SEM Core (nao brilha): quase parte do piso; a raridade se le pelo tamanho e pela cor"""
    z = L.PIT
    k = 0.6
    shard(mb, (x, y, z), rng.uniform(2.0, 2.4) * k, 1.55 * k * 1.15, "Cliff_Rock", rng, n=6, top=0.55, blunt=True,
          sink=0.45, squash=0.85)
    b = rng.uniform(0, math.tau)
    shard(mb, (x + 1.35 * k * math.cos(b), y + 1.35 * k * math.sin(b), z), 1.2 * k, 0.85 * k * 1.1, "Cliff_Rock", rng,
          n=5, top=0.5, blunt=True, sink=0.4)
    for j in range(1 + (rng.random() < 0.5)):
        a = b + math.pi + (j - 0.5) * 1.3 + rng.uniform(-0.3, 0.3)
        d = rng.uniform(0.2, 0.45)
        crystal(mb, (x + d * math.cos(a), y + d * math.sin(a), z + rng.uniform(0.75, 0.95)), rng.uniform(0.6, 0.85),
                rng.uniform(0.2, 0.24), lean(a, rng.uniform(0.3, 0.5)), "Crystal_Blue", "Crystal_Blue", rng, 5, 0.42,
                0.3)
    for j in range(2):
        a = rng.uniform(0, math.tau)
        d = rng.uniform(1.25, 1.5)
        shard(mb, (x + d * math.cos(a), y + d * math.sin(a), z), 0.4, 0.34, "Cliff_Rock", rng, n=5, top=0.5,
              sink=0.3, blunt=True)
    return 1.8, 1.5


def _ore_uncommon(mb, x, y, r, rng):
    """UNCOMMON (rodada 2): rocha cinza com cristais azul-ciano (~70,160,255), sem brilho (ponta clara, nao Neon)"""
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
                lean(a, 0.1 if k == 1 else rng.uniform(0.3, 0.55)), "Crystal_MineCyan", "Crystal_MineCyan_Tip",
                rng, 6, 0.36, 0.4)
    for k in range(3):
        a = rng.uniform(0, math.tau)
        d = rng.uniform(2.0, 2.45)
        shard(mb, (x + d * math.cos(a), y + d * math.sin(a), z), 0.5, 0.4, "Cliff_Rock", rng, n=5, top=0.5,
              sink=0.3, blunt=True)
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
              sink=0.3, blunt=True)
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
                lean(a, 0.55), "Crystal_MineGold", "Crystal_MineGold_Glow", rng, 5, 0.4, 0.3)
    return 5.0, 3.2


ORE_BUILD = {"COMMON": _ore_common, "UNCOMMON": _ore_uncommon, "EPIC": _ore_epic, "SUPERLEGENDARY": _ore_super}


def ores(pts):
    mbs = {}
    skipped = []
    for kind, _ in L.ORE_KINDS:
        mbs[kind] = MMB("MINE_Ore_%s" % kind, random.Random(zlib.crc32(kind.encode()) & 0xffff), detail="near",
                        vcap=1, remap={"Cliff_Rock": "Cliff_Rock_C", "Cliff_Rock_Dark": "Cliff_Rock_Dark_B"})
    for kind, i, x, y, r in pts:
        if on_stairs(x, y, r):
            skipped.append("ORE_%s_%02d" % (kind, i))
            continue
        rng = random.Random(zlib.crc32(("%s_%d" % (kind, i)).encode()) & 0xffffff)
        ORE_BUILD[kind](mbs[kind], x, y, r, rng)
        # (rodada 2: sem COL_MineOre - o jogo gera as rochas mineraveis nos marcadores ORE_*; isto e so previa)
    for mb in mbs.values():
        mb.finish()
    if skipped:
        print("MINE AVISO: pontos de minerio DENTRO das escadas N/S (sem visual/colisao): %s" % ", ".join(skipped))
    return skipped


# ------------------------------------------------------------------ 7. props de borda (junto ao pe do muro)
def _at(r, a_deg):
    a = D(a_deg)
    return r * math.cos(a), r * math.sin(a)


# pecas proprias (rodada 2): os kits do lobby (PK.crate/keg/cart/tool_rack) tem cintas e aros a 0,03-0,05 do corpo
# (z-fighting no Roblox) e laminas de 0,1. Aqui: cintas/aros >= 0,12 salientes, secoes >= 0,2, fundos enterrados.
def m_crate(mb, loc, s, yaw, lid=True, fill=None):
    """caixote (loc = centro do fundo). lid=False: caixa aberta com enchimento de pedra 0,15 abaixo da borda"""
    x, y, z = loc
    F = Frame(x, y, z, yaw)
    WP, WD = "Wood_Plank", "Wood_Dark"
    if lid:
        mb.box((s, s, s), F.p(0, 0, s / 2), F.r(), WP, 0.0)
        for dz in (0.35, s - 0.35):
            mb.box((s + 0.24, s + 0.24, 0.3), F.p(0, 0, dz), F.r(), WD, 0.0)
        return F
    th = 0.3
    mb.box((s, s, s - 0.45), F.p(0, 0, (s - 0.45) / 2), F.r(), WP, 0.0)          # miolo ate o enchimento
    for sx in (-1, 1):
        mb.box((th, s, 0.45), F.p(sx * (s - th) / 2, 0, s - 0.225), F.r(), WP, 0.0)
        mb.box((s - 2 * th, th, 0.45), F.p(0, sx * (s - th) / 2, s - 0.225), F.r(), WP, 0.0)
    mb.box((s - 2 * th, s - 2 * th, 0.3), F.p(0, 0, s - 0.3), F.r(), fill or "Cliff_Rock_Dark", 0.0)
    mb.box((s + 0.24, s + 0.24, 0.3), F.p(0, 0, 0.35), F.r(), WD, 0.0)
    mb.box((s + 0.24, s + 0.24, 0.3), F.p(0, 0, s - 1.0), F.r(), WD, 0.0)
    return F


def m_keg(mb, loc, r, h):
    """barril (loc = centro do fundo, ja enterrado pelo chamador) com 2 aros 0,12 salientes"""
    x, y, z = loc
    mb.cyl(r, h * 0.5, (x, y, z + h * 0.25), (0, 0, 0), "Wood_Plank", 8, r2=r * 1.12, bevel=0.0)
    mb.cyl(r * 1.12, h * 0.5, (x, y, z + h * 0.75), (0, 0, 0), "Wood_Plank", 8, r2=r, bevel=0.0)
    for zz in (0.35, h - 0.35):
        f = zz / (h * 0.5) if zz < h * 0.5 else (h - zz) / (h * 0.5)
        mb.cyl(r * (1 + 0.12 * f) + 0.12, 0.26, (x, y, z + zz), (0, 0, 0), "Metal_Dark", 8, bevel=0.0)


def m_rails(mb, pts, gauge=2.6, step=1.7):
    """trilho curto: dormentes enterrados (topo 0,4) + 2 barras em vigas (0,4..0,7)"""
    fine = fm_lib.resample(pts, step)
    for i, p in enumerate(fine):
        j, k = min(i + 1, len(fine) - 1), max(i - 1, 0)
        t = fine[j] - fine[k]
        mb.box((0.8, gauge + 1.4, 0.6), (p.x, p.y, L.PIT + 0.1), (0, 0, math.atan2(t.y, t.x)), "Wood_Dark", 0.0)
    for sg in (-1, 1):
        off = []
        for i, p in enumerate(pts):
            j, k = min(i + 1, len(pts) - 1), max(i - 1, 0)
            t = (pts[j] - pts[k]).normalized()
            off.append(p + V((-t.y, t.x, 0)) * sg * gauge / 2)
        for a, b in zip(off, off[1:]):
            mb.beam(V((a.x, a.y, L.PIT + 0.55)), V((b.x, b.y, L.PIT + 0.55)), 0.32, 0.3, "Metal_Dark", 0.0)


def m_cart(mb, loc, yaw, rng, load="ore"):
    """vagonete de mina: rodas no trilho (loc.z = topo do trilho), chassi, cacamba de tabua com aro e carga"""
    x, y, z = loc
    F = Frame(x, y, z, yaw)                     # x local = ao longo do trilho
    MD, WP = "Metal_Dark", "Wood_Plank"
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.cyl(0.55, 0.3, F.p(sx * 1.0, sy * 1.3, 0.55), F.r(math.pi / 2, 0, 0), MD, 8, bevel=0.0)
        mb.rod(F.p(sx * 1.0, -1.5, 0.55), F.p(sx * 1.0, 1.5, 0.55), 0.15, MD, 6)
    mb.box((3.0, 1.8, 0.4), F.p(0, 0, 0.95), F.r(), MD, 0.0)
    zt = 2.75
    mb.cyl(1.75, zt - 1.15, F.p(0, 0, (1.15 + zt) / 2), F.r(0, 0, math.pi / 4), WP, 4, r2=2.1, bevel=0.0)
    hs = 2.1 / math.sqrt(2.0)
    sq = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    for i in range(4):
        a, b = sq[i], sq[(i + 1) % 4]
        mb.beam(F.p(a[0] * (hs + 0.15), a[1] * (hs + 0.15), zt), F.p(b[0] * (hs + 0.15), b[1] * (hs + 0.15), zt),
                0.3, 0.34, MD, 0.0)
    mb.cyl(2.1, 0.6, F.p(0, 0, zt + 0.02 + 0.3), F.r(0, 0, math.pi / 4), "Cliff_Rock_Dark", 4, r2=0.9, bevel=0.0)
    if load == "crystal":
        for k in range(3):
            a = rng.uniform(0, math.tau)
            crystal(mb, F.p(0.5 * math.cos(a), 0.5 * math.sin(a), zt + 0.4), rng.uniform(0.9, 1.3), 0.3,
                    lean(a, 0.35), "Crystal_Blue", "Crystal_Blue", rng, 5, 0.4, 0.3)


def m_tools(mb, F, rng, kinds=("pick", "shovel", "pick", "pick", "shovel")):
    """cavalete de ferramentas (F: +y local = frente): 2 montantes, 2 travessas, picaretas e pas (secoes >= 0,2)"""
    w = 1.2 * len(kinds) + 0.8
    WD, WP, MD = "Wood_Dark", "Wood_Plank", "Metal_Dark"
    for sx in (-1, 1):
        mb.box((0.5, 0.5, 3.8), F.p(sx * w / 2, 0, 1.85), F.r(), WD, 0.0)
    for zz in (0.9, 3.0):
        mb.box((w + 0.4, 0.36, 0.36), F.p(0, 0.2, zz), F.r(), WD, 0.0)
    for i, k in enumerate(kinds):
        xx = -w / 2 + 0.8 + i * ((w - 1.6) / max(1, len(kinds) - 1))
        a = F.p(xx + rng.uniform(-0.1, 0.1), 1.0, 0.0)
        b = F.p(xx, 0.62, 3.4)
        ax = (b - a).normalized()
        if k == "pick":
            mb.beam(a, b + ax * 0.2, 0.24, 0.24, WP, 0.0)
            hd = F.p(1, 0) - F.p(0, 0)
            for sg in (-1, 1):
                mb.beam(b, b + hd * sg * 1.0 - ax * 0.3, 0.3, 0.3, MD, 0.0)
        else:
            mb.beam(a + ax * 1.0, b, 0.22, 0.22, WP, 0.0)
            mb.beam(a, a + ax * 1.05, 0.9, 0.22, MD, 0.0)
            side = F.p(1, 0) - F.p(0, 0)
            mb.beam(b - side * 0.35, b + side * 0.35, 0.22, 0.22, WP, 0.0)


def props(ore_pts):
    rng = random.Random(8101)
    mb = MMB("MINE_Props", rng, detail="near", vcap=1,
             remap={"Wood_Light": "Wood_Plank", "Metal_Iron": "Metal_Dark"})
    z = L.PIT
    zb = z - 0.15                          # fundo das pecas apoiadas no piso (enterrado 0,15)
    # vagonetes em trilho curto perto do pe da rampa leste (vao livre entre o minerio e a torre NE)
    R = 56.4
    a0, a1 = 32.8, 44.2
    pts = [V((*_at(R, a0 + (a1 - a0) * k / 8), z)) for k in range(9)]
    m_rails(mb, pts)
    t_end = (pts[-1] - pts[-2]).normalized()
    ye = math.atan2(t_end.y, t_end.x)
    pe = pts[-1] + t_end * 0.5
    mb.box((1.1, 4.2, 1.3), (pe.x, pe.y, z + 1.2), (0, 0, ye), "Wood_Dark", 0.05)          # para-choque
    for sg in (-1, 1):
        q = pe + t_end * 0.9 + V((-t_end.y, t_end.x, 0)) * sg * 1.5
        mb.box((0.6, 0.6, 2.2), (q.x, q.y, z + 0.9), (0, 0, ye), "Wood_Dark", 0.0)
    for ac, load in ((35.6, "crystal"), (40.3, "ore")):
        x, y = _at(R, ac)
        m_cart(mb, (x, y, z + 0.7), D(ac) + math.pi / 2, rng, load)
    m0, m1 = V((*_at(R, 34.0), z)), V((*_at(R, 42.0), z))
    c = (m0 + m1) / 2
    col_box("MiningProps", ((m1 - m0).length + 3.2, 2.6, 3.6), (c.x, c.y, z + 1.8),
            (0, 0, math.atan2(m1.y - m0.y, m1.x - m0.x)))
    # pilha de caixas NO (112 graus)
    x, y = _at(56.0, 112.0)
    yaw = D(112.0) + math.pi / 2
    F = Frame(x, y, z, yaw)
    q = F.p(-1.3, 0.0)
    m_crate(mb, (q.x, q.y, zb), 2.3, yaw + 0.08)
    q = F.p(1.2, 0.2)
    m_crate(mb, (q.x, q.y, zb), 2.1, yaw - 0.12)
    q = F.p(-0.9, 0.1)
    m_crate(mb, (q.x, q.y, zb + 2.3), 1.8, yaw + 0.3)
    q = F.p(3.5, 0.9)
    m_keg(mb, (q.x, q.y, zb), 0.8, 2.05)
    col_box("MiningProps", (7.6, 3.2, 3.0), tuple(F.p(0.9, 0.3, 1.5)), F.r())
    # suporte de ferramentas (146 graus), encostado no muro, de frente para o centro
    x, y = _at(57.2, 146.0)
    F = Frame(x, y, z, D(146.0) + math.pi / 2)
    m_tools(mb, F, rng)
    col_box("MiningProps", (7.2, 1.8, 3.8), tuple(F.p(0, 0.3, 1.9)), F.r())
    # mesa de triagem (215 graus): pes, tampo, travessa, bandeja de ferro com pedras e 2 cristais azuis
    x, y = _at(55.6, 215.0)
    F = Frame(x, y, z, D(215.0) + math.pi / 2)
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.box((0.4, 0.4, 2.75), F.p(sx * 1.9, sy * 0.95, 1.225), F.r(), "Wood_Dark", 0.0)
    mb.box((4.6, 2.5, 0.32), F.p(0, 0, 2.72), F.r(), "Wood_Plank", 0.0)
    mb.box((4.0, 0.3, 0.3), F.p(0, 0, 0.7), F.r(), "Wood_Dark", 0.0)
    mb.box((2.0, 1.7, 0.24), F.p(-1.0, 0.0, 3.1), F.r(0.14, 0, 0), "Metal_Dark", 0.0)
    for k in range(3):
        a = rng.uniform(0, math.tau)
        shard(mb, F.p(-1.0 + 0.45 * math.cos(a), 0.35 * math.sin(a), 3.2), 0.45, 0.36, "Cliff_Rock_Dark", rng, n=5,
              top=0.5, sink=0.15, blunt=True)
    for k in range(2):
        crystal(mb, F.p(0.9 + k * 0.6, -0.3 + k * 0.6, 2.88), 0.9, 0.24, lean(rng.uniform(0, 6), 0.25),
                "Crystal_Blue", "Crystal_Blue", rng, 5, 0.4, 0.1)
    q = F.p(3.1, 0.9)
    m_keg(mb, (q.x, q.y, zb), 0.62, 1.35)
    col_box("MiningProps", (5.4, 3.0, 3.2), tuple(F.p(0.3, 0.1, 1.6)), F.r())
    # caixas (250 graus): uma fechada, uma aberta com pedra e cristais azuis, uma empilhada
    x, y = _at(56.0, 250.0)
    yaw = D(250.0) + math.pi / 2
    F = Frame(x, y, z, yaw)
    q = F.p(-1.2, 0.2)
    m_crate(mb, (q.x, q.y, zb), 2.2, yaw - 0.1)
    q = F.p(1.3, 0.0)
    m_crate(mb, (q.x, q.y, zb), 2.2, yaw + 0.15, lid=False)
    top = V((q.x, q.y, zb + 2.2 - 0.15))
    for k in range(3):
        a = rng.uniform(0, math.tau)
        crystal(mb, top + V((0.4 * math.cos(a), 0.4 * math.sin(a), 0.0)), rng.uniform(0.9, 1.4), 0.3,
                lean(a, 0.3), "Crystal_Blue", "Crystal_Blue", rng, 5, 0.4, 0.25)
    q = F.p(-1.0, 0.1)
    m_crate(mb, (q.x, q.y, zb + 2.2), 1.7, yaw + 0.35)
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
        mb.box((5.2, 0.6, 0.4), F.p(0, 0, 0.15), F.r(), "Wood_Dark", 0.0)
        for sx in (-1, 1):
            mb.beam(F.p(-sx * 2.0, 0.18, 0.5), F.p(sx * 2.0, 0.18, 5.75), 0.34, 0.34, "Wood_Dark", 0.0)
        if k % 2 == 0:
            top = F.p(0, 0.75, 6.1)
            mb.box((0.36, 1.1, 0.36), F.p(0, 0.45, 6.1), F.r(), "Metal_Dark", 0.0)
            mb.rod(top, top - V((0, 0, 0.5)), 0.1, "Metal_Dark", 4)
            box_lantern(mb, top - V((0, 0, 1.3)), 0.8)
    return picked


def pebble(mb, x, y, s, rng, m="Cliff_Rock"):
    """seixo baixo de 2 aneis + ponta (sem tampa plana: nada paralelo as manchas planas do piso do terreno)"""
    a0 = rng.uniform(0, math.tau)
    rings = []
    for rr, zz in ((s, -0.28), (s * 0.62, s * 0.5)):
        rings.append([V((x + rr * rng.uniform(0.85, 1.15) * math.cos(a0 + math.tau * i / 5),
                         y + rr * rng.uniform(0.85, 1.15) * math.sin(a0 + math.tau * i / 5), L.PIT + zz))
                      for i in range(5)])
    _solid(mb, rings, m, V((x + rng.uniform(-0.1, 0.1) * s, y + rng.uniform(-0.1, 0.1) * s, L.PIT + s * 0.85)))


def rubble(ore_pts):
    """cascalho solto no piso do fosso (a textura das referencias); sem colisao. Rodada 2: sem as lascas de cristal
    soltas (confete) - o azul fica nos minerios e no nucleo"""
    rng = random.Random(9901)
    mb = MMB("MINE_Pit_Rubble", rng, detail="near", vcap=1)
    z = L.PIT
    n = 0
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
        if any(math.hypot(x - L.DERRICK_R * math.cos(D(d)), y - L.DERRICK_R * math.sin(D(d))) < 5.4
               for d in L.DERRICKS):
            continue
        k = 1 + (rng.random() < 0.45) + (rng.random() < 0.2)
        for j in range(k):
            ox, oy = (rng.uniform(-0.9, 0.9), rng.uniform(-0.9, 0.9)) if j else (0.0, 0.0)
            s = rng.uniform(0.24, 0.5)
            pebble(mb, x + ox, y + oy, s, rng)
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


# ------------------------------------------------------------------ QA: rotas e sondas da zona (il_qa.module_routes)
def _qa_extra():
    rr = {}
    # escada S -> escada N contornando o nucleo pelo oeste e pelo leste (o nucleo e monumento: nao pode fechar o fosso)
    for tag, sg in (("O", -1.0), ("L", 1.0)):
        rr["FOSSO_S->N_contorna_nucleo_" + tag] = ([(0.0, -44.0), (0.0, -24.0), (sg * 9.0, -13.0), (sg * 13.0, -4.0),
                                                    (sg * 13.0, 4.0), (sg * 9.0, 13.0), (0.0, 24.0), (0.0, 44.0)],
                                                   L.PIT)
    # volta completa em r 12,5 em volta do nucleo (colisao do nucleo termina em r 8,7 no vertice)
    rr["FOSSO_volta_do_nucleo"] = ([(12.5 * math.cos(D(a)), 12.5 * math.sin(D(a))) for a in range(0, 361, 20)],
                                   L.PIT)
    pr = []
    for side, tag in ((1, "L"), (-1, "O")):
        g = _ramp_geo(side)
        P, hw = g["P"], L.PIT_RAMP_W / 2
        for s_mid in (10.0, 20.0):
            for v, sgn, lab in ((hw - 0.9, 1.0, "fora"), (-hw + 0.9, -1.0, "dentro")):
                q = P(s_mid, v)
                pr.append(("MINE_rampa_%s_%s_s%d" % (tag, lab, int(s_mid)), q.x, q.y, q.z, g["out"].x * sgn,
                           g["out"].y * sgn))
    return rr, pr


EXTRA_ROUTES, EXTRA_PROBES = _qa_extra()
