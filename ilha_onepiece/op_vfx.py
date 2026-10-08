# op_vfx - VFX da Ilha 5 (ONE PIECE / WANO), M4 (PLANO_OP secoes 1.3 "Pecas moveis / VFX", 7 "Agua/efeitos", 10;
# PROMPT_USUARIO secao 17: "petalas, agua, fumaca e movimentos ambientais discretos e otimizados; nao criar um emissor
# ou script caro para cada elemento repetido"). Zona dressing, ANTES do op_lights (que roda por ultimo).
# NAO inventa sistema: so grava nos marcadores o que o jogo JA consome (contrato da Ilha 4,
# ilha_demonslayer/roblox/DemonSlayerIsland.lua 'receita' + ILHAS_Cliente 'IlhaVFX'):
#   1. EMISSORES: cada FX_* com vfx='emissor' vira 1 ParticleEmitter (Part invisivel + tag IlhaVFX, ligado/desligado
#      pela distancia 'Dist' no cliente). As chaves sao as do emissor() das ilhas: tex, cor (cor_ini / cor_fim), rate,
#      vida, vel, tam, fim, transp, luz, infl, spread, area ("lado,altura,frente" nos eixos do marcador), forma, Dist
#      + acc_up (aceleracao vertical) e drift (deriva ao longo da frente do marcador = o VENTO).
#      PETALAS (4 emissores GRANDES por zona, nenhum por arvore):
#        FX_Petals_Tree      (op_core; aqui REPOSTO) caixa sob o LOBO OESTE da copa (o fim do arco, que enquadra o
#                            castelo pela esquerda): cai sobre a subida CasteloA/B e o lado oeste do patio. Medida na
#                            copa (faces Flower_OP do OP_Tree_Bloom), fora da torre (x <= beiral oeste).
#        FX_Petals_TreeRoots NOVO: caixa sob o LOBO LESTE (sobre as raizes/base da arvore no patio).
#        FX_Petals_Plaza     NOVO: deriva sobre a metade NORTE da praca (vem do adro com o vento), 5..22 acima do piso.
#        FX_Petals_Street    NOVO: rua de chegada + patio do torii (cerejeiras dos ombros e do recanto).
#        tex 'petala': o TEX das ilhas nao tem petala -> cai em 'fumaca' (po rosa macio, aceitavel). Proposta para o
#        M5 (1 linha de dado, nao sistema): TEX.petala = 'rbxassetid://120563379296122' (leaf_particle, ja usado pelo
#        OreVFX do jogo) no Core.OnePieceIsland. Ver roblox/AreaAtmosphere_area5.md.
#      AGUA (posicao/props sao do op_water, medidos na pedra; aqui so ENTRAM as chaves do emissor, como no ds_vfx):
#        FX_Fall_Castle_Lip/Step/Base + FX_Mist_CastleFall (cachoeira do castelo e bacia do adro),
#        FX_Fall_E_Lip/Base (queda leste -> enseada), FX_Fall_W_Lip/Base (queda oeste -> mar). DIA: branco-azulado
#        iluminado pelo sol (infl 1, luz ~0), transparente, sem cobrir arquitetura.
#      FUMACA: NENHUMA. A capital nao tem chamine nem cozinha com fogo (procurado em todos os op_*.py): fumaca sem
#        fonte seria efeito inventado.
#   2. PECAS MOVEIS (tag IlhaMovel do export; o LocalScript gira por rpm em volta de pivot/axis): CONFERIDAS, nao
#      refeitas: VFX_OP_Wheel (op_water) - pivo no centro da roda medida, eixo horizontal perpendicular ao canal, pa de
#      BAIXO andando a favor da correnteza, velocidade de aro plausivel; VFX_OPSUM_* (op_summon) - aneis e estrela no
#      MESMO pivo (o L_OPSum_Star), rpm != 0, como os VFX_DSSUM_* da Ilha 4 (mesmo codigo da Ilha 1).
#   3. PREVIA (so Blender, 00_REFERENCE / PREVIEW_VFX_*, fora do export e fora do QA): petalas (quads rosa pequenos na
#      densidade de regime = rate x vida x fracao visivel), espuma/nevoa das quedas. Materiais RBX_PREVIEW_VFX_*
#      TRANSPARENTES: o fm_lib.apply_preview('roblox') pula RBX_* (licao da Ilha 4: previa virava bloco branco
#      opaco no modo roblox) -> le igual nos 2 modos. OP_VFX_PREVIEW=0 desliga.
import os, math, random
import bpy, bmesh
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
import op_lib as DL
from op_lib import yaw_to, camera
import op_layout as L

T0, T1, P, CF, CC, SEA = L.T0, L.T1, L.P, L.CF, L.CC, L.SEA
WIND = (0.0, -1.0)            # vento das petalas: do castelo/arvore (N) para a ponte (S) - eixo da concept
# petala na MESMA linguagem das aprovadas do lobby Murim (lobby_area/murim/kit/export/hex_fase9_vegetacao.lua: cor
# 255,170,195 -> 248,140,170, tamanho 0,32 -> 0,22, velocidade 0,6..1,4, queda -1,1, giro +-60; textura padrao = a
# reserva 'petala' do Core.OnePieceIsland): aqui 0,36 (vistas um pouco mais de longe) e so 'rotv' a mais (o receita()
# do OnePieceIsland le rotv).
PETAL = dict(tex="petala", cor="255,172,198", cor_fim="248,140,170", vel=1.0, tam=0.36, fim=0.7, transp=0.22,
             luz=0.0, infl=1.0, spread="180,180", acc_up=-1.1, drift=0.5, rotv=60.0, forma="Box")
PREVIEW_K = 1.6               # previa: petala 1,6x maior so para LER na folha de 960 (o marcador grava o tamanho real)
BOX = {}
FLOOR = {"FX_Petals_Tree": L.CL, "FX_Petals_TreeRoots": CC, "FX_Petals_Plaza": P, "FX_Petals_Street": T0}   # previa
WATER = dict(cor="236,242,248", vida=2.6, vel=2.5, transp=0.6, infl=1.0, luz=0.05, tex="nevoa", forma="Box")


# ------------------------------------------------------------------ medidas na geometria
def canopy_lobes():
    """faces Flower_OP do OP_Tree_*: lobo OESTE (x < beiral oeste da torre) e lobo LESTE (x > beiral leste). Volta
    {"W": (x0, x1, y0, y1, z_baixo), "E": ...} com z_baixo = percentil 5 das faces de baixo do lobo"""
    pts = []
    for o in bpy.data.objects:
        if o.type != "MESH" or not o.name.startswith("OP_Tree_"):
            continue
        me, mw = o.data, o.matrix_world
        idx = {i for i, m in enumerate(me.materials) if m and m.name.startswith("Flower_OP")}
        for p in me.polygons:
            if p.material_index in idx:
                pts.append(mw @ p.center)
    if not pts:
        print("AVISO op_vfx: copa sem faces Flower_OP (op_tree ausente?)")
        return {}
    eave = L.KEEP_TIERS[0][0] + 7.0           # meia largura da torre + beiral (a caixa nao entra na torre)
    out = {}
    for k, sel in (("W", lambda q: q.x < -eave), ("E", lambda q: q.x > eave)):
        q = [p for p in pts if sel(p)]
        if len(q) < 50:
            continue
        zs = sorted(p.z for p in q)
        xs = sorted(p.x for p in q)
        ys = sorted(p.y for p in q)
        n = len(q)
        out[k] = (xs[n // 20], xs[-n // 20 - 1], ys[n // 20], ys[-n // 20 - 1], zs[n // 20])
        print("VFX medida copa lobo %s: x %.1f..%.1f y %.1f..%.1f, baixo da copa %.1f (%d faces)" % ((k,) + out[k] + (n,)))
    return out


def _ground_bvh():
    verts, polys = [], []
    for o in bpy.data.objects:
        if o.type != "MESH" or not o.name.startswith("COL_"):
            continue
        mw = o.matrix_world
        b = len(verts)
        verts += [mw @ v.co for v in o.data.vertices]
        polys += [[b + i for i in p.vertices] for p in o.data.polygons]
    return BVHTree.FromPolygons(verts, polys) if polys else None


# ------------------------------------------------------------------ receitas
def _emit(o, **kw):
    for k, v in kw.items():
        o[k] = v
    o["vfx"] = "emissor"


def _marker(name, loc, yaw, props):
    o = bpy.data.objects.get(name)
    if o is None:
        o = DL.mk(name, loc, (0.0, 0.0, yaw), 4.0, "CUBE", props=props)
    else:
        o.location = loc
        o.rotation_euler = (0.0, 0.0, yaw)
        for k, v in props.items():
            o[k] = v
    return o


def _box_marker(name, x0, x1, y0, y1, z0, z1, rate, vida, dist, note):
    """caixa alinhada aos eixos locais com a frente = vento (-Y): lado = X, frente = Y"""
    wy = yaw_to(*WIND)
    o = _marker(name, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), wy, {"fx": "petalas"})
    _emit(o, rate=rate, vida=vida, Dist=dist, area="%.1f,%.1f,%.1f" % (x1 - x0, z1 - z0, y1 - y0), note=note, **PETAL)
    BOX[name] = (x0, x1, y0, y1, z0, z1)         # so para a previa (fora do marcador: tupla de 6 viraria tabela
    return o                                     #   no SetAttribute do montar e quebraria a montagem)


def petals():
    out = []
    lobes = canopy_lobes()
    if "W" in lobes:
        x0, x1, y0, y1, zb = lobes["W"]
        z1 = zb - 3.0
        z0 = max(CC + 14.0, z1 - 62.0)
        out.append(_box_marker("FX_Petals_Tree", x0, x1, y0, y1, z0, z1, 10.0, 11.0, 320.0,
                               "REPOSTO pelo op_vfx (era 1 esfera no meio da copa a 284): caixa sob o lobo OESTE medido "
                               "da copa, 3 abaixo das flores ate %.0f (patio + 14); cai sobre a subida do castelo e o "
                               "lado oeste do patio; fora da torre" % z0))
    if "E" in lobes:
        x0, x1, y0, y1, zb = lobes["E"]
        z1 = zb - 3.0
        z0 = max(CC + 8.0, z1 - 50.0)
        out.append(_box_marker("FX_Petals_TreeRoots", x0, x1, y0, y1, z0, z1, 8.0, 11.0, 260.0,
                               "NOVO (op_vfx): caixa sob o lobo LESTE medido (sobre as raizes e a base da arvore)"))
    pz = [p[0] for p in L.PLAZA]
    py = [p[1] for p in L.PLAZA]
    out.append(_box_marker("FX_Petals_Plaza", min(pz) + 16.0, max(pz) - 16.0, 196.0, max(py) - 8.0, P + 5.0,
                           P + 22.0, 16.0, 8.0, 260.0,
                           "NOVO (op_vfx): deriva sobre a METADE NORTE da praca (5..22 acima do piso): as petalas vem "
                           "do adro/arvore com o vento para a ponte; particula sem colisao, nao atrapalha a mineracao"))
    out.append(_box_marker("FX_Petals_Street", -14.0, 14.0, 14.0, 112.0, T1 + 5.0, T1 + 20.0, 5.0, 8.0, 160.0,
                           "NOVO (op_vfx): rua de chegada + patio do torii (cerejeiras dos ombros de rocha e do recanto)"))
    return [o.name for o in out]


def water():
    """so as chaves do emissor nos marcadores do op_water (posicao/props medidos na pedra ficam como estao). Nomes com
    letra (Castle/E/W): o Core.OnePieceIsland do M5 usa '^FX_Fall_%w+_Lip$' (a DS usa %d+) para o deslocamento de
    nascimento da crista/degrau/pe"""
    spec = {
        "FX_Fall_Castle_Lip": dict(rate=2.0, tam=3.0, Dist=260.0, area="%s,1,1.2"),
        "FX_Fall_Castle_Step": dict(rate=6.0, tam=5.0, Dist=240.0, area="%s,1.2,2"),
        "FX_Fall_Castle_Base": dict(rate=10.0, tam=7.5, Dist=260.0, area="%s,2,5"),
        "FX_Fall_E_Lip": dict(rate=1.5, tam=2.5, Dist=300.0, area="%s,1,1.2"),
        "FX_Fall_E_Base": dict(rate=6.0, tam=9.0, Dist=420.0, area="%s,2,6"),
        "FX_Fall_W_Lip": dict(rate=1.5, tam=2.8, Dist=300.0, area="%s,1,1.2"),
        "FX_Fall_W_Base": dict(rate=6.0, tam=10.0, Dist=420.0, area="%s,2,6"),
    }
    out = []
    for nm, kw in spec.items():
        o = bpy.data.objects.get(nm)
        if o is None:
            print("AVISO op_vfx: %s nao existe (op_water)" % nm)
            continue
        w = float(o.get("width", 4.0))
        kw = dict(kw)
        kw["area"] = kw["area"] % ("%.1f" % w)
        d = dict(WATER)
        d.update(kw)
        _emit(o, **d)
        out.append(nm)
    o = bpy.data.objects.get("FX_Mist_CastleFall")
    if o is not None:
        r = float(o.get("radius", 11.0))
        _emit(o, tex="nevoa", cor="232,238,246", rate=1.0, vida=10.0, vel=0.4, tam=9.0, fim=1.3, transp=0.9, luz=0.0,
              infl=1.0, spread="90,10", acc_up=0.05, drift=0.2, area="%.0f,1.5,%.0f" % (2 * r, r), forma="Box",
              Dist=220.0)
        out.append(o.name)
    return out


# ------------------------------------------------------------------ pecas moveis: conferencia
def movers():
    ok = True
    wh = bpy.data.objects.get("VFX_OP_Wheel")
    if wh is None:
        print("AVISO op_vfx: sem VFX_OP_Wheel")
        ok = False
    else:
        mw = wh.matrix_world
        vs = [mw @ v.co for v in wh.data.vertices]
        c = Vector(((min(v.x for v in vs) + max(v.x for v in vs)) / 2, (min(v.y for v in vs) + max(v.y for v in vs)) / 2,
                    (min(v.z for v in vs) + max(v.z for v in vs)) / 2))
        piv = Vector(wh["pivot"])
        ax = Vector(wh["axis"]).normalized()
        rpm = float(wh.get("rpm", 0.0))
        R = max((Vector((0.0, v.y, v.z)) - Vector((0.0, piv.y, piv.z))).length for v in vs) if abs(ax.x) > 0.9 else 0.0
        # correnteza no ponto da roda: trecho do WATER_CanalW mais perto do pivo
        flow = None
        cw = bpy.data.objects.get("WATER_CanalW")
        if cw is not None and "waypoints" in cw.keys():
            pts = [Vector(tuple(float(t) for t in s.split(","))) for s in cw["waypoints"].split(";")]
            best = None
            for a, b in zip(pts, pts[1:]):
                d = b - a
                d.z = 0.0
                if d.length < 1e-6:
                    continue
                t = max(0.0, min(1.0, (piv - a).dot(d) / d.length_squared))
                dist = ((a + d * t) - piv).xy.length
                if best is None or dist < best[0]:
                    best = (dist, d.normalized())
            flow = best[1] if best else None
        # pa de baixo: r = (0, 0, -R); v = w x r (mao direita em volta do eixo)
        vb = (ax * (rpm * 2 * math.pi / 60.0)).cross(Vector((0.0, 0.0, -R)))
        rim = vb.length
        good_piv = (c.yz - piv.yz).length < 0.3
        good_ax = flow is None or abs(ax.dot(flow)) < 0.1
        good_dir = flow is None or vb.dot(flow) > 0
        good_v = 0.8 <= rim <= 4.5
        ok &= good_piv and good_ax and good_dir and good_v
        print(("OK   " if good_piv else "FAIL ") + "VFX roda: pivo (%.1f, %.1f, %.1f) x centro medido (%.1f, %.1f, %.1f)" % (
            tuple(piv) + tuple(c)))
        print(("OK   " if good_ax and good_dir else "FAIL ") + "VFX roda: eixo %s, correnteza %s, pa de baixo anda %s "
              "(a favor da agua)" % (tuple(round(a, 2) for a in ax), tuple(round(a, 2) for a in flow) if flow else "-",
                                     tuple(round(a, 2) for a in vb)))
        print(("OK   " if good_v else "FAIL ") + "VFX roda: %.1f rpm, raio %.2f -> aro a %.2f studs/s (0,8..4,5)" % (
            rpm, R, rim))
    sums = [o for o in bpy.data.objects if o.name.startswith("VFX_OPSUM_")]
    star = bpy.data.objects.get("L_OPSum_Star")
    for o in sums:
        piv = Vector(o.get("pivot", (0, 0, 0)))
        rpm = float(o.get("rpm", 0.0))
        same = star is None or (piv - star.matrix_world.translation).length < 0.5
        good = same and abs(rpm) > 0 and "axis" in o.keys()
        ok &= good
        print(("OK   " if good else "FAIL ") + "VFX summon %-18s rpm %4.1f eixo %s pivo %s" % (
            o.name, rpm, tuple(round(a, 2) for a in o.get("axis", (0, 0, 0))),
            "= estrela" if same else "FORA da estrela"))
    return ok


# ------------------------------------------------------------------ previa (so Blender)
def _pmat(name, rgb, alpha, emit=0.0):
    """material TRANSPARENTE da previa com prefixo RBX_ (o apply_preview('roblox') nao o refaz opaco)"""
    name = "RBX_" + name
    mt = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mt.diffuse_color = (*rgb, alpha)
    mt.use_nodes = True
    nd = next(n for n in mt.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    nd.inputs["Base Color"].default_value = (*rgb, 1.0)
    nd.inputs["Roughness"].default_value = 1.0
    nd.inputs["Alpha"].default_value = alpha
    if emit > 0:
        nd.inputs["Emission Color"].default_value = (*rgb, 1.0)
        nd.inputs["Emission Strength"].default_value = emit
    for attr, val in (("surface_render_method", "BLENDED"), ("blend_method", "BLEND"), ("use_transparent_shadow", True)):
        try:
            setattr(mt, attr, val)
        except Exception:
            pass
    return mt


def _link(ob):
    coll = bpy.data.collections.get("00_REFERENCE")
    (coll or bpy.context.scene.collection).objects.link(ob)
    try:
        ob.visible_shadow = False
    except Exception:
        pass
    return ob


def _puffs(name, items, mats):
    """items: (centro, raio, (sx, sy, sz), indice do material) -> 1 objeto de icosferas suaves"""
    bm = bmesh.new()
    for c, r, sc, mi in items:
        M = Matrix.Translation(Vector(c)) @ Matrix.Diagonal((r * sc[0], r * sc[1], r * sc[2], 1.0))
        res = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=M)
        for f in {f for v in res["verts"] for f in v.link_faces}:
            f.material_index = mi
            f.smooth = True
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for mt in mats:
        me.materials.append(mt)
    return _link(bpy.data.objects.new(name, me))


def _petal_cloud(name, markers, mats, rng):
    """petalas no REGIME: rate x vida particulas vivas; a fracao visivel (transparencia 1 nos 20% iniciais e somindo
    nos ultimos 25%) ~ 60%. Cada uma nasce num ponto da caixa e ja caiu 0,5 x acc x idade^2 e derivou com o vento"""
    bm = bmesh.new()
    wx, wy = WIND
    n_tot = 0
    gb = _ground_bvh()            # M6b (item 49): petala a menos de 0,6 do chao REAL (colisao) ja pousou -> fora
    n_chao = 0
    for o in markers:
        x0, x1, y0, y1, z0, z1 = BOX[o.name]
        n = int(o["rate"] * o["vida"] * 0.6)
        a_up, dr, life = float(o["acc_up"]), float(o["drift"]), float(o["vida"])
        for _ in range(n):
            age = rng.uniform(0.2, 0.8) * life
            fall = 0.5 * a_up * age * age
            drift = 0.5 * dr * age * age
            c = Vector((rng.uniform(x0, x1) + wx * drift, rng.uniform(y0, y1) + wy * drift, rng.uniform(z0, z1) + fall))
            if c.z < FLOOR.get(o.name, -1e9) + 0.3:
                continue                         # ja pousou / passou do piso: no jogo some na transparencia
            if gb is not None:
                h = gb.ray_cast(c, Vector((0.0, 0.0, -1.0)), 0.6)
                if h[0] is not None:
                    n_chao += 1
                    continue
            s = float(o["tam"]) * PREVIEW_K * rng.uniform(0.75, 1.0)
            R = Matrix.Rotation(rng.uniform(0, 6.283), 4, "Z") @ Matrix.Rotation(rng.uniform(-1.2, 1.2), 4, "X")
            vs = [bm.verts.new(c + (R @ Vector(p)).to_3d()) for p in
                  ((-0.5 * s, 0.0, 0.0), (0.0, -0.32 * s, 0.0), (0.5 * s, 0.0, 0.0), (0.0, 0.32 * s, 0.0))]
            f = bm.faces.new(vs)
            f.material_index = rng.randrange(len(mats))
        n_tot += n
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for mt in mats:
        me.materials.append(mt)
    print("VFX previa petalas: %d quads (%s); %d no chao descartadas" % (n_tot, ", ".join(o.name for o in markers),
                                                                        n_chao))
    return _link(bpy.data.objects.new(name, me))


def preview():
    for o in [o for o in bpy.data.objects if o.name.startswith("PREVIEW_VFX_")]:
        bpy.data.objects.remove(o, do_unlink=True)
    rng = random.Random(5505)
    pet = [o for o in bpy.data.objects if o.name in BOX]
    if pet:
        mats = [_pmat("PREVIEW_VFX_Petal_A", (0.95, 0.58, 0.74), 0.92), _pmat("PREVIEW_VFX_Petal_B", (0.86, 0.30, 0.55), 0.92)]
        _petal_cloud("PREVIEW_VFX_Petals", pet, mats, rng)
    # espuma (degraus e pes) e nevoa baixa da bacia: brancas e transparentes (dia)
    foam = [_pmat("PREVIEW_VFX_Foam", (0.84, 0.88, 0.92), 0.16)]
    items = []
    for nm, k, up in (("FX_Fall_Castle_Step", 0.40, 0.6), ("FX_Fall_Castle_Base", 0.42, 0.8), ("FX_Fall_E_Base", 0.45, 1.0),
                      ("FX_Fall_W_Base", 0.45, 1.0)):
        o = bpy.data.objects.get(nm)
        if o is None:
            continue
        w = float(o.get("width", 4.0))
        for _ in range(8):
            c = o.location + Vector((rng.uniform(-w / 3, w / 3), rng.uniform(-1.2, 1.2), rng.uniform(0.2, 1.4) * up))
            items.append((tuple(c), w * k * rng.uniform(0.35, 0.6), (1.0, 0.8, 0.6), 0))
    for nm in ("FX_Fall_Castle_Lip", "FX_Fall_E_Lip", "FX_Fall_W_Lip"):
        o = bpy.data.objects.get(nm)
        if o is None:
            continue
        w = float(o.get("width", 4.0))
        for _ in range(3):
            c = o.location + Vector((rng.uniform(-w / 3, w / 3), rng.uniform(-1.4, -0.4), rng.uniform(-1.6, -0.2)))
            items.append((tuple(c), w * 0.18, (1.0, 0.7, 0.8), 0))
    if items:
        _puffs("PREVIEW_VFX_Foam", items, foam)
    mist = [_pmat("PREVIEW_VFX_Mist", (0.80, 0.84, 0.90), 0.07)]
    o = bpy.data.objects.get("FX_Mist_CastleFall")
    if o is not None:
        r = float(o.get("radius", 11.0))
        items = [((o.location.x + rng.uniform(-r, r), o.location.y + rng.uniform(-r / 2, r / 2), o.location.z + 0.2),
                  rng.uniform(3.5, 5.5), (1.0, 0.8, 0.22), 0) for _ in range(9)]
        _puffs("PREVIEW_VFX_Mist", items, mist)


# ------------------------------------------------------------------ cameras da folha (fora do export)
def cams():
    e = L.EYE
    return {
        "CAM_OPVfx_PetalsSubida": ((-74.0, 384.0, L.CL + e), (-58.0, 418.0, 182.0), 22),
        "CAM_OPVfx_PetalsPatio": ((-14.0, 362.0, CC + e), (-52.0, 416.0, 190.0), 20),
        "CAM_OPVfx_PetalsRaizes": ((40.0, 410.0, CC + e), (75.0, 450.0, 175.0), 20),
        "CAM_OPVfx_PetalsPlaza": ((-30.0, 190.0, P + e), (0.0, 300.0, P + 16.0), 22),
        "CAM_OPVfx_PetalsStreet": ((4.0, 30.0, T0 + e), (0.0, 112.0, T1 + 10.0), 22),
        "CAM_OPVfx_CastleFall": ((8.0, 330.0, CF + e), (0.0, 348.0, 104.0), 24),
        "CAM_OPVfx_FallE": ((230.0, 200.0, L.HARBOR + e), (248.5, 297.0, 62.0), 26),
        "CAM_OPVfx_FallW": ((-200.0, -60.0, 95.0), (-174.0, 46.0, 60.0), 26),
        "CAM_OPVfx_Wheel": ((-186.0, 74.0, T1 + e), (-174.0, 90.0, 91.5), 22),
    }


def roblox_hide(*_a):
    """M6b (item 49): no modo roblox (FM_MAT_PREVIEW=roblox no build OU fm_lib.apply_preview('roblox') num .blend
    pronto, como fazem os runners da auditoria) a previa das PETALAS sai do render: o que o Roblox mostra e a particula
    de 0,36 transparente, nao os quads 1,6x da folha. Espuma/nevoa continuam (leem como agua nos 2 modos)"""
    try:
        import fm_lib
        rb = (str(getattr(fm_lib, "PREVIEW", "")).lower() == "roblox" or
              os.environ.get("FM_MAT_PREVIEW", "").lower() == "roblox")
    except Exception:
        rb = os.environ.get("FM_MAT_PREVIEW", "").lower() == "roblox"
    o = bpy.data.objects.get("PREVIEW_VFX_Petals")
    if o is not None and o.hide_render != rb:
        o.hide_render = rb


if not any(getattr(f, "__name__", "") == "roblox_hide" for f in bpy.app.handlers.render_pre):
    bpy.app.handlers.render_pre.append(roblox_hide)


def build():
    bpy.context.view_layer.update()
    BOX.clear()
    em = petals() + water()
    ok = movers()
    if os.environ.get("OP_VFX_PREVIEW", "1") != "0":
        preview()
        roblox_hide()
    for n, (loc, tgt, lens) in cams().items():
        camera(n, loc, tgt, lens)
    print("op_vfx emissores=%d (%s) moveis=%s" % (len(em), ",".join(em), "OK" if ok else "FAIL"))
    return em
