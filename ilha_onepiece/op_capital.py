# op_capital.py - V2-3 da Ilha 5 (ONE PIECE / WANO): a CAPITAL inteira com o KIT V2 (op_kit2, aprovado no gate V2-1
# com UMA correcao: "os modelos estao vindo dentro um do outro"). Zona "capital" do build_op (ZONE_MODULES_V2_0).
# Prefixo OP_Cap_, colecao 05_CAPITAL. Le SO a planta V2 (op_layout: ROWS -> block_lots(), STREETS_V2, AVENUE, NE) e
# SO o op_kit2 (o op_kit V1 so empresta o cull_hidden). O trecho M2 (op_m2_trecho.build) foi ABSORVIDO: a quadra AvO
# da avenida E a quadra-modelo; o op_m2_trecho.build() nao roda mais (o build_praca dele continua sendo do agente da
# praca via op_m2_praca - nada aqui depende da zona plaza).
#
# ZERO INTERPENETRACAO (PLANO_V2 3.2 "parede-meia, sem frestas" + feedback 10/10 G2):
#   * cada edificio cabe no SEU lote: o lote geminado e construido com W - SEAM (0,03 de cada lado) e o kit CORTA na
#     divisa tudo o que passaria para o vizinho (soco, frechal, hisashi, saia mokoshi, beiral/aba do telhado, udatsu,
#     molduras): a lateral encostada vira PAREDE-MEIA de reboco rente a divisa e a empena cortada vira empena de divisa
#     (op_kit2.party_clip / roof2(clip) / pent2(clip) / skirt2(clip));
#   * fundos encostados (fileiras de costas uma para a outra) e laterais com predio a < 6: o telhado corta na metade
#     da distancia (back / lim);
#   * TESTE AUTOMATICO malha x malha (BVHTree.overlap) entre todos os edificios vizinhos (caixas que se tocam) + todo
#     vertice de um edificio dentro do lote do outro tem de ficar >= 0,12 ACIMA do telhado dele (sobreposicao so por
#     cima). O build REPROVA (RuntimeError) se houver 1 interseccao (OP_CAP_SOFT=1 so avisa: uso de bancada).
# CIDADE: 101 lotes em 12 quadras; tipo/pisos/flags da planta, variedade dirigida (cor por quadra com ~1 lote em 5 na
#   cor vizinha, altura do hash da planta, shop_side/upper/toldo/tsuma alternados: nunca a mesma casa lado a lado na
#   mesma rotacao), 4 interiores vivos (flag 'i'), o resto com vitrine rasa. Avenida com o street2 (leito assentado,
#   sarjeta, meio-fio, calcadas); vielas/cais/sando em pedra assentada por grade (lajes so na face de cima). Andon do
#   kit2 nos nos das ruas, 6 toro no sando, torii do santuario com 2 nobori (U16: as unicas bandeiras daqui).
# ORCAMENTO (PLANO_V2 10 / lead): <= 195k tris, <= 140 MeshParts (1 MB por SETOR de quadras e por material, lod 1 nas
#   fileiras de tras, cull_hidden por setor), colisoes por VOLUME DE FILEIRA (1 caixa por trecho continuo de lotes ate
#   o frechal mais baixo) + interiores + props; nada de rampa de telhado (o gate 'visual' prova que nao se alcanca).
# LUZES: interiores de dia L_OPCap_Int_* (4), resto NightOnly (L_OPProp_*).
# CAMERAS: CAM_OP_V23Cap_* (folhas; fora do export).
import math, os, time
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import op_lib as DL
from op_lib import MB, col_box, col_ramp, Frame, ccw, light
import fm_lib
import op_layout as L
import op_kit2 as K2
import op_kit as K
import op_col

COLL = "05_CAPITAL"
T1, P = L.T1, L.P
SEAM = 0.06               # fresta total entre 2 lotes geminados (0,03 de cada lado: nada se toca, nada se cruza)
STREET_DZ = 0.2           # topo das lajes acima do piso de colisao (berco a +0,08: 0,12 de cada lado, sem z-fight)
GAP_EPS = 0.3             # lateral a menos disto de outro lote = encostada (parede-meia)
NEAR = 6.0                # predio a menos disto: o telhado corta na metade da distancia
REGION = {"AvO": "Avenida", "AvL": "Avenida", "PortoAlto1": "Avenida", "PortoAlto2": "Avenida",
          "BairroN": "Bairro", "BairroS": "Bairro", "OesteS": "Oeste", "OesteM": "Oeste", "OesteN": "Oeste",
          "AlemCanal": "Oeste", "W3": "Oeste", "NE": "NE"}
# fileiras que o jogador ve de perto (avenida, fachada da praca, sando): lod 0; o resto lod 1
HERO_ROWS = {("AvO", "F1"), ("AvO", "F2"), ("AvL", "F1"), ("NE", "Haiden"), ("NE", "Honden")}
BACK_ROWS = {("AvO", "B1"), ("AvO", "B2"), ("AvL", "B1"), ("BairroS", "B1"), ("OesteS", "B"), ("OesteM", "B1"),
             ("OesteM", "B2"), ("OesteN", "B"), ("PortoAlto1", "B"), ("PortoAlto2", "B"), ("W3", "M1"), ("W3", "M2"),
             ("AlemCanal", "F1"), ("AlemCanal", "F2"), ("BairroN", "F1"), ("BairroN", "M"), ("BairroS", "F1"),
             ("PortoAlto1", "F"), ("PortoAlto2", "F")}
SECOND = {L.R_COB: L.R_TEAL, L.R_TEAL: L.R_COB, L.R_VIO: L.R_COB, L.R_RED: L.R_VIO, L.R_GRN: L.R_TEAL}
INTERIOR_LIGHT = {"AvO_F14": "L_OPCap_Int_LojaTecidos", "AvL_F15": "L_OPCap_Int_Izakaya",
                  "OesteM_F21": "L_OPCap_Int_Cha", "NE_Haiden1": "L_OPCap_Int_Haiden"}
SUMMON_RECT = (116.0, 150.0, 206.0, 264.0)       # lajeado do op_summon (as ruas 16-18 da planta sao dele)
STATS = {}


def h01(*a):
    return K._h01(*a)


# ================================================================== vizinhanca dos lotes
def _lot_frame(lt, setback=0.0):
    """referencial do EDIFICIO: centro da planta (recuado setback/2 do fundo), no chao, +y = frente"""
    c, s = math.cos(lt["yaw"]), math.sin(lt["yaw"])
    return Frame(lt["x"] + c * setback / 2, lt["y"] + s * setback / 2, lt["z"], lt["yaw"] - math.pi / 2)


def _local(lt, x, y):
    """mundo -> local do lote (x ao longo da fachada, y para a frente)"""
    c, s = math.cos(lt["yaw"]), math.sin(lt["yaw"])
    dx, dy = x - lt["x"], y - lt["y"]
    return dx * s * 1.0 - dy * c * 1.0, dx * c + dy * s


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
    """por lote: lados encostados (parede-meia), limite de corte das laterais expostas e do fundo quando ha predio a
    menos de NEAR (metade da distancia; se o outro mostra a FRENTE, distancia - FRONT_REACH)"""
    out = {}
    polys = {lt["name"]: L.lot_poly(lt) for lt in lots}
    for lt in lots:
        W, D = lt["W"], lt["D"]
        R = (W + D) / 2 + NEAR + 2.0
        cands = [(o, polys[o["name"]]) for o in lots if o is not lt and
                 math.hypot(o["x"] - lt["x"], o["y"] - lt["y"]) < R + (o["W"] + o["D"]) / 2]
        res = dict(party=[False, False], lim=[None, None], back=None, back_gap=None, nb=set())
        vs = (-D / 2 + 0.8, -D / 4, 0.0, D / 4, D / 2 - 0.8)
        for k, sx in enumerate((-1, 1)):
            m = _march(cands, lt, [(sx * W / 2, v) for v in vs], sx, 0.0)
            if m:
                d, o, face = m
                res["nb"].add(o["name"])
                if d <= GAP_EPS:
                    res["party"][k] = True
                else:
                    res["lim"][k] = W / 2 + (d - FRONT_REACH if face == "front" else d / 2) - 0.03
            # piso MAIS ALTO alcancavel (terraco, mirante) a 6..9: o beiral fica a > 6 dele (fora do alcance do pulo)
            if not res["party"][k]:
                dh = _march_high(lt, [(sx * W / 2, v) for v in vs], sx, 0.0)
                if dh is not None and dh > 6.2:
                    lk = W / 2 + dh - 6.2
                    res["lim"][k] = lk if res["lim"][k] is None else min(res["lim"][k], lk)
        us = (-W / 2 + 0.6, -W / 4, 0.0, W / 4, W / 2 - 0.6)
        m = _march(cands, lt, [(u, -D / 2) for u in us], 0.0, -1.0)
        if m:
            d, o, face = m
            res["nb"].add(o["name"])
            res["back_gap"] = 0.0 if d <= GAP_EPS else d
            res["back"] = D / 2 + (d - FRONT_REACH if face == "front" else d / 2) - 0.03
        out[lt["name"]] = res
    return out


# ================================================================== lote -> chamada do kit
def _dh(lt):
    return lt["eave"] - lt["z"] - L.EAVE_H.get((lt["kind"], lt["floors"]), 8.8 + 6.0 * (lt["floors"] - 1))


def plan(lots):
    nbs = neighbors(lots)
    specs = []
    for lt in lots:
        nb = nbs[lt["name"]]
        sides = (not nb["party"][0], not nb["party"][1])
        kind = lt["kind"]
        seed = int(h01(lt["name"], "seed") * 9973)
        dh = _dh(lt)
        roof = lt["roof"]
        if lt["roof"] == L.ROWS[[r[0] + r[1] for r in L.ROWS].index(lt["block"] + lt["row"])][7] and kind not in (
                "portal", "santuario", "honden") and h01(lt["name"], "cor") < 0.2:
            roof = SECOND.get(roof, roof)
        setback = 0.4 if (nb["back_gap"] is not None and nb["back_gap"] < 0.5) else 0.0
        if kind in ("kura", "armazem") and setback:
            setback = 0.6
        Wb, Db = lt["W"] - SEAM, lt["D"] - setback
        back = None
        if nb["back"] is not None:                       # limite do fundo no referencial do EDIFICIO (recuado)
            back = max(Db / 2, nb["back"] + setback / 2)
        lim = tuple((max(Wb / 2, v - SEAM / 2) if v is not None else K2.BIG) for v in nb["lim"])
        lod = 0 if (lt["block"], lt["row"]) in HERO_ROWS else (2 if (lt["block"], lt["row"]) in BACK_ROWS else 1)
        if kind == "esquina" or lt["interior"]:
            lod = 1 if kind == "esquina" else 0             # interiores vivos sempre lod 0; esquinas lod 1
        hide_back = nb["back_gap"] is not None and nb["back_gap"] < 1.0
        lname = INTERIOR_LIGHT.get(lt["name"]) if lt["interior"] else None
        kw = dict(W=Wb, D=Db, roof_m=roof, lod=lod, seed=seed, back=back, lim=lim)
        if kind in ("loja", "sobrado", "esquina", "fundo", "moinho", "chaya", "mansao") and hide_back:
            kw["hide_back"] = True
        zw = None
        if kind == "loja":
            kw.update(sides=sides, tsuma=lt["tsuma"], shop_side=1 if h01(lt["name"], "ss") < 0.5 else -1,
                      upper=("mushiko", "shoji", "double")[int(h01(lt["name"], "up") * 3)],
                      awning=h01(lt["name"], "aw") < 0.3, roof="irimoya" if (not lt["tsuma"] and
                                                                              h01(lt["name"], "iri") < 0.15) else "kirizuma",
                      h0=9.0 + 0.4 * dh, h1=7.0 + 0.6 * dh, interior=lt["interior"], light_name=lname)
            fn, zw = K2.loja, 0.8 + kw["h0"] + kw["h1"]
        elif kind == "sobrado":
            kw.update(sides=sides, shop=h01(lt["name"], "sh") < 0.5, rail_m=K2.LAC if h01(lt["name"], "rl") < 0.5
                      else K2.WD, h0=8.6 + 0.3 * dh, h1=7.0 + 0.3 * dh, h2=6.4 + 0.4 * dh, chidori=lod == 0)
            kw["top"] = "irimoya" if lod < 2 else "yosemune"
            fn, zw = K2.sobrado, 0.8 + kw["h0"] + kw["h1"]
        elif kind == "esquina":
            if sides[0] and sides[1]:
                corner, solo = (1 if h01(lt["name"], "c") < 0.5 else -1), True
            else:
                corner, solo = (1 if sides[1] else -1), False
            kw.update(corner=corner, solo=solo, tower_m=SECOND.get(roof, L.R_COB), h0=9.0 + 0.4 * dh,
                      h1=7.0 + 0.6 * dh, light_name=lname)
            fn, zw = K2.esquina, 0.8 + kw["h0"] + kw["h1"]
        elif kind in ("kura", "armazem"):
            kw.update(sides=sides, tsuma=lt["tsuma"] if kind == "kura" else False,
                      h=(12.5 if kind == "kura" else 13.6) + dh, crest=lod == 0)
            fn, zw = K2.kura, 1.4 + kw["h"]
        elif kind == "chaya":
            gs = 1 if (sides[1] and not sides[0]) else (-1 if (sides[0] and not sides[1]) else
                                                       (1 if h01(lt["name"], "gs") < 0.5 else -1))
            kw.update(sides=sides, garden_side=gs, garden_w=4.0, light_name=lname, h0=9.0, h1=6.8)
            fn, zw = K2.chaya, 1.0 + 9.0
        elif kind == "mansao":
            kw.update(sides=sides)
            fn, zw = K2.mansao2, 0.8 + 8.6 + 7.0
        elif kind in ("fundo", "moinho"):
            kw.update(sides=sides, tsuma=(lt["tsuma"] or h01(lt["name"], "ts") < 0.35 or kind == "moinho"),
                      h0=(9.0 if kind == "moinho" else 8.0) + max(0.0, dh), hisashi=lt["hisashi"])
            kw["lod"] = 2                      # fundos = Tier B (PLANO_V2 3.2): sempre lod 2 (telha ondulada mantida)
            fn, zw = K2.fundo, 0.6 + kw["h0"]
        elif kind == "portal":
            kw.update(sides=sides, h=lt["eave"] - lt["z"])
            fn, zw = K2.portal2, kw["h"]
        elif kind == "santuario":
            kw.update(sides=sides, light_name=lname)
            fn, zw = K2.haiden2, 1.6 + 9.0
        elif kind == "honden":
            kw.update(sides=sides)
            fn, zw = K2.honden2, 7.0
        else:
            raise RuntimeError("op_capital: tipo sem kit: %s" % kind)
        specs.append(dict(lot=lt, fn=fn, kw=kw, F=_lot_frame(lt, setback), zw=zw, sides=sides, nb=nb,
                          region=REGION[lt["block"]], setback=setback))
    _variety(specs)
    return specs


def _sig(s):
    kw = s["kw"]
    return (s["fn"].__name__, kw.get("tsuma"), kw.get("shop_side"), kw.get("upper"), kw.get("roof"))


def _variety(specs):
    """nunca a mesma casa lado a lado na mesma rotacao: vizinho de fileira com a mesma assinatura troca o lado da
    loja e o 2o piso (ou vira tsumairi)"""
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
                elif "tsuma" in kw:
                    kw["tsuma"] = not kw["tsuma"]


# ================================================================== geometria por lote + teste de interpenetracao
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
    """TESTE malha x malha entre edificios vizinhos: (1) interseccao de triangulos (BVHTree.overlap) e (2) vertice de
    um edificio dentro do lote do outro que nao esteja >= 0,12 ACIMA da malha dele. -> lista de problemas"""
    probs = []
    n_pairs = 0
    names = [s["lot"]["name"] for s in specs]
    polys = {s["lot"]["name"]: L.lot_poly(s["lot"], -0.01) for s in specs}
    for i in range(len(specs)):
        gi = geos[names[i]]
        if gi is None:
            continue
        for j in range(i + 1, len(specs)):
            gj = geos[names[j]]
            if gj is None or not _bb_hit(gi["bb"], gj["bb"]):
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
    STATS["pares"] = n_pairs
    return probs


# ================================================================== montagem dos lotes
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


CULL_IN = {K2.loja: 4.0, K2.sobrado: 4.0, K2.fundo: 0.7, K2.kura: 0.7}   # recuo da frente do terreo (vitrine)


def cull_inside(mb, s):
    """apaga as faces DENTRO do volume fechado da casa (frente/fundos/laterais + forro do frechal): paredes,
    pilares e soleiras vistos por dentro. So nas casas fechadas (sem interior vivo; a vitrine da loja fica: o terreo
    so e cortado atras dela). -> tris cortados"""
    if s["lot"]["interior"] or s["fn"] not in CULL_IN:
        return 0
    F, kw = s["F"], s["kw"]
    W, D = kw["W"], kw["D"]
    ins = 0.7
    z0, zw = F.o.z + 0.3, F.o.z + s["zw"] - 0.05
    zg = F.o.z + 0.8 + kw.get("h0", 8.0)              # topo do terreo
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
    n = sum(len(f.verts) - 2 for f in kill)
    bmesh.ops.delete(mb.bm, geom=kill, context="FACES")
    return n


def build_lots(specs):
    regions = {}
    geos, infos = {}, {}
    tris = {}
    for s in specs:
        lt = s["lot"]
        mb = MB("OP_Cap_tmp_" + lt["name"], COLL)
        info = s["fn"](mb, s["F"], **s["kw"])
        STATS["cull_in"] = STATS.get("cull_in", 0) + cull_inside(mb, s)
        infos[lt["name"]] = info
        geos[lt["name"]] = _geo(mb)
        tris[lt["name"]] = sum(len(f.verts) - 2 for f in mb.bm.faces)
        rg = regions.get(s["region"])
        if rg is None:
            rg = regions[s["region"]] = MB("OP_Cap_Q_" + s["region"], COLL)
        _merge(rg, mb)
    probs = interpen(specs, geos)
    STATS["tris_lote"] = tris
    cut = 0
    objs = []
    for nm, rg in regions.items():
        cut += K.cull_hidden(rg, dmax=6.0)
        objs.append(rg.finish())
    STATS["cull"] = cut
    return infos, probs, objs


# ================================================================== colisao por volume de fileira
def _col_lot_box(area, F, x0, x1, y0, y1, z0, z1):
    col_box(area, (x1 - x0, y1 - y0, z1 - z0), F.p((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), F.r())


def _interior_cols(s, area):
    """lote com interior vivo: piso, paredes, o vao de entrada livre e o teto (o jogador entra e sai pela frente)"""
    lt, kw, F = s["lot"], s["kw"], s["F"]
    W, D = kw["W"], kw["D"]
    zw = s["zw"]
    n = 0
    if s["fn"] is K2.loja:
        z0 = 0.8
        kw_ = 3.0 if W >= 13.0 else 0.0
        bays = ([("koshi", kw_)] if kw_ else []) + [("door", 4.4), {"t": "shop", "upper_board": True}]
        if kw["shop_side"] < 0:
            bays = list(reversed(bays))
        xs, sp = K2._posts_x(W, bays)
        a, b = [(a, b) for t, o, a, b in sp if t == "shop"][0]
        yf = D / 2 - 0.86
        depth = min(7.5, D * 0.5)
        yb = yf - depth
        ya = yb + depth * 0.52
        _col_lot_box(area, F, -W / 2, W / 2, -D / 2, yb, -0.5, zw)                      # fundos (macico)
        _col_lot_box(area, F, -W / 2, a, yb, D / 2 + 0.35, -0.5, zw)                    # parede/porta a esquerda
        _col_lot_box(area, F, b, W / 2, yb, D / 2 + 0.35, -0.5, zw)                     # parede a direita
        _col_lot_box(area, F, a, b, yb, D / 2 + 0.35, 7.0 + z0, zw)                     # verga + 2o piso
        _col_lot_box(area, F, a, b, yb, D / 2 + 0.35, -0.5, z0)                         # piso de terra (doma)
        _col_lot_box(area, F, a, b, yb, ya, z0, z0 + 1.15)                              # estrado (agari)
        n += 6
    elif s["fn"] is K2.chaya:
        gs = kw["garden_side"]
        gw = kw["garden_w"]
        Wb = W - gw
        xb_ = -gs * gw / 2
        eng = 3.0
        z0 = 1.0
        Fb = K2.sub(F, xb_)
        xs, sp = K2._posts_x(Wb, K2.chaya_bays(Wb, gs))
        a, b = [(a, b) for t, o, a, b in sp if t == "open"][0]
        yf = D / 2 - eng                                   # face da frente do corpo (no referencial Fb)
        yb = yf - 0.86 - 6.6
        _col_lot_box(area, Fb, -Wb / 2, Wb / 2, -D / 2, yb, -0.5, zw)
        _col_lot_box(area, Fb, -Wb / 2, a, yb, yf, -0.5, zw)
        _col_lot_box(area, Fb, b, Wb / 2, yb, yf, -0.5, zw)
        _col_lot_box(area, Fb, a, b, yb, yf, 7.0 + z0, zw)
        _col_lot_box(area, Fb, -Wb / 2, Wb / 2, yb, D / 2 + 0.35, -0.5, z0 + 0.45)        # engawa + tatami
        xg0, xg1 = (W / 2 - gw, W / 2) if gs > 0 else (-W / 2, -W / 2 + gw)
        _col_lot_box(area, F, xg0, xg1, -D / 2, D / 2, -0.5, zw + 0.4)                    # jardim cercado (alto:
        n += 6                                                                           # nao vira degrau)
    elif s["fn"] is K2.haiden2:
        ph = 1.6
        Do = D * 0.45
        yi = D / 2 - Do
        _col_lot_box(area, F, -W / 2, W / 2, -D / 2, yi, -0.5, zw + 0.5)                   # santuario interno
        _col_lot_box(area, F, -W / 2, W / 2, yi, D / 2, -0.5, ph)                          # assoalho
        for sx in (-1, 1):                                                               # guardas laterais
            x0, x1 = sorted((sx * (W / 2 - 0.9), sx * W / 2))
            _col_lot_box(area, F, x0, x1, yi, D / 2, ph, zw)
        _col_lot_box(area, F, -W / 2, W / 2, yi, D / 2, zw - 0.4, zw + 0.5)               # forro/telhado
        _col_lot_box(area, F, -1.9, 1.9, yi + 0.9, yi + 2.3, ph, zw - 0.4)                # caixa de oferendas
        for x in (-W / 4, W / 4):                                                        # pilares da frente
            _col_lot_box(area, F, x - 0.45, x + 0.45, D / 2 - 1.05, D / 2 - 0.15, ph, zw - 0.4)
        for i in range(1, 5):                                                            # escada
            zz = ph - 0.32 * i
            y0 = D / 2 + 0.4 * (i - 1) - 0.05
            _col_lot_box(area, F, -3.6, 3.6, y0, y0 + 0.45, -0.5, zz)
        n += 12
    return n


def _reach_src(lt, d_max=6.0):
    """maior piso ALCANCAVEL (planta) num anel de ate d_max em volta do lote, acima do piso do proprio lote"""
    best = None
    for d in (1.0, 2.5, 4.0, 5.5, 7.0, 8.5):
        if d > d_max:
            break
        poly = L.lot_poly(lt, d)
        for (ax, ay), (bx, by) in zip(poly, poly[1:] + poly[:1]):
            n = max(2, int(math.hypot(bx - ax, by - ay) / 1.5))
            for i in range(n):
                x, y = ax + (bx - ax) * i / n, ay + (by - ay) * i / n
                z = L.zone_of(x, y)
                if z is not None and z > lt["z"] + 0.3 and (best is None or z > best):
                    best = z
    return best


def _roof_ramps(s, info, area):
    """telhado ao alcance: 1 rampa por agua principal (corda beiral -> cumeeira 0,35 abaixo da telha), cortada como o
    telhado (clip)"""
    r = info.get("roof")
    if not r:
        return 0
    Fr = r["F"]
    cl = r["clip"]
    n = 0
    if r["kind"] in ("kirizuma", "irimoya", "yosemune"):
        xa, xb = max(-r["Xe"], -cl[0]), min(r["Xe"], cl[1])
        for sg, ye in ((1, min(r["Ye"], cl[3])), (-1, min(r["Ye"], cl[2]))):
            za = r["Hf"](0.0, ye) - 0.35
            zb = r["zr"] - 0.35
            col_ramp(area, Fr.p((xa + xb) / 2, sg * ye, za), Fr.p((xa + xb) / 2, 0.0, zb), xb - xa, thick=1.2)
            n += 1
    return n


def lot_collisions(specs, infos):
    """1 caixa por TRECHO CONTINUO de lotes de cada fileira com frechal parecido (ate o frechal mais baixo do trecho),
    interiores/portal/honden a parte, rampas nos telhados ao alcance de um piso mais alto (terraco, mirante) e as
    calcadas da avenida. A caixa vai do fundo ao soco da frente (+0,35)."""
    n = 0
    rows = {}
    for s in specs:
        rows.setdefault((s["lot"]["block"], s["lot"]["row"]), []).append(s)
    for key, ss in rows.items():
        seg = []

        def flush(seg):
            if not seg:
                return 0
            lt0 = seg[0]["lot"]
            us = []
            for s in seg:
                for u in (-s["lot"]["W"] / 2, s["lot"]["W"] / 2):
                    x, y = _world(s["lot"], u, 0.0)
                    us.append(_local(lt0, x, y)[0])
            D = lt0["D"]
            zt = min(s["zw"] for s in seg) - 0.3
            F = Frame(lt0["x"], lt0["y"], lt0["z"], lt0["yaw"] - math.pi / 2)
            # ponta EXPOSTA do trecho: a caixa cobre tambem o soco (0,35-0,5 alem da parede)
            ext = [0.0, 0.0]
            for s in seg:
                for k, u in enumerate((-s["lot"]["W"] / 2, s["lot"]["W"] / 2)):
                    x, y = _world(s["lot"], u, 0.0)
                    uu = _local(lt0, x, y)[0]
                    if not s["nb"]["party"][k] and s["lot"]["kind"] in ("kura", "armazem"):   # soco alto (1,4)
                        if abs(uu - min(us)) < 0.05:
                            ext[0] = 0.6
                        if abs(uu - max(us)) < 0.05:
                            ext[1] = 0.6
            _col_lot_box("OP_CapRow" + key[0] + key[1], F, min(us) - ext[0], max(us) + ext[1], -D / 2, D / 2 + 0.35, -0.5,
                         zt)
            return 1
        for s in ss:
            k = s["lot"]["kind"]
            if s["lot"]["interior"] or k in ("portal", "santuario", "honden"):
                n += flush(seg)
                seg = []
                area = "OP_CapLot" + s["lot"]["name"]
                W, D = s["kw"]["W"], s["kw"]["D"]
                if k == "portal":
                    _col_lot_box(area, s["F"], -W / 2, W / 2, -D / 2, D / 2, 7.4, s["zw"])
                    n += 1
                elif k == "honden":
                    _col_lot_box(area, s["F"], -W / 2, W / 2, -D / 2, D / 2, -0.5, s["zw"] + 1.0)
                    n += 1
                else:
                    n += _interior_cols(s, area)
                continue
            seg.append(s)
        n += flush(seg)
    # telhados ao alcance de um piso mais alto (terraco W3, mirante NE)
    reach = []
    for s in specs:
        src = _reach_src(s["lot"])
        info = infos[s["lot"]["name"]]
        if src is not None and src + L.JUMP + 0.5 >= s["lot"]["z"] + 7.4:
            n += _roof_ramps(s, info, "OP_CapRoof" + s["lot"]["name"])
            reach.append(s["lot"]["name"])
    STATS["telhados_rampa"] = reach
    # calcadas da avenida (o pe nao afunda 0,47)
    av = L.AVENUE
    y0, y1 = av["y"]
    for sg in (-1, 1):
        xa, xb = sorted((sg * (av["x"][1] + 0.3), sg * av["front"]))
        col_box("OP_CapCalcada", (xb - xa, y1 - y0, 0.5), ((xa + xb) / 2, (y0 + y1) / 2, T1 + 0.47 - 0.25))
        n += 1
    return n


# ================================================================== ruas
def _in_rect(x, y, r, pad=0.0):
    return r[0] - pad <= x <= r[2] + pad and r[1] - pad <= y <= r[3] + pad


def _blocked(x, y, lots_poly, stairs_poly):
    for p in lots_poly:
        if L.point_in_poly(x, y, p):
            return True
    for p in stairs_poly:
        if L.point_in_poly(x, y, p):
            return True
    return False


def _street_list():
    """ruas da planta pavimentadas aqui: todas menos a avenida (street2 proprio) e as do terraco do summon (op_summon)"""
    out = []
    for k, (pts, w, z) in enumerate(L.STREETS_V2):
        if k == 0:
            continue
        mx = sum(p[0] for p in pts) / len(pts)
        my = sum(p[1] for p in pts) / len(pts)
        if _in_rect(mx, my, SUMMON_RECT, 0.0):
            continue
        out.append((pts, w, z))
    return out


def streets(lots):
    """avenida com o street2 (leito assentado + sarjeta + meio-fio + calcadas, lajes so na face de cima) e as outras
    ruas/vielas/cais/sando em PEDRA ASSENTADA por trecho (fiadas ao longo do trecho, juntas desencontradas, lajes
    cortadas retas na ponta) com BORDA de pedra nas 2 margens (PLANO_V2 3.3: sem meio-fio), so fora dos lotes (+soco),
    das escadas e do summon, na cota do piso. O trecho que ja foi pavimentado ganha (cruzamentos sem sobreposicao)."""
    t0 = time.time()
    mp = MB("OP_Cap_Streets", COLL, detail="far", floor=-999)
    av = L.AVENUE
    y0, y1 = av["y"]
    walk = av["front"] - av["x"][1] - 0.3
    Fa = Frame(0.0, (y0 + y1) / 2, T1 + 0.12, math.pi / 2)
    K2.street2(mp, Fa, y1 - y0, av["x"][1] - av["x"][0], walk, key=3, thin=True)
    done = [((0.0, (y0 + y1) / 2), math.pi / 2, (y1 - y0) / 2, av["front"])]     # (centro, rumo, meio-comp., meia-larg.)
    lots_poly = [L.lot_poly(lt, 0.4) for lt in lots]
    stairs_poly = [op_col.stair_footprint(st[0], 0.3) for st in L.STAIRS]
    nq = 0
    SX, SY, BW = 2.6, 1.5, 0.55
    g = 0.04

    def in_done(x, y):
        for (cx, cy), a, hl, hw in done:
            u = (x - cx) * math.cos(a) + (y - cy) * math.sin(a)
            v = -(x - cx) * math.sin(a) + (y - cy) * math.cos(a)
            if abs(u) <= hl and abs(v) <= hw:
                return True
        return False

    def ok_at(F, zr, ua, ub, va, vb):
        cx, cy = F.p((ua + ub) / 2, (va + vb) / 2).xy
        if in_done(cx, cy) or _blocked(cx, cy, lots_poly, stairs_poly):
            return False
        for u, v in ((ua, va), (ub, va), (ub, vb), (ua, vb), ((ua + ub) / 2, (va + vb) / 2)):
            p = F.p(u, v)
            zz = L.zone_of(p.x, p.y)
            if zz is None or abs(zz - zr) > 0.05:
                return False
        return True
    for si, (pts, w, zr) in enumerate(_street_list()):
        hw = w / 2
        new = []
        for i, (a, b) in enumerate(zip(pts, pts[1:])):
            dx, dy = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(dx, dy)
            if ln < 0.5:
                continue
            ang = math.atan2(dy, dx)
            e0 = hw if i > 0 else 0.0                   # emenda nas quinas internas
            e1 = hw if i < len(pts) - 2 else 0.0
            L_ = ln + e0 + e1
            cxy = (a[0] + dx / ln * (ln / 2 - e0 / 2 + e1 / 2), a[1] + dy / ln * (ln / 2 - e0 / 2 + e1 / 2))
            z = zr + STREET_DZ
            F = Frame(cxy[0], cxy[1], z, ang)
            rows = max(1, int(round((w - 2 * BW) / SY)))
            rh = (w - 2 * BW) / rows
            bands = [(-hw, -hw + BW, "b")] + [(-hw + BW + r * rh, -hw + BW + (r + 1) * rh, r) for r in range(rows)] + \
                [(hw - BW, hw, "b")]
            for va, vb, r in bands:
                border = r == "b"
                sx = 1.7 if border else SX
                off = 0.0 if border else (0.5 * SX if r % 2 else 0.0) + 0.23 * SX * h01("rua", si, i, r)
                u = -L_ / 2 - off
                k = 0
                run = None
                while u < L_ / 2 - 0.05:
                    wd = sx * (0.8 + 0.4 * h01("rua", si, i, r, k)) if not border else sx
                    ua, ub = max(-L_ / 2, u), min(L_ / 2, u + wd)
                    u += wd
                    k += 1
                    if ub - ua < 0.3 or not ok_at(F, zr, ua, ub, va, vb):
                        if run:
                            mp.quad(F.p(run[0], va, -0.12), F.p(run[1], va, -0.12), F.p(run[1], vb, -0.12),
                                    F.p(run[0], vb, -0.12), "Stone_OP_Dark")
                        run = None
                        continue
                    m = "Stone_OP" if border else "Stone_OP_Path"
                    mp.quad(F.p(ua + g, va + g, 0.0), F.p(ub - g, va + g, 0.0), F.p(ub - g, vb - g, 0.0),
                            F.p(ua + g, vb - g, 0.0), m)
                    nq += 1
                    run = (run[0], ub) if run else (ua, ub)
                if run:
                    mp.quad(F.p(run[0], va, -0.12), F.p(run[1], va, -0.12), F.p(run[1], vb, -0.12),
                            F.p(run[0], vb, -0.12), "Stone_OP_Dark")
            done.append((cxy, ang, L_ / 2, hw))
    ob = mp.finish(recalc=False)
    STATS["lajes"] = nq
    STATS["t_ruas"] = time.time() - t0
    return ob


# ================================================================== pecas: andon, toro, torii, bancas
def _lamp_spots(lots):
    """andon nos NOS das ruas (pontas e quinas das faixas da planta + avenida a cada ~20), na borda da faixa, longe
    dos lotes (>= 1,6) e do eixo das rotas"""
    spots = []
    av = L.AVENUE
    for y in (52.0, 72.0, 92.0):
        for s in (-1, 1):
            spots.append((s * (av["x"][1] + 1.3), y, T1, T1 + 0.12 + 0.35))
    for pts, w, z in _street_list():
        for i, p in enumerate(pts):
            if i not in (0, len(pts) - 1):
                continue
            q = pts[1] if i == 0 else pts[-2]
            dx, dy = q[0] - p[0], q[1] - p[1]
            ln = math.hypot(dx, dy) or 1.0
            nx, ny = -dy / ln, dx / ln
            for sgn in (1, -1):
                x, y = p[0] + nx * sgn * (w / 2 - 0.9) + dx / ln * 3.0, p[1] + ny * sgn * (w / 2 - 0.9) + dy / ln * 3.0
                spots.append((x, y, z, z + STREET_DZ))
                break
    out = []
    lp = [L.lot_poly(lt, 1.6) for lt in lots]
    for x, y, zb, z in spots:
        if any(L.point_in_poly(x, y, p) for p in lp) or _in_rect(x, y, SUMMON_RECT, 2.0):
            continue
        zz = L.zone_of(x, y)
        if zz is None or abs(zz - zb) > 0.05:
            continue
        if any(math.hypot(x - a, y - b) < 14.0 for a, b, c in out):
            continue
        out.append((x, y, z))
    return out


def props(lots):
    mb = MB("OP_Cap_Props", COLL)
    n_col = 0
    nl = 0
    for i, (x, y, z) in enumerate(_lamp_spots(lots)):
        nm = "L_OPProp_Lamp_Cap_%d" % i if nl < 10 and i % 2 == 0 else None
        nl += 1 if nm else 0
        K2.lamp_andon(mb, Frame(x, y, z, 0.0), nm)
        col_box("OP_CapLamp", (2.3, 2.3, L.GUARD_V2 + 0.5), (x, y, z - 0.5 + (L.GUARD_V2 + 0.5) / 2))   # nao se escala
        n_col += 1
    # sando NE: 6 toro (luz em 3) + torii de laca com 2 nobori (as unicas bandeiras da capital)
    for i, (x, y) in enumerate(L.NE_TORO):
        z = P + STREET_DZ
        K2.toro2(mb, Frame(x, y, z, 0.0), "L_OPProp_Toro_Sando_%d" % i if i % 2 == 0 else None, 0.8)
        col_box("OP_CapToro", (2.6, 2.6, L.GUARD_V2 + 0.5), (x, y, z - 0.5 + (L.GUARD_V2 + 0.5) / 2))
        n_col += 1
    n_col += torii_ne(mb)
    # carga (vida na travessa da rua alta do porto)
    for k, (x, y, z, kind) in enumerate(((95.5, 71.0, T1, "barrels"),)):
        K2.goods_pile(mb, Frame(x, y, z + STREET_DZ, 0.0), kind)
        col_box("OP_CapCarga", (5.0, 4.0, L.GUARD_V2 + 0.5), (x + 0.8, y, z + (L.GUARD_V2 + 0.5) / 2 - 0.5))
        n_col += 1
    K.cull_hidden(mb)
    mb.finish()
    return n_col


def torii_ne(mb):
    """torii (myojin) de laca na entrada do sando NE: pilares em pedras-base, nuki, kasagi com pontas levantadas,
    placa; 2 nobori ao lado. Rumo +x (quem entra no sando)."""
    x0, y0 = L.SHRINE_TORII
    z = P
    F = Frame(x0, y0, z, 0.0)                       # +x local = rumo do sando; pilares em y = +-w/2
    w, h = 9.0, 10.6                                 # nuki a 2,9 acima do olho (camera PlayerHeight_NE no eixo)
    for s in (-1, 1):
        Fp = K2.sub(F, 0.0, s * (w / 2 + 0.7))
        K.rock_base(mb, Fp, 0.0, 0.0, 0.0, 1.15, 0.6)
        K.lathe(mb, Fp, (0, 0, 0.4), [(0.62, 0.0), (0.56, h - 0.4)], 12, K2.LAC)
        K.lathe(mb, Fp, (0, 0, 0.35), [(0.78, 0.0), (0.78, 0.9), (0.66, 1.05)], 12, K2.WD)
    yy = w / 2 + 2.6
    K.bb(mb, F, -0.45, 0.45, -yy, yy, h - 2.3, h - 1.5, K2.LAC)                           # nuki
    K.bb(mb, F, -0.5, 0.5, -0.45, 0.45, h - 1.5, h - 0.2, K2.LAC)                         # gakuzuka
    K.bb(mb, F, -0.62, -0.5, -1.0, 1.0, h - 1.4, h + 0.0, K2.GOLD)                        # placa
    zk = h + 0.25
    prof = [(-0.6, -0.45), (0.6, -0.45), (0.6, 0.35), (-0.6, 0.35)]
    pts = [(0.0, -(yy + 1.4), zk + 0.9), (0.0, -(yy - 0.6), zk + 0.25), (0.0, -w / 4, zk), (0.0, 0.0, zk - 0.03),
           (0.0, w / 4, zk), (0.0, yy - 0.6, zk + 0.25), (0.0, yy + 1.4, zk + 0.9)]
    K.sweep(mb, F, pts, prof, K2.LAC)                                                      # shimaki
    K.sweep(mb, F, [(p[0], p[1] * 1.04, p[2] + 0.75) for p in pts], [(-0.75, -0.4), (0.75, -0.4), (0.75, 0.4),
                                                                      (-0.75, 0.4)], K2.WD)   # kasagi
    for s in (-1, 1):
        K2.nobori2(mb, Frame(x0 - 1.6, y0 + s * (w / 2 + 3.4), z + STREET_DZ, math.pi), 8.5, K2.CWHITE, K2.CRED)
    n = 0
    for s in (-1, 1):
        col_box("OP_CapTorii", (2.0, 2.0, h + 1.0), F.p(0.0, s * (w / 2 + 0.7), (h + 1.0) / 2))
        col_box("OP_CapTorii", (1.4, 1.4, L.GUARD_V2 + 0.5), (x0 - 1.6, y0 + s * (w / 2 + 3.4), z + 4.25))
        n += 2
    return n


# ================================================================== escadas da planta (visual; colisao do op_col)
def stairs():
    mb = MB("OP_Cap_Stairs", COLL, detail="far", floor=None)
    for nm in ("Praca", "Sudoeste", "OesteAlta", "Mirante"):
        DL.plan_stair(mb, nm)
    mb.finish()


# ================================================================== cameras das folhas (fora do export)
def cams():
    E = L.EYE
    C = {
        # de cima (camera do jogo ~35 graus), por quadra
        "CAM_OP_V23Cap_Cima_Avenida": ((0.0, 18.0, T1 + 62.0), (0.0, 78.0, T1 + 6.0), 24),
        "CAM_OP_V23Cap_Cima_AvL_Porto": ((60.0, 30.0, T1 + 58.0), (80.0, 88.0, T1 + 6.0), 24),
        "CAM_OP_V23Cap_Cima_Bairro": ((-100.0, 30.0, T1 + 60.0), (-110.0, 86.0, T1 + 6.0), 24),
        "CAM_OP_V23Cap_Cima_OesteS": ((-100.0, 120.0, P + 55.0), (-145.0, 150.0, P + 6.0), 24),
        "CAM_OP_V23Cap_Cima_OesteM": ((-100.0, 200.0, P + 55.0), (-150.0, 220.0, P + 6.0), 24),
        "CAM_OP_V23Cap_Cima_OesteN_W3": ((-110.0, 270.0, P + 60.0), (-150.0, 320.0, P + 8.0), 24),
        "CAM_OP_V23Cap_Cima_AlemCanal": ((-150.0, 160.0, P + 60.0), (-200.0, 220.0, P + 6.0), 24),
        "CAM_OP_V23Cap_Cima_NE": ((130.0, 250.0, P + 58.0), (170.0, 296.0, P + 6.0), 24),
        # aerea (comparar com a ref_03)
        "CAM_OP_V23Cap_Aerea_Ref03": ((0.0, -40.0, T1 + 80.0), (0.0, 160.0, T1 + 20.0), 24),
        "CAM_OP_V23Cap_Aerea_Cidade": ((60.0, -60.0, 240.0), (-60.0, 160.0, 90.0), 24),
        # altura do jogador
        "CAM_OP_V23Cap_Jog_Avenida": ((3.0, 47.0, T1 + 0.47 + E), (-4.0, 110.0, T1 + 9.0), 22),
        "CAM_OP_V23Cap_Jog_AvenidaO": ((-11.0, 60.0, T1 + 0.47 + E), (-15.5, 78.0, T1 + 6.5), 20),
        "CAM_OP_V23Cap_Jog_Viela": ((-60.0, 86.0, T1 + E), (-140.0, 86.0, T1 + 8.0), 22),
        "CAM_OP_V23Cap_Jog_Portal": ((-6.0, 86.0, T1 + E), (-40.0, 86.0, T1 + 5.0), 20),
        "CAM_OP_V23Cap_Jog_Oeste": ((-112.0, 140.0, P + E), (-121.0, 190.0, P + 7.0), 22),
        "CAM_OP_V23Cap_Jog_Cais": ((-164.0, 130.0, P + E), (-164.0, 200.0, P + 6.0), 22),
        "CAM_OP_V23Cap_Jog_Sando": ((112.0, 296.0, P + E), (190.0, 300.0, P + 7.0), 22),
        "CAM_OP_V23Cap_Jog_PortoAlto": ((60.0, 111.0, T1 + E), (120.0, 108.0, T1 + 7.0), 22),
    }
    for nm, (a, b, lens) in C.items():
        fm_lib.camera(nm, Vector(a), Vector(b), lens)
        if "_Jog_" in nm:                              # boneco de 5 a ~9 a frente (escala nas folhas)
            dx, dy = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(dx, dy) or 1.0
            x, y = a[0] + dx / ln * 15.0 + dy / ln * 2.6, a[1] + dy / ln * 15.0 - dx / ln * 2.6
            zz = L.zone_of(x, y)
            if zz is not None:
                DL.dummy("SCALE_Dummy_Cap_" + nm.split("_Jog_")[1], x, y, zz + STREET_DZ, math.atan2(dy, dx) + math.pi / 2)
    return list(C)


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
            kw_ = 3.0 if W >= 13.0 else 0.0
            bays = ([("koshi", kw_)] if kw_ else []) + [("door", 4.4), {"t": "shop", "upper_board": True}]
            if kw["shop_side"] < 0:
                bays = list(reversed(bays))
            xs, sp = K2._posts_x(W, bays)
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
        nm = "CAM_OP_V23Cap_Int_" + lt["name"]
        fm_lib.camera(nm, Fc.p(xc + 0.8, D / 2 + 6.5, L.EYE + 0.5), Fc.p(xc, D / 2 - 6.0, zf + 2.6), 26)
        DL.dummy("SCALE_Dummy_Cap_" + lt["name"], *Fc.p(xc + 1.0, D / 2 - 4.2, zf)[:], F.a)
        out.append(nm)
    return out


def junction_cams(specs, n=8):
    """closes das JUNCOES entre casas vizinhas (prova de zero interpenetracao): olhando de cima-frente para a divisa
    de pares com alturas diferentes"""
    out = []
    seen = set()
    by = {s["lot"]["name"]: s for s in specs}
    cand = []
    for s in specs:
        for o in s["nb"]["nb"]:
            t = by.get(o)
            if not t or (o, s["lot"]["name"]) in seen:
                continue
            seen.add((s["lot"]["name"], o))
            cand.append((abs(s["zw"] - t["zw"]) + (3.0 if s["lot"]["tsuma"] != t["lot"]["tsuma"] else 0.0), s, t))
    cand.sort(key=lambda c: -c[0])
    used = set()
    for sc, s, t in cand:
        if s["lot"]["block"] in used and len(out) < n - 2:
            pass
        if len(out) >= n:
            break
        a, b = s["lot"], t["lot"]
        mx, my = (a["x"] + b["x"]) / 2, (a["y"] + b["y"]) / 2
        c, sn = math.cos(a["yaw"]), math.sin(a["yaw"])
        zt = a["z"] + max(s["zw"], t["zw"]) + 2.0
        fx, fy = mx + c * a["D"] / 2, my + sn * a["D"] / 2
        cx_, cy_ = fx + c * 20.0, fy + sn * 20.0
        if any(L.point_in_poly(cx_, cy_, L.lot_poly(o["lot"], 2.0)) for o in specs) or abs(s["zw"] - t["zw"]) < 2.0:
            continue
        nm = "CAM_OP_V23Cap_Juncao_%s_%s" % (a["name"], b["name"])
        fm_lib.camera(nm, Vector((cx_, cy_, zt + 2.0)), Vector((mx + c * a["D"] * 0.2, my + sn * a["D"] * 0.2, zt - 5.0)),
                      32)
        out.append(nm)
        used.add(a["block"])
    return out


# ================================================================== montagem
def build():
    t0 = time.time()
    lots = L.block_lots()
    specs = plan(lots)
    infos, probs, objs = build_lots(specs)
    t1 = time.time()
    ncol = lot_collisions(specs, infos)
    streets(lots)
    ncol += props(lots)
    stairs()
    cams()
    interior_cams(specs)
    jc = junction_cams(specs)
    STATS["juncoes"] = jc
    tri = 0
    for o in bpy.data.objects:
        if o.type == "MESH" and o.name.startswith("OP_Cap_"):
            tri += sum(len(p.vertices) - 2 for p in o.data.polygons)
    by_kind = {}
    for s in specs:
        k = s["lot"]["kind"]
        by_kind.setdefault(k, []).append(STATS["tris_lote"][s["lot"]["name"]])
    print("op_capital: %d lotes, %d tris (cull -%d, dentro -%d), colisoes %d, lajes %d (%.1fs), pares testados %d, "
          "%.1fs" % (len(specs), tri, STATS["cull"], STATS.get("cull_in", 0), ncol, STATS["lajes"], STATS["t_ruas"],
                     STATS["pares"], time.time() - t0))
    print("op_capital: telhados com rampa (ao alcance de piso mais alto): %s" % (
        ", ".join(STATS["telhados_rampa"]) or "-"))
    print("op_capital: tris por tipo (antes do cull): " + ", ".join(
        "%s %d x ~%d" % (k, len(v), sum(v) / len(v)) for k, v in sorted(by_kind.items())))
    if os.environ.get("OP_CAP_LOTES") == "1":
        for s in sorted(specs, key=lambda s: -STATS["tris_lote"][s["lot"]["name"]]):
            print("op_capital lote %-14s %-9s lod %d tris %5d" % (s["lot"]["name"], s["lot"]["kind"], s["kw"]["lod"],
                                                                  STATS["tris_lote"][s["lot"]["name"]]))
    if probs:
        for p in probs[:40]:
            print("op_capital INTERPENETRACAO %s %s x %s n=%d em %s" % p)
        msg = "op_capital: FAIL interpenetracao entre edificios: %d problemas em %d pares testados" % (
            len(probs), STATS["pares"])
        print(msg)
        if os.environ.get("OP_CAP_SOFT") != "1":
            raise RuntimeError(msg)
    else:
        print("op_capital: OK interpenetracao entre edificios: 0 (%d pares vizinhos testados malha x malha)" %
              STATS["pares"])
    return dict(specs=specs, infos=infos, probs=probs)
