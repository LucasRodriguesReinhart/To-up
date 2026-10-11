# op_qa - testes automaticos da Ilha 5 (ONE PIECE / WANO): navegacao sobre as colisoes COL_ (mesmo andador do lobby e
# das ilhas: degrau 2,3, queda 2,3, altura livre 6,5, corpo 1,1) nas rotas da planta (+ portao aberto/fechado), sondas
# de borda, PRACA_LIVRE (nada colidivel na MiningZone ate piso + 12) + PRACA_PISO (raycast plano a 92,2), marcadores e
# cameras obrigatorios, encaixe 0,000, auditoria tecnica, BUDGET (PLANO_OP secao 9) e as medidas do GATE do blockout.
# uso: blender -b ilha_onepiece.blend --python op_qa.py -- [nav] [tech] [markers] [clear] [budget] [gate] [col]
#      (padrao: tudo). RODADA 3 (colisao V3): antes de qualquer teste roda o colv3 EM MEMORIA (lista branca das COL_ +
#      colisao pela forma do visual) e TODO teste usa a colisao como o Roblox vai fazer (COL_ restantes + fecho convexo
#      das MeshParts Hull; Precise = a malha). 'col' = so o gate visual + COLV3 GATE (AR/PET_AR/CASA/INTERIOR/TELHADO/
#      MURO/CAIXA). PRACA_BOUNDS emula o GetPartBoundsInBox do minerio; SUMMON_PISO o raio da maquina de invocacao.
import sys, os, math, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import op_lib as DL
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import op_layout as L
import op_col
import fm_qa
import numpy as np

T0, T1, P, CF, CC = L.T0, L.T1, L.P, L.CF, L.CC


# ------------------------------------------------------------------ COLISAO V3: o modelo do que o Roblox vai colidir
# Rodada 3: o gate antigo media o visual contra as caixas COL_ e passou com o jogo quebrado. Agora TODO teste de colisao
# (rotas, sondas, praca, gate visual) roda sobre a colisao COMO O ROBLOX VAI FAZER: as COL_ que sobram na lista branca
# (chao da planta, lajes de modulo, jogabilidade) + o FECHO CONVEXO de cada MeshPart colidivel da colv3 (Hull = fecho
# exato; Precise = a propria malha). O passe colv3 roda aqui em memoria (o .blend nao e salvo).
_PREP = {}


def prep():
    if "rep" not in _PREP:
        rep, cfg = op_col.v3_prepare(log=print)
        _PREP["rep"], _PREP["cfg"] = rep, cfg
        nh = sum(1 for o in bpy.data.objects if o.get("colv3") == "H")
        npr = sum(1 for o in bpy.data.objects if o.get("colv3") == "P")
        print("TECH COLV3 %d agrupamentos -> %d MeshParts colidiveis (Hull %d, Precise %d) | %d props pequenos sem "
              "colisao | %d pecas de pele no chao | COL_ apagadas %d, mantidas %d (lajes de modulo %d) | pontos livres "
              "%d, alcancados %d | %s" % (rep["agrupamentos"], rep["portadores"], nh, npr, rep["pequenos"],
                                         rep["pecas_pele"], sum(rep["col_apagadas"].values()),
                                         sum(rep["col_mantidas"].values()), len(op_col.V3_SLABS), rep["pontos_livres"],
                                         rep["alcancados"], rep["tempo"]))
        for a in rep["avisos"][:12]:
            print("AVISO COLV3 %s %s %s" % a)
        top = sorted(rep["por_objeto"].items(), key=lambda t: -t[1][4])[:16]
        print("TECH COLV3 por objeto (pecas, grupos, particao, agrupamentos, MeshParts): %s" % top)
        print("TECH COLV3 folhas concavas pequenas sem colisao %d, troncos cortados %d, telhados ao alcance %d/%d, faces "
              "cortadas %d" % (rep.get("folhas_soltas", 0), rep.get("troncos_cortados", 0),
                               rep.get("telhados_alcancaveis", 0), rep.get("telhados", 0), rep.get("faces_cortadas", 0)))
    return _PREP["rep"]


def model():
    """[(nome, verts, faces, tipo)] da colisao (cache): 'box' (COL_), 'hull' (MeshPart Hull), 'mesh' (Precise)"""
    import colv3
    if "model" not in _PREP:
        prep()
        out = []
        for nm, vs, fs, kind in colv3.meshes(_PREP["cfg"]):
            o = bpy.data.objects.get(nm)
            if o is not None and o.get("colv3") == "P":          # Precise: a propria malha
                mw = o.matrix_world
                vs = [tuple(mw @ v.co) for v in o.data.vertices]
                fs = [list(p.vertices) for p in o.data.polygons]
                kind = "mesh"
            out.append((nm, vs, fs, kind))
        _PREP["model"] = out
    return _PREP["model"]


def col_bvh(exclude=()):
    verts, polys = [], []
    fm_qa.OWNER.clear()
    live = [(o.name, [tuple(o.matrix_world @ v.co) for v in o.data.vertices], [list(p.vertices) for p in o.data.polygons],
             "box") for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("COL_QA_")]
    for nm, vs, fs, kind in model() + live:
        if exclude and nm.startswith(exclude):
            continue
        base = len(verts)
        verts += vs
        polys += [[base + i for i in f] for f in fs]
        fm_qa.OWNER.extend([nm] * len(fs))
    return BVHTree.FromPolygons(verts, polys), len(polys)


# ------------------------------------------------------------------ navegacao


def ds_stub():
    """cabeceira da Demon Slayer (so para o teste DS_GATE->ENTRY): 30 de tabuleiro antes do WORLD_FROM_PREV, no lugar
    do trecho portao One Piece -> ancora da DS"""
    if bpy.data.objects.get("COL_QA_DSStub_001"):
        return
    DL.col_box("QA_DSStub", (L.DECK_W, 30.5, 2.0), (L.PREV_X, L.PREV_Y - 14.75, L.DECK - 1.0))
    bpy.context.view_layer.update()


def _probes():
    out = []
    ux, uy = L.exit_dir()
    ap = L.anchor_opm_pos()
    out.append(("ANCORA_OPM_guarda", ap[0] - ux * 2.0, ap[1] - uy * 2.0, T1, ux, uy, 4.0))
    for d, nm in ((44.0, "PONTE_SAIDA"),):
        p = L.exit_point(d)
        out.append((nm + "_lado_E", p[0], p[1], T1, -uy, ux, L.EXIT_W / 2 + 3.0))
        out.append((nm + "_lado_D", p[0], p[1], T1, uy, -ux, L.EXIT_W / 2 + 3.0))
    for y in (-90.0, -60.0, -30.0):
        z = L.DECK + (L.T0 - L.DECK) * (y - L.PREV_Y) / L.BRIDGE_IN_LEN
        out.append(("PONTE_CHEGADA_%d_O" % y, 0.0, y, z, -1.0, 0.0, L.DECK_W / 2 + 3.0))
        out.append(("PONTE_CHEGADA_%d_L" % y, 0.0, y, z, 1.0, 0.0, L.DECK_W / 2 + 3.0))
    # V2-0 (PLANO_V2 9.4): guarda so onde a queda leva ao vazio/mar ou passa do pulo; quedas internas <= 7,2 sobre
    # chao colidivel ficam abertas (praca -> rua, margem -> leito). Sonda (dx, dy) = (0, 0): raio PARA BAIXO no meio do
    # canal/bacia/lago: tem de achar o LEITO colidivel (sem buraco ate o vazio).
    out += [("PATIO_TORII_O", -10.0, 12.0, T0, -1.0, 0.0, 22.0), ("PATIO_TORII_L", 10.0, 12.0, T0, 1.0, 0.0, 22.0),
            ("BAIRRO_penhasco_sul", -110.0, 42.0, T1, 0.0, -1.0, 12.0),
            ("NE_borda_leste", 222.0, 268.0, P, 0.9, -0.44, 12.0),
            ("MIRANTE_NE_borda_canal", 204.0, 334.0, L.NEM, 0.0, 1.0, 8.0),
            ("W2b_borda_oeste", -212.0, 230.0, P, -1.0, 0.0, 16.0),
            ("CANAL_O_leito_praca", -174.0, 220.0, P, 0.0, 0.0, 6.0),
            ("CANAL_O_leito_bairro", -174.0, 100.0, T1, 0.0, 0.0, 6.0),
            ("CANAL_O_boca_queda", -174.0, 58.0, T1 - L.CANAL_DROP - L.CANAL_BED, 0.0, -1.0, 8.0),
            ("ADRO_bacia_leito", 0.0, 342.0, CF, 0.0, 0.0, 6.0), ("CANAL_L_leito", 160.0, 341.5, P, 0.0, 0.0, 6.0),
            ("LAGO_NE_leito", 148.0, 322.0, P, 0.0, 0.0, 6.0),
            ("PATIO_CASTELO_varanda", 0.0, 362.0, CC, 0.0, -1.0, 16.0),
            ("PATIO_CASTELO_oeste", -84.0, 450.0, CC, -1.0, 0.0, 12.0),
            ("TERRACO_ALTO_oeste", -200.0, 360.0, L.W3, -1.0, 0.0, 30.0),
            ("SUMMON_borda_porto", 190.0, 200.0, T1, 1.0, 0.0, 22.0),
            ("SUMMON_borda_sul", 180.0, 156.0, T1, 0.0, -1.0, 12.0),
            ("CAIS_borda_agua", 214.0, 230.0, L.HARBOR, 1.0, 0.0, 16.0),
            ("PIER_borda", 228.0, 180.0, L.HARBOR, 1.0, 0.0, 12.0),
            ("NAVIO_amurada", 248.0, 170.0, L.SHIP, 1.0, 0.0, 14.0),
            ("PROMONTORIO_borda_S", L.exit_point(110.0, -20.0)[0], L.exit_point(110.0, -20.0)[1], T1, uy, -ux, 16.0),
            ("ESCADA_PortoA_guarda", 180.0, 140.0, L.HMID + 8.0, 0.0, -1.0, 10.0)]
    return out


# V3: sem guarda invisivel no labio. Sonda OBRIGATORIA = leito sob a agua (raio para baixo), ancora (guarda de jogo) e
# lados das pontes sobre o vazio (o parapeito VISIVEL tem de segurar). As outras bordas viraram INFORMATIVAS: borda
# aberta = o visual nao tem guarda-corpo ali (quem cai e resgatado pelo VOID_CATCH/IslandTravel); se a zona quiser
# segurar, o dono poe guarda-corpo/muro VISIVEL.
PROBE_MUST = ("ANCORA_OPM_guarda", "PONTE_SAIDA_", "PONTE_CHEGADA_")


def probes(bvh):
    res = []
    for name, x, y, z, dx, dy, reach in _probes():
        o = Vector((x, y, z + 2.0))
        if dx == 0.0 and dy == 0.0:                      # leito: raio para baixo ate 'reach' abaixo do piso
            hit = bvh.ray_cast(o, Vector((0.0, 0.0, -1.0)), reach + 2.0)
        else:
            hit = bvh.ray_cast(o, Vector((dx, dy, 0.0)).normalized(), reach)
        ok = hit[0] is not None
        must = (dx == 0.0 and dy == 0.0) or name.startswith(PROBE_MUST)
        res.append((name, ok or not must))
        if ok:
            own = fm_qa.OWNER[hit[2]] if hit[2] is not None and hit[2] < len(fm_qa.OWNER) else "?"
            print("OK   SONDA %s  (segura: %s)" % (name, own))
        else:
            print(("FAIL " if must else "AVISO ") + "SONDA " + name + "  (borda aberta: nada visivel segura o jogador%s)" % (
                "" if must else " - resgate do VOID_CATCH; guarda-corpo visivel e do dono da zona"))
    return res


def nav():
    # V3: o andador anda sobre a colisao REAL (visual solido): beiral/hisashi a >= 6 do piso nao e 'teto baixo' (o
    # personagem R15 tem ~5,2); a regra antiga de 6,5 era folga sobre caixas invisiveis
    fm_qa.HEAD = 6.0
    ds_stub()
    bvh, n = col_bvh()
    print("COL faces:", n)
    res = {}
    ok = 0
    R = L.routes()
    for name, (pts, z0) in R.items():
        f, zend = fm_qa.walk(bvh, pts, z0)
        res[name] = f
        ok += not f
        print(("OK   " if not f else "FAIL ") + "ROTA " + name + ("" if not f else "  " + str(f)))
        if f and f[0][0] == "OBSTACULO":
            o = bpy.data.objects.get(f[0][3])
            if o is not None:
                ws = [o.matrix_world @ v.co for v in o.data.vertices]
                print("AVISO ROTA %s obstaculo %s: fidelidade %s, material %s, de %s, caixa %s..%s" % (
                    name, o.name, o.get("colv3", "COL"), [m.name for m in o.data.materials if m][:2], o.get("colv3_src", "-"),
                    [round(min(v[i] for v in ws), 1) for i in range(3)], [round(max(v[i] for v in ws), 1) for i in range(3)]))
    print("ROTAS %d/%d OK" % (ok, len(res)))
    bvh2, _ = col_bvh(exclude=("COL_GateOnePunchManLock",))
    f, zend = fm_qa.walk(bvh2, L.gate_open_route(), T1)
    print(("OK   " if not f else "FAIL ") + "ROTA PORTAO_OPM_ABERTO->ANCORA" + ("" if not f else "  " + str(f)))
    f2, _ = fm_qa.walk(bvh, L.gate_open_route(), T1)
    print(("OK   " if f2 else "FAIL ") + "PORTAO_OPM_FECHADO bloqueia a passagem: %s" % (f2[:1] if f2 else "NAO bloqueia"))
    ap = L.anchor_opm_pos()
    ux, uy = L.exit_dir()
    f3, _ = fm_qa.walk(bvh2, [(ap[0] - ux * 6.0, ap[1] - uy * 6.0), (ap[0] + ux * 6.0, ap[1] + uy * 6.0)], T1)
    print(("OK   " if f3 else "FAIL ") + "TERMINO_SEGURO ancora OPM fechada pela guarda provisoria: %s" % (
        f3[:1] if f3 else "NAO fecha (passagem para a queda!)"))
    pr = probes(bvh)
    print("SONDAS %d/%d OK" % (sum(1 for _, k in pr if k), len(pr)))
    old = fm_qa.BODY_R
    fm_qa.BODY_R = 1.7
    try:
        estreitas = [nm for nm, (pts, z0) in R.items() if fm_qa.walk(bvh, pts, z0)[0]]
    finally:
        fm_qa.BODY_R = old
    print("LARGURA rotas com trecho < 3,4 de largura: %s" % (estreitas or "nenhuma"))
    o = bpy.data.objects.get("COL_QA_DSStub_001")
    if o:
        bpy.data.objects.remove(o, do_unlink=True)
    return res


# ------------------------------------------------------------------ praca livre
def _box_bvh(p0, p1):
    x0, y0, z0 = p0
    x1, y1, z1 = p1
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    f = [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return BVHTree.FromPolygons(v, f)


def _obj_hits_box(o, p0, p1):
    mw = o.matrix_world
    vs = [mw @ v.co for v in o.data.vertices]
    for v in vs:
        if p0[0] < v.x < p1[0] and p0[1] < v.y < p1[1] and p0[2] < v.z < p1[2]:
            return True
    if not vs:
        return False
    xs = [v.x for v in vs]
    ys = [v.y for v in vs]
    zs = [v.z for v in vs]
    if max(xs) < p0[0] or min(xs) > p1[0] or max(ys) < p0[1] or min(ys) > p1[1] or max(zs) < p0[2] or min(zs) > p1[2]:
        return False
    t = BVHTree.FromPolygons(vs, [list(p.vertices) for p in o.data.polygons])
    return bool(t.overlap(_box_bvh(p0, p1)))


def clear():
    """PRACA_LIVRE: nada COLIDIVEL dentro da MiningZone entre piso + 0,3 e piso + 12; malha visual de outra zona dentro
    da zona acima de piso + 0,3 = aviso (o emblema fica a +0,24: rente); piso plano em 92,2 (raycast de +12)"""
    x0, y0, x1, y1 = L.MINE_RECT
    p0, p1 = (x0, y0, P + 0.3), (x1, y1, P + L.CLEAR_H)
    bad = []
    bb = _box_bvh(p0, p1)
    for nm, vs, fs, kind in model():
        V = np.array(vs)
        if V[:, 0].max() < p0[0] or V[:, 0].min() > p1[0] or V[:, 1].max() < p0[1] or V[:, 1].min() > p1[1] or \
                V[:, 2].max() < p0[2] or V[:, 2].min() > p1[2]:
            continue
        if any(p0[0] < v[0] < p1[0] and p0[1] < v[1] < p1[1] and p0[2] < v[2] < p1[2] for v in vs) or \
                BVHTree.FromPolygons(vs, fs).overlap(bb):
            bad.append(nm)
    # V3: o SpawnMinerio/OnePieceIsland testam GetPartBoundsInBox(ponto + 5, 7x8x7 de MUNDO) com RespectCanCollide:
    # qualquer peca colidivel cuja CAIXA (MeshPart = AABB de mundo; Part = caixa orientada) entre na zona entre
    # piso + 1 e piso + 9 bloqueia o minerio ali - a AABB de mundo de uma peca girada 145 graus e enorme
    import colv3
    W = np.array(L.world_matrix())
    rect = [(x0 - 3.5, y0 - 3.5), (x1 + 3.5, y0 - 3.5), (x1 + 3.5, y1 + 3.5), (x0 - 3.5, y1 + 3.5)]
    rw = [tuple((W[:3, :3] @ np.array((x, y, 0.0)) + W[:3, 3])[:2]) for x, y in rect]
    bnd = []
    for nm, vs, fs, kind in model():
        V = np.array(vs)
        if V[:, 2].max() < P + 1.0 or V[:, 2].min() > P + 9.0:
            continue
        if kind == "box":
            if colv3._rect_poly_overlap(V[:, :2].min(axis=0), V[:, :2].max(axis=0), rect):
                bnd.append(nm)
            continue
        o = bpy.data.objects.get(nm)
        if o is None:
            continue
        Q = np.array([tuple(o.matrix_world @ v.co) for v in o.data.vertices])
        Qw = Q @ W[:3, :3].T + W[:3, 3]
        lo, hi = Qw.min(axis=0), Qw.max(axis=0)
        if colv3._rect_poly_overlap(lo[:2], hi[:2], rw):
            bnd.append(nm)
    print(("OK   " if not bnd else "FAIL ") + "PRACA_BOUNDS caixas colidiveis (AABB de mundo) na MiningZone entre piso+1 e "
          "piso+9 (GetPartBoundsInBox do minerio): %s" % (bnd[:10] or "nenhuma"))
    # V3: o OnePieceIsland.invocacao raia de pad + 20 para baixo (RespectCanCollide) para assentar a maquina: o primeiro
    # colisor tem de ser o piso do SUMMON_Interact (nada colidivel da torre por cima dele)
    si = bpy.data.objects.get("SUMMON_Interact")
    if si is not None:
        bv0, _ = col_bvh()
        h = bv0.ray_cast(Vector((si.location.x, si.location.y, si.location.z + 20.0)), Vector((0, 0, -1)), 40.0)
        dz = (h[0].z - si.location.z) if h[0] is not None else None
        okz = dz is not None and abs(dz) < 1.0
        print(("OK   " if okz else "AVISO ") + "SUMMON_PISO raio de +20 no SUMMON_Interact acha o piso (a maquina invisivel "
              "e o GachaPosition assentam no 1o colisor): %s" % (
            ("dz %.2f em %s" % (dz, fm_qa.OWNER[h[2]])) if dz is not None else "nada"))
    vis = [o.name for o in bpy.data.objects if o.type == "MESH" and not o.name.startswith(("COL_", "OP_Ter_",
           "SCALE_", "PREVIEW_", "OP_Plz_OreProxy")) and _obj_hits_box(o, p0, p1)]
    print(("OK   " if not bad else "FAIL ") + "PRACA_LIVRE colisores na MiningZone (piso+0,3..+12): %s" % (bad[:10] or "nenhum"))
    print(("OK   " if not vis else "AVISO ") + "PRACA_LIVRE malhas visuais na MiningZone acima de +0,3: %s" % (vis[:10] or "nenhuma"))
    bvh, n = col_bvh()
    worst, nbad = 0.0, 0
    badp = []
    x = x0 + 2.0
    while x < x1:
        y = y0 + 2.0
        while y < y1:
            hit = bvh.ray_cast(Vector((x, y, P + 12.0)), Vector((0, 0, -1)), 30.0)
            if hit[0] is None or abs(hit[0].z - P) > 0.5 or hit[1].z < 0.85:
                nbad += 1
                badp.append((round(x, 1), round(y, 1), round(hit[0].z, 2) if hit[0] is not None else None,
                             fm_qa.OWNER[hit[2]] if hit[2] is not None else "-"))
            else:
                worst = max(worst, abs(hit[0].z - P))
            y += 7.5
        x += 7.5
    print(("OK   " if nbad == 0 else "FAIL ") + "PRACA_PISO raycast de +12 na grade 7,5: %d pontos fora (|piso-92,2|<0,5, "
          "normal>0,85); desvio max %.3f %s" % (nbad, worst, badp[:6]))
    return bad


# ------------------------------------------------------------------ marcadores
REQUIRED = ["WORLD_FROM_PREV", "WORLD_ENTRY_OnePiece", "PATH_ENTRY_CENTER", "MiningZone_OnePiece",
            "SUMMON_Main", "SUMMON_Interact", "SUMMON_PlayerPosition", "ISLAND_EXIT_OnePiece",
            "ISLAND_NEXT_ANCHOR_OnePunchMan", "GATE_OnePunchMan", "GATE_OnePunchMan_INTERACT", "GATE_OnePunchMan_LOCKED",
            "GATE_OnePunchMan_EXIT", "GATE_OnePunchMan_OpenFX", "PURCHASE_UI_ANCHOR_OnePunchMan",
            "COL_GateOnePunchManLock_001", "COL_OPAnchorGuard_001", "OP_Exit_AnchorGuard",
            "SAFE_Entrada", "SAFE_Ponte_Chegada", "SAFE_Rua_Chegada", "SAFE_Praca_S", "SAFE_Praca_N", "SAFE_Praca_O",
            "SAFE_Praca_L", "SAFE_Summon", "SAFE_Bairro_Canal", "SAFE_Oeste_Alem", "SAFE_Terraco_Alto", "SAFE_Adro",
            "SAFE_Castelo", "SAFE_Porto_Alto", "SAFE_Cais", "SAFE_NE", "SAFE_Promontorio",
            "AUDIO_Plaza", "AUDIO_Street", "AUDIO_CastleFall", "AUDIO_FallE", "AUDIO_FallW", "AUDIO_Wheel",
            "AUDIO_Harbor", "AUDIO_Summon", "AUDIO_Castle",
            "FX_Fall_Castle_Lip", "FX_Fall_Castle_Base", "FX_Fall_E_Lip", "FX_Fall_E_Base", "FX_Fall_W_Lip",
            "FX_Fall_W_Base", "FX_Weir_E", "FX_Weir_W", "FX_Petals_Tree", "FX_Mist_CastleFall", "FX_Spring_W",
            "WATER_Sea", "WATER_Basin", "WATER_CanalE", "WATER_CanalW", "VFX_OP_Wheel"]
REQUIRED_CAMS = list(L.cams().keys())


def markers():
    names = {o.name for o in bpy.data.objects}
    miss = [n for n in REQUIRED + REQUIRED_CAMS if n not in names]
    ores = {}
    pts = []
    for o in bpy.data.objects:
        m = re.match(r"ORE_(COMMON|UNCOMMON|EPIC|SUPERLEGENDARY)_\d+$", o.name)
        if m:
            ores[m.group(1)] = ores.get(m.group(1), 0) + 1
            pts.append((o.location.x, o.location.y, o.get("radius", 2.5), o.name))
    x0, y0, x1, y1 = L.MINE_RECT
    fora = [n for x, y, r, n in pts if not (x0 < x < x1 and y0 < y < y1)]
    overl = 0
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            a, b = pts[i], pts[j]
            if math.hypot(a[0] - b[0], a[1] - b[1]) < a[2] + b[2] + 1.0:
                overl += 1
    gp = {}
    for o in bpy.data.objects:
        if o.name.startswith("GP_Block_"):
            gp[o.get("kind")] = gp.get(o.get("kind"), 0) + 1
    g = bpy.data.objects.get("GATE_OnePunchMan")
    wp = bpy.data.objects.get("WORLD_FROM_PREV")
    print("MARKERS faltando=%d %s" % (len(miss), miss))
    print("MARKERS minerio=%s total=%d fora_da_zona=%d sobrepostos=%d GP_Block=%s portao_OPM_area=%s" % (
        ores, len(pts), len(fora), overl, gp, g.get("area_id") if g else None))
    nmk = sum(1 for o in bpy.data.objects if o.type == "EMPTY" and o.users_collection
              and o.users_collection[0].name == "14_GAMEPLAY_MARKERS")
    print("MARKERS total na colecao 14_GAMEPLAY_MARKERS: %d" % nmk)
    if wp:
        r = L.to_roblox(wp.location.x, wp.location.y, wp.location.z)
        d = math.dist((r[0], r[1], r[2]), L.A_RBX)
        f = (wp.matrix_world.to_3x3() @ Vector((0.0, 1.0, 0.0))).normalized()
        fr = L.dir_to_roblox(f.x, f.y)
        print(("OK   " if d < 1e-3 else "FAIL ") + "ENCAIXE WORLD_FROM_PREV -> Roblox (%.3f, %.3f, %.3f) vs ancora DS (%.3f, %.3f, "
              "%.3f): %.4f | frente (%.4f, %.4f) vs (%.4f, %.4f)" % (r + tuple(L.A_RBX) + (d, fr[0], fr[2], L.A_FWD[0], L.A_FWD[2])))
    return miss


# ------------------------------------------------------------------ tecnico
def tech():
    gen = re.compile(r"^(Cube|Cylinder|Sphere|Plane|Icosphere|Cone|Torus|Object|Mesh|Empty|Camera|Light)(\.\d+)?$")
    dup = re.compile(r".+\.\d{3}$")
    bad, dups, nomat, scale, degen, tris, per = [], [], [], [], 0, 0, []
    for o in bpy.data.objects:
        if gen.match(o.name):
            bad.append(o.name)
        if dup.match(o.name):
            dups.append(o.name)
        if o.type != "MESH" or o.name.startswith(("COL_", "PREVIEW_", "SCALE_")):
            continue
        me = o.data
        t = sum(len(p.vertices) - 2 for p in me.polygons)
        tris += t
        per.append((t, o.name))
        if not me.materials or any(m is None for m in me.materials):
            nomat.append(o.name)
        if any(abs(s - 1.0) > 1e-4 for s in o.scale) or any(abs(r) > 1e-6 for r in o.rotation_euler):
            scale.append(o.name)
        for p in me.polygons:
            if p.area < 1e-6:
                degen += 1
    per.sort(reverse=True)
    ncol = sum(1 for o in bpy.data.objects if o.name.startswith("COL_"))
    nl = sum(1 for o in bpy.data.objects if o.type == "LIGHT" and not o.name.startswith("SUN_"))
    print("TECH nomes_genericos=%d duplicados=%d sem_material=%d transform_nao_aplicado=%d degeneradas=%d" % (
        len(bad), len(dups), len(nomat), len(scale), degen))
    print("TECH tris=%d objetos=%d malhas=%d materiais=%d colisoes=%d luzes=%d" % (
        tris, len(bpy.data.objects), sum(1 for o in bpy.data.objects if o.type == "MESH"),
        len([m for m in bpy.data.materials if m.users]), ncol, nl))
    print("TECH maiores:", per[:8])
    for lab, lst in (("genericos", bad), ("duplicados", dups), ("sem material", nomat), ("transform", scale)):
        if lst:
            print("TECH %s: %s" % (lab, lst[:12]))
    cnt = {}
    for o in bpy.data.objects:
        if o.name.startswith("COL_"):
            k = re.sub(r"_\d{3}$", "", o.name)
            k = re.sub(r"(HouseX?)[A-Z]\d$", r"\1*", k)
            cnt[k] = cnt.get(k, 0) + 1
    print("TECH colisoes por area: %s" % sorted(cnt.items(), key=lambda t: -t[1])[:12])
    return dict(bad=bad, dups=dups, nomat=nomat, scale=scale, degen=degen, tris=tris)


# ------------------------------------------------------------------ orcamento (PLANO_OP secao 9)
# V3 (rodada 3): static_meshes 650 -> 1950. A colisao pela forma separa cada estrutura solida em MeshParts proprias
# (fecho convexo justo por casa/trecho de muro/guarda-corpo/tronco/poste); o numero de TRIANGULOS nao muda. col 1500 ->
# 900: so ficam as COL_ de chao/jogabilidade.
BUDGET_ISLAND = {"static_tris": 640000, "static_meshes": 1950, "vfx_tris": 15000, "vfx_meshes": 30, "materials": 110,
                 "day_lights": 36, "col": 900}


def budget():
    import studio_op
    st, sm, vt, vm, mats = 0, 0, 0, 0, set()
    per = {}
    for o in bpy.data.objects:
        if o.type != "MESH" or o.name.startswith(("COL_", "PREVIEW_", "SCALE_", "OP_Plz_OreProxy")):
            continue
        if o.users_collection and o.users_collection[0].name in ("00_REFERENCE", "_SCALE_REFERENCE"):
            continue
        t = sum(len(p.vertices) - 2 for p in o.data.polygons)
        m = studio_op.est_meshparts(o)
        own = studio_op.owner_of(o.name)
        a = per.setdefault(own, [0, 0])
        a[0] += t
        a[1] += m
        for mt in o.data.materials:
            if mt:
                mats.add(mt.name)
        if o.name.startswith("VFX_"):
            vt += t
            vm += m
        else:
            st += t
            sm += m
    nl = sum(1 for o in bpy.data.objects if o.type == "LIGHT" and not o.name.startswith("SUN_")
             and not o.name.startswith(("L_OPProp_", "L_OPCap_Win_")))
    ncol = sum(1 for o in bpy.data.objects if o.name.startswith("COL_"))
    B = BUDGET_ISLAND
    for lab, v, lim in (("static_tris", st, B["static_tris"]), ("static_meshes~", sm, B["static_meshes"]),
                        ("vfx_tris", vt, B["vfx_tris"]), ("vfx_meshes~", vm, B["vfx_meshes"]),
                        ("materials", len(mats), B["materials"]), ("day_lights", nl, B["day_lights"]),
                        ("col", ncol, B["col"])):
        print(("OK   " if v <= lim else "FAIL ") + "BUDGET %-15s %7d / %d" % (lab, v, lim))
    for k in sorted(per):
        print("BUDGET dono %-11s tris %7d  MeshParts~ %4d" % (k, per[k][0], per[k][1]))
    return st, sm


# ------------------------------------------------------------------ gate do blockout (medidas)
VIS_OWNER = []


def vis_bvh():
    verts, polys = [], []
    VIS_OWNER.clear()
    for o in bpy.data.objects:
        if o.type != "MESH" or o.name.startswith(("COL_", "SCALE_", "PREVIEW_", "OP_Plz_OreProxy")) or o.hide_render:
            continue
        mw = o.matrix_world
        base = len(verts)
        verts += [mw @ v.co for v in o.data.vertices]
        polys += [[base + i for i in p.vertices] for p in o.data.polygons]
        VIS_OWNER.extend([o.name] * len(o.data.polygons))
    return BVHTree.FromPolygons(verts, polys)


def _zmax(prefixes=None, exclude=()):
    best = (-1e9, None)
    for o in bpy.data.objects:
        if o.type != "MESH" or o.name.startswith(("COL_", "SCALE_", "PREVIEW_")) or o.name.startswith(exclude):
            continue
        if prefixes and not o.name.startswith(prefixes):
            continue
        mw = o.matrix_world
        z = max((mw @ v.co).z for v in o.data.vertices)
        if z > best[0]:
            best = (z, o.name)
    return best


def gate():
    """medidas do GATE do blockout (PLANO_OP secao 13)"""
    lx = [q[0] for q in L.RIM_CTRL]
    ly = [q[1] for q in L.RIM_CTRL]
    print("GATE forma: topo %.0f x %.0f, area %.0f (DS 153k) | praca %.0f studs2 | MiningZone %.0f x %.0f" % (
        max(lx) - min(lx), max(ly) - min(ly), L.area(L.ISLAND_RIM), L.area(L.PLAZA), L.MINE_RECT[2] - L.MINE_RECT[0],
        L.MINE_RECT[3] - L.MINE_RECT[1]))
    zt, nt = _zmax(("OP_Tree_",))
    zk, nk = _zmax(("OP_Cas_Blockout", "OP_Cas_Keep"))   # M3 op_castle (acrescimo pontual): torre do modulo de detalhe
    zo, no = _zmax(None, exclude=("OP_Tree_", "OP_Cas_", "OP_Lmk_"))
    zs, ns = _zmax(("OP_Sum_", "VFX_OPSUM_"))
    zw, nw = _zmax(("OP_Lmk_",))
    print(("OK   " if zt > zk > zo else "FAIL ") + "GATE marco: arvore %.1f > castelo %.1f > resto da cidade %.1f (%s)" % (
        zt, zk, zo, no))
    print(("OK   " if zs < zk else "FAIL ") + "GATE summon: topo %.1f (%s) abaixo do castelo %.1f" % (zs, ns, zk))
    print(("OK   " if zw < zt else "FAIL ") + "GATE secundarios: caveira/espada/pagode ate %.1f (%s), abaixo da arvore" % (zw, nw))
    bvh = vis_bvh()
    keep_top = Vector((L.KEEP_C[0], L.KEEP_C[1], L.KEEP_TOP_Z + 2.0))        # acima da cumeeira (silhueta)
    tree_top = Vector((L.TREE_TRUNK[8][0], L.TREE_TRUNK[8][1], L.TREE_TRUNK[8][2] + L.TREE_TRUNK[8][3] + 3.0))
    star = None
    for o in bpy.data.objects:
        if o.type == "LIGHT" and o.name == "L_OPSum_Star":
            star = o.location.copy()
    fall = Vector((L.CASTLE_FALL[0], L.CASTLE_FALL[1] - 1.0, L.CASTLE_FALL[2] - 4.0))   # terco de cima da queda
    ship = Vector((L.SHIP_C[0], L.SHIP_C[1] + 10.0, L.SHIP + 40.0))
    gopm = Vector((L.gate_opm_pos()[0], L.gate_opm_pos()[1], T1 + 12.0))
    blocker = {}

    def visible(eye, tgt, tol=3.0):
        if tgt is star:
            tol = 10.5                                   # a estrela fica DENTRO da esfera armilar (gaiola r 9,2)
        d = tgt - eye
        hit = bvh.ray_cast(eye, d.normalized(), d.length)
        ok = hit[0] is None or (hit[0] - eye).length >= d.length - tol
        if not ok and tgt is tree_top and VIS_OWNER[hit[2]].startswith("OP_Tree_"):
            ok = True          # M3 op_tree (acrescimo pontual): o raio bate na PROPRIA arvore = arvore visivel
        if not ok:
            blocker["last"] = "%s a %.0f" % (VIS_OWNER[hit[2]], (hit[0] - eye).length)
        return ok
    cams = L.cams()
    for cn in L.PLAYER_CAMS:
        loc, tgt, lens = cams[cn]
        eye = Vector(loc)
        fwd = (Vector(tgt) - eye).normalized()
        near = bvh.find_nearest(eye, 2.0)
        ray = bvh.ray_cast(eye, fwd, 12.0)
        occl = near[0] is not None or ray[0] is not None
        msg = []
        for lab, p in (("torre", keep_top), ("arvore", tree_top), ("estrela", star)):
            if p is not None:
                msg.append("%s %s(%.0fg)" % (lab, "V" if visible(eye, p) else "-", math.degrees(fwd.angle(p - eye))))
        print(("OK   " if not occl else "FAIL ") + "GATE camera %-30s oclusao<12: %s | %s" % (
            cn, "nenhuma" if not occl else "SIM (%s)" % (("perto %.1f" % (near[0] - eye).length) if near[0] else
                                                       ("raio %.1f" % (ray[0] - eye).length)), "  ".join(msg)))
    checks = [("castelo (torre) do inicio da ponte de chegada (0,-100)", (0.0, -100.0, L.DECK + 0.6 + L.EYE), keep_top),
              ("arvore arqueada do inicio da ponte de chegada (0,-100)", (0.0, -100.0, L.DECK + 0.6 + L.EYE), tree_top),
              ("castelo do patio do torii (0,24)", (0.0, 24.0, T0 + L.EYE), keep_top),
              ("arvore arqueada do patio do torii (0,24)", (0.0, 24.0, T0 + L.EYE), tree_top),
              ("castelo do topo da escada Praca (0,124)", (0.0, 124.0, P + L.EYE), keep_top),
              ("cachoeira do castelo do centro da praca", (L.MINE_C[0], L.MINE_C[1], P + L.EYE), fall),
              ("estrela do summon do centro da praca", (L.MINE_C[0], L.MINE_C[1], P + L.EYE), star),
              ("estrela do summon da rua de chegada (0,100)", (0.0, 100.0, T1 + L.EYE), star),
              ("mastros do navio do terraco do summon", (160.0, 180.0, T1 + L.EYE), ship),
              ("portao OPM da cabeca da ponte de saida", (L.EXIT_START[0] - 4.0, L.EXIT_START[1], T1 + L.EYE), gopm)]
    nok = 0
    for lab, eye, p in checks:
        if p is None:
            continue
        v = visible(Vector(eye), p)
        nok += v
        print(("OK   " if v else "FAIL ") + "GATE visada %s%s" % (lab, "" if v else "  (bloqueada: %s)" % blocker.get("last")))
    return nok


# ------------------------------------------------------------------ GATE VISUAL (PLANO_V2 secao 9.8; V2-0 integracao)
# Os scripts da auditoria V2 (feedback_20261010/aud/scripts: audit_rays + analyze + inside + u5) viraram este modulo e
# rodam na CENA (visual = toda malha renderizavel fora de COL_/PREVIEW_/SCALE_/proxies/00_REFERENCE; colisao = as
# caixas COL_ da cena, 1 caixa por objeto). Mesmo raio, mesma grade (1,5 com origem deslocada), mesmo pulo (7,2),
# corpo 5, alcance horizontal 6 e tolerancia 1,5 da auditoria. Diferenca pontual: visual DENTRO de um solido de
# colisao conta como coberto (o jogador nao chega nele: e o caso dos banzos sob a guarda da escada).
#   U8  chao/rocha visual alcancavel sem colisao <= 20 studs2; telhado alcancavel sem colisao = 0; copa so aviso
#   U8b corpo dentro do modelo = 0 (pe afundando > 0,3 e cabeca dentro: aviso)
#   U5  fresta visual >= 0,6 na faixa do jogador = 0; vao de colisao >= 0,6 = 0
VG_JUMP, VG_BODY, VG_TOL, VG_NEAR, VG_STEP = 7.2, 5.0, 1.5, 6.0, 1.5
VG_LIM_CHAO, VG_LIM_TELHADO = 20.0, 0.0


def _vg_cat(m):
    if m.startswith(("Leaf", "Flower")):
        return 3                                             # copa
    if m.startswith("Roof"):
        return 2                                             # telhado
    if m.startswith(("Glass", "Window", "Cloth", "Rope", "P_", "Energy", "Summon", "Crystal")) or "Glow" in m:
        return 4                                             # outro (pano, vidro, efeito)
    return 1                                                 # chao / rocha / construcao


def _vg_scene():
    import numpy as np
    dg = bpy.context.evaluated_depsgraph_get()
    verts, tris, tobj, tcat, names = [], [], [], [], []
    skip_cols = ("00_REFERENCE", "_SCALE_REFERENCE")
    for o in bpy.data.objects:
        if o.type != "MESH" or o.name.startswith(("COL_", "PREVIEW_", "SCALE_", "OP_Plz_OreProxy")) or o.hide_render:
            continue
        if o.users_collection and o.users_collection[0].name in skip_cols:
            continue
        oe = o.evaluated_get(dg)
        me = oe.to_mesh()
        mw = o.matrix_world
        base = len(verts)
        verts += [tuple(mw @ v.co) for v in me.vertices]
        me.calc_loop_triangles()
        cats = [(_vg_cat(s.material.name) if s.material else 1) for s in o.material_slots] or [1]
        oi = len(names)
        names.append(o.name)
        for t in me.loop_triangles:
            tris.append(tuple(base + i for i in t.vertices))
            tobj.append(oi)
            tcat.append(cats[min(t.material_index, len(cats) - 1)])
        oe.to_mesh_clear()
    BV = BVHTree.FromPolygons(verts, tris, all_triangles=True)
    cverts, cpolys, cown, cnames, czmin = [], [], [], [], []
    for nm, vs, fs, kind in model():                 # V3: a colisao como o Roblox faz (COL_ + fechos das MeshParts)
        base = len(cverts)
        cverts += [Vector(v) for v in vs]
        ci = len(cnames)
        cnames.append(nm)
        czmin.append(min(v[2] for v in vs))
        for f in fs:
            cpolys.append([base + i for i in f])
            cown.append(ci)
    CB = BVHTree.FromPolygons(cverts, cpolys)
    return BV, np.array(tobj, np.int32), np.array(tcat, np.int8), names, CB, np.array(cown, np.int32), cnames, czmin


def visual(out_dir=None, lines=True):
    import numpy as np, json, collections, time
    t0 = time.time()
    BV, tobj, tcat, vnames, CB, cown, cnames, czmin = _vg_scene()
    DOWN, UP = Vector((0, 0, -1)), Vector((0, 0, 1))
    ZTOP, MAXH = 420.0, 16
    ST = VG_STEP
    xs = np.arange(-276.0 + 0.0371, 376.0 + 0.0371 + 1e-6, ST)
    ys = np.arange(-160.0 + 0.0613, 640.0 + 0.0613 + 1e-6, ST)
    NX, NY = len(xs), len(ys)
    zv = np.full((NY, NX), np.nan, np.float32)
    nv = np.zeros((NY, NX), np.float32)
    vo = np.full((NY, NX), -1, np.int32)
    vc = np.zeros((NY, NX), np.int8)
    zcb = np.full((NY, NX), np.nan, np.float32)
    surf = {}
    covered = np.zeros((NY, NX), bool)
    for j in range(NY):
        y = float(ys[j])
        for i in range(NX):
            x = float(xs[i])
            h = BV.ray_cast(Vector((x, y, ZTOP)), DOWN, 1000.0)
            if h[0] is not None:
                zv[j, i] = h[0].z
                nv[j, i] = abs(h[1].z)
                vo[j, i] = tobj[h[2]]
                vc[j, i] = tcat[h[2]]
            # todos os hits de colisao (de cima para baixo) -> intervalos solidos por caixa
            z = ZTOP
            iv = {}
            for _ in range(MAXH):
                c = CB.ray_cast(Vector((x, y, z)), DOWN, 1000.0)
                if c[0] is None:
                    break
                b = int(cown[c[2]])
                iv.setdefault(b, []).append(c[0].z)
                z = c[0].z - 0.002
            if not iv:
                continue
            ints = sorted(((min(v) if len(v) > 1 else czmin[b]), max(v)) for b, v in iv.items())
            u = []
            for a, b in ints:
                if u and a <= u[-1][1] + 0.05:
                    u[-1] = (u[-1][0], max(u[-1][1], b))
                else:
                    u.append((a, b))
            surf[(j, i)] = [(b, u[k + 1][0] if k + 1 < len(u) else 1e9) for k, (a, b) in enumerate(u)]
            if h[0] is not None:
                zz = h[0].z
                c = CB.ray_cast(Vector((x, y, zz + VG_TOL)), DOWN, 1000.0)
                if c[0] is not None:
                    zcb[j, i] = c[0].z
                covered[j, i] = any(a - 0.1 <= zz <= b + VG_TOL for a, b in u)
    t1 = time.time()
    # ---------------- alcance (BFS: pulo 7,2, corpo 5, cai de qualquer altura), a partir do spawn
    def cell(x, y):
        return int(round((y - ys[0]) / ST)), int(round((x - xs[0]) / ST))
    sj, si = cell(L.SPAWN[0], L.SPAWN[1])
    seen, q = set(), collections.deque()
    parent = {}
    for k, (hh, cc) in enumerate(surf.get((sj, si), [])):
        if abs(hh - L.T0) < 1.0:
            q.append((sj, si, k))
            seen.add((sj, si, k))
    reach = collections.defaultdict(list)
    NB = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    while q:
        j, i, k = q.popleft()
        hh, cc = surf[(j, i)][k]
        reach[(j, i)].append(hh)
        for dj, di in NB:
            jj, ii = j + dj, i + di
            S = surf.get((jj, ii))
            if not S:
                continue
            best = None
            for kk, (s, c2) in enumerate(S):
                if s <= hh + VG_JUMP and c2 >= max(s, hh) + VG_BODY and (best is None or s > S[best][0]):
                    best = kk
            if best is not None and (jj, ii, best) not in seen:
                seen.add((jj, ii, best))
                parent[(jj, ii, best)] = (j, i, k)
                q.append((jj, ii, best))
    reach_h = np.full((NY, NX, 4), np.nan, np.float32)
    for (j, i), hs in reach.items():
        hs = sorted(set(round(v, 2) for v in hs), reverse=True)[:4]
        reach_h[j, i, :len(hs)] = hs
    rmask = np.isfinite(reach_h[..., 0])
    # ---------------- U8: chao visual andavel sem colisao, perto (6) de algo alcancado e ao alcance do pulo
    with np.errstate(invalid="ignore"):
        walk = (nv >= 0.7) & np.isfinite(zv) & (zv > L.SEA + 0.25)     # abaixo do mar local: e agua, nao chao
        okcol = covered | (np.isfinite(zcb) & (zv - zcb <= VG_TOL))
    miss = walk & ~okcol
    R = int(round(VG_NEAR / ST))
    near = np.zeros_like(miss)
    for dj in range(-R, R + 1):
        for di in range(-R, R + 1):
            if dj * dj + di * di > R * R:
                continue
            sh = np.full_like(reach_h, np.nan)
            j0, j1 = max(0, dj), NY + min(0, dj)
            i0, i1 = max(0, di), NX + min(0, di)
            sh[j0 - dj:j1 - dj, i0 - di:i1 - di] = reach_h[j0:j1, i0:i1]
            with np.errstate(invalid="ignore"):
                near |= np.any((zv[..., None] <= sh + VG_JUMP) & (zv[..., None] >= sh - 25.0), axis=2)
    hit = miss & near
    A1 = ST * ST
    area = {c: float((hit & (vc == k)).sum() * A1) for c, k in (("chao", 1), ("telhado", 2), ("copa", 3), ("outro", 4))}
    lab = np.zeros(zv.shape, np.int32)
    regs = []
    for j, i in zip(*np.nonzero(hit & (vc != 3))):
        if lab[j, i]:
            continue
        n = len(regs) + 1
        st, cells = [(j, i)], []
        lab[j, i] = n
        while st:
            a, b = st.pop()
            cells.append((a, b))
            for dj, di in NB:
                aa, bb = a + dj, b + di
                if 0 <= aa < NY and 0 <= bb < NX and hit[aa, bb] and vc[aa, bb] != 3 and not lab[aa, bb]:
                    lab[aa, bb] = n
                    st.append((aa, bb))
        J = np.array([c[0] for c in cells])
        I = np.array([c[1] for c in cells])
        ob = collections.Counter(vnames[vo[a, b]] for a, b in cells).most_common(2)
        a0, b0 = cells[0]
        cul = None
        for dj in range(-R, R + 1):
            for di in range(-R, R + 1):
                aa, bb = a0 + dj, b0 + di
                if dj * dj + di * di > R * R or not (0 <= aa < NY and 0 <= bb < NX):
                    continue
                for hh in reach_h[aa, bb]:
                    if hh == hh and hh - 25.0 <= zv[a0, b0] <= hh + VG_JUMP and (cul is None or hh > cul[2]):
                        cul = (round(float(xs[bb]), 1), round(float(ys[aa]), 1), round(float(hh), 2))
        regs.append(dict(area=round(len(cells) * A1, 1), c=(round(float(xs[I].mean()), 1), round(float(ys[J].mean()), 1)),
                         bbox=(round(float(xs[I].min()), 1), round(float(ys[J].min()), 1), round(float(xs[I].max()), 1),
                               round(float(ys[J].max()), 1)), z=(round(float(np.nanmin(zv[J, I])), 1),
                                                                  round(float(np.nanmax(zv[J, I])), 1)),
                         cat=dict(collections.Counter({1: "chao", 2: "telhado", 4: "outro"}[int(vc[a, b])] for a, b in cells)),
                         objs=ob, vazio=int(np.sum(~np.isfinite(zcb[J, I]))), alcance=cul))
    regs.sort(key=lambda r: -r["area"])

    def chain(x, y, h):
        """caminho do BFS ate a superficie (x, y, h): os pontos onde a cota sobe > 1 (os degraus da escalada)"""
        j, i = cell(x, y)
        node = next(((j, i, k) for k, (hh, cc) in enumerate(surf.get((j, i), [])) if abs(hh - h) < 0.05), None)
        out = []
        while node in parent:
            pj, pi, pk = parent[node]
            h1, h0 = surf[node[:2]][node[2]][0], surf[(pj, pi)][pk][0]
            if h1 - h0 > 1.0:
                out.append((round(float(xs[node[1]]), 1), round(float(ys[node[0]]), 1), round(h1, 1)))
            node = (pj, pi, pk)
        return list(reversed(out))[-6:]
    for r in regs[:8]:
        if r["alcance"]:
            r["escalada"] = chain(*r["alcance"])
    # copa a <= 7,2 de um topo alcancavel (aviso)
    t2 = time.time()
    # ---------------- U8b: de cada superficie alcancada, raio para cima no visual
    inside = collections.Counter()
    inside_pts = []
    for (j, i), hs in reach.items():
        for hh in set(round(v, 2) for v in hs):
            r = BV.ray_cast(Vector((float(xs[i]), float(ys[j]), hh + 0.4)), UP, 4.6)
            if r[0] is None:
                continue
            d = r[0].z - hh
            back = r[1].z > 0
            kind = ("corpo" if d >= 1.5 else ("pe" if d > 0.3 + 0.05 else None)) if back else "cabeca"
            if kind and tcat[r[2]] == 3:              # V3: copa nao colide por regra (andar dentro da folhagem: aviso)
                kind = kind + "_copa"
            if kind:
                inside[kind] += A1
                inside_pts.append((kind, round(float(xs[i]), 1), round(float(ys[j]), 1), round(hh, 2), round(d, 2),
                                   vnames[tobj[r[2]]]))
    v3 = v3_checks(BV, tobj, tcat, vnames, surf, reach, xs, ys, cell, R, chain, CB, cown, cnames)
    t3 = time.time()
    # ---------------- U5: linhas finas (passo 0,2, uma linha a cada 3, nos eixos X e Y)
    gaps = []
    if lines:
        FS = 0.2

        def reach_at(x, y, z=None):
            j, i = cell(x, y)
            hs = reach_h[max(0, j - 1):j + 2, max(0, i - 1):i + 2]
            if z is None:
                return bool(np.isfinite(hs).any())
            with np.errstate(invalid="ignore"):
                return bool(((z >= hs - 1.0) & (z <= hs + VG_JUMP)).any())
        movel = np.array([n.startswith("VFX_") for n in vnames] + [False])
        copa = np.zeros(len(vnames) + 1, bool)      # objeto so de folhagem (lado de fresta entre copas: nao e vao)
        for oi in range(len(vnames)):
            cs = tcat[tobj == oi]
            copa[oi] = bool(len(cs)) and bool((cs == 3).all())
        xr = (float(xs[0]), float(xs[-1]))
        yr = (float(ys[0]), float(ys[-1]))
        for ax in ("x", "y"):
            fixed = np.arange(yr[0], yr[1] + 1e-6, 3.0) if ax == "x" else np.arange(xr[0], xr[1] + 1e-6, 3.0)
            run = np.arange(xr[0], xr[1] + 1e-6, FS) if ax == "x" else np.arange(yr[0], yr[1] + 1e-6, FS)
            for f in fixed:
                # so as linhas que passam pela faixa do jogador
                if ax == "x":
                    jf = int(round((f - ys[0]) / ST))
                    rowmask = rmask[max(0, jf - 1):jf + 2].any(axis=0)
                    if not rowmask.any():
                        continue
                    idx = np.nonzero(rowmask)[0]
                    lo, hi = xs[idx.min()] - 4.0, xs[idx.max()] + 4.0
                else:
                    jf = int(round((f - xs[0]) / ST))
                    colmask = rmask[:, max(0, jf - 1):jf + 2].any(axis=1)
                    if not colmask.any():
                        continue
                    idx = np.nonzero(colmask)[0]
                    lo, hi = ys[idx.min()] - 4.0, ys[idx.max()] + 4.0
                rr = run[(run >= lo) & (run <= hi)]
                n = len(rr)
                z = np.full(n, np.nan)
                nn = np.zeros(n)
                c = np.full(n, np.nan)
                ob = np.full(n, -1, np.int32)
                ct = np.zeros(n, np.int8)
                for b_, r_ in enumerate(rr):
                    x, y = (float(r_), float(f)) if ax == "x" else (float(f), float(r_))
                    h = BV.ray_cast(Vector((x, y, ZTOP)), DOWN, 1000.0)
                    if h[0] is None:
                        continue
                    z[b_], nn[b_], ob[b_], ct[b_] = h[0].z, abs(h[1].z), tobj[h[2]], tcat[h[2]]
                    cc = CB.ray_cast(Vector((x, y, h[0].z + VG_TOL)), DOWN, 1000.0)
                    if cc[0] is not None:
                        c[b_] = cc[0].z
                    up = CB.ray_cast(Vector((x, y, h[0].z + 0.05)), UP, 40.0)
                    if up[0] is not None and up[1].z > 0.0:      # visual DENTRO de uma caixa de colisao: coberto
                        c[b_] = h[0].z
                wk = np.isfinite(z) & (nn >= 0.7) & ~movel[ob] & (ct != 3) & (z > L.SEA + 0.25)
                with np.errstate(invalid="ignore"):
                    good = wk & np.isfinite(c) & (np.abs(z - c) <= VG_TOL)
                pos = (lambda k: (float(rr[k]), float(f))) if ax == "x" else (lambda k: (float(f), float(rr[k])))
                k = 0
                while k < n:                                  # A) vao de colisao sob visual continuo
                    if good[k] or not wk[k]:
                        k += 1
                        continue
                    s = k
                    while k < n and wk[k] and not good[k]:
                        k += 1
                    w = (k - s) * FS
                    if s > 0 and k < n and good[s - 1] and good[k] and 0.6 <= w <= 6.0 \
                            and abs(z[s - 1] - z[k]) < 0.6 and np.nanmax(np.abs(z[s:k] - z[s - 1])) < 0.6:
                        xm, ym = pos((s + k) // 2)
                        if reach_at(xm, ym, float(z[s - 1])):
                            gaps.append(("A_colisao", round(xm, 1), round(ym, 1), round(float(z[s - 1]), 2), round(w, 2),
                                         vnames[ob[(s + k) // 2]]))
                k = 1
                while k < n - 1:                              # B) fresta visual entre 2 pisos na mesma cota
                    if not wk[k - 1]:
                        k += 1
                        continue
                    zl = z[k - 1]
                    if np.isfinite(z[k]) and z[k] > zl - 0.8:
                        k += 1
                        continue
                    s = k
                    while k < n and (not np.isfinite(z[k]) or z[k] < zl - 0.8) and (k - s) * FS <= 4.2:
                        k += 1
                    w = (k - s) * FS
                    deep = (not np.isfinite(z[s:k]).all()) or float(zl - np.nanmin(z[s:k])) >= 2.3
                    if k < n and wk[k] and abs(z[k] - zl) < 0.6 and 0.6 <= w + 1e-6 <= 4.0 and deep:
                        xm, ym = pos((s + k) // 2)
                        if reach_at(xm, ym, float(zl)) and L.point_in_poly(xm, ym, L.ISLAND_RIM):
                            gaps.append(("B_fresta", round(xm, 1), round(ym, 1), round(float(zl), 2), round(w, 2),
                                         vnames[ob[s - 1]]))
                    k = max(k, s + 1)
    t4 = time.time()
    nA = sum(1 for g in gaps if g[0] == "A_colisao")
    nB = sum(1 for g in gaps if g[0] == "B_fresta")
    ok_chao = area["chao"] <= VG_LIM_CHAO
    ok_tel = area["telhado"] <= VG_LIM_TELHADO
    ok_in = inside["corpo"] == 0
    print("VISUAL grade %dx%d, colisoes %d, celulas alcancadas %d (%.0f studs2) | tempos raios %.0fs alcance+U8 %.0fs "
          "U8b %.0fs U5 %.0fs" % (NX, NY, len(cnames), int(rmask.sum()), rmask.sum() * A1, t1 - t0, t2 - t1, t3 - t2, t4 - t3))
    print(("OK   " if ok_chao else "FAIL ") + "VISUAL U8 chao/rocha alcancavel sem colisao: %.1f studs2 (limite %.0f)" % (
        area["chao"], VG_LIM_CHAO))
    print(("OK   " if ok_tel else "FAIL ") + "VISUAL U8 telhado alcancavel sem colisao: %.1f studs2 (limite 0)" % area["telhado"])
    print("AVISO VISUAL U8 copa ao alcance sem colisao: %.1f studs2 | outro (pano/vidro): %.1f" % (area["copa"], area["outro"]))
    print(("OK   " if ok_in else "FAIL ") + "VISUAL U8b corpo dentro do modelo: %.1f studs2" % inside["corpo"])
    print("%s VISUAL U8b pe afundando > 0,3: %.1f studs2 | cabeca dentro (teto < 5): %.1f studs2" % (
        "OK  " if inside["pe"] == 0 else "AVISO", inside["pe"], inside["cabeca"]))
    print("AVISO VISUAL U8b dentro da COPA (folhagem nao colide por regra): corpo %.1f, pe %.1f, cabeca %.1f studs2" % (
        inside["corpo_copa"], inside["pe_copa"], inside["cabeca_copa"]))
    if lines:
        print(("OK   " if nB == 0 else "FAIL ") + "VISUAL U5 frestas visuais >= 0,6 na faixa do jogador: %d" % nB)
        print(("OK   " if nA == 0 else "FAIL ") + "VISUAL U5 vaos de colisao >= 0,6: %d" % nA)
    for r in regs[:25]:
        print("VISUAL regiao %6.1f studs2 c=%s bbox=%s z=%s %s %s vazio=%d alcance_de=%s%s" % (
            r["area"], r["c"], r["bbox"], r["z"], r["cat"], [o[0] for o in r["objs"]], r["vazio"], r["alcance"],
            (" escalada=%s" % r["escalada"]) if r.get("escalada") else ""))
    ins = collections.Counter((k, o) for k, x, y, h, d, o in inside_pts)
    for (k, o), n in ins.most_common(12):
        ex = next(p for p in inside_pts if p[0] == k and p[5] == o)
        print("VISUAL dentro %-6s %-34s %6.1f studs2 ex=(%.1f, %.1f, h %.1f, d %.2f)" % (k, o, n * A1, ex[1], ex[2], ex[3], ex[4]))
    for g in gaps[:30]:
        print("VISUAL vao %s (%.1f, %.1f) z=%.2f larg=%.2f %s" % g)
    ok = ok_chao and ok_tel and ok_in and (not lines or (nA == 0 and nB == 0))
    print(("OK   " if ok else "FAIL ") + "VISUAL GATE (secao 9.8): %s" % ("VERDE" if ok else "VERMELHO"))
    print(("OK   " if v3["ok"] else "FAIL ") + "COLV3 GATE (o que se ve e o que colide): %s" % (
        "VERDE" if v3["ok"] else "VERMELHO"))
    ok = ok and v3["ok"]
    if out_dir:
        out_dir = os.path.abspath(out_dir)             # o save de imagem do Blender nao aceita caminho relativo
        os.makedirs(out_dir, exist_ok=True)
        json.dump(dict(area=area, dentro=dict(inside), U5_A=nA, U5_B=nB, regioes=regs[:200], dentro_pts=inside_pts[:400],
                       vaos=gaps[:400], alcancado_studs2=float(rmask.sum() * A1), verde=ok,
                       colv3={k: v for k, v in v3.items() if k != "ok"}),
                  open(os.path.join(out_dir, "gate_visual.json"), "w"), indent=1, default=str)
        _vg_map(os.path.join(out_dir, "gate_visual_mapa.png"), xs, ys, zv, rmask, hit, vc, inside_pts, gaps)
    return ok


# ------------------------------------------------------------------ COLV3 GATE (rodada 3)
# Mede o que o jogador (e o pet que segue o jogador) VAI ver no Roblox, sobre o modelo de colisao do Roblox:
#   AR      superficie ALCANCADA sem visual a <= 1,0 (em pe no ar: as guardas erguidas da V2)              -> FAIL > 50 studs2
#   PET_AR  topo de colisao ate +9 acima do chao alcancado (o PetsSeguidores raia de HRP+6) sem visual   -> AVISO (lista)
#   CASA    celula alcancada DENTRO da planta de lote FECHADO (sem interior/alpendre/portal) no terreo   -> FAIL > 0
#   TELHADO em pe SOBRE telhado ou com telhado a < 3 em cima (dentro do telhado)                       -> FAIL no castelo
#   MURO    topo de muro/estrutura do castelo alcancavel (> 3 acima do patio)                           -> AVISO (lista)
#   CAIXA   COL_ invisivel: contagem por categoria; topo de caixa NAO-piso acima do visual (amostra)    -> FAIL > 0
#           e nenhuma com tag CamOccluder (export: CAM_COL_AREAS vazio)
V3_LIM_AR = 50.0     # area total (studs2) alcancada com o visual a mais de 1,0 abaixo do pe (folga de quina de fecho)
V3_ALLOW_LOT = ("portal", "santuario", "honden")


def _lots_closed():
    out = []
    try:
        lots = L.block_lots()
    except Exception:
        return out
    for lt in lots:
        if lt["interior"] or lt["open"] or lt["kind"] in V3_ALLOW_LOT:
            continue
        out.append((lt["name"], L.lot_poly(lt, pad=-1.2), lt["z"]))
    return out


def v3_checks(BV, tobj, tcat, vnames, surf, reach, xs, ys, cell, R, chain, CB, cown, cnames):
    import collections
    DOWN, UP = Vector((0, 0, -1)), Vector((0, 0, 1))
    A1 = (xs[1] - xs[0]) * (ys[1] - ys[0])
    out = {}

    def under(x, y, hh):
        c = CB.ray_cast(Vector((x, y, hh + 0.3)), DOWN, 1.0)
        return cnames[cown[c[2]]] if c[0] is not None else "?"

    def grp(n):
        import re as _re
        return _re.sub(r"(_k\d+_\d+|_\d+)$", "", n)
    # AR: superficie alcancada sem visual a <= 0,6 abaixo / 0,5 acima
    air, air_pts = 0.0, []
    air_own = collections.Counter()
    roof_on, roof_in, castle_top = [], [], []
    court = L.CC
    for (j, i), hs in reach.items():
        x, y = float(xs[i]), float(ys[j])
        for hh in set(round(v, 2) for v in hs):
            h = BV.ray_cast(Vector((x, y, hh + 0.5)), DOWN, 1.5)
            if h[0] is None:
                air += A1
                own = under(x, y, hh)
                air_own[grp(own)] += A1
                if len(air_pts) < 400:
                    air_pts.append((round(x, 1), round(y, 1), round(hh, 2), own))
                continue
            cat = tcat[h[2]]
            on = vnames[tobj[h[2]]]
            if cat == 2:
                roof_on.append((round(x, 1), round(y, 1), round(hh, 2), on))
            u = BV.ray_cast(Vector((x, y, hh + 0.2)), UP, 3.0)
            if u[0] is not None and tcat[u[2]] == 2:
                roof_in.append((round(x, 1), round(y, 1), round(hh, 2), vnames[tobj[u[2]]]))
            if on.startswith("OP_Cas_") and hh > court + 3.0 and cat == 1:
                castle_top.append((round(x, 1), round(y, 1), round(hh, 2), on))
    out["ar_studs2"] = round(air, 1)
    out["ar_pts"] = air_pts[:200]
    out["ar_por_colisor"] = air_own.most_common(40)
    print(("OK   " if air <= V3_LIM_AR else "FAIL ") + "COLV3 AR superficie alcancada sem visual a <= 1,0 (em pe no ar): "
          "%.1f studs2 (limite %.0f)" % (air, V3_LIM_AR))
    for nm, a in air_own.most_common(14):
        ex = next(p for p in air_pts if grp(p[3]) == nm) if any(grp(p[3]) == nm for p in air_pts) else None
        print("AVISO COLV3 AR %-34s %7.1f studs2 ex=%s escalada=%s" % (nm, a, ex[:3] if ex else "-",
                                                                     chain(*ex[:3]) if ex else "-"))
    # PET_AR: o PetsSeguidores raia de HRP+6 (~ chao + 9) para baixo, respeitando CanCollide
    pet, pet_pts = 0.0, []
    for (j, i), S in surf.items():
        hs = [v for (jj, ii) in ((j + a, i + b) for a in (-2, -1, 0, 1, 2) for b in (-2, -1, 0, 1, 2))
              for v in reach.get((jj, ii), ())]
        if not hs:
            continue
        H = max(hs)
        own = max(reach.get((j, i), [-1e9]))
        tops = [t for t, c in S if t <= H + 9.0]
        if not tops:
            continue
        t = max(tops)
        if t <= own + 0.3:
            continue
        x, y = float(xs[i]), float(ys[j])
        h = BV.ray_cast(Vector((x, y, t + 0.5)), DOWN, 1.0)
        if h[0] is None:
            pet += A1
            if len(pet_pts) < 400:
                pet_pts.append((round(x, 1), round(y, 1), round(t, 2)))
    out["pet_ar_studs2"] = round(pet, 1)
    out["pet_ar_pts"] = pet_pts[:60]
    print("AVISO COLV3 PET_AR topo de colisao ate +9 do chao alcancado sem visual (o pet do jogador pousa ali): %.1f "
          "studs2 %s" % (pet, pet_pts[:6]))
    # CASA: alcance dentro de lote fechado (terreo)
    lots = _lots_closed()
    inside_lot = collections.Counter()
    ex = {}
    for nm, poly, zl in lots:
        xs_ = [p[0] for p in poly]
        ys_ = [p[1] for p in poly]
        for (j, i), hs in reach.items():
            x, y = float(xs[i]), float(ys[j])
            if not (min(xs_) <= x <= max(xs_) and min(ys_) <= y <= max(ys_)):
                continue
            if not L.point_in_poly(x, y, poly):
                continue
            for hh in hs:
                if not (zl - 0.6 <= hh <= zl + 4.0):
                    continue
                # DENTRO da casa = coberto (algo visivel a <= 12 em cima) e fechado (>= 6 de 8 direcoes batem em visual
                # a <= 8): em cima de alpendre/hisashi ou em patio aberto do lote nao conta
                P0 = Vector((x, y, hh + 1.5))
                u = BV.ray_cast(P0, UP, 8.0)
                if u[0] is None or tcat[u[2]] == 3:
                    continue
                nh = 0
                for kk in range(8):
                    a = kk * math.pi / 4
                    if BV.ray_cast(P0, Vector((math.cos(a), math.sin(a), 0.0)), 6.0)[0] is not None:
                        nh += 1
                if nh < 8:
                    continue
                inside_lot[nm] += A1
                ex.setdefault(nm, (round(x, 1), round(y, 1), round(hh, 2)))
                break
    nin = sum(inside_lot.values())
    out["casa"] = {k: (round(v, 1), ex[k]) for k, v in inside_lot.items()}
    print(("OK   " if nin == 0 else "FAIL ") + "COLV3 CASA alcance dentro de lote FECHADO (terreo; atravessar parede): "
          "%.1f studs2 em %d lotes %s" % (nin, len(inside_lot), [(k, out["casa"][k]) for k in list(inside_lot)[:6]]))
    for k in list(inside_lot)[:4]:
        e = ex[k]
        print("AVISO COLV3 CASA %s em %s sobre %s escalada=%s" % (k, e, under(*e), chain(*e)))
    # INTERIOR: os 4 interiores vivos da capital e o salao do castelo (luzes L_OPCap_Int_* / L_OPCas_Hall_*) tem de ser
    # ALCANCADOS pela porta modelada (o fecho convexo nao pode fechar a casa)
    ints, bad_int = {}, []
    for o in bpy.data.objects:
        if o.type == "LIGHT" and o.name.startswith(("L_OPCap_Int_", "L_OPCas_Hall_")):
            key = "Salao do castelo" if o.name.startswith("L_OPCas_Hall_") else o.name[len("L_OPCap_Int_"):]
            ints.setdefault(key, []).append(o.location.copy())
    for key, locs in sorted(ints.items()):
        ok_i = False
        for loc in locs:
            f = CB.ray_cast(Vector((loc.x, loc.y, loc.z)), DOWN, 30.0)
            if f[0] is None:
                continue
            j0, i0 = cell(loc.x, loc.y)
            for dj in (-2, -1, 0, 1, 2):
                for di in (-2, -1, 0, 1, 2):
                    if any(abs(hh - f[0].z) < 0.8 for hh in reach.get((j0 + dj, i0 + di), ())):
                        ok_i = True
        if not ok_i:
            bad_int.append(key)
        print(("OK   " if ok_i else "FAIL ") + "COLV3 INTERIOR %s alcancado pela porta modelada" % key)
    out["interior_fechado"] = bad_int
    # TELHADO
    cas_roof = [p for p in roof_on + roof_in if p[3].startswith("OP_Cas_")]
    out["telhado_sobre"] = roof_on[:60]
    out["telhado_dentro"] = roof_in[:60]
    print(("OK   " if not cas_roof else "FAIL ") + "COLV3 TELHADO do castelo alcancado (sobre ou dentro): %d celulas %s" % (
        len(cas_roof), cas_roof[:4]))
    if cas_roof:
        cr = collections.Counter(grp(under(p[0], p[1], p[2])) for p in cas_roof)
        print("AVISO COLV3 TELHADO castelo por colisor: %s | escalada ate %s: %s" % (cr.most_common(6), cas_roof[0][:3],
                                                                                     chain(*cas_roof[0][:3])))
    print("AVISO COLV3 TELHADO (fora do castelo) alcancado: sobre %d celulas, dentro (telhado a < 3 em cima) %d celulas %s" % (
        len([p for p in roof_on if not p[3].startswith("OP_Cas_")]),
        len([p for p in roof_in if not p[3].startswith("OP_Cas_")]), (roof_on + roof_in)[:4]))
    out["castelo_topo"] = castle_top[:80]
    regs = collections.Counter((round(p[0] / 10) * 10, round(p[1] / 10) * 10) for p in castle_top)
    print("AVISO COLV3 MURO topo de estrutura do castelo alcancavel (> 3 acima do patio): %d celulas em %d trechos de 10 "
          "%s" % (len(castle_top), len(regs), regs.most_common(6)))
    # CAIXA: COL_ invisiveis por categoria; topo de caixa nao-piso acima do visual
    cats = collections.Counter()
    above = []
    for o in bpy.data.objects:
        if o.type != "MESH" or not o.name.startswith("COL_") or o.name.startswith("COL_QA_"):
            continue
        if o.name.startswith(op_col.V3_FLOOR_COL):
            cats["PISO_PLANTA"] += 1
            continue
        if o.name.startswith("COL_OP_V3Slab"):
            cats["PISO_MODULO"] += 1
            continue
        if o.name.startswith(op_col.V3_TRUNK_COL):
            cats["TRONCO"] += 1                       # dentro do tronco visivel (o topo fica DENTRO do tronco)
            continue
        if o.name.startswith("COL_OP_Fall"):
            cats["QUEDA"] += 1
        else:
            cats["JOGO"] += 1
        ws = [o.matrix_world @ v.co for v in o.data.vertices]
        zt = max(v.z for v in ws)
        cx = sum(v.x for v in ws) / len(ws)
        cy = sum(v.y for v in ws) / len(ws)
        h = BV.ray_cast(Vector((cx, cy, zt + 0.6)), DOWN, 2.0)
        if not (o.name.startswith(("COL_GateOnePunchMan", "COL_OPAnchorGuard", "COL_OP_WheelEnvelope"))) and                 (h[0] is None or zt - h[0].z > 1.0):
            above.append(o.name)
    out["caixas"] = dict(cats)
    out["caixa_acima"] = above[:40]
    nbar = cats["JOGO"] + cats["QUEDA"] + cats["TRONCO"]
    print(("OK   " if nbar < 150 and not above else "FAIL ") + "COLV3 CAIXA invisiveis por categoria %s (barreira "
          "= JOGO + QUEDA + TRONCO = %d, meta < 150); caixa de barreira com topo > 1 acima do visual: %s" % (
              dict(cats), nbar, above[:8] or "nenhuma"))
    out["ok"] = air <= V3_LIM_AR and nin == 0 and not cas_roof and nbar < 150 and not above and not bad_int
    return out


def _vg_map(path, xs, ys, zv, rmask, hit, vc, inside_pts, gaps):
    """mapa de cima (como o U8_mapa da auditoria): cinza = visual, verde = alcancado com colisao, vermelho = chao sem
    colisao, laranja = telhado, magenta = copa, ciano = corpo dentro, azul = pe afundando, amarelo = vaos (U5)"""
    import numpy as np
    NY, NX = zv.shape
    img = np.zeros((NY, NX, 4), np.float32)
    img[..., 3] = 1.0
    img[..., 2] = 0.30
    zn = np.where(np.isfinite(zv), np.clip((zv - 20.0) / 140.0, 0, 1), 0)
    vis = np.isfinite(zv)
    for k in range(3):
        img[..., k] = np.where(vis, 0.25 + 0.45 * zn, img[..., k])
    img[rmask] = (0.25, 0.62, 0.30, 1.0)
    img[hit & (vc == 1)] = (0.95, 0.10, 0.10, 1.0)
    img[hit & (vc == 2)] = (1.0, 0.55, 0.05, 1.0)
    img[hit & (vc == 3)] = (0.90, 0.20, 0.90, 1.0)
    img[hit & (vc == 4)] = (0.60, 0.10, 0.10, 1.0)

    def put(x, y, col, r=1):
        i = int(round((x - xs[0]) / (xs[1] - xs[0])))
        j = int(round((y - ys[0]) / (ys[1] - ys[0])))
        img[max(0, j - r):j + r + 1, max(0, i - r):i + r + 1] = col
    for k, x, y, h, d, o in inside_pts:
        put(x, y, (0.1, 0.9, 0.95, 1.0) if k == "corpo" else ((0.2, 0.3, 1.0, 1.0) if k == "pe" else (0.6, 0.6, 1.0, 1.0)), 0)
    for g in gaps:
        put(g[1], g[2], (1.0, 1.0, 0.1, 1.0), 2)
    im = bpy.data.images.new("QA_VisualMap", NX, NY, alpha=False)
    im.pixels.foreach_set(img.ravel())
    im.filepath_raw = path
    im.file_format = "PNG"
    im.save()
    bpy.data.images.remove(im)
    print("VISUAL mapa ->", path)


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    lines_ = "semlinhas" not in argv
    argv = [a for a in argv if a != "semlinhas"]
    argv = argv or ["nav", "tech", "markers", "clear", "budget", "gate", "visual"]
    if any(a in argv for a in ("nav", "clear", "visual", "budget", "tech", "col")):
        prep()                                        # V3: colisao pela forma do visual (em memoria)
    if "col" in argv and "visual" not in argv:
        argv.append("visual")
    if "visual" in argv:
        visual(os.environ.get("OP_QA_OUT"), lines=lines_)
    if "nav" in argv:
        nav()
    if "markers" in argv:
        markers()
    if "clear" in argv:
        clear()
    if "tech" in argv:
        tech()
    if "budget" in argv:
        budget()
    if "gate" in argv:
        gate()
