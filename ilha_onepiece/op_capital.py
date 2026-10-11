# op_capital.py - R3 da Ilha 5 (ONE PIECE / WANO): a CAPITAL de CASAS SOLTAS com o KIT V2 (op_kit2, aprovado no
# gate V2-1: "as casas melhoraram"). Zona "capital" do build_op (ZONE_MODULES_V2_0). Prefixo OP_Cap_, colecao
# 05_CAPITAL. Le a planta (op_layout: ROWS -> block_lots(), STREETS_V2, AVENUE, NE) e o op_kit2.
#
# RODADA 3 (10/10, o usuario jogando a V2: "casas horriveis, grudadas uma na outra", "caminhos mal montados tortos",
# "modelos flutuando", "hitboxes mal feitas", capturas 02/05/06/08/09/17 em feedback_20261010/rodada3):
#   R2 CASAS SOLTAS: a V2 era 101 lotes geminados (parede-meia) em 12 quadras -> telhados encostando/sobrepostos e becos
#      de 0,8 entre fundos (captura 06: jogadores presos num corredor entre paredes). A R3 tem ~74 casas ISOLADAS
#      (op_layout.ROWS R3): vao entre corpos = beiral A + beiral B + 2,0 (>= 4,5), recuos variados, casas viradas para a
#      outra rua no bairro do canal (becos de rua a rua), patios de quadra abertos (jardim/cerejeiras do op_veg), MURO
#      nos vaos da frente (tsuiji na avenida/NE/praca, tabuado ou bambu no resto) - a rua continua lendo como rua. A
#      passagem coberta (portal) saiu: a viela do canal e uma viela de verdade. O TESTE do build mede malha x malha:
#      zero interseccao e beiral a >= 1,0 do vizinho (falha = RuntimeError; OP_CAP_SOFT=1 so avisa).
#   R6 PAVIMENTO CONTINUO (secao "PAVIMENTO"): as ruas/vielas/cais/sando + frentes das casas + vaos + becos + patamares
#      das escadas viram UMA superficie: convexos mitrados recortados pelo piso real da cota, menos exclusoes e menos o
#      que um trecho de prioridade maior ja pegou; lajes numa grade FIXA por regiao recortada exatamente pelas pecas
#      (sem buraco, sem sobreposicao, topo unico a +0,2), berco escuro continuo, GUIA de pedra na borda com a grama,
#      sarjeta onde o pavimento encontra um muro que sobe e saia onde ele acaba num desnivel.
#   R1/V3 COLISAO = O QUE SE VE: cada casa fechada tem 1 caixa do TAMANHO DO CORPO (paredes + soco, ate o frechal) -
#      nao se entra numa casa fechada; os 4 interiores (AvO_F13, AvL_F13, OesteM_F21 casa de cha, NE_Haiden1) tem
#      paredes/piso/forro proprios e o vao de entrada livre; muros, andon, toro, torii e carga com caixa do tamanho do
#      visual (as caixas altas de 8,5..11 da V2 sairam). Nenhuma caixa nova acima do visual.
# ORCAMENTO: <= ~200k tris (lod 0 so na avenida/NE, lod 2/3 nos fundos e longe das rotas, cull_hidden por setor).
# LUZES: interiores de dia L_OPCap_Int_* (4), resto NightOnly (L_OPProp_*). CAMERAS: CAM_OP_R3Cap_* (folhas; fora do
# export) nas posicoes das capturas do usuario + de cima (25-40) + altura do jogador.
import math, os, time
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import op_lib as DL
from op_lib import MB, col_box, Frame, ccw, light
import fm_lib
import op_layout as L
import op_kit2 as K2
import op_kit as K
import op_col

COLL = "05_CAPITAL"
T1, P = L.T1, L.P
STREET_DZ = 0.2           # topo das lajes acima do piso de colisao
BED_DZ = 0.08             # berco escuro (aparece nas juntas)
NEAR = 6.0                # predio a menos disto: o telhado corta na metade da distancia (seguranca; na R3 quase nunca)
CLEAR_MIN = 1.0           # beiral a >= isto do vizinho (teste do build)
REGION = {"AvO": "Avenida", "AvL": "Avenida", "PortoAlto1": "Avenida", "PortoAlto2": "Avenida",
          "BairroN": "Bairro", "BairroS": "Bairro", "OesteS": "Oeste", "OesteM": "Oeste", "OesteN": "Oeste",
          "AlemCanal": "Oeste", "W3": "Oeste", "NE": "NE"}
# fileiras que o jogador ve de perto (avenida, sando): lod 0; fundos lod 2; o resto lod 1
HERO_ROWS = {("AvO", "F1"), ("AvO", "F2"), ("AvL", "F1"), ("NE", "Haiden"), ("NE", "Honden")}
BACK_ROWS = {("AvO", "B1"), ("AvO", "B2"), ("AvL", "B1"), ("BairroS", "B1"), ("OesteS", "B"), ("OesteM", "B1"),
             ("OesteM", "B2"), ("OesteN", "B"), ("PortoAlto1", "B"), ("PortoAlto2", "B"), ("W3", "M1"), ("W3", "M2"),
             ("AlemCanal", "F1"), ("AlemCanal", "F2")}
FAR_D = 11.0              # frente a mais disto de TODA rota do jogo = lod 3 (op_kit2: casa longe)
FAR_KINDS = ("loja", "fundo", "sobrado", "kura", "armazem", "moinho")
SECOND = {L.R_COB: L.R_TEAL, L.R_TEAL: L.R_COB, L.R_VIO: L.R_COB, L.R_RED: L.R_VIO, L.R_GRN: L.R_TEAL}
INTERIOR_LIGHT = {"AvO_F13": "L_OPCap_Int_LojaTecidos", "AvL_F13": "L_OPCap_Int_Izakaya",
                  "OesteM_F21": "L_OPCap_Int_Cha", "NE_Haiden1": "L_OPCap_Int_Haiden"}
SUMMON_RECT = (116.0, 150.0, 206.0, 264.0)       # lajeado do op_summon (as ruas 16-18 da planta sao dele)
# caminho que a planta nao tem como rua: topo da escada Sudoeste -> praca (rota BAIRRO_CANAL->OESTE) e -> cais leste
EXTRA_PATHS = [([(-169.0, 121.2), (-116.0, 121.2)], 6.0, P)]
FENCE_TSUIJI = {"AvO", "AvL", "NE", "OesteS", "OesteM", "OesteN"}    # muro de reboco (frente nobre); resto tabuado/bambu
VEG_SPOTS = []            # (x, y, z, tipo, nota) - jardins dos vaos largos (op_veg.capital_spots le depois do build)
STATS = {}


def h01(*a):
    return K._h01(*a)


# ================================================================== vizinhanca das casas
def _lot_frame(lt):
    """referencial da CASA: centro da planta, no chao, +y = frente (o recuo ja esta no centro do lote R3)"""
    return Frame(lt["x"], lt["y"], lt["z"], lt["yaw"] - math.pi / 2)


def _local(lt, x, y):
    """mundo -> local do lote (x ao longo da fachada, y para a frente)"""
    c, s = math.cos(lt["yaw"]), math.sin(lt["yaw"])
    dx, dy = x - lt["x"], y - lt["y"]
    return dx * s - dy * c, dx * c + dy * s


def _world(lt, u, v):
    c, s = math.cos(lt["yaw"]), math.sin(lt["yaw"])
    return lt["x"] + u * s + v * c, lt["y"] - u * c + v * s


FRONT_REACH = 3.4         # o que a FRENTE de um predio projeta sobre a rua (beiral, hisashi, placa, degrau, chochin)


def _march(cands, me, pts, du, dv):
    """anda de cada ponto local (u, v) de 'me' na direcao (du, dv) ate entrar noutro lote (passo 0,1 ate NEAR) ->
    (distancia, lote, face do outro que foi cruzada: 'front' | 'back' | 'side') do primeiro encontro"""
    best = None
    for u, v in pts:
        d = 0.05
        while d <= NEAR + 1e-6 and (best is None or d < best[0]):
            x, y = _world(me, u + du * d, v + dv * d)
            hit = None
            for o in cands:
                if L.point_in_poly(x, y, o[1]):
                    hit = o[0]
                    break
            if hit:
                uu, vv = _local(hit, x, y)
                face = "front" if vv > hit["D"] / 2 - 0.25 else ("back" if vv < -hit["D"] / 2 + 0.25 else "side")
                best = (d, hit, face)
                break
            d += 0.1
    return best


def _march_high(me, pts, du, dv, maxd=9.0):
    """distancia ate um piso da planta mais alto que o lote (z > z + 0,3) andando para fora"""
    best = None
    for u, v in pts:
        d = 0.1
        while d <= maxd and (best is None or d < best):
            x, y = _world(me, u + du * d, v + dv * d)
            z = L.zone_of(x, y)
            if z is not None and z > me["z"] + 0.3:
                best = d
                break
            d += 0.2
    return best


def neighbors(lots):
    """por casa: limite de corte das laterais/fundo quando ha predio a menos de NEAR (metade da distancia; se o outro
    mostra a FRENTE, distancia - FRONT_REACH) ou piso mais alto alcancavel a 6..9 (o beiral fica a > 6 dele)"""
    out = {}
    polys = {lt["name"]: L.lot_poly(lt) for lt in lots}
    for lt in lots:
        W, D = lt["W"], lt["D"]
        R = (W + D) / 2 + NEAR + 2.0
        cands = [(o, polys[o["name"]]) for o in lots if o is not lt and
                 math.hypot(o["x"] - lt["x"], o["y"] - lt["y"]) < R + (o["W"] + o["D"]) / 2]
        res = dict(lim=[None, None], back=None, back_gap=None, nb=set(), free=[True, True])
        vs = (-D / 2 + 0.8, -D / 4, 0.0, D / 4, D / 2 - 0.8)
        for k, sx in enumerate((-1, 1)):
            m = _march(cands, lt, [(sx * W / 2, v) for v in vs], sx, 0.0)
            if m:
                d, o, face = m
                res["nb"].add(o["name"])
                res["free"][k] = False
                res["lim"][k] = W / 2 + (d - FRONT_REACH if face == "front" else d / 2) - 0.03
            dh = _march_high(lt, [(sx * W / 2, v) for v in vs], sx, 0.0)
            if dh is not None and dh > 6.2:
                lk = W / 2 + dh - 6.2
                res["lim"][k] = lk if res["lim"][k] is None else min(res["lim"][k], lk)
        us = (-W / 2 + 0.6, -W / 4, 0.0, W / 4, W / 2 - 0.6)
        m = _march(cands, lt, [(u, -D / 2) for u in us], 0.0, -1.0)
        if m:
            d, o, face = m
            res["nb"].add(o["name"])
            res["back_gap"] = d
            res["back"] = D / 2 + (d - FRONT_REACH if face == "front" else d / 2) - 0.03
        out[lt["name"]] = res
    return out


# ================================================================== casa -> chamada do kit
def _dh(lt):
    return lt["eave"] - lt["z"] - L.EAVE_H.get((lt["kind"], lt["floors"]), 8.8 + 6.0 * (lt["floors"] - 1))


def _seg_d(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / max(1e-9, dx * dx + dy * dy)))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)


def route_dist(lt):
    """distancia do meio da FACHADA da casa ate a rota do jogo mais proxima (op_layout.routes)"""
    c, s = math.cos(lt["yaw"]), math.sin(lt["yaw"])
    p = (lt["x"] + c * lt["D"] / 2, lt["y"] + s * lt["D"] / 2)
    return min(_seg_d(p, a, b) for pts, z in L.routes().values() for a, b in zip(pts, pts[1:]))


def plan(lots):
    nbs = neighbors(lots)
    row_roof = {(r[0], r[1]): r[7] for r in L.ROWS}
    specs = []
    for lt in lots:
        nb = nbs[lt["name"]]
        sides = (True, True)                              # R3: TODA casa e solta (sem parede-meia)
        kind = lt["kind"]
        seed = int(h01(lt["name"], "seed") * 9973)
        dh = _dh(lt)
        roof = lt["roof"]
        if roof == row_roof.get((lt["block"], lt["row"])) and kind not in ("santuario", "honden") and \
                h01(lt["name"], "cor") < 0.2:
            roof = SECOND.get(roof, roof)
        Wb, Db = lt["W"], lt["D"]
        back = max(Db / 2, nb["back"]) if nb["back"] is not None else None
        lim = tuple((max(Wb / 2, v) if v is not None else K2.BIG) for v in nb["lim"])
        key = (lt["block"], lt["row"])
        lod = 0 if key in HERO_ROWS else (2 if key in BACK_ROWS else 1)
        if lod == 0 and kind in ("sobrado", "esquina", "loja"):  # R3 (orcamento 195k): a avenida em lod 1; lod 0 so
            lod = 1                                       # nos interiores vivos (o jogador entra) e no santuario
        if lt["interior"]:
            lod = 0
        if kind == "mansao":
            lod = 3
        far = (lod == 2 or kind in ("fundo", "moinho")) and kind in FAR_KINDS and not lt["interior"] and \
            route_dist(lt) > FAR_D
        if far:
            lod = 3
        lname = INTERIOR_LIGHT.get(lt["name"]) if lt["interior"] else None
        kw = dict(W=Wb, D=Db, roof_m=roof, lod=lod, seed=seed, back=back, lim=lim)
        zw = None
        if kind == "loja":
            kw.update(sides=sides, tsuma=lt["tsuma"], shop_side=1 if h01(lt["name"], "ss") < 0.5 else -1,
                      upper=("mushiko", "shoji", "double")[int(h01(lt["name"], "up") * 3)],
                      awning=lt["awning"] or h01(lt["name"], "aw") < 0.3,
                      roof="irimoya" if lt["irimoya"] else "kirizuma",
                      h0=9.0 + 0.4 * dh, h1=7.0 + 0.6 * dh, interior=lt["interior"], light_name=lname)
            if lt["interior"]:                         # R3: loja com interior = salao fundo (D - 4) e pe-direito >= 9,5
                kw["idepth"] = Db - 4.0
                kw["h0"] = max(kw["h0"], 9.5)
            fn, zw = K2.loja, 0.8 + kw["h0"] + kw["h1"]
        elif kind == "sobrado":
            kw.update(sides=sides, shop=h01(lt["name"], "sh") < 0.5, rail_m=K2.LAC if h01(lt["name"], "rl") < 0.5
                      else K2.WD, h0=8.6 + 0.3 * dh, h1=7.0 + 0.3 * dh, h2=6.4 + 0.4 * dh, chidori=lod == 0)
            kw["top"] = "irimoya" if lod < 2 else "yosemune"
            fn, zw = K2.sobrado, 0.8 + kw["h0"] + kw["h1"]
        elif kind == "esquina":
            fr = nb["free"]
            corner = (1 if fr[1] else -1) if fr[0] != fr[1] else (1 if h01(lt["name"], "c") < 0.5 else -1)
            kw.update(corner=corner, solo=True, tower_m=SECOND.get(roof, L.R_COB), h0=9.0 + 0.4 * dh,
                      h1=7.0 + 0.6 * dh, light_name=lname)
            fn, zw = K2.esquina, 0.8 + kw["h0"] + kw["h1"]
        elif kind in ("kura", "armazem"):
            kw.update(sides=sides, tsuma=lt["tsuma"] if kind == "kura" else False,
                      h=(12.5 if kind == "kura" else 13.6) + dh, crest=lod == 0)
            fn, zw = K2.kura, 1.4 + kw["h"]
        elif kind == "chaya":
            fr = nb["free"]
            gs = (1 if not fr[1] else -1) if fr[0] != fr[1] else (1 if h01(lt["name"], "gs") < 0.5 else -1)
            kw.update(sides=sides, garden_side=gs, garden_w=4.0, light_name=lname, h0=9.0, h1=6.8)
            fn, zw = K2.chaya, 1.0 + 9.0
        elif kind == "mansao":
            kw.update(sides=sides)
            fn, zw = K2.mansao2, 0.8 + 8.6 + 7.0
        elif kind in ("fundo", "moinho"):
            kw.update(sides=sides, tsuma=(lt["tsuma"] or kind == "moinho"),
                      h0=(9.0 if kind == "moinho" else 8.0) + max(0.0, dh), hisashi=lt["hisashi"])
            kw["lod"] = max(2, lod)            # fundos = Tier B (PLANO_V2 3.2): sempre lod 2 (telha ondulada mantida)
            fn, zw = K2.fundo, 0.6 + kw["h0"]
        elif kind == "santuario":
            kw.update(sides=sides, light_name=lname)
            fn, zw = K2.haiden2, 1.6 + 9.0
        elif kind == "honden":
            kw.update(sides=sides)
            fn, zw = K2.honden2, 7.0
        else:
            raise RuntimeError("op_capital: tipo sem kit: %s" % kind)
        back_coarse = kw["lod"] >= 1 and not kw.get("tsuma") and kind != "esquina" and lt["block"] not in ("AvO", "AvL")
        specs.append(dict(lot=lt, fn=fn, kw=kw, F=_lot_frame(lt), zw=zw, sides=sides, nb=nb,
                          region=REGION[lt["block"]], back_coarse=back_coarse))
    _variety(specs)
    return specs


def _sig(s):
    kw = s["kw"]
    return (s["fn"].__name__, kw.get("tsuma"), kw.get("shop_side"), kw.get("upper"), kw.get("roof"))


def _variety(specs):
    """nunca a mesma casa lado a lado na mesma rotacao: vizinho de fileira com a mesma assinatura troca o lado da
    loja e o 2o piso (fundo: vira tsumairi - o beiral lateral muda < 0,2, o vao do layout cobre)"""
    by = {s["lot"]["name"]: s for s in specs}
    for s in specs:
        for o in s["nb"]["nb"]:
            t = by.get(o)
            if not t or t["lot"]["row"] != s["lot"]["row"] or t["lot"]["block"] != s["lot"]["block"]:
                continue
            if _sig(s) == _sig(t) and s["lot"]["name"] < t["lot"]["name"]:
                kw = t["kw"]
                if "shop_side" in kw:
                    kw["shop_side"] = -kw["shop_side"]
                    kw["upper"] = {"mushiko": "shoji", "shoji": "double", "double": "mushiko"}[kw["upper"]]
                elif t["fn"] is K2.fundo:
                    kw["tsuma"] = not kw["tsuma"]


# ================================================================== geometria por casa + teste de interpenetracao
def _geo(mb):
    """malha do edificio (coordenadas de mundo) -> (verts, tris, BVH, bbox)"""
    bm = mb.bm
    bm.verts.ensure_lookup_table()
    bm.verts.index_update()
    lt = bm.calc_loop_triangles()
    vs = [v.co.copy() for v in bm.verts]
    tris = [(a.vert.index, b.vert.index, c.vert.index) for a, b, c in lt]
    mats = [str(mb.mats[a.face.material_index]) if a.face.material_index < len(mb.mats) else "?" for a, b, c in lt]
    if not vs:
        return None
    bv = BVHTree.FromPolygons(vs, tris, all_triangles=True)
    xs = [v.x for v in vs]
    ys = [v.y for v in vs]
    zs = [v.z for v in vs]
    return dict(v=vs, t=tris, m=mats, bvh=bv, bb=(min(xs), min(ys), min(zs), max(xs), max(ys), max(zs)))


def _bb_hit(a, b, pad=1.0):
    return not (a[3] < b[0] - pad or b[3] < a[0] - pad or a[4] < b[1] - pad or b[4] < a[1] - pad or
                a[5] < b[2] - pad or b[5] < a[2] - pad)


def interpen(specs, geos):
    """TESTE malha x malha entre casas vizinhas: (1) interseccao de triangulos (BVHTree.overlap), (2) vertice de uma
    casa dentro da planta da outra que nao esteja >= 0,12 ACIMA da malha dela e (3) R3: BEIRAL a menos de CLEAR_MIN do
    vizinho (casas soltas: os telhados nao se tocam). -> lista de problemas"""
    probs = []
    n_pairs = 0
    names = [s["lot"]["name"] for s in specs]
    polys = {s["lot"]["name"]: L.lot_poly(s["lot"], -0.01) for s in specs}
    gaps = []
    for i in range(len(specs)):
        gi = geos[names[i]]
        if gi is None:
            continue
        for j in range(i + 1, len(specs)):
            gj = geos[names[j]]
            if gj is None or not _bb_hit(gi["bb"], gj["bb"], CLEAR_MIN + 0.5):
                continue
            n_pairs += 1
            ov = gi["bvh"].overlap(gj["bvh"])
            if ov:
                a, b = ov[0]
                ta = gi["t"][a]
                c = sum((gi["v"][k] for k in ta), Vector()) / 3
                mm = sorted(set("%s/%s" % (gi["m"][p], gj["m"][q]) for p, q in ov))[:4]
                probs.append(("cruza", names[i], names[j], len(ov), tuple(round(x, 2) for x in c) + tuple(mm)))
            for (ga, gb, nb_) in ((gi, gj, names[j]), (gj, gi, names[i])):
                poly = polys[nb_]
                bad = 0
                ex = None
                xs = [p[0] for p in poly]
                ys = [p[1] for p in poly]
                bx0, by0, bx1, by1 = min(xs), min(ys), max(xs), max(ys)
                for v in ga["v"]:
                    if v.x < bx0 or v.x > bx1 or v.y < by0 or v.y > by1:
                        continue
                    if not L.point_in_poly(v.x, v.y, poly):
                        continue
                    h = gb["bvh"].ray_cast(Vector((v.x, v.y, 1000.0)), Vector((0, 0, -1)), 2000.0)
                    if h[0] is not None and v.z < h[0].z + 0.12:
                        bad += 1
                        ex = ex or tuple(round(x, 2) for x in v)
                if bad:
                    probs.append(("dentro_do_lote", names[i] if ga is gi else names[j], nb_, bad, ex))
            # folga dos beirais (so o que fica acima do soco: telhado/beiral/hisashi)
            dmin, pt = 1e9, None
            for ga, gb in ((gi, gj), (gj, gi)):
                z0 = ga["bb"][2] + 2.5
                for v in ga["v"][::2]:
                    if v.z < z0:
                        continue
                    if v.x < gb["bb"][0] - 3 or v.x > gb["bb"][3] + 3 or v.y < gb["bb"][1] - 3 or v.y > gb["bb"][4] + 3:
                        continue
                    r = gb["bvh"].find_nearest(v, 3.0)
                    if r[0] is not None and r[3] < dmin:
                        dmin, pt = r[3], v
            if dmin < 3.0:
                gaps.append((round(dmin, 2), names[i], names[j]))
                if dmin < CLEAR_MIN:
                    probs.append(("beiral_encostado", names[i], names[j], 1, (round(dmin, 2),) +
                                  tuple(round(x, 1) for x in pt)))
    STATS["pares"] = n_pairs
    STATS["folgas"] = sorted(gaps)[:12]
    return probs


# ================================================================== montagem das casas
def _merge(dst, src):
    """copia o bmesh do MB do edificio para o MB do setor (materiais remapeados; tint/UV preservados)"""
    me = bpy.data.meshes.new("_op_cap_merge")
    src.bm.to_mesh(me)
    n0 = len(dst.bm.faces)
    dst.bm.from_mesh(me)
    remap = [dst._mi(k) for k in src.mats]
    dst.bm.faces.ensure_lookup_table()
    for f in dst.bm.faces[n0:]:
        if f.material_index < len(remap):
            f.material_index = remap[f.material_index]
    bpy.data.meshes.remove(me)
    src.bm.free()


CULL_IN = {K2.loja: 4.0, K2.sobrado: 4.0, K2.fundo: 0.7, K2.kura: 0.7, K2.mansao2: 4.0}   # recuo da frente do terreo


def cull_inside(mb, s, info=None):
    """apaga as faces DENTRO do volume fechado da casa (frente/fundos/laterais + forro do frechal): paredes,
    pilares e soleiras vistos por dentro. So nas casas fechadas (sem interior vivo; a vitrine da loja fica: o terreo
    so e cortado atras dela) + o SOTAO dos telhados kirizuma. -> tris cortados"""
    if s["lot"]["interior"] or s["fn"] not in CULL_IN:
        return 0
    F, kw = s["F"], s["kw"]
    W, D = kw["W"], kw["D"]
    if s["fn"] is K2.mansao2:
        gd = kw.get("gd", 7.0)
        F = K2.sub(F, 0.0, -gd / 2)
        W, D = min(W - 2.0, 16.0), D - gd
    ins = 0.7
    z0, zw = F.o.z + 0.3, F.o.z + s["zw"] - 0.05
    zg = F.o.z + 0.8 + kw.get("h0", 8.0)
    yfg = D / 2 - CULL_IN[s["fn"]]
    ca, sa = math.cos(-F.a), math.sin(-F.a)
    kill = []
    for f in mb.bm.faces:
        c = f.calc_center_median()
        if not (z0 < c.z < zw):
            continue
        dx, dy = c.x - F.o.x, c.y - F.o.y
        u, v = dx * ca - dy * sa, dx * sa + dy * ca
        if abs(u) < W / 2 - ins and -D / 2 + ins < v < ((yfg if c.z < zg else D / 2 - ins)):
            kill.append(f)
    r = (info or {}).get("roof")
    if r and r.get("kind") == "kirizuma" and s["fn"] is not K2.mansao2:
        Fr, Hf, tv = r["F"], r["Hf"], r["tv"]
        cr, sr = math.cos(-Fr.a), math.sin(-Fr.a)
        ia = 0.5
        done = set(kill)
        for f in mb.bm.faces:
            if f in done or f.calc_center_median().z < zw:
                continue
            ok = True
            for vv in f.verts:
                p = vv.co
                dx, dy = p.x - F.o.x, p.y - F.o.y
                if abs(dx * ca - dy * sa) > W / 2 - ia or abs(dx * sa + dy * ca) > D / 2 - ia:
                    ok = False
                    break
                rx, ry = p.x - Fr.o.x, p.y - Fr.o.y
                if p.z > Fr.o.z + Hf(rx * cr - ry * sr, rx * sr + ry * cr) - tv + 0.03:
                    ok = False
                    break
            if ok:
                kill.append(f)
    n = sum(len(f.verts) - 2 for f in kill)
    bmesh.ops.delete(mb.bm, geom=kill, context="FACES")
    return n


def build_lots(specs):
    regions = {}
    geos, infos = {}, {}
    tris = {}
    K2.DETACHED = True                                 # R3: fundos/laterais das casas soltas com 3 panos
    for s in specs:
        lt = s["lot"]
        mb = MB("OP_Cap_tmp_" + lt["name"], COLL)
        K2.BACK_P = K2.LOD3_P if s["back_coarse"] else 1.0
        K2.DETACHED = s["kw"]["lod"] <= 2                  # lod 3 (longe de toda rota): fundos lisos
        info = s["fn"](mb, s["F"], **s["kw"])
        K2.BACK_P = 1.0
        STATS["cull_in"] = STATS.get("cull_in", 0) + cull_inside(mb, s, info)
        infos[lt["name"]] = info
        geos[lt["name"]] = _geo(mb)
        tris[lt["name"]] = sum(len(f.verts) - 2 for f in mb.bm.faces)
        rg = regions.get(s["region"])
        if rg is None:
            rg = regions[s["region"]] = MB("OP_Cap_Q_" + s["region"], COLL)
        _merge(rg, mb)
    K2.DETACHED = False
    probs = interpen(specs, geos)
    STATS["tris_lote"] = tris
    cut = 0
    objs = []
    for nm, rg in regions.items():
        cut += K.cull_hidden(rg, dmax=6.0)
        objs.append(rg.finish())
    STATS["cull"] = cut
    return infos, probs, objs


# ================================================================== colisao V3 (op_col.V3 / colv3): o visual colide
# R3: a colisao da capital e a FORMA do visual (colv3.split no export/QA: cada casa/muro/andon/toro vira MeshPart Hull
# justa; telhado nao colide). Aqui so ficam as LAJES DE PISO dos interiores (topo = piso visivel: doma, agari, engawa,
# assoalho do haiden - o op_col.v3_floor_slabs as reconhece e mantem) e as calcadas da avenida. Nenhuma caixa de corpo,
# de muro, de poste ou de telhado (a V2 tinha caixas de 8,5..11 acima do visual: o 'em pe no ar').
def _col_lot_box(area, F, x0, x1, y0, y1, z0, z1):
    col_box(area, (x1 - x0, y1 - y0, z1 - z0), F.p((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), F.r())


def _interior_floors(s, area):
    """lajes de piso do interior vivo (o resto - paredes, verga, forro, pilares, escada - colide pela forma)"""
    lt, kw, F = s["lot"], s["kw"], s["F"]
    W, D = kw["W"], kw["D"]
    n = 0
    if s["fn"] is K2.loja:
        z0 = 0.8
        xs, sp = K2._posts_x(W, K2.loja_bays(W, kw["shop_side"], True))
        a, b = [(a, b) for t, o, a, b in sp if t == "shop"][0]
        yf = D / 2 - 0.86
        depth = kw.get("idepth") or min(7.5, D * 0.5)
        yb = yf - depth
        ya = yb + depth * 0.52
        _col_lot_box(area, F, a - 0.6, b + 0.6, yb, D / 2 + 0.35, -0.5, z0)              # piso de terra (doma) + soco
        _col_lot_box(area, F, a - 0.6, b + 0.6, yb, ya, z0, z0 + 1.15)                  # estrado (agari)
        n += 2
    elif s["fn"] is K2.chaya:
        gs = kw["garden_side"]
        gw = kw["garden_w"]
        Wb = W - gw
        Fb = K2.sub(F, -gs * gw / 2)
        eng = 3.0
        yb = D / 2 - eng - 0.86 - 6.6
        _col_lot_box(area, Fb, -Wb / 2, Wb / 2, yb, D / 2 + 0.35, -0.5, 1.0 + 0.45)       # engawa + tatami
        n += 1
    elif s["fn"] is K2.haiden2:
        Do = D * 0.45
        _col_lot_box(area, F, -W / 2, W / 2, D / 2 - Do, D / 2, -0.5, 1.6)                # assoalho
        n += 1
    return n


def lot_collisions(specs, infos):
    """lajes de piso dos interiores + calcadas da avenida (o resto colide pela forma do visual: op_col.V3)"""
    n = 0
    for s in specs:
        if s["lot"]["interior"]:
            n += _interior_floors(s, "OP_CapPiso" + s["lot"]["name"])
    av = L.AVENUE
    y0, y1 = av["y"]
    for sg in (-1, 1):
        xa, xb = sorted((sg * (av["x"][1] + 0.3), sg * av["front"]))
        col_box("OP_CapCalcada", (xb - xa, y1 - y0, 0.5), ((xa + xb) / 2, (y0 + y1) / 2, T1 + 0.47 - 0.25))
        n += 1
    return n


# ================================================================== R3 PAVIMENTO CONTINUO (geometria 2D pura)
# R6 (capturas 09/17: "caminhos tortos, lajes desencontradas, buracos e sobreposicao"): a V2 assentava lajes por
# RETANGULO de trecho e so pulava a laje cujo CENTRO caia num trecho ja feito -> nas quinas e cruzamentos sobravam
# buracos (laje pulada) e sobreposicoes (laje com o centro fora mas o corpo dentro). A R3 faz o pavimento como UMA
# superficie: cada trecho vira um CONVEXO MITRADO (as quinas da polilinha cortadas na bissetriz), recortado pelo PISO
# real da cota (decomposicao convexa dos pisos da planta menos os pisos de prioridade maior), menos as exclusoes (casas
# + soco, escadas, praca, avenida, summon, agua + capa, pontes) e menos o que um trecho de prioridade maior ja pegou
# (ruas largas primeiro, depois as estreitas, frentes das casas, becos e patamares de escada). As LAJES saem de uma
# grade FIXA por regiao (fiadas ao longo do trecho, juntas desencontradas) recortada exatamente pelas pecas: emenda
# sem buraco e sem sobreposicao; entre 2 regioes fica uma junta de 0,08 sobre o berco escuro continuo. Na borda
# externa (grama/terra) entra uma GUIA de pedra; onde o pavimento acaba num desnivel, uma saia ate o terreno.

EPS = 1e-6


def area(p):
    a = 0.0
    n = len(p)
    for i in range(n):
        x0, y0 = p[i]
        x1, y1 = p[(i + 1) % n]
        a += x0 * y1 - x1 * y0
    return a / 2.0


def ccw(p):
    return list(p) if area(p) > 0 else list(reversed(p))


def bbox(p):
    xs = [q[0] for q in p]
    ys = [q[1] for q in p]
    return (min(xs), min(ys), max(xs), max(ys))


def bb_hit(a, b, pad=0.0):
    return not (a[2] < b[0] - pad or b[2] < a[0] - pad or a[3] < b[1] - pad or b[3] < a[1] - pad)


def half(poly, a, b, c):
    """parte do poligono com a*x + b*y + c >= 0"""
    out = []
    n = len(poly)
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        fp, fq = a * p[0] + b * p[1] + c, a * q[0] + b * q[1] + c
        if fp >= -EPS:
            out.append(p)
        if (fp > EPS and fq < -EPS) or (fp < -EPS and fq > EPS):
            t = fp / (fp - fq)
            out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
    return _clean(out)


def _clean(p, tol=1e-5):
    out = []
    for q in p:
        if not out or abs(q[0] - out[-1][0]) > tol or abs(q[1] - out[-1][1]) > tol:
            out.append(q)
    if len(out) > 1 and abs(out[0][0] - out[-1][0]) <= tol and abs(out[0][1] - out[-1][1]) <= tol:
        out.pop()
    # tira colineares
    k = 0
    while len(out) >= 3 and k < len(out):
        a, b, c = out[k - 1], out[k], out[(k + 1) % len(out)]
        if abs((b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])) < 1e-7:
            out.pop(k)
        else:
            k += 1
    return out if len(out) >= 3 else []


def _edge_hp(a, b):
    """semiplano a ESQUERDA da aresta a->b (dentro de um ccw): (A, B, C) com A x + B y + C >= 0"""
    ex, ey = b[0] - a[0], b[1] - a[1]
    return -ey, ex, ey * a[0] - ex * a[1]


def clip(poly, cl):
    """poly (convexo ou nao) recortado pelo convexo ccw cl"""
    out = list(poly)
    n = len(cl)
    for i in range(n):
        A, B, C = _edge_hp(cl[i], cl[(i + 1) % n])
        out = half(out, A, B, C)
        if not out:
            return []
    return out


def sub(poly, cut, cbb=None):
    """convexo poly MENOS o convexo ccw cut -> lista de convexos"""
    if cbb is not None and not bb_hit(bbox(poly), cbb):
        return [poly]
    out = []
    rest = poly
    n = len(cut)
    for i in range(n):
        A, B, C = _edge_hp(cut[i], cut[(i + 1) % n])
        piece = half(rest, -A, -B, -C)
        if piece and abs(area(piece)) > 1e-4:
            out.append(piece)
        rest = half(rest, A, B, C)
        if not rest:
            return out
    return out


def grow(poly, d):
    """convexo ccw com cada aresta deslocada d para fora (cantos em quina)"""
    n = len(poly)
    lines = []
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        ex, ey = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(ex, ey) or 1.0
        nx, ny = ey / ln, -ex / ln                          # normal para FORA (ccw)
        lines.append(((a[0] + nx * d, a[1] + ny * d), (ex / ln, ey / ln)))
    out = []
    for i in range(n):
        (p1, u1), (p2, u2) = lines[i - 1], lines[i]
        den = u1[0] * u2[1] - u1[1] * u2[0]
        if abs(den) < 1e-6:
            out.append(p2)
            continue
        t = ((p2[0] - p1[0]) * u2[1] - (p2[1] - p1[1]) * u2[0]) / den
        out.append((p1[0] + u1[0] * t, p1[1] + u1[1] * t))
    return out


def pip(x, y, poly):
    ins = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi:
            ins = not ins
        j = i
    return ins


def convex_decomp(poly):
    """poligono simples -> convexos (orelhas + fusao Hertel-Mehlhorn)"""
    P = _clean(ccw(poly), 1e-4)
    if len(P) < 3:
        return []
    if _is_convex(P):
        return [P]
    idx = list(range(len(P)))
    tris = []
    guard = 0
    while len(idx) > 3 and guard < 10000:
        guard += 1
        n = len(idx)
        found = False
        for k in range(n):
            i0, i1, i2 = idx[k - 1], idx[k], idx[(k + 1) % n]
            a, b, c = P[i0], P[i1], P[i2]
            cr = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
            if cr <= 1e-9:
                continue
            ok = True
            for j in idx:
                if j in (i0, i1, i2):
                    continue
                q = P[j]
                if _in_tri(q, a, b, c):
                    ok = False
                    break
            if ok:
                tris.append([a, b, c])
                idx.pop(k)
                found = True
                break
        if not found:                                   # degenerado: tira o vertice mais "reto"
            idx.pop(0)
    if len(idx) == 3:
        t = [P[i] for i in idx]
        if area(t) > 1e-6:
            tris.append(t)
    return _merge_convex(tris)


def _in_tri(q, a, b, c):
    def s(p1, p2, p3):
        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
    d1, d2, d3 = s(q, a, b), s(q, b, c), s(q, c, a)
    return d1 >= -1e-9 and d2 >= -1e-9 and d3 >= -1e-9


def _is_convex(P):
    n = len(P)
    for i in range(n):
        a, b, c = P[i - 1], P[i], P[(i + 1) % n]
        if (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0]) < -1e-7:
            return False
    return True


def _key(p):
    return (round(p[0], 4), round(p[1], 4))


def _merge_convex(polys):
    polys = [list(p) for p in polys]
    changed = True
    while changed:
        changed = False
        for i in range(len(polys)):
            A = polys[i]
            ea = {(_key(A[k]), _key(A[(k + 1) % len(A)])): k for k in range(len(A))}
            for j in range(len(polys)):
                if i == j:
                    continue
                B = polys[j]
                for m in range(len(B)):
                    e = (_key(B[(m + 1) % len(B)]), _key(B[m]))
                    if e in ea:
                        k = ea[e]
                        # A: ... A[k] -> A[k+1] ...; B: B[m] -> B[m+1] (= A[k+1] -> A[k])
                        na = len(A)
                        nb = len(B)
                        mrg = [A[(k + 1 + t) % na] for t in range(na)]             # comeca em A[k+1], termina em A[k]
                        mrg += [B[(m + 2 + t) % nb] for t in range(nb - 2)]       # B depois de B[m+1] ate antes de B[m]
                        mrg = _clean(mrg, 1e-6)
                        if len(mrg) >= 3 and _is_convex(mrg):
                            polys[i] = mrg
                            polys.pop(j)
                            changed = True
                        break
                if changed:
                    break
            if changed:
                break
    return polys


def seg_regions(pts, w, ext_free=0.0, ext_end=None):
    """convexos MITRADOS de cada segmento da polilinha (quinas cortadas na bissetriz) -> [(poly, origem, rumo)]"""
    hw = w / 2.0
    dirs = []
    for a, b in zip(pts, pts[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy)
        dirs.append((dx / ln, dy / ln, ln) if ln > 1e-6 else None)
    out = []
    n = len(pts)
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        if dirs[i] is None:
            continue
        ux, uy, ln = dirs[i]
        vx, vy = -uy, ux
        e0 = 3.0 * hw if i > 0 else ext_free
        e1 = 3.0 * hw if i < n - 2 else (ext_free if ext_end is None else ext_end)
        A = (a[0] - ux * e0, a[1] - uy * e0)
        B = (b[0] + ux * e1, b[1] + uy * e1)
        poly = [(A[0] - vx * hw, A[1] - vy * hw), (B[0] - vx * hw, B[1] - vy * hw), (B[0] + vx * hw, B[1] + vy * hw),
                (A[0] + vx * hw, A[1] + vy * hw)]
        if i > 0 and dirs[i - 1]:
            mx, my = dirs[i - 1][0] + ux, dirs[i - 1][1] + uy
            ml = math.hypot(mx, my)
            if ml > 1e-6:
                mx, my = mx / ml, my / ml
                poly = half(poly, mx, my, -(mx * a[0] + my * a[1]))
        if i < n - 2 and dirs[i + 1]:
            mx, my = ux + dirs[i + 1][0], uy + dirs[i + 1][1]
            ml = math.hypot(mx, my)
            if ml > 1e-6:
                mx, my = mx / ml, my / ml
                poly = half(poly, -mx, -my, mx * b[0] + my * b[1])
        if poly:
            out.append((poly, (a[0], a[1]), math.atan2(uy, ux)))
    return out


def rect(org, ang, u0, u1, v0, v1):
    c, s = math.cos(ang), math.sin(ang)
    return [(org[0] + u * c - v * s, org[1] + u * s + v * c) for u, v in ((u0, v0), (u1, v0), (u1, v1), (u0, v1))]


def to_local(p, org, ang):
    c, s = math.cos(ang), math.sin(ang)
    x, y = p[0] - org[0], p[1] - org[1]
    return (x * c + y * s, -x * s + y * c)


def to_world(p, org, ang):
    c, s = math.cos(ang), math.sin(ang)
    return (org[0] + p[0] * c - p[1] * s, org[1] + p[0] * s + p[1] * c)


class Grid:
    """indice espacial de convexos (celula 'cell') para ponto-dentro rapido"""

    def __init__(self, cell=8.0):
        self.cell = cell
        self.cells = {}
        self.items = []

    def add(self, poly, tag=None):
        b = bbox(poly)
        k = len(self.items)
        self.items.append((poly, b, tag))
        c = self.cell
        for i in range(int(math.floor(b[0] / c)), int(math.floor(b[2] / c)) + 1):
            for j in range(int(math.floor(b[1] / c)), int(math.floor(b[3] / c)) + 1):
                self.cells.setdefault((i, j), []).append(k)

    def near(self, b):
        c = self.cell
        seen = set()
        for i in range(int(math.floor(b[0] / c)), int(math.floor(b[2] / c)) + 1):
            for j in range(int(math.floor(b[1] / c)), int(math.floor(b[3] / c)) + 1):
                for k in self.cells.get((i, j), ()):
                    if k not in seen:
                        seen.add(k)
                        yield self.items[k]

    def find(self, x, y):
        c = self.cell
        for k in self.cells.get((int(math.floor(x / c)), int(math.floor(y / c))), ()):
            poly, b, tag = self.items[k]
            if b[0] - 1e-6 <= x <= b[2] + 1e-6 and b[1] - 1e-6 <= y <= b[3] + 1e-6 and pip(x, y, poly):
                return tag if tag is not None else True
        return None


def subtract_all(pieces, cutters_grid, pad=0.0):
    """pecas convexas MENOS todos os convexos do indice (com a mesma folga 'pad' de crescimento)"""
    out = []
    for p in pieces:
        cur = [p]
        for cpoly, cb, tag in list(cutters_grid.near(bbox(p))):
            if not bb_hit(bbox(p), cb, pad):
                continue
            cp = grow(cpoly, pad) if pad else cpoly
            nxt = []
            for q in cur:
                nxt += sub(q, cp, bbox(cp))
            cur = nxt
            if not cur:
                break
        out += cur
    return out


def intersect_all(pieces, convs_grid):
    """pecas convexas recortadas por um conjunto de convexos (ex.: o piso decomposto): uniao das interseccoes"""
    out = []
    for p in pieces:
        pb = bbox(p)
        for cpoly, cb, tag in convs_grid.near(pb):
            if not bb_hit(pb, cb):
                continue
            q = clip(p, cpoly)
            if q and abs(area(q)) > 1e-4:
                out.append(q)
    return out


# ================================================================== R3 PLANO DO PAVIMENTO + MUROS (2D puro)

JOINT = 0.04                    # meia junta entre lajes / entre regioes (junta de 0,08 sobre o berco)
LOT_PAD = 0.4                   # soco (0,35) + 0,05
CAP_STAIRS = ("Praca", "Sudoeste", "OesteAlta", "Mirante")
SUMMON_RECT = (116.0, 150.0, 206.0, 264.0)


def stair_fp(L, nm, pad=0.0):
    foot, deg, w, n, tread, g = L.stair_frame(nm)
    a = math.radians(deg)
    ux, uy = math.cos(a), math.sin(a)
    vx, vy = -uy, ux
    x0, y0 = foot[0] - ux * (tread / 2 + pad), foot[1] - uy * (tread / 2 + pad)
    x1, y1 = foot[0] + ux * (tread * n + pad), foot[1] + uy * (tread * n + pad)
    hw = w / 2 + pad
    return ccw([(x0 + vx * hw, y0 + vy * hw), (x0 - vx * hw, y0 - vy * hw), (x1 - vx * hw, y1 - vy * hw),
                (x1 + vx * hw, y1 + vy * hw)])


def rect_xy(r):
    return [(r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3])]


def street_list(L):
    out = []
    for k, (pts, w, z) in enumerate(L.STREETS_V2):
        if k == 0:
            continue
        mx = sum(p[0] for p in pts) / len(pts)
        my = sum(p[1] for p in pts) / len(pts)
        r = SUMMON_RECT
        if r[0] <= mx <= r[2] and r[1] <= my <= r[3]:
            continue
        out.append((k, pts, w, z))
    return out


class Plan:
    def __init__(self, L, lots, water_polys, plaza_reg, sando, extra_paths=()):
        self.L = L
        self.lots = lots
        self.regions = []            # dict(key, z, org, ang, bed=[...], slab=[...], kind)
        self.fences = []             # dict(org, ang, s0, s1, t, z, kind, row)
        self.curbs = []              # (a, b, z, kind, (nx, ny))
        self.levels = sorted(set(z for k, pts, w, z in street_list(L)) | set(lt["z"] for lt in lots))
        self.floor = {}
        for z in self.levels:
            g = Grid(16.0)
            for p in self._floor_convex(z):
                g.add(p)
            self.floor[z] = g
        ex = Grid(8.0)
        for lt in lots:
            ex.add(ccw(L.lot_poly(lt, LOT_PAD)), "lot")
        for nm, foot, deg, w, n, tread, g_ in L.STAIRS:
            ex.add(stair_fp(L, nm, 0.3), "stair")
        ex.add(rect_xy(SUMMON_RECT), "summon")
        av = L.AVENUE
        ex.add(rect_xy((-av["front"], av["y"][0], av["front"], av["y"][1])), "avenue")
        for p in sub(ccw(plaza_reg), ccw(rect_xy(sando))):
            ex.add(p, "plaza")
        for nm, poly, zb in water_polys:
            for p in convex_decomp(poly):
                ex.add(grow(p, L.CANAL_COPE_W), "water")
        for nm, a, b, w in L.bridge_list():
            if nm in ("CanalS", "CanalN"):
                ex.add(ccw(L.ribbon([a[:2], b[:2]], w / 2 + 0.3)), "bridge")
        self.excl = ex
        self.claimed = {z: Grid(8.0) for z in self.levels}
        self.extra_paths = list(extra_paths)
        self.street_rib = Grid(8.0)                       # para medir a distancia da casa ate a rua
        for k, pts, w, z in street_list(L) + [(0, p, w, z) for p, w, z in self.extra_paths]:
            for poly, org, ang in seg_regions(pts, w):
                self.street_rib.add(poly, z)
        self.street_rib.add(rect_xy((-av["front"], av["y"][0], av["front"], av["y"][1])), L.T1)
        self.street_rib.add(ccw(plaza_reg), L.P)

    # ---------------------------------------------------------------- pisos convexos da cota z
    def _floor_convex(self, z):
        L = self.L
        fl = L.floors()
        out = []
        for nm, poly, zz, pr in fl:
            if callable(zz) or abs(zz - z) > 0.05:
                continue
            higher = [p2 for n2, p2, z2, pr2 in fl if pr2 > pr]
            hconv = []
            for h in higher:
                hconv += convex_decomp(h)
            for piece in L.floor_pieces(nm):
                cur = convex_decomp(piece)
                for h in hconv:
                    hb = bbox(h)
                    nxt = []
                    for c in cur:
                        nxt += sub(c, h, hb)
                    cur = nxt
                out += cur
        return out

    # ---------------------------------------------------------------- regioes
    def add_region(self, key, poly, org, ang, z, kind, dz=None):
        L = self.L
        if z not in self.floor:
            return None
        pieces = intersect_all([ccw(poly)], self.floor[z])
        pieces = subtract_all(pieces, self.excl)
        bed = subtract_all(pieces, self.claimed[z])
        bed = [p for p in bed if abs(area(p)) > 0.05]
        if not bed:
            return None
        slab = subtract_all(bed, self.claimed[z], 2 * JOINT)
        slab = [p for p in slab if abs(area(p)) > 0.02]
        for p in bed:
            self.claimed[z].add(p, key)
        r = dict(key=key, z=z, org=org, ang=ang, bed=bed, slab=slab, kind=kind, dz=dz)
        self.regions.append(r)
        return r

    def dist_to_street(self, x, y, dx, dy, z, dmax=8.0, stop_lot=False):
        d = 0.0
        while d <= dmax:
            t = self.street_rib.find(x + dx * d, y + dy * d)
            if t is not None and abs(t - z) < 0.05:
                return d
            if stop_lot and d > 0.6 and self.excl.find(x + dx * d, y + dy * d) == "lot":
                return None
            d += 0.25
        return None

    def build(self):
        L = self.L
        # 1. ruas (largas primeiro)
        ss = sorted(street_list(L), key=lambda s: (-s[2], s[0]))
        ends = []
        for nm in CAP_STAIRS:
            foot, deg, w_, n_, tread, g_ = L.stair_frame(nm)
            top = L.stair_top(nm)
            ends += [(foot[0], foot[1], foot[2]), (top[0], top[1], top[2])]

        def ext_at(p, z, w):
            return min(w / 2, 3.0) if any(math.hypot(p[0] - e[0], p[1] - e[1]) < 7.0 and abs(e[2] - z) < 0.05
                                          for e in ends) else 0.0
        for k, pts, w, z in ss:
            for i, (poly, org, ang) in enumerate(seg_regions(pts, w, ext_at(pts[0], z, w), ext_at(pts[-1], z, w))):
                self.add_region("rua%d_%d" % (k, i), poly, org, ang, z, "rua")
        for j, (pts, w, z) in enumerate(self.extra_paths):
            for i, (poly, org, ang) in enumerate(seg_regions(pts, w)):
                self.add_region("extra%d_%d" % (j, i), poly, org, ang, z, "rua")
        # 2. patamares das escadas da capital (o pavimento encosta no 1o/ultimo degrau)
        for nm in CAP_STAIRS:
            foot, deg, w, n, tread, g_ = L.stair_frame(nm)
            a = math.radians(deg)
            top = L.stair_top(nm)
            org_t = (top[0], top[1])
            self.add_region("patamar_" + nm + "_t", rect(org_t, a, -0.5, 4.5, -w / 2, w / 2), org_t, a, top[2], "patamar")
            org_f = (foot[0] - math.cos(a) * tread / 2, foot[1] - math.sin(a) * tread / 2)
            self.add_region("patamar_" + nm + "_p", rect(org_f, a, -4.5, 0.5, -w / 2, w / 2), org_f, a, foot[2], "patamar")
        # 3. frentes das casas, vaos (muro) e becos
        rows = {}
        for lt in self.lots:
            rows.setdefault((lt["block"], lt["row"]), []).append(lt)
        for key, lts in rows.items():
            lts.sort(key=lambda t: t["s0"])
            lt0 = lts[0]
            a, b = lt0["row_a"], lt0["row_b"]
            ux, uy = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(ux, uy)
            ux, uy = ux / ln, uy / ln
            side = lt0["row_side"]
            nx, ny = -uy * side, ux * side
            ang = math.atan2(uy, ux)
            z = lt0["z"]
            Drow = lt0["rowD"]

            def P(s, t):
                return (a[0] + ux * s + nx * t, a[1] + uy * s + ny * t)

            def R(s0, s1, t0, t1):
                return ccw([P(s0, t0), P(s1, t0), P(s1, t1), P(s0, t1)])

            def dout(s, t, sg):
                ds = [self.dist_to_street(*P(s + f, t), nx * sg, ny * sg, z) for f in (-2.0, 0.0, 2.0)]
                ds = [d for d in ds if d is not None]
                return min(ds) if ds else None
            avenue = key in L.FLAT_FRONT and key[0] in ("AvO", "AvL")
            for lt in lts:
                s0, s1 = lt["s0"], lt["s0"] + lt["W"]
                if avenue:
                    continue
                if not lt["flip"]:
                    tf = -lt["setback"]
                    d = dout((s0 + s1) / 2, 0.0, 1)
                    t1 = (d + 0.4) if d is not None else 2.0
                    self.add_region("frente_" + lt["name"], R(s0, s1, tf - 0.5, t1), a, ang, z, "frente")
                else:
                    tf = -Drow + lt["setback"]
                    d = dout((s0 + s1) / 2, -Drow, -1)
                    t1 = (d + 0.4) if d is not None else 2.0
                    self.add_region("frente_" + lt["name"], R(s0, s1, -Drow - t1, tf + 0.5), a, ang, z, "frente")
            # LATERAIS das casas de ponta viradas para uma rua proxima (<= 5): o pavimento vai ate a parede
            for lt in lts:
                s0, s1 = lt["s0"], lt["s0"] + lt["W"]
                if lt["flip"]:
                    ta, tb = -Drow + lt["setback"], -Drow + lt["setback"] + lt["D"]
                else:
                    ta, tb = -lt["setback"] - lt["D"], -lt["setback"]
                for sg, se in ((-1, s0), (1, s1)):
                    ds = [self.dist_to_street(*P(se, t), ux * sg, uy * sg, z, 5.0, True) for t in (ta + 1.0, (ta + tb) / 2,
                                                                                               tb - 1.0)]
                    ds = [d_ for d_ in ds if d_ is not None]
                    if not ds or max(ds) < 0.3:
                        continue
                    d_ = max(ds) + 0.4
                    sa, sb_ = (se - d_, se + 0.5) if sg < 0 else (se - 0.5, se + d_)
                    self.add_region("lado_%s_%d" % (lt["name"], sg), R(sa, sb_, ta - 0.5, tb + 0.5), a, ang, z, "frente")
            for A, B in zip(lts, lts[1:]):
                s0, s1 = A["s0"] + A["W"], B["s0"]
                if s1 - s0 < 0.5:
                    continue
                if A["flip"] != B["flip"]:
                    # BECO: atravessa a faixa de rua a rua
                    df = dout((s0 + s1) / 2, 0.0, 1)
                    db = dout((s0 + s1) / 2, -Drow, -1)
                    t1 = (df + 0.4) if df is not None else 1.0
                    t0 = -Drow - ((db + 0.4) if db is not None else 1.0)
                    self.add_region("beco_%s_%s" % (A["name"], B["name"]), R(s0, s1, t0, t1), P(s0, 0.0),
                                    ang + math.pi / 2, z, "beco")
                    continue
                if not A["flip"]:
                    tf = -(max(A["setback"], B["setback"]) + 1.0) if not avenue else -1.25
                    d = dout((s0 + s1) / 2, 0.0, 1)
                    t1 = (d + 0.4) if d is not None else 2.0
                    if not avenue:
                        self.add_region("vao_%s_%s" % (A["name"], B["name"]), R(s0, s1, tf + 0.3, t1), a, ang, z,
                                        "vao")
                    else:                                  # avenida: o muro recua 1,25 (o chapeu nao invade a calcada)
                        self.add_region("vao_%s_%s" % (A["name"], B["name"]), R(s0, s1, tf + 0.3, 0.02), a, ang, z,
                                        "vao", dz=0.47)    # e o vao e calcada na cota da calcada (+0,47)
                else:
                    tf = -Drow + max(A["setback"], B["setback"]) + 1.0
                    d = dout((s0 + s1) / 2, -Drow, -1)
                    t1 = (d + 0.4) if d is not None else 2.0
                    self.add_region("vao_%s_%s" % (A["name"], B["name"]), R(s0, s1, -Drow - t1, tf - 0.3), a, ang,
                                    z, "vao")
                self.fences.append(dict(org=a, ang=ang, u=(ux, uy), n=(nx, ny), s0=s0, s1=s1, t=tf, z=z,
                                        row=key, avenue=avenue, a=A["name"], b=B["name"],
                                        face=(-1 if A["flip"] else 1)))
        self._curbs()
        return self

    # ---------------------------------------------------------------- guias / saias na borda externa
    def _curbs(self, step=1.0):
        L = self.L
        for r in self.regions:
            z = r["z"]
            for p in r["bed"]:
                n = len(p)
                for i in range(n):
                    a, b = p[i], p[(i + 1) % n]
                    ex, ey = b[0] - a[0], b[1] - a[1]
                    ln = math.hypot(ex, ey)
                    if ln < 0.05:
                        continue
                    nx, ny = ey / ln, -ex / ln                       # para fora (ccw)
                    k = max(1, int(math.ceil(ln / step)))
                    run = None
                    for j in range(k):
                        t0, t1 = j / k, (j + 1) / k
                        mx, my = a[0] + ex * (t0 + t1) / 2, a[1] + ey * (t0 + t1) / 2
                        cls = self._classify(mx + nx * 0.15, my + ny * 0.15, z)
                        if cls == "skirt":                      # desnivel: parede que SOBE logo adiante = sarjeta
                            for dd in (0.5, 0.9):
                                zz = L.zone_of(mx + nx * dd, my + ny * dd)
                                if zz is not None and zz > z + 0.3:
                                    cls = "wall"
                                    break
                        if run and run[2] == cls:
                            run[1] = t1
                        else:
                            if run and run[2] in ("curb", "skirt", "wall"):
                                self._emit(a, ex, ey, run, z, (nx, ny), r["dz"])
                            run = [t0, t1, cls]
                    if run and run[2] in ("curb", "skirt", "wall"):
                        self._emit(a, ex, ey, run, z, (nx, ny), r["dz"])

    def _emit(self, a, ex, ey, run, z, nrm, dz=None):
        pa = (a[0] + ex * run[0], a[1] + ey * run[0])
        pb = (a[0] + ex * run[1], a[1] + ey * run[1])
        self.curbs.append((pa, pb, z, run[2], nrm, dz))

    def _classify(self, x, y, z):
        if self.claimed[z].find(x, y) is not None:
            return "path"
        t = self.excl.find(x, y)
        if t is not None:
            return "excl:" + t
        zz = self.L.zone_of(x, y)
        if zz is not None and abs(zz - z) <= 0.05:
            return "curb"
        return "skirt"


def _ph01(*a):
    """hash murmur-like (fmix32) -> [0, 1)"""
    k = "|".join("%.2f" % v if isinstance(v, float) else str(v) for v in a)
    h = 2166136261
    for ch in k:
        h = ((h ^ ord(ch)) * 16777619) & 0xffffffff
    h ^= h >> 16
    h = (h * 0x85ebca6b) & 0xffffffff
    h ^= h >> 13
    h = (h * 0xc2b2ae35) & 0xffffffff
    h ^= h >> 16
    return h / 4294967296.0


def slabs(r, sx=2.6, sy=1.5, gap=JOINT, min_area=0.06):
    """lajes da regiao: grade FIXA (fiadas de 'sy' ao longo do rumo, comprimentos 0,8..1,2 x sx, juntas desencontradas)
    recortada por cada peca convexa da regiao -> [(poligono mundo, indice da fiada, indice da laje)]"""
    org, ang = r["org"], r["ang"]
    loc = [[to_local(p, org, ang) for p in piece] for piece in r["slab"]]
    if not loc:
        return []
    u0 = min(p[0] for pc in loc for p in pc)
    u1 = max(p[0] for pc in loc for p in pc)
    v0 = min(p[1] for pc in loc for p in pc)
    v1 = max(p[1] for pc in loc for p in pc)
    out = []
    key = r["key"]
    row = int(math.floor(v0 / sy))
    while row * sy < v1:
        va, vb = row * sy + gap, (row + 1) * sy - gap
        off = (0.5 * sx if row % 2 else 0.0) + 0.23 * sx * _ph01(key, row, "o")
        u = math.floor((u0 + off) / sx) * sx - off - sx
        k = 0
        while u < u1:
            w = sx * (0.8 + 0.4 * _ph01(key, row, k))
            ua, ub = u + gap, u + w - gap
            u += w
            k += 1
            if ub < u0 or ua > u1:
                continue
            rc = [(ua, va), (ub, va), (ub, vb), (ua, vb)]
            for pc in loc:
                q = clip(rc, pc)
                if q and abs(area(q)) >= min_area:
                    out.append(([to_world(p, org, ang) for p in q], row, k))
        row += 1
    return out


# ================================================================== pavimento -> malha
def _face(mb, pts, z, m):
    """face plana (so o topo, virada para cima) - poligono convexo"""
    pts = ccw(pts)
    vs = [mb.bm.verts.new((p[0], p[1], z)) for p in pts]
    try:
        mb.bm.faces.new(vs)
    except ValueError:
        return
    mb._post(vs, m, None, 0, 1)


PAVE_MATS = {"rua": [("Stone_OP_Path", 8), ("Stone_OP", 1)], "patamar": [("Stone_OP_Path", 8), ("Stone_OP", 1)],
             "beco": [("Stone_OP_Path", 6), ("Stone_OP", 2)], "frente": [("Stone_OP", 5), ("Stone_OP_Path", 2)],
             "vao": [("Stone_OP", 5), ("Stone_OP_Path", 2)]}
PAVE_SLAB = {"rua": (3.4, 1.7), "patamar": (3.4, 1.7), "beco": (2.8, 1.5), "frente": (2.8, 1.5), "vao": (2.8, 1.5)}


def _pick(mats, *key):
    tot = sum(w for _, w in mats)
    x = h01(*key) * tot
    for m, w in mats:
        x -= w
        if x < 0:
            return m
    return mats[-1][0]


def streets(lots):
    """avenida com o street2 (aprovada) + o PAVIMENTO CONTINUO R3 (ruas, vielas, cais, sando, frentes das casas,
    vaos, becos, patamares das escadas) + guias/sarjetas/saias na borda. Devolve o plano (muros dos vaos)."""
    t0 = time.time()
    mp = MB("OP_Cap_Streets", COLL, detail="far", floor=-999)
    av = L.AVENUE
    y0, y1 = av["y"]
    walk = av["front"] - av["x"][1] - 0.3
    Fa = Frame(0.0, (y0 + y1) / 2, T1 + 0.12, math.pi / 2)
    K2.street2(mp, Fa, y1 - y0, av["x"][1] - av["x"][0], walk, key=3, thin=True)
    import op_plaza as PZ
    pl = Plan(L, lots, op_col.water_polys(), PZ.REG, PZ.SANDO, EXTRA_PATHS).build()
    nq = 0
    for r in pl.regions:
        dz = r["dz"] if r["dz"] is not None else STREET_DZ
        zb, zt = r["z"] + dz - (STREET_DZ - BED_DZ), r["z"] + dz
        for p in r["bed"]:
            _face(mp, p, zb, "Stone_OP_Dark")
        sx, sy = PAVE_SLAB[r["kind"]]
        mats = PAVE_MATS[r["kind"]]
        for q, row, k in slabs(r, sx, sy):
            _face(mp, q, zt, _pick(mats, r["key"], row, k))
            nq += 1
    mp.finish(recalc=False)
    # guias (grama), sarjetas (muro que sobe) e saias (desnivel)
    mg = MB("OP_Cap_Guias", COLL, detail="near")
    ng = {"curb": 0, "wall": 0, "skirt": 0}
    for a, b, z, kind, nrm, rdz in pl.curbs:
        ex, ey = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(ex, ey)
        if ln < 0.2:
            continue
        sdz = STREET_DZ if rdz is None else rdz
        F = Frame(a[0], a[1], z, math.atan2(ey, ex))           # +x ao longo, -y = para fora (ccw)
        if kind == "curb":                                    # guia: topo em pecas de ~3 + face de fora e de dentro
            zt, x0, x1 = sdz + 0.1, -0.25, ln + 0.25
            nseg = max(1, int(round(ln / 3.0)))
            for i in range(nseg):
                xa = x0 + (x1 - x0) * i / nseg + (0.03 if i else 0.0)
                xb = x0 + (x1 - x0) * (i + 1) / nseg - (0.03 if i < nseg - 1 else 0.0)
                mg.quad(F.p(xa, -0.5, zt), F.p(xb, -0.5, zt), F.p(xb, 0.0, zt), F.p(xa, 0.0, zt), K2.CURB)
            mg.quad(F.p(x1, -0.5, -0.45), F.p(x1, -0.5, zt), F.p(x0, -0.5, zt), F.p(x0, -0.5, -0.45), K2.CURB)
            mg.quad(F.p(x0, 0.0, sdz - 0.17), F.p(x0, 0.0, zt), F.p(x1, 0.0, zt), F.p(x1, 0.0, sdz - 0.17), K2.CURB)
        elif kind == "wall":                                  # sarjeta rente ate o pe do muro que sobe
            zt = sdz - 0.04
            mg.quad(F.p(-0.05, -1.0, zt), F.p(ln + 0.05, -1.0, zt), F.p(ln + 0.05, 0.0, zt), F.p(-0.05, 0.0, zt), K2.GUTTER)
        else:
            mg.quad(F.p(0.0, 0.0, sdz), F.p(0.0, 0.0, -1.4), F.p(ln, 0.0, -1.4), F.p(ln, 0.0, sdz), "Stone_OP")
        ng[kind] += 1
    mg.finish(recalc=False)
    STATS["lajes"] = nq
    STATS["guias"] = ng
    STATS["regioes"] = len(pl.regions)
    STATS["t_ruas"] = time.time() - t0
    return pl


# ================================================================== muros dos vaos entre casas (R2)
def wall_tsuiji(mb, F, Lf, h=2.8, cap="Stone_OP_Dark"):
    """MURO TSUIJI baixo dos vaos (R3): soco de pedra, pano de reboco com 2 frisos, CHAPEU de telha cinza (kawara
    escura) de 2 aguas com cumeeira - o chapeu e de material SOLIDO (colide pela forma: quem pula no muro fica em cima
    do chapeu que se ve, nao dentro dele). Baixo (2,8 + chapeu) para nao virar degrau ate o beiral das casas.
    F no meio, ao longo de x"""
    K.bb(mb, F, -Lf / 2, Lf / 2, -0.5, 0.5, -0.25, 0.55, "Stone_OP")
    K.bb(mb, F, -Lf / 2 + 0.05, Lf / 2 - 0.05, -0.4, 0.4, 0.55, h, K2.PLW)
    for zz in (h - 1.0, h - 0.6):
        K.bb(mb, F, -Lf / 2 + 0.05, Lf / 2 - 0.05, -0.46, 0.46, zz - 0.07, zz + 0.07, K2.PL)
    for sg in (-1, 1):
        K.bx(mb, F, 0.0, sg * 0.4, h + 0.2, Lf + 0.3, 0.95, 0.16, cap, 0.0, rx=-sg * 0.5)
    K.bb(mb, F, -Lf / 2 - 0.15, Lf / 2 + 0.15, -0.15, 0.15, h + 0.34, h + 0.56, cap)


def board_fence(mb, F, Lf, h=3.0):
    """MURO DE TABUAS (itabei): soleira de pedra, mouroes escuros a <= 2,4, painel de tabuas verticais com mata-juntas,
    capa de madeira com pingadeira. F no meio, ao longo de x"""
    K.bb(mb, F, -Lf / 2, Lf / 2, -0.4, 0.4, -0.25, 0.35, "Stone_OP")
    xs = [-Lf / 2 + 0.2] + K.even(-Lf / 2 + 0.2, Lf / 2 - 0.2, 2.4)[1:-1] + [Lf / 2 - 0.2]
    for x in sorted(set(round(v, 3) for v in xs)):
        K.bb(mb, F, x - 0.18, x + 0.18, -0.2, 0.2, 0.35, h + 0.1, K2.WD)
    K.bb(mb, F, -Lf / 2 + 0.05, Lf / 2 - 0.05, -0.1, 0.1, 0.4, h - 0.25, K2.WM)
    for x in K.even(-Lf / 2 + 0.4, Lf / 2 - 0.4, 0.9):
        K.bb(mb, F, x - 0.06, x + 0.06, 0.1, 0.17, 0.5, h - 0.3, K2.WD)
    K.bb(mb, F, -Lf / 2, Lf / 2, -0.28, 0.28, h - 0.25, h - 0.05, K2.WD)
    K.bb(mb, F, -Lf / 2 - 0.05, Lf / 2 + 0.05, -0.36, 0.36, h - 0.05, h + 0.12, K2.WD)


def fences(pl, specs):
    """muro em cada VAO da frente entre 2 casas viradas para a mesma rua (o vao vira jardim/patio de fundo): tsuiji
    (reboco com chapeu de telha) na avenida/NE/fachada da praca, tabuado ou bambu no resto. Colide pela forma (V3)."""
    roof_of = {s["lot"]["name"]: s["kw"]["roof_m"] for s in specs}
    mb = MB("OP_Cap_Muros", COLL, detail="near")
    n = 0
    for f in pl.fences:
        ln = f["s1"] - f["s0"]
        if ln < 0.6:
            continue
        sm = (f["s0"] + f["s1"]) / 2
        ox, oy = f["org"]
        ux, uy = f["u"]
        nx, ny = f["n"]
        cx, cy = ox + ux * sm + nx * f["t"], oy + uy * sm + ny * f["t"]
        F = Frame(cx, cy, f["z"], f["ang"])
        blk = f["row"][0]
        if blk in FENCE_TSUIJI:
            wall_tsuiji(mb, F, ln, 2.8)
        elif h01("muro", f["a"]) < 0.55:
            board_fence(mb, F, ln, 3.0)
        else:
            K2.bamboo_fence(mb, F, ln, 2.9)
        n += 1
        if ln >= 9.0 and blk not in ("AvO", "AvL"):            # jardim largo: arvore (op_veg) atras do muro
            dd = 3.6 * (1 if f["face"] > 0 else -1)
            VEG_SPOTS.append((cx - nx * dd, cy - ny * dd, f["z"], "cerejeira" if h01("vg", f["a"]) < 0.6 else "pinheiro",
                              "jardim entre casas " + f["a"]))
    K.cull_hidden(mb)
    mb.finish()
    STATS["muros"] = n
    return n


# ================================================================== pecas: andon, toro, torii, carga
def _lamp_spots(lots):
    """andon nos NOS das ruas (pontas das faixas da planta + avenida a cada ~20), na borda da faixa, longe das casas"""
    spots = []
    av = L.AVENUE
    for y in (52.0, 72.0, 92.0):
        for s in (-1, 1):
            spots.append((s * (av["x"][1] - 1.5), y, T1, T1 + 0.12))
    for k, pts, w, z in street_list(L):
        for i, p in enumerate(pts):
            if i not in (0, len(pts) - 1):
                continue
            q = pts[1] if i == 0 else pts[-2]
            dx, dy = q[0] - p[0], q[1] - p[1]
            ln = math.hypot(dx, dy) or 1.0
            nx, ny = -dy / ln, dx / ln
            x, y = p[0] + nx * (w / 2 - 0.9) + dx / ln * 3.0, p[1] + ny * (w / 2 - 0.9) + dy / ln * 3.0
            spots.append((x, y, z, z + STREET_DZ))
    out = []
    lp = [L.lot_poly(lt, 1.6) for lt in lots]
    segs = [(a, b, zr) for pts, zr in L.routes().values() for a, b in zip(pts, pts[1:])]
    for x, y, zb, z in spots:
        if any(_seg_d((x, y), a, b) < 3.2 for a, b, zr in segs):      # R3: nada no corredor das rotas (QA)
            continue
        if any(L.point_in_poly(x, y, p) for p in lp) or (SUMMON_RECT[0] - 2 <= x <= SUMMON_RECT[2] + 2 and
                                                         SUMMON_RECT[1] - 2 <= y <= SUMMON_RECT[3] + 2):
            continue
        zz = L.zone_of(x, y)
        if zz is None or abs(zz - zb) > 0.05:
            continue
        if any(math.hypot(x - a, y - b) < 20.0 for a, b, c in out):
            continue
        out.append((x, y, z))
    return out


def props(lots):
    """andon/toro/torii/carga (V3: colidem pela forma do visual - nenhuma caixa)"""
    mb = MB("OP_Cap_Props", COLL)
    n_col = 0
    nl = 0
    for i, (x, y, z) in enumerate(_lamp_spots(lots)):
        nm = "L_OPProp_Lamp_Cap_%d" % i if nl < 10 and i % 2 == 0 else None
        nl += 1 if nm else 0
        K2.lamp_andon(mb, Frame(x, y, z, 0.0), nm)
    for i, (x, y) in enumerate(L.NE_TORO):
        z = P + STREET_DZ
        K2.toro2(mb, Frame(x, y, z, 0.0), "L_OPProp_Toro_Sando_%d" % i if i % 2 == 0 else None, 0.8)
    n_col += torii_ne(mb)
    for k, (x, y, z, kind) in enumerate(((95.5, 71.0, T1, "barrels"),)):
        K2.goods_pile(mb, Frame(x, y, z + STREET_DZ, 0.0), kind)
    K.cull_hidden(mb)
    mb.finish()
    return n_col


def torii_ne(mb):
    """torii (myojin) de laca na entrada do sando NE: pilares em pedras-base, nuki, kasagi com pontas levantadas,
    placa; 2 nobori ao lado. Rumo +x (quem entra no sando)."""
    x0, y0 = L.SHRINE_TORII
    z = P
    F = Frame(x0, y0, z, 0.0)
    w, h = 9.0, 10.6
    for s in (-1, 1):
        Fp = K2.sub(F, 0.0, s * (w / 2 + 0.7))
        K.rock_base(mb, Fp, 0.0, 0.0, 0.0, 1.15, 0.6)
        K.lathe(mb, Fp, (0, 0, 0.4), [(0.62, 0.0), (0.56, h - 0.4)], 12, K2.LAC)
        K.lathe(mb, Fp, (0, 0, 0.35), [(0.78, 0.0), (0.78, 0.9), (0.66, 1.05)], 12, K2.WD)
    yy = w / 2 + 2.6
    K.bb(mb, F, -0.45, 0.45, -yy, yy, h - 2.3, h - 1.5, K2.LAC)
    K.bb(mb, F, -0.5, 0.5, -0.45, 0.45, h - 1.5, h - 0.2, K2.LAC)
    K.bb(mb, F, -0.62, -0.5, -1.0, 1.0, h - 1.4, h + 0.0, K2.GOLD)
    zk = h + 0.25
    prof = [(-0.6, -0.45), (0.6, -0.45), (0.6, 0.35), (-0.6, 0.35)]
    pts = [(0.0, -(yy + 1.4), zk + 0.9), (0.0, -(yy - 0.6), zk + 0.25), (0.0, -w / 4, zk), (0.0, 0.0, zk - 0.03),
           (0.0, w / 4, zk), (0.0, yy - 0.6, zk + 0.25), (0.0, yy + 1.4, zk + 0.9)]
    K.sweep(mb, F, pts, prof, K2.LAC)
    K.sweep(mb, F, [(p[0], p[1] * 1.04, p[2] + 0.75) for p in pts], [(-0.75, -0.4), (0.75, -0.4), (0.75, 0.4),
                                                                      (-0.75, 0.4)], K2.WD)
    for s in (-1, 1):
        K2.nobori2(mb, Frame(x0 - 1.6, y0 + s * (w / 2 + 3.4), z + STREET_DZ, math.pi), 8.5, K2.CWHITE, K2.CRED)
    return 0


# ================================================================== guarda-corpos VISIVEIS nas bordas abertas (V3)
# R3/V3 (lead): borda de penhasco dentro da capital onde a queda nao faz sentido = MURETA DE PEDRA + GUARDA-CORPO de
# madeira escura (colide pela forma; nada invisivel). (nome, cota, poligono do piso, trecho da borda)
EDGE_RAILS = [
    ("BairroSul", T1, "T1", [(-160.0, 47.0), (-150.0, 42.0), (-110.0, 36.0), (-70.0, 34.0), (-46.0, 34.0)]),
    ("NELeste", P, "Plaza", [(222.0, 262.0), (234.0, 286.0), (236.0, 316.0)]),
    ("MiranteN", L.NEM, "NEMirante", [(172.0, 316.0), (172.0, 338.0), (236.0, 338.0), (236.0, 316.0), (172.0, 316.0)]),
    ("W2bOeste", P, "W2b", [(-214.0, 126.0), (-219.0, 140.0), (-224.0, 172.0), (-224.0, 214.0), (-222.0, 262.0),
                            (-214.0, 296.0)]),
    ("TerracoOeste", L.W3, "W3", [(-212.0, 300.0), (-221.0, 334.0), (-216.0, 386.0), (-200.0, 420.0), (-170.0, 436.0),
                                  (-130.0, 430.0)]),
]
EDGE_IN = 1.3              # recuo da mureta para dentro do piso


def edge_rails(lots):
    mb = MB("OP_Cap_Guarda", COLL, detail="near")
    pads = [L.lot_poly(lt, 1.2) for lt in lots]
    stairs_fp = [stair_fp(L, nm, 1.0) for nm, foot, deg, w, n, tread, g in L.STAIRS]
    water = [w[1] for w in op_col.water_polys()]
    n_runs = 0
    tot = 0.0
    for nm, z, floor_nm, pts in EDGE_RAILS:
        poly = L.floor_poly(floor_nm)
        # trecho recuado para DENTRO do piso (lado testado no poligono)
        off = []
        for i, (a, b) in enumerate(zip(pts, pts[1:])):
            dx, dy = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(dx, dy)
            nx, ny = -dy / ln, dx / ln
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            if not L.point_in_poly(mx + nx * 2.0, my + ny * 2.0, poly):
                nx, ny = -nx, -ny
            off.append(((a[0] + nx * EDGE_IN, a[1] + ny * EDGE_IN), (b[0] + nx * EDGE_IN, b[1] + ny * EDGE_IN)))
        # amostra a cada ~1 e corta onde nao ha piso na cota, casa, escada ou agua
        for (a, b) in off:
            ln = math.hypot(b[0] - a[0], b[1] - a[1])
            k = max(2, int(ln / 1.0))
            ok = []
            for i in range(k + 1):
                t = i / k
                x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
                zz = L.zone_of(x, y)
                good = zz is not None and abs(zz - z) < 0.05 and not any(L.point_in_poly(x, y, q) for q in pads) and                     not any(L.point_in_poly(x, y, q) for q in stairs_fp) and not any(L.point_in_poly(x, y, q) for q in water)
                ok.append((t, good))
            runs, cur = [], None
            for t, g in ok:
                if g:
                    cur = [t, t] if cur is None else [cur[0], t]
                elif cur is not None:
                    runs.append(cur)
                    cur = None
            if cur is not None:
                runs.append(cur)
            for t0, t1 in runs:
                pa = (a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0)
                pb = (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)
                rl = math.hypot(pb[0] - pa[0], pb[1] - pa[1])
                if rl < 2.0:
                    continue
                F = Frame(pa[0], pa[1], z + STREET_DZ - 0.2, math.atan2(pb[1] - pa[1], pb[0] - pa[0]))
                K.bb(mb, F, 0.0, rl, -0.45, 0.45, -0.45, 0.85, "Stone_OP_Wall")                # mureta
                K.bb(mb, F, -0.06, rl + 0.06, -0.55, 0.55, 0.85, 1.05, "Stone_OP_Path")      # capa
                K2.rail2(mb, F, [(0.3, 0.0), (rl - 0.3, 0.0)], h=2.3, base=1.05, step=4.0, m=K2.WD, gold=False)
                n_runs += 1
                tot += rl
    K.cull_hidden(mb)
    mb.finish()
    STATS["guarda"] = (n_runs, round(tot))
    return n_runs


# ================================================================== escadas da planta (visual; colisao do op_col)
def stairs():
    """degraus (OP_Cap_Stairs: piso - a colisao e a rampa do op_col) + BANZOS em objeto proprio (OP_Cap_StairSides:
    parede visivel da escada, colide pela forma na V3 - o banzo que se ve segura o jogador)"""
    mb = MB("OP_Cap_Stairs", COLL, detail="far", floor=None)
    ms = MB("OP_Cap_StairSides", COLL, detail="far", floor=None)
    for nm in ("Praca", "Sudoeste", "OesteAlta", "Mirante"):
        DL.plan_stair(mb, nm, stringers=False)
        foot, deg, w, n, tread, g = L.stair_frame(nm)
        rise = L.stair_rise(nm)
        F = Frame(foot[0], foot[1], foot[2], math.radians(deg))
        for s in (-1, 1):                                  # = op_lib.plan_stair(stringers=True)
            for i in range(n):
                h = rise * (i + 1) + 1.0
                ms.box((tread + 0.05, 1.2, h), F.p(tread * i + tread / 2, s * (w / 2 + 0.6), rise * (i + 1) + 1.0 - h / 2),
                       F.r(), "Stone_OP", 0.0)
    mb.finish()
    K.cull_hidden(ms)
    ms.finish()


# ================================================================== cameras das folhas (fora do export)
# posicoes das capturas do usuario (rodada 3) + de cima (camera do jogo com zoom-out) + altura do jogador
R3_CAMS = {
    "CAM_OP_R3Cap_S01_BordaPraca": ((126.0, 112.0, T1 + 22.0), (40.0, 170.0, P), 16),
    "CAM_OP_R3Cap_S02_PortoAlto": ((140.0, 20.0, T1 + 10.0), (165.0, 90.0, L.HMID), 16),
    "CAM_OP_R3Cap_S05_VielaLeste": ((50.0, 112.0, T1 + 12.0), (130.0, 108.0, T1 + 2.0), 16),
    "CAM_OP_R3Cap_S06_PatioAvO": ((-38.5, 45.0, T1 + 6.0), (-38.5, 80.0, T1 + 5.0), 16),
    "CAM_OP_R3Cap_S08_EscadaPraca": ((20.0, 112.0, T1 + 12.0), (-30.0, 140.0, P + 2.0), 16),
    "CAM_OP_R3Cap_S09_OesteAlta": ((-104.0, 270.0, P + 18.0), (-112.0, 310.0, L.W3), 16),
    "CAM_OP_R3Cap_S17_CaminhoW3": ((-112.0, 330.0, L.W3 + 40.0), (-115.0, 331.0, L.W3), 20),
    "CAM_OP_R3Cap_Cima_Avenida": ((0.0, 20.0, T1 + 38.0), (0.0, 80.0, T1 + 4.0), 20),
    "CAM_OP_R3Cap_Cima_Bairro": ((-60.0, 40.0, T1 + 36.0), (-120.0, 86.0, T1 + 4.0), 20),
    "CAM_OP_R3Cap_Cima_Oeste": ((-95.0, 170.0, P + 34.0), (-150.0, 215.0, P + 4.0), 20),
    "CAM_OP_R3Cap_Cima_AlemCanal": ((-150.0, 150.0, P + 36.0), (-200.0, 210.0, P + 4.0), 20),
    "CAM_OP_R3Cap_Cima_PortoAlto": ((60.0, 125.0, T1 + 34.0), (95.0, 85.0, T1 + 4.0), 20),
    "CAM_OP_R3Cap_Cima_NE": ((125.0, 255.0, P + 34.0), (165.0, 290.0, P + 4.0), 20),
    "CAM_OP_R3Cap_Aerea_Cidade": ((60.0, -60.0, 240.0), (-60.0, 160.0, 90.0), 24),
    "CAM_OP_R3Cap_Jog_Avenida": ((3.0, 47.0, T1 + 0.47 + L.EYE), (-4.0, 110.0, T1 + 9.0), 22),
    "CAM_OP_R3Cap_Jog_VielaCanal": ((-20.0, 86.0, T1 + L.EYE), (-100.0, 86.0, T1 + 6.0), 22),
    "CAM_OP_R3Cap_Jog_Bairro": ((-140.0, 111.0, T1 + L.EYE), (-70.0, 111.0, T1 + 6.0), 22),
    "CAM_OP_R3Cap_Jog_Oeste": ((-113.0, 128.0, P + L.EYE), (-121.0, 190.0, P + 7.0), 22),
    "CAM_OP_R3Cap_Jog_Cais": ((-164.0, 126.0, P + L.EYE), (-164.0, 200.0, P + 6.0), 22),
    "CAM_OP_R3Cap_Jog_Sando": ((112.0, 296.0, P + L.EYE), (190.0, 300.0, P + 7.0), 22),
    "CAM_OP_R3Cap_Jog_PortoAlto": ((60.0, 111.0, T1 + L.EYE), (120.0, 108.0, T1 + 7.0), 22),
    # closes: muro da avenida, beco do bairro, muro da praca oeste, patio de fundos, guia com a grama, vao do porto
    "CAM_OP_R3Cap_Det_MuroAvenida": ((-8.0, 44.0, T1 + 0.47 + L.EYE), (-17.0, 51.0, T1 + 3.0), 24),
    "CAM_OP_R3Cap_Det_BecoBairro": ((-85.0, 83.0, T1 + L.EYE), (-85.0, 110.0, T1 + 3.0), 24),
    "CAM_OP_R3Cap_Det_MuroOeste": ((-110.0, 168.0, P + L.EYE), (-121.0, 177.0, P + 3.0), 24),
    "CAM_OP_R3Cap_Det_PatioOeste": ((-141.0, 157.0, P + 16.0), (-141.0, 195.0, P + 2.0), 22),
    "CAM_OP_R3Cap_Det_GuiaW3": ((-111.0, 318.0, L.W3 + 4.5), (-118.0, 326.0, L.W3), 24),
    "CAM_OP_R3Cap_Det_VaoPorto": ((78.0, 114.0, T1 + L.EYE), (78.0, 98.0, T1 + 3.0), 24),
    "CAM_OP_R3Cap_Det_BordaPraca": ((74.0, 107.0, T1 + L.EYE), (84.0, 120.0, P + 0.5), 24),
}


def cams():
    for nm, (a, b, lens) in R3_CAMS.items():
        fm_lib.camera(nm, Vector(a), Vector(b), lens)
        if "_Jog_" in nm:                              # boneco de 5 a ~15 a frente (escala nas folhas)
            dx, dy = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(dx, dy) or 1.0
            x, y = a[0] + dx / ln * 15.0 + dy / ln * 2.6, a[1] + dy / ln * 15.0 - dx / ln * 2.6
            zz = L.zone_of(x, y)
            if zz is not None:
                DL.dummy("SCALE_Dummy_Cap_" + nm.split("_Jog_")[1], x, y, zz + STREET_DZ, math.atan2(dy, dx) + math.pi / 2)
    return list(R3_CAMS)


def interior_cams(specs):
    """1 camera por interior vivo: da rua/sando, na altura do olho, olhando para dentro do vao aberto + boneco de 5"""
    out = []
    for s in specs:
        lt = s["lot"]
        if not lt["interior"]:
            continue
        kw, F = s["kw"], s["F"]
        W, D = kw["W"], kw["D"]
        if s["fn"] is K2.loja:
            xs, sp = K2._posts_x(W, K2.loja_bays(W, kw["shop_side"], True))
            a, b = [(a, b) for t, o, a, b in sp if t == "shop"][0]
            xc, zf, Fc = (a + b) / 2, 0.8, F
        elif s["fn"] is K2.chaya:
            gs, gw = kw["garden_side"], kw["garden_w"]
            Fc = K2.sub(F, -gs * gw / 2)
            xs, sp = K2._posts_x(W - gw, K2.chaya_bays(W - gw, gs))
            a, b = [(a, b) for t, o, a, b in sp if t == "open"][0]
            xc, zf = (a + b) / 2, 1.45
        else:
            xc, zf, Fc = 0.0, 1.6, F
        nm = "CAM_OP_R3Cap_Int_" + lt["name"]
        fm_lib.camera(nm, Fc.p(xc + 0.8, D / 2 + 6.5, L.EYE + 0.5), Fc.p(xc, D / 2 - 6.0, zf + 2.6), 26)
        DL.dummy("SCALE_Dummy_Cap_" + lt["name"], *Fc.p(xc + 1.0, D / 2 - 4.2, zf)[:], F.a)
        out.append(nm)
    return out


# ================================================================== montagem
def build():
    t0 = time.time()
    del VEG_SPOTS[:]
    lots = L.block_lots()
    specs = plan(lots)
    infos, probs, objs = build_lots(specs)
    ncol = lot_collisions(specs, infos)
    pl = streets(lots)
    nm_ = fences(pl, specs)
    ncol += nm_
    ncol += props(lots)
    edge_rails(lots)
    stairs()
    inner = [L.lot_poly(lt, 1.5) for lt in lots if lt["interior"]]

    def g_at(p):                                      # interiores vivos: bolso de 0,5 (o jogador entra)
        return 0.5 if any(L.point_in_poly(p.x, p.y, q) for q in inner) else 99.0
    STATS["bolsos"] = K2.cull_pockets([o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("OP_Cap_")],
                                      ("OP_Ter_",), tag="op_capital", g_at=g_at, under=True)
    cams()
    interior_cams(specs)
    tri = 0
    parts = {}
    for o in bpy.data.objects:
        if o.type == "MESH" and o.name.startswith("OP_Cap_"):
            t = sum(len(p.vertices) - 2 for p in o.data.polygons)
            tri += t
            parts[o.name] = t
    by_kind = {}
    for s in specs:
        k = s["lot"]["kind"]
        by_kind.setdefault(k, []).append(STATS["tris_lote"][s["lot"]["name"]])
    print("op_capital R3: %d casas soltas, %d tris (cull -%d, dentro -%d), colisoes %d (muros %d), lajes %d em %d "
          "regioes (guias %s, %.1fs), pares testados %d, %.1fs" % (
              len(specs), tri, STATS["cull"], STATS.get("cull_in", 0), ncol, nm_, STATS["lajes"], STATS["regioes"],
              STATS["guias"], STATS["t_ruas"], STATS["pares"], time.time() - t0))
    print("op_capital: tris por objeto: " + ", ".join("%s %d" % (k, v) for k, v in sorted(parts.items(), key=lambda t: -t[1])))
    print("op_capital: tris por tipo (antes do cull): " + ", ".join(
        "%s %d x ~%d" % (k, len(v), sum(v) / len(v)) for k, v in sorted(by_kind.items())))
    print("op_capital: guarda-corpos visiveis nas bordas abertas: %d trechos, %d studs" % STATS["guarda"])
    print("op_capital: menores folgas de beiral entre vizinhos: %s" % STATS["folgas"][:8])
    if os.environ.get("OP_CAP_LOTES") == "1":
        for s in sorted(specs, key=lambda s: -STATS["tris_lote"][s["lot"]["name"]]):
            print("op_capital lote %-14s %-9s lod %d tris %5d" % (s["lot"]["name"], s["lot"]["kind"], s["kw"]["lod"],
                                                                  STATS["tris_lote"][s["lot"]["name"]]))
    if probs:
        for p in probs[:40]:
            print("op_capital INTERPENETRACAO %s %s x %s n=%d em %s" % p)
        msg = "op_capital: FAIL interpenetracao/beiral entre casas: %d problemas em %d pares testados" % (
            len(probs), STATS["pares"])
        print(msg)
        if os.environ.get("OP_CAP_SOFT") != "1":
            raise RuntimeError(msg)
    else:
        print("op_capital: OK casas soltas: 0 interseccao, beirais a >= %.1f (%d pares vizinhos testados malha x malha)"
              % (CLEAR_MIN, STATS["pares"]))
    return dict(specs=specs, infos=infos, probs=probs, plan=pl)
