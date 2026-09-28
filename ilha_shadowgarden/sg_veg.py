# sg_veg - VESTIR / VEGETACAO da Ilha 3 (Shadow Garden). Junto com sg_props e sg_lights substitui sg_blockout.dressing.
# Prefixo SG_Veg_, colecao 10_VEGETATION. Sem luzes (sg_lights).
#   1. pinheiros/abetos escuros estilizados (camadas conicas escalonadas de saia caida, fundo escuro, topo raspado de
#      luar vindo de noroeste) em GRUPOS que emolduram: borda sul da praca, pescoco da entrada, terreno bravo oeste e
#      noroeste do castelo, norte atras da torre-coroa, nordeste junto aos montes de basalto, beira leste;
#   2. poucos pinheiros e ciprestes finos no P2 (grama) entre as casas e atras delas; no piso calcado (P1/P3) a arvore
#      nasce num canteiro de cantaria (le como plantada, nao como enfeite solto);
#   3. arbustos baixos e tufos de grama fria SO na base de algumas arvores.
# Tudo assentado no chao REAL: raio de cima para baixo contra as malhas ja montadas (terreno e zonas). O pe precisa cair
# em SG_Ter_*; a copa nao pode encostar em predio, muro, ponte, rua, escada, agua; nada em rua/escada/ponte/praca/patio
# do castelo/salao/summon/craft/portaria/ilhota. Arvore em piso andavel: colisao so no tronco (caixa fina) e copa longe
# das rotas do QA; no terreno bravo (fora de piso: nao alcancavel, guarda invisivel na borda) sem colisao.
import math, random
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import sg_lib as SL
from sg_lib import MB, col_box, fm_lib
import sg_layout as L
import fm_veg_kit as VK

P1, P2, P3, SUM = L.P1, L.P2, L.P3, L.SUM
COLL = "10_VEGETATION"
LEAF = "Leaf_SG_Pine"
BARK = "Wood_SG_Dark"
GRASS = "Grass_SG"
TRIM = "Stone_SG_Trim"
# materiais novos da zona (2 de 4): topo de agulhas raspado pelo luar (azul-esverdeado frio) e fundo das saias
MOON = "Leaf_SGVegMoon"
SHADE = "Leaf_SGVegShade"
fm_lib.MATS.setdefault(MOON, (fm_lib.S(66, 96, 104), 0.85, 0.0, 0, None, 0.08))
fm_lib.MATS.setdefault(SHADE, (fm_lib.S(16, 24, 30), 0.9, 0.0, 0, None, 0.06))
MOON_DIR = Vector((-0.45, 0.55, 0.70)).normalized()      # = sg_scene.MOON_DIR (luar de noroeste)

CAMS = {
    # 360: frente (sul), tras (norte), lados; + altura do jogador no P1, no P2 e no beco oeste do castelo
    "CAM_SGVeg_Front": ((30.0, -262.0, 70.0), (0.0, -150.0, 40.0), 24),
    "CAM_SGVeg_Back": ((40.0, 330.0, 120.0), (0.0, 150.0, 60.0), 24),
    "CAM_SGVeg_West": ((-250.0, 60.0, 90.0), (-100.0, 60.0, 48.0), 24),
    "CAM_SGVeg_East": ((270.0, 60.0, 100.0), (110.0, 90.0, 50.0), 24),
    "CAM_SGVeg_Neck": ((95.0, -300.0, 62.0), (0.0, -200.0, 22.0), 22),
    "CAM_SGVeg_NorthWest": ((-300.0, 320.0, 120.0), (-40.0, 100.0, 30.0), 24),
    "CAM_SGVeg_CliffSE": ((260.0, -250.0, 80.0), (100.0, -150.0, 36.0), 24),
    "CAM_SGVeg_PH_P1South": ((-4.0, -150.0, P1 + 5.2), (-80.0, -165.0, P1 + 8.0), 22),
    "CAM_SGVeg_PH_P2": ((-10.0, -58.0, P2 + 5.2), (-90.0, -30.0, P2 + 8.0), 22),
    "CAM_SGVeg_PH_P3North": ((-22.0, 170.0, P3 + 5.2), (14.0, 196.0, P3 - 4.0), 22),
}
# rotas extras: a faixa do P1 ao pe do arrimo entre as casas e a escada (onde ha canteiros) continua livre
EXTRA_ROUTES = {
    "VEG_P1_canteiros_O": ([(-14.0, -104.0), (-40.0, -106.0), (-56.0, -106.0)], P1),
    "VEG_P1_canteiros_L": ([(14.0, -104.0), (40.0, -106.0), (56.0, -106.0)], P1),
    "VEG_P2_ciprestes": ([(-100.0, -40.0), (-76.0, -40.0), (-76.0, -30.0), (-40.0, -34.0)], P2),
}
EXTRA_PROBES = []

# arvores ja plantadas (x, y, z_pe, raio_copa, altura) - os props consultam
PLACED = []


# ------------------------------------------------------------------ o chao real (raios contra as malhas montadas)
class Scene:
    SKIP = ("COL_", "SG_Sky_", "PREVIEW_", "SCALE_", "SG_Veg_", "SG_Prop_", "CAM_", "L_")

    def __init__(self):
        vs, tris, owner, self.names = [], [], [], []
        base = 0
        for o in bpy.data.objects:
            if o.type != "MESH" or o.name.startswith(self.SKIP) or o.hide_render:
                continue
            me = o.data
            if not me.polygons:
                continue
            me.calc_loop_triangles()
            nv = len(me.vertices)
            co = np.empty(nv * 3, dtype=np.float64)
            me.vertices.foreach_get("co", co)
            co = co.reshape(nv, 3)
            M = np.array(o.matrix_world)
            co = co @ M[:3, :3].T + M[:3, 3]
            nt = len(me.loop_triangles)
            tv = np.empty(nt * 3, dtype=np.int64)
            me.loop_triangles.foreach_get("vertices", tv)
            tris.append(tv.reshape(nt, 3) + base)
            vs.append(co)
            owner.append(np.full(nt, len(self.names), dtype=np.int32))
            self.names.append(o.name)
            base += nv
        V = np.concatenate(vs)
        T = np.concatenate(tris)
        self.owner = np.concatenate(owner)
        self.bvh = BVHTree.FromPolygons(V.tolist(), T.tolist(), all_triangles=True)

    def hit(self, x, y, z0=420.0):
        loc, nrm, idx, d = self.bvh.ray_cast(Vector((x, y, z0)), Vector((0.0, 0.0, -1.0)), 700.0)
        if loc is None:
            return None, None, None
        return loc.z, self.names[int(self.owner[idx])], nrm


def is_ter(nm):
    return nm is not None and nm.startswith("SG_Ter_")


# ------------------------------------------------------------------ rotas do QA (a copa e o tronco ficam longe delas)
def route_lines():
    import sys
    out = []
    try:
        import sg_qa
        for pts, z in list(sg_qa.routes().values()) + list(sg_qa.open_routes().values()):
            out.append((list(pts), z))
    except Exception as ex:
        print("VEG AVISO rotas do sg_qa indisponiveis (%s)" % ex)
    try:
        import build_sg
        for mods in build_sg.ZONE_MODULES.values():
            for m in mods:
                mod = sys.modules.get(m)
                if mod is None or m == __name__:
                    continue
                for pts, z in getattr(mod, "EXTRA_ROUTES", {}).values():
                    out.append((list(pts), z))
    except Exception as ex:
        print("VEG AVISO rotas dos modulos indisponiveis (%s)" % ex)
    for pts, z in EXTRA_ROUTES.values():
        out.append((list(pts), z))
    return out


_PROPS = []


def prop_spots():
    """postes e bancos do sg_props (a copa nao engole a lanterna nem o banco)"""
    if not _PROPS:
        try:
            import sg_props as PR
            _PROPS.extend((x, y, 1.5) for n, x, y, z, lit in PR.LAMPS)
            for a in PR.BENCH_A:
                r = math.radians(a)
                _PROPS.append((L.PLAZA_C[0] + PR.BENCH_R * math.cos(r), L.PLAZA_C[1] + PR.BENCH_R * math.sin(r), 3.0))
        except Exception as ex:
            print("VEG AVISO sg_props indisponivel (%s)" % ex)
            _PROPS.append((1e6, 1e6, 0.0))
    return _PROPS


def route_dist(x, y, routes, zmin=20.0):
    best = 1e9
    for pts, z in routes:
        if z < zmin or len(pts) < 2:
            continue
        best = min(best, L.polyline_dist(x, y, pts))
    return best


# ------------------------------------------------------------------ especies (forma estilizada da concept)
# T camadas, r0 raio da saia de baixo (x h), droop queda das pontas (graus), base inicio da copa (x h), taper reducao
# do raio ate o topo, span fracao da copa ocupada pelas bases, th altura da camada (x copa), sh ombro, tr raio do tronco
FORMS = {
    "fir":   dict(T=4, r0=0.28, droop=22.0, base=0.12, taper=0.72, span=0.74, th=0.40, sh=0.5, tr=0.040),
    "spire": dict(T=5, r0=0.22, droop=26.0, base=0.09, taper=0.78, span=0.82, th=0.30, sh=0.55, tr=0.034),
    "stout": dict(T=3, r0=0.33, droop=18.0, base=0.10, taper=0.64, span=0.64, th=0.50, sh=0.5, tr=0.048),
}
LOBES = (6, 6, 4)
WHY = {}


def why(k):
    WHY[k] = WHY.get(k, 0) + 1
    return None


def crown_r(form, h):
    return h * (0.13 if form == "cypress" else FORMS[form]["r0"])


def pine(mb, x, y, z, h, rng, form="fir", lod=1):
    """abeto escuro estilizado: camadas conicas escalonadas com saia caida (pontas pendentes, vaos recolhidos), fundo
    escuro (SHADE), faces de cima voltadas para a lua em MOON (so nas 2 camadas de cima), topo levemente torto"""
    P = FORMS[form]
    T = P["T"] - (1 if lod == 2 else 0)
    lobes = LOBES[lod]
    r0 = h * P["r0"] * rng.uniform(0.92, 1.08)
    droop = P["droop"] * rng.uniform(0.85, 1.15)
    tr = h * P["tr"]
    zb = z + h * P["base"] * rng.uniform(0.9, 1.25)
    zt = z + h
    ch = zt - zb
    ta = rng.uniform(0, math.tau)
    tl = h * rng.uniform(0.02, 0.05)
    tx, ty = math.cos(ta) * tl, math.sin(ta) * tl
    VK.ttube(mb, [(x, y, z - 0.6), (x + tx * 0.2, y + ty * 0.2, z + h * 0.45)], [tr * 1.35, tr * 0.7], BARK,
             n=(6, 5, 4)[lod], cap1=False)
    rot0 = rng.uniform(0, math.tau)
    for k in range(T):
        u = k / (T - 1)
        zc = zb + ch * P["span"] * (u ** 0.92)
        r = r0 * (1.0 - P["taper"] * u) * rng.uniform(0.9, 1.1)
        top = k == T - 1
        th = (zt - zc) if top else ch * P["th"] * (1.0 - 0.3 * u) * rng.uniform(0.92, 1.08)
        cxy = (x + tx * u * 0.5, y + ty * u * 0.5)
        lean = (tx, ty) if top else (tx * 0.2, ty * 0.2)
        shoulder = P["sh"] if ((lod == 0 and k < T - 2) or (lod == 1 and k == 0)) else None
        under = 0.14 if (lod < 2 or k == 0) else None
        lm = MOON if (lod < 2 and k >= T - 2) else None
        VK.skirt(mb, (cxy[0], cxy[1], zc), r, th, lobes, LEAF, rng, rot=rot0 + k * 0.9 + rng.uniform(-0.3, 0.3),
                 droop=droop * (1.0 - 0.25 * u), lob=0.3 if lod < 2 else 0.22, shoulder=shoulder, under=under,
                 under_m=SHADE, lean=lean, lit=lm, lit_k=(0.2 if top else 0.45), asym=0.06, wind=ta)
    if lod < 2:
        ap = Vector((x + tx, y + ty, zt))
        VK.spike(mb, ap - Vector((0, 0, h * 0.05)), ap + Vector((tx * 0.8, ty * 0.8, h * 0.06)), h * 0.018, MOON, 3)


def cypress(mb, x, y, z, h, rng, lod=0):
    """cipreste fino (chama escura): 3 fusos lobados sobrepostos, quase sem queda, ombro alto"""
    r = h * 0.13 * rng.uniform(0.9, 1.08)
    VK.ttube(mb, [(x, y, z - 0.6), (x, y, z + h * 0.3)], [h * 0.035, h * 0.02], BARK, n=5, cap1=False)
    rot0 = rng.uniform(0, math.tau)
    parts = ((0.07, 1.0, 0.50), (0.30, 0.9, 0.46), (0.54, 0.66, 0.46))
    for k, (zb, rr, th) in enumerate(parts):
        VK.skirt(mb, (x, y, z + h * zb), r * rr, h * th, 5 if lod < 2 else 4, LEAF, rng, rot=rot0 + k * 1.1,
                 droop=8.0, lob=0.18, shoulder=0.82, under=0.1, under_m=SHADE, lit=MOON if k >= 1 else None,
                 lit_k=0.4, jit=0.08)


# ------------------------------------------------------------------ grupos (a planta PINE_GROVES + moldura)
# (grupo, centro, raio, n, h_min, h_max, formas, piso_ok, lod)
# grupo: so rotulo de leitura; o objeto de destino sai de region(x, y) (cada objeto < ~160 studs: 1 MeshPart/material)
FIR_MIX = (("fir", 5), ("spire", 3), ("stout", 2))
TALL_MIX = (("spire", 5), ("fir", 4), ("stout", 1))
LOW_MIX = (("stout", 4), ("fir", 4), ("spire", 1))
GROVES = [
    # borda sul (frente da ilha): emoldura a praca vista da chegada; mais baixos que as casas do P1
    ("South", (-90.0, -158.0), 10.0, 6, 13.0, 20.0, FIR_MIX, False, 1),
    ("South", (-62.0, -168.0), 8.0, 3, 11.0, 16.0, LOW_MIX, False, 1),
    ("South", (-40.0, -172.0), 7.0, 3, 11.0, 16.0, LOW_MIX, False, 1),
    ("South", (28.0, -172.0), 7.0, 3, 11.0, 16.0, LOW_MIX, False, 1),
    ("SouthE", (82.0, -162.0), 11.0, 6, 13.0, 20.0, FIR_MIX, False, 1),
    ("SouthE", (116.0, -146.0), 8.0, 4, 12.0, 18.0, FIR_MIX, False, 1),
    ("SouthE", (146.0, -126.0), 6.0, 2, 11.0, 15.0, LOW_MIX, False, 1),
    # pescoco da entrada: pinheiros baixos na espinha de rocha, dos dois lados da escadaria (nao escondem os porticos)
    ("South", (-18.0, -184.0), 3.0, 2, 9.0, 12.0, LOW_MIX, False, 1),
    ("South", (18.0, -183.0), 3.0, 2, 9.0, 12.0, LOW_MIX, False, 1),
    # P1 calcado: par de cada lado da calcada alta (plan: (-20,-150) e (30,-150)) e canteiros ao pe do arrimo
    ("VillageS", (-24.0, -153.0), 4.0, 2, 14.0, 17.0, FIR_MIX, True, 0),
    ("VillageS", (26.0, -153.0), 4.0, 2, 14.0, 17.0, FIR_MIX, True, 0),
    ("VillageS", (-40.0, -97.0), 5.0, 2, 15.0, 19.0, TALL_MIX, True, 0),
    ("VillageS", (40.0, -97.0), 5.0, 2, 15.0, 19.0, TALL_MIX, True, 0),
    ("VillageS", (-92.0, -100.0), 5.0, 2, 14.0, 18.0, FIR_MIX, True, 0),
    ("SouthE", (128.0, -92.0), 8.0, 3, 14.0, 19.0, FIR_MIX, True, 0),
    # P2 (grama): canto noroeste (plan (-104,-20)), entre e atras das casas; ciprestes finos entre as casas
    ("VillageW", (-104.0, -22.0), 9.0, 5, 15.0, 22.0, TALL_MIX, True, 0),
    ("VillageW", (-77.0, -70.0), 3.0, 2, 13.0, 16.0, (("cypress", 1),), True, 0),
    ("VillageW", (-75.0, -22.0), 3.0, 1, 13.0, 16.0, (("cypress", 1),), True, 0),
    ("VillageW", (-30.0, -24.0), 5.0, 2, 15.0, 19.0, FIR_MIX, True, 0),
    ("VillageW", (-30.0, -70.0), 4.0, 1, 13.0, 16.0, (("cypress", 1),), True, 0),
    ("VillageE", (22.0, -68.0), 4.0, 2, 13.0, 16.0, (("cypress", 1),), True, 0),
    ("VillageE", (28.0, -24.0), 5.0, 2, 15.0, 19.0, FIR_MIX, True, 0),
    ("VillageE", (62.0, -74.0), 4.0, 1, 13.0, 16.0, (("cypress", 1),), True, 0),
    ("VillageE", (76.0, -24.0), 6.0, 2, 15.0, 19.0, FIR_MIX, True, 0),
    ("VillageE", (140.0, -16.0), 6.0, 3, 14.0, 19.0, FIR_MIX, True, 0),
    ("VillageE", (138.0, -62.0), 6.0, 2, 13.0, 17.0, FIR_MIX, True, 0),
    ("NorthE", (123.0, 22.0), 5.0, 2, 16.0, 20.0, TALL_MIX, True, 0),
    # terreno bravo oeste do castelo (os grupos (-96,40) e (-86,120) da planta saem de dentro das alas: x < -100)
    ("CastleW", (-106.0, 40.0), 10.0, 7, 16.0, 24.0, TALL_MIX, False, 1),
    ("CastleW", (-108.0, 90.0), 10.0, 7, 17.0, 24.0, TALL_MIX, False, 1),
    ("CastleW", (-102.0, 146.0), 8.0, 4, 15.0, 22.0, FIR_MIX, False, 1),
    ("VillageW", (-116.0, -10.0), 5.0, 2, 14.0, 18.0, FIR_MIX, False, 1),
    # norte (atras da torre-coroa) e nordeste (entre os montes de basalto; plan (84,150))
    ("North", (-74.0, 170.0), 9.0, 4, 14.0, 21.0, FIR_MIX, False, 1),
    ("North", (-24.0, 189.0), 9.0, 4, 14.0, 21.0, FIR_MIX, False, 1),
    ("North", (24.0, 189.0), 9.0, 4, 14.0, 21.0, FIR_MIX, False, 1),
    ("NorthE", (74.0, 158.0), 12.0, 8, 15.0, 24.0, TALL_MIX, False, 1),
    ("NorthE", (63.0, 124.0), 5.0, 2, 15.0, 21.0, FIR_MIX, False, 1),
    ("NorthE", (104.0, 112.0), 5.0, 2, 14.0, 19.0, FIR_MIX, False, 1),
    ("NorthE", (137.0, 28.0), 6.0, 3, 13.0, 18.0, LOW_MIX, False, 1),
]


def pick(rng, mix):
    tot = sum(w for _, w in mix)
    x = rng.uniform(0, tot)
    for f, w in mix:
        x -= w
        if x <= 0:
            return f
    return mix[-1][0]


# ------------------------------------------------------------------ regras de lugar
PAVED = ("P1", "P3", "EntryHigh", "EntryLow")


def forbidden_floor(x, y, fl):
    """areas de piso onde NUNCA vai arvore (alem do que os raios ja pegam: ruas, praca, escadas, predios)"""
    if fl == "Summon":
        return True
    fx0, fy0, fx1, fy1 = L.CASTLE_FORECOURT
    if fx0 - 6.0 < x < fx1 + 6.0 and fy0 - 2.0 < y < fy1 + 4.0:
        return True
    if math.hypot(x - L.CRAFT_C[0], y - L.CRAFT_C[1]) < L.CRAFT_R + 8.0:
        return True
    hx, hy, hw, hd = L.DUNGEON_HOUSE
    if abs(x - hx) < hw / 2 + 8.0 and abs(y - hy) < hd / 2 + 10.0:
        return True
    if math.hypot(x - L.PLAZA_C[0], y - L.PLAZA_C[1]) < L.PLAZA_R + 5.0:
        return True
    return False


def site_ok(S, x, y, h, form, floor_ok, routes, placed):
    """(z_pe, piso) se a arvore cabe em (x, y); None se nao"""
    rc = crown_r(form, h)
    for ox, oy, orr in prop_spots():
        if math.hypot(x - ox, y - oy) < rc + orr:
            return why("prop")
    for px, py, pz, pr, ph in placed:
        if math.hypot(x - px, y - py) < 0.52 * (rc + pr) + 0.5:
            return why("vizinha")
    fl = L.floor_name(x, y)
    if fl is not None:
        if not floor_ok or forbidden_floor(x, y, fl):
            return why("piso_proibido")
        if route_dist(x, y, routes) < rc + 1.6:
            return why("rota")
    else:
        # terreno bravo: a copa nao pode avancar sobre um piso andavel perto de rota (folha no meio do caminho)
        for k in range(8):
            a = k * math.tau / 8
            if L.zone_of(x + math.cos(a) * rc * 0.8, y + math.sin(a) * rc * 0.8) is not None and \
                    route_dist(x, y, routes) < rc + 1.6:
                return why("rota_bravo")
    zc, nm, nrm = S.hit(x, y)
    if not is_ter(nm) or zc < 20.0 or nrm.z < 0.8:
        return why("pe_fora_do_terreno")
    # pe: 6 raios em volta do tronco (o pe senta no mais baixo; nada de degrau no meio do tronco)
    zs = [zc]
    for k in range(6):
        a = k * math.tau / 6
        z1, n1, _ = S.hit(x + math.cos(a) * 1.1, y + math.sin(a) * 1.1)
        if not is_ter(n1):
            return why("pe_borda")
        zs.append(z1)
    if max(zs) - min(zs) > 1.6:
        return why("pe_degrau")
    zg = min(zs)
    if fl is not None and abs(zg - L.zone_of(x, y)) > 0.6:
        return why("pe_cota")
    base = zg + h * 0.10
    void = 0
    # copa: 2 aneis de raios; qualquer outra malha (predio, muro, ponte, rua, agua) no alcance da copa = nao cabe;
    # terreno que sobe acima do pe da copa (arrimo, monte, coluna) = nao cabe; vazio (copa sobre a beira do penhasco)
    # = ate metade do anel de fora (pinheiro no topo da coluna da borda, como na concept)
    for rr, n in ((rc * 0.5, 6), (rc * 1.0, 10)):
        for k in range(n):
            a = k * math.tau / n + 0.3
            z1, n1, _ = S.hit(x + math.cos(a) * rr, y + math.sin(a) * rr)
            if n1 is None:
                void += 1 if rr > rc * 0.7 else 3
                continue
            if not is_ter(n1):
                if z1 > zg - 3.0:
                    return why("copa_em_" + n1.split("_")[1])
                continue
            if z1 > base + (1.2 if rr > rc * 0.7 else 0.0):
                return why("copa_no_terreno")
    if void > 5:
        return why("copa_no_vazio")
    return zg, fl


# ------------------------------------------------------------------ build
def tree_pit(mb, x, y, z, rng):
    """canteiro de cantaria (octogono baixo) + terra/grama: arvore no piso calcado"""
    r = 1.9
    mb.cyl(r, 0.42, (x, y, z + 0.13), (0, 0, math.pi / 8), TRIM, n=8, bevel=0.0)
    mb.cyl(r - 0.38, 0.1, (x, y, z + 0.36), (0, 0, math.pi / 8), GRASS, n=8, bevel=0.0)


def base_dressing(mb, S, x, y, zg, h, rng, wild):
    """1 arbusto baixo e/ou 1-2 tufos de grama fria no pe (so em parte das arvores: nada de tapete)"""
    if wild and rng.random() < 0.55:
        a = rng.uniform(0, math.tau)
        d = rng.uniform(1.4, 2.6)
        bx, by = x + math.cos(a) * d, y + math.sin(a) * d
        z1, n1, _ = S.hit(bx, by)
        if is_ter(n1) and abs(z1 - zg) < 1.2:
            s = rng.uniform(1.1, 1.8)
            VK.puff(mb, (bx, by, z1 - 0.1), s, LEAF, rng, 1, rng.uniform(0.7, 0.95))
    for k in range(rng.choice((0, 1, 1, 2))):
        a = rng.uniform(0, math.tau)
        d = rng.uniform(1.0, 2.4)
        bx, by = x + math.cos(a) * d, y + math.sin(a) * d
        z1, n1, _ = S.hit(bx, by)
        if is_ter(n1) and abs(z1 - zg) < 1.0:
            VK.grass_tuft(mb, (bx, by, z1), rng.uniform(0.7, 1.1), rng, m=GRASS, n=rng.randint(3, 4))


def build():
    PLACED.clear()
    WHY.clear()
    old_sun = VK.SUN
    VK.SUN = MOON_DIR
    try:
        _build()
    finally:
        VK.SUN = old_sun


def region(x, y, fl):
    """objeto de destino (cada um com extensao < ~160 studs: 1 MeshPart por material no export)"""
    if fl in ("P1", "EntryHigh", "EntryLow"):
        return "VillageS"
    if fl == "P2":
        return "VillageW" if x < 10.0 else "VillageE"
    if fl == "P3":
        return "VillageE" if y < 60.0 else "North"
    if y < -140.0 and x < 25.0:
        return "South"
    if x >= 25.0 and y < -60.0:
        return "SouthE"
    if x >= 95.0 and y < 100.0:
        return "East"
    if y >= 100.0:
        return "NorthE" if x >= 20.0 else "North"
    return "West"


class Planter:
    def __init__(self, S, routes):
        self.S, self.routes = S, routes
        self.mbs = {}
        self.placed = []
        self.ncol = 0

    def mb(self, key):
        mb = self.mbs.get(key)
        if mb is None:
            mb = self.mbs[key] = MB("SG_Veg_Pines_%s" % key, COLL, random.Random(331 + len(self.mbs)), detail="near",
                                    floor=-999)
        return mb

    def plant(self, x, y, zg, fl, h, form, lod, g, dress=True):
        mb = self.mb(region(x, y, fl))
        if fl in PAVED:
            tree_pit(mb, x, y, zg, g)
        if form == "cypress":
            cypress(mb, x, y, zg, h, g, lod)
        else:
            pine(mb, x, y, zg, h, g, form, lod)
        if dress:
            base_dressing(mb, self.S, x, y, zg, h, g, wild=fl is None)
        if fl is not None:
            tr = h * (0.035 if form == "cypress" else FORMS[form]["tr"]) * 1.35
            w = max(0.9, tr * 2.0)
            col_box("SG_VegTrunk", (w, w, 7.0), (x, y, zg + 3.5))
            self.ncol += 1
        self.placed.append((x, y, zg, crown_r(form, h), h))
        PLACED.append((x, y, zg, crown_r(form, h), h, form))

    def finish(self):
        for mb in self.mbs.values():
            mb.finish()


def groves(P):
    stats = {}
    for gi, (grp, c, R, n, hmin, hmax, mix, floor_ok, lod) in enumerate(GROVES):
        g = random.Random(3310 + gi * 97)
        WHY.clear()
        # alturas do grupo: a mais alta no miolo, as outras caem (composicao, nao fila)
        hs = sorted([g.uniform(hmin, hmax) for _ in range(n)], reverse=True)
        hs[0] = max(hs[0], hmin + (hmax - hmin) * 0.8)
        got = 0
        for i, h in enumerate(hs):
            form = pick(g, mix)
            ok = None
            for t in range(48):
                rr = R * math.sqrt(g.random()) * (0.35 if i == 0 and t < 12 else 1.0)
                a = g.uniform(0, math.tau)
                x, y = c[0] + math.cos(a) * rr, c[1] + math.sin(a) * rr
                hh = h if t < 24 else max(8.0, h * 0.8)
                ok = site_ok(P.S, x, y, hh, form, floor_ok, P.routes, P.placed)
                if ok is not None:
                    h = hh
                    break
            if ok is None:
                continue
            zg, fl = ok
            P.plant(x, y, zg, fl, h, form, lod, g)
            got += 1
        stats[gi] = (got, n, dict(WHY))
    return stats


def rim_pass(P):
    """pinheiros no TOPO das colunas da borda (a concept: penhascos escuros com pinheiros no topo), em manchas (ruido
    ao longo da borda, nunca em fila): a cada passo, se a mancha esta 'ligada', tenta recuar 2..10 para dentro"""
    g = random.Random(3377)
    rim = SL.rim()
    n = len(rim)
    per = sum(math.hypot(rim[(i + 1) % n][0] - rim[i][0], rim[(i + 1) % n][1] - rim[i][1]) for i in range(n))
    step = 6.0
    s = 0.0
    i = 0
    acc = 0.0
    got = 0
    WHY.clear()
    while s < per:
        a, b = rim[i % n], rim[(i + 1) % n]
        seg = math.hypot(b[0] - a[0], b[1] - a[1]) or 1e-6
        while acc <= seg and s < per:
            t = acc / seg
            px, py = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            ux, uy = (b[0] - a[0]) / seg, (b[1] - a[1]) / seg
            nx, ny = -uy, ux                                        # para dentro (contorno anti-horario)
            m = math.sin(s / 31.0 + 0.7) + 0.75 * math.sin(s / 11.7 + 2.1) + 0.35 * math.sin(s / 5.3)
            if m > 0.25:
                h = g.uniform(9.0, 15.0) + (3.0 if m > 1.3 else 0.0)
                form = pick(g, LOW_MIX if h < 12.0 else FIR_MIX)
                for d in (g.uniform(2.0, 4.0), g.uniform(4.0, 7.0), g.uniform(7.0, 10.0)):
                    j = g.uniform(-1.8, 1.8)
                    x, y = px + nx * d + ux * j, py + ny * d + uy * j
                    ok = site_ok(P.S, x, y, h, form, False, P.routes, P.placed)
                    if ok is not None:
                        zg, fl = ok
                        P.plant(x, y, zg, fl, h, form, 1, g, dress=g.random() < 0.5)
                        got += 1
                        break
            s += step
            acc += step
        acc -= seg
        i += 1
    return got, dict(WHY)


def _build():
    S = Scene()
    P = Planter(S, route_lines())
    stats = groves(P)
    nrim, why_rim = rim_pass(P)
    P.finish()
    miss = ["%d:%s(%d/%d)%s" % (gi, GROVES[gi][0], a, b, sorted(w.items(), key=lambda t: -t[1])[:3])
            for gi, (a, b, w) in stats.items() if a < b]
    print("VEG arvores=%d (borda %d) colisoes_tronco=%d" % (len(PLACED), nrim, P.ncol))
    print("VEG grupos_incompletos=%s" % miss)
    print("VEG recusas_borda=%s" % sorted(why_rim.items(), key=lambda t: -t[1])[:6])
