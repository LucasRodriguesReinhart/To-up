# ds_vfx - VFX da Ilha 4 (DEMON SLAYER), agente 3c da Onda 3 (PLANO_DS secoes 1.1 "Pecas moveis", 6 "Efeitos", 10;
# fase 15). Roda na zona dressing (antes do ds_lights). NAO inventa sistema: so prepara o que o jogo JA consome.
#   1. EMISSORES (ParticleEmitter feito no Roblox pela Core.DemonSlayerIsland na onda 5, como o emissor() das Ilhas 1
#      e 3: Part invisivel + ParticleEmitter com atributo Dist e tag IlhaVFX, ligado/desligado por distancia pelo
#      cliente). Aqui os marcadores FX_* do ds_core sao MEDIDOS na geometria e ganham a receita do emissor nos
#      atributos (as MESMAS chaves da tabela s do emissor(): tex, cor, rate, vida, vel, tam, fim, transp, luz, infl,
#      spread, area, forma, Dist; + acc_up (aceleracao vertical) e drift (deriva ao longo do fwd do marcador)):
#        FX_Forge_Smoke       fumaca da chamine (topo MEDIDO da coroa de pedra), Dist 400, deriva para lesnordeste;
#        FX_Forge_Smoke_Vent  NOVO (unico marcador criado aqui): fumaca do lanternim da cumeeira do salao (onde a coifa
#                             da fornalha despeja; medido nas ripas de fuligem do ds_forge), Dist 300;
#        FX_Forge_Embers      brasas saindo da BOCA (medida na face do bloco de alvenaria), Dist 120;
#        FX_Mist_Bamboo / FX_Mist_Ravine  nevoa BAIXA (assentada no chao medido), Dist 260;
#        FX_Fall_1_* / FX_Fall_2_*        espuma/nevoa da cascata e do sangradouro: posicao e props de agua sao do
#                             ds_water (medidos na pedra) - aqui so ENTRAM as chaves do emissor (rate/tam/Dist/...).
#      'area' = "lado,altura,frente" nos eixos LOCAIS do marcador (Part com o CFrame do marcador); cores "r,g,b" 0-255.
#   2. PECAS MOVEIS (tag IlhaMovel, LocalScript ILHA_NARUTO_Movel: so rpm em volta de pivot/axis e bob/rate): roda
#      d'agua (ds_forge) + pilao: VFX_DS_KineAxle (gira com a roda) e VFX_DS_Kine_A/_B (bob com rate do came). Aqui a
#      coerencia e CONFERIDA e corrigida no build: rpm do eixo = rpm da roda; rate = rpm / 60 x ressaltos.
#   3. PREVIA (so Blender, 00_REFERENCE / PREVIEW_VFX_*, fora do export): baforadas de fumaca, nevoa rasteira, espuma
#      e algumas brasas, para as folhas noturnas lerem o efeito pretendido. DS_VFX_PREVIEW=0 desliga. A previa NAO
#      esconde modelagem: fumaca fina e alta, nevoa < 2,5 de altura, sem cobrir fachada. ONDA 6b: materiais RBX_PREVIEW_
#      VFX_* (transparentes; o apply_preview('roblox') do fm_lib nao os torna opacos - continuam lendo como particula).
import os, math, random
import bpy, bmesh
from mathutils import Vector, Matrix
import ds_lib as DL
from ds_lib import yaw_to
import ds_layout as L

T1, T2, T3, T4 = L.T1, L.T2, L.T3, L.T4
DRIFT = (0.82, 0.57)            # vento de previa/deriva da fumaca: para lesnordeste (sai da visada da clareira de lado)


# ------------------------------------------------------------------ medidas na geometria
def _verts(prefix, box, mat=None):
    """vertices (mundo) de objetos com o prefixo dentro da caixa (x0, x1, y0, y1); mat = so faces desse material"""
    x0, x1, y0, y1 = box
    out = []
    for o in bpy.data.objects:
        if o.type != "MESH" or not o.name.startswith(prefix):
            continue
        mw = o.matrix_world
        me = o.data
        if mat is None:
            for v in me.vertices:
                p = mw @ v.co
                if x0 <= p.x <= x1 and y0 <= p.y <= y1:
                    out.append(p)
        else:
            idx = {i for i, m in enumerate(me.materials) if m and m.name.startswith(mat)}
            for pl in me.polygons:
                if pl.material_index in idx:
                    for vi in pl.vertices:
                        p = mw @ me.vertices[vi].co
                        if x0 <= p.x <= x1 and y0 <= p.y <= y1:
                            out.append(p)
    return out


_GBVH = []


def _ground(x, y, z0=200.0, prefixes=("DS_Ter_", "DS_Water_")):
    """cota do chao visivel: raio para baixo SO no terreno e na pedra da agua (copa de bambu/arvore nao conta)"""
    from mathutils.bvhtree import BVHTree
    if not _GBVH:
        verts, polys = [], []
        for o in bpy.data.objects:
            if o.type != "MESH" or not o.name.startswith(prefixes):
                continue
            mw = o.matrix_world
            base = len(verts)
            verts += [mw @ v.co for v in o.data.vertices]
            polys += [[base + i for i in p.vertices] for p in o.data.polygons]
        _GBVH.append(BVHTree.FromPolygons(verts, polys) if polys else None)
    t = _GBVH[0]
    if t is None:
        return None
    hit = t.ray_cast(Vector((x, y, z0)), Vector((0.0, 0.0, -1.0)), 400.0)
    return hit[0].z if hit[0] is not None else None


def measure():
    """chamine (topo da coroa), lanternim (ripas de fuligem) e boca (face do bloco). Volta dict com o que achou"""
    m = {}
    cx, cy, s = L.CHIMNEY
    vs = _verts("DS_Frg_", (cx - 4.0, cx + 4.0, cy - 4.0, cy + 4.0))
    if vs:
        top = max(v.z for v in vs)
        m["chimney"] = (cx, cy, top)
        print("VFX medida chamine: topo %.2f (planta %.2f)" % (top, L.CHIMNEY_TOP))
    hx0, hy0, hx1, hy1 = L.FORGE["hall"][:4]
    hc = (hy0 + hy1) / 2
    vs = _verts("DS_Frg_Hall", (-7.2, 7.2, hc - 2.6, hc + 2.6), mat="Stone_DS_Soot")
    vs = [v for v in vs if v.z > T4 + 15.0]
    if vs:
        z0, z1 = min(v.z for v in vs), max(v.z for v in vs)
        xs = [v.x for v in vs]
        m["vent"] = (0.0, hc, (z0 + z1) / 2, max(xs) - min(xs), z1 - z0)
        print("VFX medida lanternim: ripas %.2f..%.2f, largura %.1f" % (z0, z1, max(xs) - min(xs)))
    fx = L.FURNACE_MOUTH[0]
    vs = _verts("DS_Frg_Hall", (fx - 6.0, fx + 6.0, L.FORGE["hall"][1] - 6.0, L.FORGE["hall"][1] + 2.0),
                mat="Stone_DS_Brick")
    if vs:
        yf = min(v.y for v in vs)
        zs = sorted(v.z for v in vs)
        m["mouth"] = (fx, yf, zs[0], zs[-1])
        print("VFX medida boca: face do arco y %.2f, tijolo z %.2f..%.2f" % (yf, zs[0], zs[-1]))
    return m


# ------------------------------------------------------------------ receitas (as chaves do emissor() das ilhas)
def _emit(o, **kw):
    for k, v in kw.items():
        o[k] = v
    o["vfx"] = "emissor"


def _marker(name, loc, yaw, props):
    o = bpy.data.objects.get(name)
    if o is None:
        o = DL.mk(name, loc, (0.0, 0.0, yaw), 2.0, "SPHERE")
    else:
        o.location = loc
        o.rotation_euler = (0.0, 0.0, yaw)
    for k, v in props.items():
        o[k] = v
    return o


def emitters(m):
    out = []
    drift_yaw = yaw_to(*DRIFT)
    # fumaca da chamine: coluna fina, cinza-fuligem com o pe aquecido pela brasa, sobe 1,3 e deriva 0,5 ao vento
    if "chimney" in m:
        x, y, z = m["chimney"]
        o = _marker("FX_Forge_Smoke", (x, y, z - 0.8), drift_yaw, {"fx": "fumaca"})
        _emit(o, tex="fumaca", cor="96,90,88", cor_ini="138,96,70", rate=3.0, vida=9.0, vel=3.5, tam=4.5, fim=2.6,
              transp=0.55, luz=0.05, infl=1.0, spread="10,10", acc_up=1.3, drift=0.5, area="3.4,1,3.4", forma="Box",
              Dist=400.0, note="topo MEDIDO da coroa da chamine (sai de dentro do coroamento); deriva = fwd do marcador")
        out.append(o.name)
    # lanternim: fumaca baixa e larga escapando pelas ripas (dos dois lados da cumeeira), mais rala que a da chamine
    if "vent" in m:
        x, y, z, w, h = m["vent"]
        o = _marker("FX_Forge_Smoke_Vent", (x, y, z), 0.0, {"fx": "fumaca"})
        _emit(o, tex="fumaca", cor="104,98,94", rate=1.6, vida=6.0, vel=1.6, tam=3.2, fim=2.4, transp=0.68, luz=0.0,
              infl=1.0, spread="70,20", acc_up=1.0, drift=0.4, area="%.1f,%.1f,4.4" % (w - 0.6, max(1.0, h - 0.6)),
              forma="Box", Dist=300.0,
              note="NOVO (onda 3c): lanternim de fumaca (kemuri-dashi) na cumeeira do salao; ripas medidas no ds_forge")
        out.append(o.name)
    # brasas da boca: fagulhas pequenas que saem pelo alto do arco e sobem; Neon-like (LightEmission 1)
    if "mouth" in m:
        x, yf, z0, z1 = m["mouth"]
        o = _marker("FX_Forge_Embers", (x, yf + 0.6, z0 + 4.8), yaw_to(0.0, -1.0), {"fx": "brasas"})
        _emit(o, tex="brilho", cor="255,140,60", cor_fim="255,72,24", rate=6.0, vida=2.2, vel=2.6, tam=0.28, fim=0.15,
              transp=0.15, luz=1.0, infl=0.0, spread="28,28", acc_up=2.6, drift=0.6, area="6.5,3,1.2", forma="Box",
              Dist=120.0, note="face do arco de tijolo MEDIDA; sai para fora (fwd = sul, a clareira) e sobe")
        out.append(o.name)
    # nevoa baixa: bambuzal (ate a pergola) e ravina (3 pocos do sangradouro): rasteira, larga, muito transparente
    for nm, area, rate in (("FX_Mist_Bamboo", 40.0, 1.2), ("FX_Mist_Ravine", 22.0, 0.9)):
        o = bpy.data.objects.get(nm)
        if o is None:
            continue
        g = _ground(o.location.x, o.location.y)
        if g is not None:
            o.location.z = g + 1.2
        _emit(o, tex="nevoa", cor="176,188,214", rate=rate, vida=10.0, vel=0.5, tam=14.0, fim=1.3, transp=0.86, luz=0.0,
              infl=1.0, spread="90,10", acc_up=0.05, drift=0.3, area="%.0f,1.5,%.0f" % (area, area), forma="Box",
              Dist=260.0)
        o["note"] = (o.get("note", "") + " | onda 3c: assentado no chao medido + 1,2; nevoa < 2,5 de altura").strip(" |")
        out.append(nm)
    # agua (ds_water mediu na pedra): so as chaves do emissor - mesma receita do agua() da Ilha 3
    water = {"FX_Fall_1_Lip": dict(tex="nevoa", rate=3.0, Dist=220.0), "FX_Fall_1_Step": dict(tex="nevoa", rate=8.0,
             Dist=200.0), "FX_Fall_1_Base": dict(tex="nevoa", rate=14.0, Dist=260.0),
             "FX_Fall_2_Lip": dict(tex="nevoa", rate=2.0, Dist=260.0), "FX_Fall_2_Base": dict(tex="nevoa", rate=6.0,
                                                                                              Dist=420.0)}
    for nm, kw in water.items():
        o = bpy.data.objects.get(nm)
        if o is None:
            continue
        w = float(o.get("width", 3.0))
        tam = {"Lip": 0.5, "Step": 0.8, "Base": 1.6}[nm.rsplit("_", 1)[1]] * w
        _emit(o, cor="214,228,248", tam=round(tam, 2), vida=2.6, vel=2.5, transp=0.55, infl=0.9, luz=0.1, **kw)
        out.append(nm)
    return out


# ------------------------------------------------------------------ pecas moveis: coerencia do pilao com a roda
def movers():
    wh = bpy.data.objects.get("VFX_DS_Wheel")
    ax = bpy.data.objects.get("VFX_DS_KineAxle")
    kines = [o for o in bpy.data.objects if o.name.startswith("VFX_DS_Kine_")]
    if wh is None:
        print("AVISO ds_vfx: sem VFX_DS_Wheel")
        return
    rpm = float(wh.get("rpm", 0.0))
    if ax is not None:
        if abs(float(ax.get("rpm", 0.0)) - rpm) > 1e-6 or tuple(ax.get("axis", ())) != tuple(wh.get("axis", ())):
            print("VFX eixo do pilao: rpm %.2f -> %.2f (o da roda)" % (float(ax.get("rpm", 0.0)), rpm))
            ax["rpm"] = rpm
            ax["axis"] = tuple(wh["axis"])
            ax["pivot"] = tuple(wh["pivot"])
    for k in kines:
        lobes = int(k.get("lobes", 2))
        want = round(rpm / 60.0 * lobes, 4)
        if abs(float(k.get("rate", 0.0)) - want) > 1e-6:
            k["rate"] = want
        print("VFX pilao %s: bob %.2f, %d ressaltos, rate %.3f batida/s (roda %.1f rpm) -> 1 batida a cada %.1f s" % (
            k.name, float(k.get("bob", 0.0)), lobes, want, rpm, 1.0 / want if want else 0.0))
    if ax is None and not kines:
        print("AVISO ds_vfx: pilao estatico (ds_forge sem VFX_DS_Kine_*)")


# ------------------------------------------------------------------ previa (so Blender)
def _pmat(name, rgb, alpha, emit=0.0):
    """material TRANSPARENTE da previa. ONDA 6b (item 56): o nome leva o prefixo RBX_ - o fm_lib.apply_preview('roblox')
    (o que as folhas de QA rodam num .blend pronto) refaz OPACO todo material fora de MATS a partir da cor de viewport
    (branca por padrao) e so pula 'RBX_*': a nevoa virava neve no chao e as brasas bolas brancas. A previa ja e a
    leitura do jogo (particula translucida), entao fica igual nos 2 modos. diffuse_color = a cor (qualquer outro
    caminho que leia a cor de viewport acha a certa, nao o branco)."""
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


def _puffs(name, items, mats):
    """items: (centro, raio, (sx, sy, sz), indice do material) -> 1 objeto de icosferas suaves em 00_REFERENCE"""
    bm = bmesh.new()
    for c, r, sc, mi in items:
        M = Matrix.Translation(Vector(c)) @ Matrix.Diagonal((r * sc[0], r * sc[1], r * sc[2], 1.0))
        res = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=M)
        fs = {f for v in res["verts"] for f in v.link_faces}
        for f in fs:
            f.material_index = mi
            f.smooth = True
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for mt in mats:
        me.materials.append(mt)
    ob = bpy.data.objects.new(name, me)
    coll = bpy.data.collections.get("00_REFERENCE")
    (coll or bpy.context.scene.collection).objects.link(ob)
    try:
        ob.visible_shadow = False
    except Exception:
        pass
    return ob


def preview():
    for o in [o for o in bpy.data.objects if o.name.startswith("PREVIEW_VFX_")]:
        bpy.data.objects.remove(o, do_unlink=True)
    for m in [m for m in bpy.data.materials if m.name.startswith("PREVIEW_VFX_") and not m.users]:
        bpy.data.materials.remove(m)            # nomes antigos (antes do prefixo RBX_)
    rng = random.Random(3303)
    smoke = [_pmat("PREVIEW_VFX_SmokeWarm", (0.20, 0.12, 0.08), 0.32, 0.06),
             _pmat("PREVIEW_VFX_Smoke_A", (0.11, 0.105, 0.10), 0.26), _pmat("PREVIEW_VFX_Smoke_B", (0.12, 0.12, 0.125), 0.17),
             _pmat("PREVIEW_VFX_Smoke_C", (0.13, 0.135, 0.15), 0.09)]
    dx, dy = DRIFT
    items = []
    o = bpy.data.objects.get("FX_Forge_Smoke")
    if o is not None and o.get("vfx"):
        b = o.location
        for i in range(12):                     # baforadas irregulares (1 + satelites), abrem e clareiam ao subir
            t = i / 11.0
            up = 1.2 + i * 3.6 + i * i * 0.14
            side = (i ** 1.5) * 1.1
            r = (1.5 + i * 0.62) * rng.uniform(0.8, 1.15)
            c = Vector((b.x + dx * side, b.y + dy * side, b.z + up))
            mi = 0 if i == 0 else (1 if t < 0.35 else (2 if t < 0.7 else 3))
            items.append((tuple(c + Vector((rng.uniform(-0.3, 0.3) * r, rng.uniform(-0.3, 0.3) * r, 0.0))), r,
                          (1.0, rng.uniform(0.85, 1.0), rng.uniform(0.8, 1.0)), mi))
            for _ in range(1 if i < 3 else 2):
                a = rng.uniform(0, 2 * math.pi)
                off = Vector((math.cos(a) * r * 0.55, math.sin(a) * r * 0.55, rng.uniform(-0.3, 0.4) * r))
                items.append((tuple(c + off), r * rng.uniform(0.5, 0.7), (1.0, 1.0, 0.9), min(3, mi + 1)))
    o = bpy.data.objects.get("FX_Forge_Smoke_Vent")
    if o is not None and o.get("vfx"):
        b = o.location
        for s in (-1, 1):
            for k in range(4):
                x = b.x + (k - 1.5) * 3.2
                items.append(((x + dx * 1.5, b.y + s * 2.6 + dy * 1.0, b.z + 1.2 + k % 2 * 0.6), 1.6 + k % 2 * 0.4,
                              (1.2, 0.9, 0.7), 2))
            items.append(((b.x + dx * 4.0, b.y + s * 2.0 + dy * 3.0, b.z + 4.5), 2.6, (1.3, 1.0, 0.75), 3))
    if items:
        _puffs("PREVIEW_VFX_Smoke", items, smoke)
    # nevoa rasteira: discos achatados sobrepostos (< 2,5 de altura)
    mist = [_pmat("PREVIEW_VFX_Mist", (0.27, 0.29, 0.36), 0.06)]          # 6b: 0,075 -> 0,06 (veu perto da camera)
    items = []
    for nm, R, n in (("FX_Mist_Bamboo", 22.0, 14), ("FX_Mist_Ravine", 11.0, 7)):
        o = bpy.data.objects.get(nm)
        if o is None:
            continue
        for _ in range(n):
            a = rng.uniform(0, 2 * math.pi)
            d = R * math.sqrt(rng.uniform(0.0, 1.0))
            x, y = o.location.x + math.cos(a) * d, o.location.y + math.sin(a) * d
            g = _ground(x, y)
            if g is None:
                continue
            items.append(((x, y, g + 0.6), rng.uniform(5.0, 8.0), (1.0, rng.uniform(0.7, 1.0), 0.16), 0))
    if items:
        _puffs("PREVIEW_VFX_Mist", items, mist)
    # espuma da cascata e do sangradouro (degrau e pe)
    foam = [_pmat("PREVIEW_VFX_Foam", (0.66, 0.72, 0.82), 0.09)]
    items = []
    for nm, k in (("FX_Fall_1_Step", 0.45), ("FX_Fall_1_Base", 0.55), ("FX_Fall_2_Base", 0.4)):
        o = bpy.data.objects.get(nm)
        if o is None:
            continue
        w = float(o.get("width", 3.0))
        for j in range(7):                      # nuvem de respingo baixa e macia (nao "bolachas" soltas)
            c = o.location + Vector((rng.uniform(-w / 3, w / 3), rng.uniform(-0.8, 0.8), rng.uniform(0.3, 1.4)))
            items.append((tuple(c), w * k * rng.uniform(0.45, 0.7), (1.0, 0.8, 0.7), 0))
    if items:
        _puffs("PREVIEW_VFX_Foam", items, foam)
    # brasas: poucas fagulhas no alto do arco
    ember = [_pmat("PREVIEW_VFX_Ember", (1.0, 0.26, 0.045), 1.0, 0.9)]    # 6b: cor do emissor (255,140,60); 1,3 amarelava
    items = []
    o = bpy.data.objects.get("FX_Forge_Embers")
    if o is not None and o.get("vfx"):
        b = o.location
        for _ in range(16):
            items.append(((b.x + rng.uniform(-3.0, 3.0), b.y - rng.uniform(0.2, 2.6), b.z + rng.uniform(-0.5, 5.0)),
                          rng.uniform(0.07, 0.14), (1.0, 1.0, 1.0), 0))
    if items:
        _puffs("PREVIEW_VFX_Embers", items, ember)


# ------------------------------------------------------------------ cameras da folha 3c (studio_ds pega CAMS)
CAMS = {
    "CAM_DSVfx_Chimney": ((-40.0, 380.0, T4 + 30.0), (37.0, 493.0, 150.0), 26),
    "CAM_DSVfx_Mill": ((L.FORGE["east"][2] + 5.0, 472.0, T4 + 4.5), (L.FORGE["east"][2] + 8.4, 485.6, T4 + 5.5), 28),
    "CAM_DSVfx_Bamboo": ((6.0, 28.0, 60.5), (48.0, 84.0, 58.0), 24),
    "CAM_DSVfx_Cascade": ((L.CASCADE[0] - 6.0, L.CASCADE[1] - 34.0, T1 + 9.0), (L.CASCADE[0], L.CASCADE[1], 70.0), 26),
}


def build():
    bpy.context.view_layer.update()
    _GBVH.clear()
    m = measure()
    em = emitters(m)
    movers()
    if os.environ.get("DS_VFX_PREVIEW", "1") != "0":
        preview()
    print("ds_vfx emissores=%d (%s)" % (len(em), ",".join(em)))
