# vm_lights.py - LUZ + VFX do lobby Vila Medieval (onda V3b). Acrescimo pontual depois da vila (vm_town) e da forja
# (vm_forge), sem editar os arquivos deles: mexe so em LUZES (objetos LIGHT), no sol da previa e em PREVIEW_VFX_*.
#
# DIA (o lobby e ensolarado): sol quente a sudoeste e alto (~50 graus, o SUN_DIR do vm_scene), sombra SUAVE (angulo
#   do sol 2 -> 4 graus). No Roblox a luz do dia e o perfil do lobby (Lighting do Edit = base do AreaAtmosphere, area 0):
#   LOBBY_PROFILE abaixo, que o export_vm grava no APLICAR_LIGHTING do montar (lighting_cfg) e o PLANO_VM secao 11
#   documenta para o lead.
# LUZES DE DIA (<= 30; o V2 deixou 19): so as de antes. A BOCA DA FORNALHA (L_Hearth_Fire_VM) vira a mais forte do
#   lobby (Roblox: alcance 24, brilho 2,2, sombra); portais e pads ficam como estao (14 / 1,0 e 12,6 / 0,71).
# NOITE (NightOnly = Enabled false + atributo NightOnly; quem liga e o ciclo/ceu, como nas ilhas):
#   - lanternas dos postes do kit (L_VM_Lamp_*): poca de luz no chao, sem estourar (alcance 14, brilho 0,8);
#   - JANELAS com brilho so a noite (L_VM_Night_Win_*): as vidracas do kit sao a junta escura (Stone_VM_Mortar), entao
#     o "brilho" e uma luz quente 1 stud a FRENTE de uma vidraca escolhida (a face do vidro olha para a luz e acende);
#     ~30 janelas viradas para as rotas (spawn, praca, ruas), 10 studs entre si; no Blender ficam fora do render de dia;
#   - camara de fogo da chamine (L_VM_Night_Chimney): acende a capa e a fumaca por baixo a noite.
#   Overrides do Roblox (alcance/brilho/sombra) ficam nas props rbx_* das luzes e o export_vm aplica (apply_rbx).
# VFX: o movimento (roda, pilao) e as particulas (fumaca, brasas, faiscas, vapor, respingos, quedas, portais) sao do
#   export_vm_vfx.py (mesmo mecanismo do lobby atual). Aqui so os PROXIES de previa PREVIEW_VFX_* (pluma da chamine,
#   chamas da boca, faiscas, vapor, respingos), escondidos no render normal e nunca exportados (prefixo PREVIEW_).
#
# uso: build_vm.py chama build() depois do vm_town (e das ondas V3) e cameras() no fim das cameras.
#   blender -b --factory-startup <x.blend> --python vm_lights.py -- apply <saida.blend>     aplica num .blend pronto
#   blender -b --factory-startup <x.blend> --python vm_lights.py -- render <pasta> [CAM...] [--roblox] [--noite] [--vfx]
#                                                                    [--pilao-alto] [--sem-golem]
#   blender -b --factory-startup <x.blend> --python vm_lights.py -- qa [json]          contagem de luzes / sol / proxies
#   python -B vm_lights.py sheet <dia_prev> <dia_rbx> <noite_prev> <noite_rbx> <closes_prev> <closes_rbx> <pasta>
import sys, os, math, json
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
try:
    import bpy
except ImportError:
    bpy = None

if bpy is not None:
    import bmesh
    from mathutils import Vector, Matrix, kdtree
    import vm_lib as VL
    import vm_layout as L
    import fm_lib

# ------------------------------------------------------------------ perfil do lobby no Roblox (area 0 = Edit Lighting)
# Sol = SUN_Key do vm_scene: GetSunDirection ~ (-0,42; 0,76; 0,50) -> ClockTime / latitude calculados em sun_rbx().
LOBBY_PROFILE = {
    "Lighting": {"Brightness": 2.3, "ExposureCompensation": -0.05, "EnvironmentDiffuseScale": 0.5,
                 "EnvironmentSpecularScale": 0.3, "ShadowSoftness": 0.35, "Ambient": [104, 100, 98],
                 "OutdoorAmbient": [150, 158, 178], "ColorShift_Top": [255, 238, 214],
                 "ColorShift_Bottom": [0, 0, 0]},
    "Atmosphere": {"Density": 0.26, "Offset": 0.12, "Color": [196, 218, 244], "Decay": [116, 150, 198],
                   "Glare": 0.1, "Haze": 0.9},
    "Sky": {"SunAngularSize": 14, "MoonAngularSize": 11, "StarCount": 0},     # (CelestialBodiesShown = true: sem booleano aqui, o montar escreve o valor cru)
    "BloomEffect": {"Intensity": 0.22, "Size": 24, "Threshold": 1.6},
    "SunRaysEffect": {"Intensity": 0.03, "Spread": 0.12},
    "ColorCorrectionEffect": {"Brightness": 0.0, "Contrast": 0.06, "Saturation": 0.08, "TintColor": [255, 250, 242]},
}
CLOUDS = {"Cover": 0.45, "Density": 0.55, "Color": [255, 255, 255]}       # workspace.Terrain.Clouds (opcional)
SUN_ANGLE_DEG = 4.0              # sombra suave da previa (era 2)

# ------------------------------------------------------------------ luzes
HEARTH = "L_Hearth_Fire_VM"
LAMP = "L_VM_Lamp"
NIGHT = "L_VM_Night_"            # prefixo NightOnly novo (export_vm acrescenta ao ER.NIGHT_ONLY)
WIN_MAX, WIN_GAP = 30, 10.0
# rotas de onde as janelas sao vistas (Roblox x, z)
WIN_VIEW = [(0.0, 94.0), (0.0, 60.0), (0.0, 30.0), (0.0, 6.0), (0.0, -28.0), (24.0, 74.0), (37.0, 110.0),
            (48.0, 140.0), (-30.0, 52.0), (-64.0, 60.0), (-100.0, 70.0), (60.0, 43.0)]
# overrides do Roblox (o export_roblox calcula alcance/brilho pela energia e corta em 20 / 1,5)
RBX = {
    HEARTH: dict(range=24.0, brightness=2.2, shadows=True, color=(255, 122, 41)),
    LAMP: dict(range=14.0, brightness=0.8),
    NIGHT + "Win": dict(range=7.0, brightness=0.9, color=(255, 178, 98)),
    NIGHT + "Chimney": dict(range=18.0, brightness=1.2, color=(255, 128, 48)),
}
ENERGY = {HEARTH: 2200.0, NIGHT + "Win": 30.0, NIGHT + "Chimney": 900.0}


def rbx_for(name):
    for k, v in RBX.items():
        if name.startswith(k):
            return v
    return None


def apply_rbx(lights_out):
    """export_vm: aplica os overrides nas luzes que o export_roblox.lights() devolveu (lista de dicts)"""
    n = 0
    for l in lights_out:
        o = rbx_for(l["name"])
        if not o:
            continue
        l["range"] = o["range"]
        l["brightness"] = o["brightness"]
        if "shadows" in o:
            l["shadows"] = o["shadows"]
        if "color" in o:
            l["color"] = list(o["color"])
        if l["name"].startswith(NIGHT) or l["name"].startswith(LAMP):
            l["night"] = True
        n += 1
    return n


def lighting_cfg(clock, lat):
    """substitui export_roblox.lighting_cfg no export_vm: perfil do DIA do lobby (APLICAR_LIGHTING do montar)"""
    cfg = json.loads(json.dumps(LOBBY_PROFILE))
    cfg["Lighting"]["ClockTime"] = clock
    cfg["Lighting"]["GeographicLatitude"] = lat
    return cfg


def sun_rbx(d):
    """mesma conta do export_roblox.sun_setup: vetor PARA o sol (Blender) -> (ClockTime, latitude, vetor Roblox)"""
    r = Vector((d[0], d[2], -d[1])).normalized()
    t = -math.asin(max(-1.0, min(1.0, r.z)))
    lat = 23.5 - math.degrees(t)
    ct = max(1e-6, math.cos(t))
    a = math.atan2(r.x / ct, -r.y / ct)
    return round((a / (2 * math.pi) * 24.0) % 24.0, 3), round(lat, 3), tuple(round(x, 3) for x in r)


# ------------------------------------------------------------------ janelas (NightOnly)
def _pane_islands(ob, mi):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bm.transform(ob.matrix_world)
    bm.faces.ensure_lookup_table()
    seen, out = set(), []
    for f in bm.faces:
        if f.material_index != mi or f.index in seen:
            continue
        st, isl = [f], []
        seen.add(f.index)
        while st:
            g = st.pop()
            isl.append(g)
            for e in g.edges:
                for h in e.link_faces:
                    if h.material_index == mi and h.index not in seen:
                        seen.add(h.index)
                        st.append(h)
        vs = {v for g in isl for v in g.verts}
        if len(vs) != 8:
            continue
        cs = [v.co.copy() for v in vs]
        mn = Vector((min(c.x for c in cs), min(c.y for c in cs), min(c.z for c in cs)))
        mx = Vector((max(c.x for c in cs), max(c.y for c in cs), max(c.z for c in cs)))
        ex = mx - mn
        th = min(ex.x, ex.y)
        if 0.2 <= th <= 0.4 and 1.0 <= max(ex.x, ex.y) <= 3.6 and 1.2 <= ex.z <= 4.0:
            ax = Vector((1, 0, 0)) if ex.x < ex.y else Vector((0, 1, 0))
            out.append(((mn + mx) / 2, ax, max(ex.x, ex.y), ex.z))
    bm.free()
    return out


def window_spots():
    """vidracas do kit (caixas finas de junta escura) viradas para as rotas: [(ponto da luz, normal, casa)]"""
    cands = []
    for ob in sorted((o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("VM_House_")),
                     key=lambda o: o.name):
        names = [m.name if m else "" for m in ob.data.materials]
        if "Stone_VM_Mortar" not in names:
            continue
        panes = _pane_islands(ob, names.index("Stone_VM_Mortar"))
        if not panes:
            continue
        vw = [ob.matrix_world @ v.co for v in ob.data.vertices]
        kd = kdtree.KDTree(len(vw))
        for i, p in enumerate(vw):
            kd.insert(p, i)
        kd.balance()
        for c, ax, w, h in panes:
            # o corpo da casa fica do lado de DENTRO: media dos vertices num raio de 6 ao longo da normal
            s = sum((vw[i] - c).dot(ax) for (_, i, _) in kd.find_range(c, 6.0))
            n = -ax if s > 0 else ax
            rx, ry, rz = VL.R(c)
            nr = (n.x, -n.y)                        # normal em Roblox (x, z)
            best = None
            for vx, vz in WIN_VIEW:
                dx, dz = vx - rx, vz - rz
                d = math.hypot(dx, dz)
                if d < 4.0 or d > 70.0:
                    continue
                if (dx * nr[0] + dz * nr[1]) / d < 0.45:
                    continue
                best = d if best is None else min(best, d)
            if best is not None:
                cands.append((best, ry, c + n * 1.0, n, ob.name))
    cands.sort(key=lambda t: (round(t[0] / 8.0), -t[1]))      # perto da rota primeiro; no empate, a janela mais alta
    pick = []
    for d, _, p, n, hn in cands:
        if all((p - q).length >= WIN_GAP for q, _, _ in pick):
            pick.append((p, n, hn))
        if len(pick) >= WIN_MAX:
            break
    return pick, len(cands)


# ------------------------------------------------------------------ proxies de previa das particulas
def _pmat(name, rgb, alpha=1.0, emit=0.0):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bs = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bs.inputs["Base Color"].default_value = (*rgb, 1.0)
    bs.inputs["Alpha"].default_value = alpha
    if emit:
        bs.inputs["Emission Color"].default_value = (*rgb, 1.0)
        bs.inputs["Emission Strength"].default_value = emit
    nt.links.new(bs.outputs[0], out.inputs[0])
    try:
        m.surface_render_method = "BLENDED"
    except Exception:
        pass
    m.diffuse_color = (*rgb, alpha)
    return m


def _ico(name, centers, mat, coll):
    """uma malha so com varias esferas (centro Blender, raio)"""
    bm = bmesh.new()
    for c, r in centers:
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r, matrix=Matrix.Translation(c))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat)
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    ob.hide_render = True
    ob["vm_lights"] = 1
    return ob


def _cones(name, items, mat, coll):
    """chamas/faiscas: cones (base Blender, altura, raio, inclinacao)"""
    bm = bmesh.new()
    for base, h, r, tilt in items:
        M = Matrix.Translation(base) @ Matrix.Rotation(tilt[0], 4, "X") @ Matrix.Rotation(tilt[1], 4, "Y") @ \
            Matrix.Translation((0, 0, h / 2))
        bmesh.ops.create_cone(bm, cap_ends=True, segments=7, radius1=r, radius2=0.0, depth=h, matrix=M)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    ob.hide_render = True
    ob["vm_lights"] = 1
    return ob


def vfx_proxies():
    import random
    coll = fm_lib.coll("12_VFX_HELPERS")
    for o in [o for o in bpy.data.objects if o.name.startswith("PREVIEW_VFX_")]:
        bpy.data.objects.remove(o, do_unlink=True)
    mk = {o.name: o for o in fm_lib.coll("15_GAMEPLAY_MARKERS").objects}
    rng = random.Random(3301)
    smoke = _pmat("RBX_VFX_Smoke", (0.42, 0.40, 0.39), 0.55)
    smoke2 = _pmat("RBX_VFX_SmokeLight", (0.72, 0.71, 0.70), 0.38)
    fire = _pmat("RBX_VFX_Fire", (1.0, 0.42, 0.08), 0.9, 6.0)
    spark = _pmat("RBX_VFX_Spark", (1.0, 0.75, 0.3), 1.0, 12.0)
    steam = _pmat("RBX_VFX_Steam", (0.93, 0.95, 0.97), 0.3)
    drop = _pmat("RBX_VFX_Splash", (0.88, 0.95, 1.0), 0.6)
    made = []
    m = mk.get("VFX_Chimney_Smoke_Emitter")
    if m:
        p0 = m.location.copy()
        dark, light = [], []
        for k in range(9):                       # pluma: nucleo escuro que sobe e deriva para +X (vento do VFX)
            t = k / 8.0
            c = p0 + Vector((2.0 + 26.0 * t ** 1.4, rng.uniform(-1.5, 1.5), 3.0 + 44.0 * t))
            (dark if k < 5 else light).append((c, 3.2 + 9.0 * t))
        made.append(_ico("PREVIEW_VFX_ChimneySmoke", dark, smoke, coll))
        made.append(_ico("PREVIEW_VFX_ChimneySmokeTop", light, smoke2, coll))
        made.append(_cones("PREVIEW_VFX_ChimneyEmbers", [(p0 + Vector((rng.uniform(-3, 3), rng.uniform(-3, 3),
                                                                        rng.uniform(1, 9))), 0.7, 0.18, (0.3, 0.2))
                                                          for _ in range(10)], spark, coll))
    m = mk.get("VFX_Hearth_Fire")
    if m:
        p0 = m.location.copy()
        made.append(_cones("PREVIEW_VFX_HearthFlames", [(p0 + Vector((rng.uniform(-3.0, 3.0), rng.uniform(-1.0, 1.0),
                                                                       0.0)), rng.uniform(1.8, 3.4),
                                                         rng.uniform(0.4, 0.7), (rng.uniform(-0.15, 0.15), 0))
                                                        for _ in range(9)], fire, coll))
    for nm in ("VFX_Anvil_Sparks", "VFX_Forge_Sparks"):
        m = mk.get(nm)
        if m:
            p0 = m.location.copy()
            made.append(_cones("PREVIEW_VFX_" + nm[4:], [(p0, rng.uniform(0.8, 1.6), 0.06,
                                                          (rng.uniform(-1.1, 1.1), rng.uniform(-1.1, 1.1)))
                                                         for _ in range(12)], spark, coll))
    m = mk.get("VFX_Quench_Steam")
    if m:
        p0 = m.location.copy()
        made.append(_ico("PREVIEW_VFX_QuenchSteam", [(p0 + Vector((rng.uniform(-1.4, 1.4), rng.uniform(-1, 1),
                                                                  0.5 + 0.8 * k)), 0.3 + 0.22 * k) for k in range(4)],
                         steam, coll))
    m = mk.get("VFX_Wheel_Splash")
    w = mk.get("VFX_Waterwheel_Rotate")
    if m and w:
        p0 = m.location.copy()
        p1 = Vector((p0.x, 2 * w.location.y - p0.y, p0.z))          # lado das pas que saem (a jusante)
        made.append(_ico("PREVIEW_VFX_WheelSplash", [(p + Vector((rng.uniform(-1.4, 1.4), rng.uniform(-0.8, 0.8),
                                                                 rng.uniform(0.1, 1.2))), rng.uniform(0.25, 0.5))
                                                     for p in (p0, p1, p1) for _ in range(5)], drop, coll))
    return made


# ------------------------------------------------------------------ build
def build():
    rep = {}
    sun = bpy.data.objects.get("SUN_Key")
    if sun is not None:
        sun.data.angle = math.radians(SUN_ANGLE_DEG)
    # nomes repetidos (L_VM_Lamp_P1.001 do vm_town x P1 do trecho): nome unico, o Roblox nao gosta de '.001'
    seen = set()
    for o in sorted((o for o in bpy.data.objects if o.type == "LIGHT"), key=lambda o: o.name):
        if "." in o.name:
            base = o.name.split(".")[0]
            k = 1
            while ("%s_%d" % (base, k)) in seen or bpy.data.objects.get("%s_%d" % (base, k)):
                k += 1
            o.name = "%s_%d" % (base, k)
        seen.add(o.name)
    h = bpy.data.objects.get(HEARTH)
    if h is not None:
        h.data.energy = ENERGY[HEARTH]
    # janelas acesas a noite
    for o in [o for o in bpy.data.objects if o.type == "LIGHT" and o.name.startswith(NIGHT)]:
        bpy.data.objects.remove(o, do_unlink=True)
    pick, ncand = window_spots()
    for i, (p, n, hn) in enumerate(pick):
        ob = fm_lib.light("%sWin_%02d" % (NIGHT, i + 1), "POINT", tuple(p), ENERGY[NIGHT + "Win"], (1.0, 0.66, 0.36), 0.4)
        ob.hide_render = True                    # so no render de noite (NightOnly)
        ob["casa"] = hn
    rep["janelas"] = (len(pick), ncand)
    m = bpy.data.objects.get("ForgeChimney")
    if m is not None:
        ob = fm_lib.light(NIGHT + "Chimney", "POINT", tuple(m.location - Vector((0, 0, 4.6))), ENERGY[NIGHT + "Chimney"],
                          (1.0, 0.5, 0.18), 1.0)
        ob.hide_render = True
    rep["proxies"] = len(vfx_proxies())
    rep.update(count())
    print("LUZES V3b: dia %d (teto 30), NightOnly %d (lanternas %d, janelas %d de %d candidatas), proxies VFX %d"
          % (rep["dia"], rep["noite"], rep["lanternas"], rep["janelas"][0], rep["janelas"][1], rep["proxies"]))
    clock, lat, r = sun_rbx(sun["sun_dir_blender"]) if sun is not None and "sun_dir_blender" in sun else (0, 0, ())
    print("SOL do lobby: ClockTime %.3f / GeographicLatitude %.3f -> GetSunDirection %s" % (clock, lat, r))
    return rep


def is_night(name):
    """mesma regra do export: prefixos NightOnly do export_roblox + os do lobby"""
    try:
        import export_roblox as ER
        pre = tuple(ER.NIGHT_ONLY)
    except Exception:
        pre = ()
    return name.startswith(pre + (LAMP, NIGHT))


def count():
    lts = [o for o in bpy.data.objects if o.type == "LIGHT" and o.data.type in ("POINT", "SPOT")]
    night = [o.name for o in lts if is_night(o.name)]
    day = sorted(o.name for o in lts if o.name not in night)
    return {"dia": len(day), "noite": len(night), "lista_dia": day,
            "lanternas": sum(1 for n in night if n.startswith(LAMP)),
            "janelas_n": sum(1 for n in night if n.startswith(NIGHT + "Win"))}


# ------------------------------------------------------------------ cameras (Roblox: pos, alvo, lente)
def cams():
    c = {}
    c["CAM_VM_L_Boca"] = ((5.0, 7.0 + 5.0, -42.0), (-1.0, 11.5, -72.0), 22)
    c["CAM_VM_L_Roda"] = ((47.0, 7.0 + 4.5, -50.0), (34.0, 8.5, -66.0), 22)
    c["CAM_VM_L_Pilao"] = ((22.5, 7.0 + 5.8, -48.5), (25.0, 10.8, -63.0), 16)
    c["CAM_VM_L_Chamine"] = ((44.0, 64.0, -30.0), (8.0, 102.0, -86.0), 22)
    c["CAM_VM_L_NoiteRua"] = ((6.0, 6.0 + 5.0, 34.0), (0.0, 12.0, -30.0), 22)
    c["CAM_VM_L_NoitePraca"] = ((-22.0, 6.0 + 7.0, 78.0), (8.0, 10.0, 30.0), 22)
    c["CAM_VM_L_NoiteCurva"] = ((50.0, 6.0 + 5.5, 132.0), (28.0, 12.0, 70.0), 22)
    return c


def cameras():
    for n, (loc, tgt, lens) in cams().items():
        fm_lib.camera(n, VL.B(loc[0], loc[2], loc[1]), VL.B(tgt[0], tgt[2], tgt[1]), lens)


# ------------------------------------------------------------------ render (dia / noite / closes)
def _night():
    sc = bpy.context.scene
    w = sc.world
    for nd in w.node_tree.nodes:
        if nd.bl_idname == "ShaderNodeValToRGB":
            els = sorted(nd.color_ramp.elements, key=lambda e: e.position)
            els[0].color = (0.035, 0.05, 0.11, 1)
            for e in els[1:]:
                e.color = (0.008, 0.014, 0.05, 1)
        if nd.bl_idname == "ShaderNodeBackground":
            if nd.inputs["Color"].is_linked:                   # ceu visto pela camera
                nd.inputs["Strength"].default_value = 0.5
            else:                                              # luz ambiente (sombras): luar fraco e frio
                nd.inputs["Color"].default_value = (0.30, 0.40, 0.75, 1)
                nd.inputs["Strength"].default_value = 0.07
    sun = bpy.data.objects.get("SUN_Key")
    if sun:
        sun.data.energy = 0.12
        sun.data.color = (0.62, 0.72, 1.0)
    fill = bpy.data.objects.get("SUN_Fill_Sky")
    if fill:
        fill.data.energy = 0.03
    # energia de PREVIA a noite (o Blender nao tem o alcance/brilho do Roblox): aproxima lanterna 14 / 0,8,
    # janela 7 / 0,9 e camara da chamine 18 / 1,2 dos overrides RBX
    for o in bpy.data.objects:
        if o.type == "LIGHT" and is_night(o.name):
            o.hide_render = False
            if o.name.startswith(LAMP):
                o.data.energy = 350.0
            elif o.name.startswith(NIGHT + "Win"):
                o.data.energy = 140.0
            elif o.name.startswith(NIGHT + "Chimney"):
                o.data.energy = 2500.0
    sc.render.use_compositing = False            # nevoa diurna do compositor fora
    sc.view_settings.exposure = 0.7
    for o in bpy.data.objects:
        if o.name.startswith("PREVIEW_Clouds"):
            o.hide_render = True


def _day():
    for o in bpy.data.objects:
        if o.type == "LIGHT" and o.name.startswith(NIGHT):
            o.hide_render = True


def _raise_hammer():
    ob = bpy.data.objects.get("VM_Frg_TripHammer")
    mh = bpy.data.objects.get("VFX_TripHammer")
    if ob is None or mh is None:
        return
    piv = Vector(tuple(mh["pivot"]))
    ax = Vector(tuple(mh.get("axis", (1, 0, 0)))).normalized()
    head = mh.location - piv
    if (Matrix.Rotation(0.05, 3, ax) @ head).z < head.z:
        ax = -ax
    lift = float(mh.get("lift", 0.16))
    ob.matrix_world = Matrix.Translation(piv) @ Matrix.Rotation(lift, 4, ax) @ Matrix.Translation(-piv) @ ob.matrix_world
    print("PILAO levantado %.2f rad em volta de %s" % (lift, tuple(round(x, 2) for x in ax)))


def _render(out, cams_, roblox=False, noite=False, vfx=False, alto=False, no_golem=False):
    if roblox:
        import fm_pv3
        fm_pv3.load()
        import fm_portals
        print("MODO roblox: %d materiais" % fm_lib.apply_preview("roblox"))
    if noite:
        _night()
    else:
        _day()
    for o in bpy.data.objects:
        if o.name.startswith("PREVIEW_VFX_"):
            o.hide_render = not vfx
    if alto:
        _raise_hammer()
    g = bpy.data.objects.get("PREVIEW_Ignis")
    if g is not None:
        g.hide_render = no_golem
    os.makedirs(out, exist_ok=True)
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = 960, 540
    sc.render.resolution_percentage = 100
    sc.eevee.taa_render_samples = 16
    sc.render.image_settings.file_format = "JPEG"
    sc.render.image_settings.quality = 90
    for cn in cams_:
        ob = bpy.data.objects.get(cn)
        if not ob:
            print("RENDER camera inexistente:", cn)
            continue
        sc.camera = ob
        sc.render.filepath = os.path.join(out, cn + ".jpg")
        bpy.ops.render.render(write_still=True)
        print("RENDER", cn)


# ------------------------------------------------------------------ folhas (PIL)
def _sheet(dp, dr, np_, nr, cp, cr, outdir):
    sys.path.insert(0, HERE)
    import vm_sheet as SH
    os.makedirs(outdir, exist_ok=True)

    def rows_for(cl, a, b, ta, tb):
        rows = []
        for cn in cl:
            row = []
            for d, tag in ((a, ta), (b, tb)):
                p = os.path.join(d, cn + ".jpg")
                if os.path.exists(p):
                    row.append(SH.label(SH.fit(p, 640), "%s  %s" % (tag, cn.replace("CAM_VM_", ""))))
            if row:
                rows.append(row)
        return rows
    sets = [
        ("FOLHA_luz_dia.jpg", "V3b luz do DIA (sol quente a sudoeste, sombra suave) - spawn, praca, rua, forja",
         ["CAM_VM_P_Spawn", "CAM_VM_P_Praca", "CAM_VM_P_Rua", "CAM_VM_P_Forja", "CAM_VM_Ref_01"], dp, dr,
         "DIA PREVIA", "DIA ROBLOX"),
        ("FOLHA_luz_noite.jpg", "V3b NOITE (so conferencia): lanternas NightOnly + janelas acesas + camara da chamine",
         ["CAM_VM_L_NoiteRua", "CAM_VM_L_NoitePraca", "CAM_VM_L_NoiteCurva", "CAM_VM_P_Spawn"], np_, nr,
         "NOITE PREVIA", "NOITE ROBLOX"),
        ("FOLHA_vfx_closes.jpg", "V3b closes (proxies de VFX): boca, roda, pilao repouso | levantado, "
         "chamine + pluma", ["CAM_VM_L_Boca", "CAM_VM_L_Roda", "CAM_VM_L_Pilao", "CAM_VM_L_Pilao_ALTO",
                                             "CAM_VM_L_Chamine"], cp, cr, "PREVIA", "ROBLOX"),
    ]
    for fn, title, cl, a, b, ta, tb in sets:
        rows = rows_for(cl, a, b, ta, tb)
        if rows:
            SH.compose(rows, os.path.join(outdir, fn), title)


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    cmd = argv[0] if argv else ""
    if cmd == "sheet":
        _sheet(*argv[1:8])
    elif cmd == "apply":
        rep = build()
        cameras()
        bpy.ops.wm.save_as_mainfile(filepath=argv[1], compress=True)
        print("APPLY OK ->", argv[1])
    elif cmd == "render":
        cl = [a for a in argv[2:] if a.startswith("CAM_")]
        _render(argv[1], cl, roblox="--roblox" in argv, noite="--noite" in argv, vfx="--vfx" in argv,
                alto="--pilao-alto" in argv, no_golem="--sem-golem" in argv)
    elif cmd == "qa":
        r = count()
        sun = bpy.data.objects.get("SUN_Key")
        r["sol"] = sun_rbx(sun["sun_dir_blender"]) if sun is not None and "sun_dir_blender" in sun else None
        r["proxies"] = sorted(o.name for o in bpy.data.objects if o.name.startswith("PREVIEW_VFX_"))
        r["ok"] = r["dia"] <= 30
        print("LUZES QA dia %d (<= 30: %s), NightOnly %d (lanternas %d, janelas %d); sol %s; proxies %d" % (
            r["dia"], r["ok"], r["noite"], r["lanternas"], r["janelas_n"], r["sol"], len(r["proxies"])))
        print("LUZES QA de dia:", ", ".join(r["lista_dia"]))
        if len(argv) > 1:
            json.dump(r, open(argv[1], "w", encoding="utf-8"), indent=1)
