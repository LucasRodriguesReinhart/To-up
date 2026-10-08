# export_vm_vfx.py - VFX e MOVIMENTO do lobby Vila Medieval para o Roblox (onda V3b), com o MESMO mecanismo do lobby
# atual (lobby_area/forja_mineradora/export_vfx.py, SO LEITURA: importado e reaproveitado aqui, nunca editado):
#   LOBBY_VFX_MOVING_<ID6>.fbx       pecas moveis (roda d'agua + eixo + cames, martelo-pilao), 1 material por malha
#   vfx_lobby_vila_medieval.lua      MONTAGEM = o SETUP_LUA do export_vfx (tags FORJA_*, atributos VFX_*, pastas
#                                    LOBBY_FORJA.VFX / VFX_MOVING, ReplicatedStorage.LOBBY_FORJA_VFX com Evento e o
#                                    RemoteEvent IgnisImpact do golem preservado) com os dados da vila e 4 trocas
#                                    pontuais: sem carrinho de mina, regras de brilho/luz com os nomes da vila, respingo
#                                    da roda no sentido da levada e textos com os nomes dos arquivos daqui
#   vfx_lobby_vila_medieval_client.lua   o CLIENT_LUA do export_vfx (o LocalScript VFX_Lobby_Forja_Client) com os dados
#                                    da vila + o gancho IgnisImpact (o mesmo patch que o jogo ja tem)
# A geometria movel ja sai em OBJETOS PROPRIOS no vm_forge (props 'source' dos marcadores): VM_Frg_Wheel gira com o
# VFX_Waterwheel_Rotate (pivot, axis_vec, rpm, R, half_w) e VM_Frg_TripHammer bate com o VFX_TripHammer (pivot, axis,
# cams, cam_len, cam_x, low_axle, rest, lift). O estatico continua exportando as duas (sem VFX a roda fica parada); a
# montagem guarda as estaticas em ServerStorage.LOBBY_FORJA_VFX_ORIGINAIS e poe as moveis no lugar (tudo ou nada).
# uso: o export_vm.py chama configure(ER) antes do export estatico e main(export_id) depois (mesmo processo/pasta).
#      sozinho: blender -b --factory-startup lobby_vila_medieval.blend --python export_vm_vfx.py -- <pasta> (le o
#      EXPORT_ID do lobby_vm_data.json da pasta; prefira o export_vm, que gera tudo junto)
import sys, os, math, json
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import vm_lib as VL                    # forja_mineradora no sys.path (so leitura)
import bpy
from mathutils import Vector, Matrix
import vm_layout as L

SOURCES = ("VM_Frg_Wheel", "VM_Frg_TripHammer")
SETUP_FILE = "vfx_lobby_vila_medieval.lua"
CLIENT_FILE = "vfx_lobby_vila_medieval_client.lua"
RELEASE_DEG = 95.0             # o came solta o cabo quando passa da vertical (fase 'fall0' do perfil do martinete)
DATA_FILE = "lobby_vm_data.json"


def configure(ER):
    """antes do export estatico: as fontes do VFX nao fundem material (a montagem troca por familia exata)"""
    ER.NO_FOLD_OBJ = tuple(ER.NO_FOLD_OBJ) + tuple(s for s in SOURCES if s not in ER.NO_FOLD_OBJ)


def _ev():
    import export_roblox as ER
    configure(ER)
    import export_vfx as EV
    return ER, EV


def B(x, z, y):
    return VL.B(x, z, y)


def vec(o, names, default=None):
    for n in names:
        if o is not None and n in o.keys():
            try:
                t = tuple(float(x) for x in o[n])
                if len(t) == 3:
                    return Vector(t)
            except TypeError:
                continue
    return default


def num(o, names, default):
    for n in names:
        if o is not None and n in o.keys():
            try:
                return float(o[n])
            except (TypeError, ValueError):
                continue
    return default


def size_rbx(o):
    """props size dos marcadores do vm_forge: ordem ROBLOX (largura x, altura, profundidade z)"""
    s = vec(o, ("size",))
    return None if s is None else (abs(s.x), abs(s.y), abs(s.z))


# ------------------------------------------------------------------ 1. roda d'agua (VM_Frg_Wheel)
def build_wheel(ctx, mk, EV):
    m = mk["VFX_Waterwheel_Rotate"]
    src = str(m.get("source", "VM_Frg_Wheel"))
    ob = bpy.data.objects[src]
    wc = vec(m, ("pivot", "center"), m.location.copy())
    axis = vec(m, ("axis_vec", "axis"), Vector((1, 0, 0))).normalized()
    rpm = num(m, ("rpm",), 6.0)
    w = 2 * math.pi * rpm / 60.0
    R = num(m, ("R", "radius", "raio"), L.WHEEL_R)
    half = num(m, ("half_w",), 1.6)
    bm = EV.world_bm(ob)
    uv = bm.loops.layers.uv.get("UVMap")
    isl = EV.islands(ob, bm)
    mats = ob.data.materials
    # conferencias: pivo no eixo de simetria (centro dos aros) e cames no eixo
    rim = [p for i in isl for p in i.cos if abs(abs(p.x - wc.x) - half) <= 0.45 and
           math.hypot(p.y - wc.y, p.z - wc.z) > R - 1.4]
    if rim:
        cy = (max(p.y for p in rim) + min(p.y for p in rim)) / 2
        cz = (max(p.z for p in rim) + min(p.z for p in rim)) / 2
        err = math.hypot(cy - wc.y, cz - wc.z)
        ctx["log"].append("roda: pivo x centro dos aros = %.3f stud" % err)
        if err > 0.15:
            raise RuntimeError("roda: pivot do VFX_Waterwheel_Rotate fora do centro dos aros (%.2f)" % err)
    if abs(abs(axis.x) - 1.0) > 1e-3:
        raise RuntimeError("roda: eixo %s (o vm_forge gira em X)" % tuple(axis))
    s = 1.0 if axis.x > 0 else -1.0              # fase phi (plano YZ do Blender, de +Y para +Z) cresce com s*w*t
    # cames: ilhas na fatia x = cam_x, fora do eixo (bracos + sapatas), angulo phi de cada uma
    mh = mk.get("VFX_TripHammer")
    cam_x = num(mh, ("cam_x",), 24.5)
    low = vec(mh, ("low_axle",), Vector((cam_x, wc.y, wc.z)))
    cl = num(mh, ("cam_len", "came"), 1.6)
    phis = []
    for i in isl:
        if all(abs(p.x - cam_x) <= 0.8 for p in i.cos) and not EV.is_shaft(i, low, rmax=0.85, minlen=0.0):
            d = math.hypot(i.c.y - low.y, i.c.z - low.z)
            if 0.3 < d <= cl + 0.4:
                phis.append(math.degrees(math.atan2(i.c.z - low.z, i.c.y - low.y)) % 360.0)
    ncam = int(num(mh, ("cams",), 3))
    span = 360.0 / ncam
    mods = sorted({round(p % span, 0) for p in phis})
    if not phis or max(mods) - min(mods) > 4.0:
        raise RuntimeError("roda: cames nao achados ou fora do passo de %.0f graus (%s)" % (span, mods))
    phi0 = sum(p % span for p in phis) / len(phis)
    o_rot = EV.faces_obj("VFX_Roda_src", list(bm.faces), mats, remap=EV.majority_remap(isl, mats), uv=uv)
    bm.free()
    fine = EV.fine_ok(src)
    fams = sorted({EV.src_key(x.name, fine) for x in mats if x})
    EV.add_obj(ctx, "roda", o_rot, name="VFX_Roda", kind="spin", assembly="RodaDagua", pivot=wc, axis=axis, speed=w)
    ctx["sources"].append((src, fams, ["roda"]))
    # pas: 16 com fase 0 (multiplos de 22,5 graus); entram na agua a montante (sul = -Y Blender) e saem a jusante
    wz = mk["VFX_Wheel_Splash"].location.z if "VFX_Wheel_Splash" in mk else L.Y_WATER
    dy = math.sqrt(max(0.0, R * R - (wz - wc.z) ** 2))
    phi_in = math.atan2(wz - wc.z, -dy)
    phi_out = math.atan2(wz - wc.z, dy)
    # o cliente dispara 'roda:entra' quando floor((w t + aIn) / passo) muda: pa k em phi = k*passo + s*w*t
    ctx["wheel"] = dict(center=wc, R=R, w=w, rpm=rpm, paddles=16, a_in=-s * phi_in, a_out=-s * phi_out, s=s,
                        dy=dy, wz=wz, half=half, phi0=phi0, ncam=ncam)
    ctx["log"].append("roda: %s gira em %s a %.1f rpm (%.3f rad/s), R %.1f, %d cames em phi %s (fase %.1f)" % (
        src, tuple(axis), rpm, w, R, len(phis) // 2 or len(phis), sorted(round(p) for p in phis), phi0))


# ------------------------------------------------------------------ 2. martelo-pilao (VM_Frg_TripHammer)
def build_hammer(ctx, mk, EV):
    mh = mk["VFX_TripHammer"]
    src = str(mh.get("source", "VM_Frg_TripHammer"))
    ob = bpy.data.objects[src]
    piv = vec(mh, ("pivot", "pivo"))
    head = mh.location.copy()
    ax = vec(mh, ("axis", "eixo"), Vector((1, 0, 0))).normalized()
    if (Matrix.Rotation(0.05, 3, ax) @ (head - piv)).z < (head - piv).z:
        ax = -ax                                  # angulo positivo = cabeca sobe
    rest = num(mh, ("rest",), 0.0)
    lift = abs(num(mh, ("lift",), 0.16))
    W = ctx["wheel"]
    span = 2 * math.pi / W["ncam"]
    # u = ((w t - camPhase) mod passo) / passo; o came passa da vertical (phi = RELEASE) em u = fall0
    fall0 = EV.HAMMER_PROFILE["fall0"]
    cam_phase = (W["s"] * (math.radians(RELEASE_DEG) - math.radians(W["phi0"])) - fall0 * span) % span
    bm = EV.world_bm(ob)
    uv = bm.loops.layers.uv.get("UVMap")
    isl = EV.islands(ob, bm)
    mats = ob.data.materials
    zmin = min(p.z for i in isl for p in i.cos)
    # cabo sobre o came em repouso: folga entre a sapata no alto (phi 90) e o fundo do cabo na fatia do came
    cam_x = num(mh, ("cam_x",), 24.5)
    low = vec(mh, ("low_axle",))
    from mathutils.bvhtree import BVHTree
    hit = BVHTree.FromBMesh(bm).ray_cast(Vector((cam_x, low.y, low.z)), Vector((0, 0, 1)), 20.0)
    clear = (hit[0].z - (low.z + num(mh, ("cam_len",), 1.6))) if hit[0] is not None else None
    o = EV.faces_obj("VFX_Martinete_src", list(bm.faces), mats, remap=EV.majority_remap(isl, mats), uv=uv)
    bm.free()
    fine = EV.fine_ok(src)
    fams = sorted({EV.src_key(x.name, fine) for x in mats if x})
    EV.add_obj(ctx, "martinete", o, name="VFX_Martinete", kind="hammer", assembly="MarteloPilao", pivot=piv, axis=ax,
               speed=W["w"], cam_phase=cam_phase, cams=W["ncam"], rest=rest, lift=lift, event="martinete")
    ctx["sources"].append((src, fams, ["martinete"]))
    ctx["hammer"] = dict(head=head, piv=piv)
    up = (Matrix.Rotation(lift, 3, ax) @ (head - piv)).z - (head - piv).z
    ctx["log"].append("martelo-pilao: pivo %s eixo %s, curso %.2f rad (cabeca sobe %.2f), fase dos cames %.3f rad, "
                      "pe da cabeca z %.2f (bigorna %.2f), folga cabo/came %s" % (
                          tuple(round(x, 2) for x in piv), tuple(ax), lift, up, cam_phase, zmin,
                          num(mh, ("anvil_top",), 0), "%.2f" % clear if clear is not None else "-"))


# ------------------------------------------------------------------ 3. portais (espirais giradas para o patio)
def build_portals(ctx, EV):
    cxr, czr = L.COURT_C
    for idx, (key, _aid) in enumerate(L.PORTALS):
        sw = bpy.data.objects.get("PORTAL_%s_Swirl" % key)
        if sw is None:
            continue
        mw = sw.matrix_world
        cs = [mw @ v.co for v in sw.data.vertices]
        mn, mx = EV.bbox_of(cs)
        c = (mn + mx) / 2
        to = B(cxr, czr, c.z) - c
        n = Vector((to.x, to.y, 0)).normalized()          # a espiral olha o centro do patio (vm_portals)
        R = max((p - c - n * (p - c).dot(n)).length for p in cs)
        dn = [(p - c).dot(n) for p in cs]
        thick = max(dn) - min(dn)
        pal = EV.PORTAL_PAL.get(key)
        smat = sw.data.materials[0].name if sw.data.materials and sw.data.materials[0] else ""
        textured = smat in EV.TX.SWIRL_TEX or smat in EV.fm_lib.SWIRLS
        rims = []
        for o in bpy.data.objects:
            if o.type != "MESH" or o is sw or not o.name.startswith("PORTAL_%s" % key):
                continue
            names = [m.name if m else "" for m in o.data.materials]
            tot, hit = {}, {}
            omw = o.matrix_world
            for p in o.data.polygons:
                m = names[p.material_index] if p.material_index < len(names) else ""
                if not m or not EV.is_glow(m) or m in EV.fm_lib.SWIRLS or m in EV.TX.SWIRL_TEX:
                    continue
                tot[m] = tot.get(m, 0) + 1
                q = omw @ p.center - c
                a = q.dot(n)
                r = (q - n * a).length
                if 0.85 * R <= r <= 1.5 * R and abs(a) <= 2.5:
                    hit[m] = hit.get(m, 0) + 1
            for m, k in hit.items():
                if k >= 4 and k >= 0.5 * tot[m]:
                    rims.append("%s__%s" % (o.name, m))
        ctx["portals"].append(dict(key=key, center=c, R=R, thick=thick, normal=n, pal=pal, idx=idx,
                                   swirl="PORTAL_%s_Swirl" % key, textured=textured,
                                   spin=EV.PORTAL_SPIN.get(key, 0.9), rims=sorted(rims)))
    ctx["log"].append("portais: %d (com textura %d; aros Neon %s)" % (
        len(ctx["portals"]), sum(1 for p in ctx["portals"] if p["textured"]),
        ", ".join("%s=%d" % (p["key"], len(p["rims"])) for p in ctx["portals"])))


# ------------------------------------------------------------------ 4. agua: quedas nas pontas do canal + correntes
def waterfalls(EV):
    out = []
    for o in bpy.data.objects:
        if o.type != "MESH" or not o.name.startswith("VM_Water_"):
            continue
        names = [m.name if m else "" for m in o.data.materials]
        if "Water_VM" not in names:
            continue
        wi = names.index("Water_VM")
        bm = EV.world_bm(o)
        for i in EV.islands(o, bm):
            pts = [v.co.copy() for f in i.faces if f.material_index == wi for v in f.verts]
            if not pts or i.mx.z - i.mn.z < 6.0 or i.mx.x - i.mn.x > 6.0:
                continue
            xm = (i.mn.x + i.mx.x) / 2
            od = Vector((1.0 if xm > 0 else -1.0, 0, 0))   # cai para fora do plato (ponta oeste -X, leste +X)
            xo = i.mx.x if od.x > 0 else i.mn.x
            ym = (i.mn.y + i.mx.y) / 2
            top = Vector((xo, ym, i.mx.z))
            base = Vector((xo, ym, i.mn.z + 1.0))
            f = dict(top=top, base=base, width=max(3.0, i.mx.y - i.mn.y), out=od, lip=0.0, obj=o.name,
                     name="Canal_%s" % ("Leste" if od.x > 0 else "Oeste"))
            f.update(EV.fit_beam(top, base, od, pts, 0.0))
            out.append(f)
        bm.free()
    return sorted(out, key=lambda f: f["name"])


def flows():
    y = L.Y_WATER + 0.08
    z0, z1 = L.CANAL_Z
    x0, x1 = L.CANAL_X
    zc = (z0 + z1) / 2
    rx = (L.RACE_X[0] + L.RACE_X[1]) / 2
    return [
        dict(name="Canal_Oeste", a=B(-4.0, zc, y), b=B(x0 + 1.0, zc, y), width=(z1 - z0) - 0.6, speed=2.5),
        dict(name="Canal_Leste", a=B(4.0, zc, y), b=B(x1 - 1.0, zc, y), width=(z1 - z0) - 0.6, speed=2.5),
        dict(name="Levada", a=B(rx, L.RACE_Z[0] - 0.5, y), b=B(rx, L.RACE_Z[1] + 0.5, y),
             width=(L.RACE_X[1] - L.RACE_X[0]) - 0.6, speed=3.5),
    ]


# ------------------------------------------------------------------ 5. pontos dos efeitos (marcadores do vm_forge)
def fx_points(ctx, mk):
    fx = {}
    m = mk.get("VFX_Hearth_Fire")
    if m:
        s = size_rbx(m) or (7.4, 3.2, 3.2)
        # props: largura x profundidade x ALTURA das chamas (ordem do vm_forge); lamina no leito de brasas
        fx["hearth"] = dict(pos=m.location.copy(), size=(max(1.0, s[0] * 0.85), 0.4, max(1.0, s[1] * 0.7)),
                            height=s[2])
    m = mk.get("VFX_Chimney_Smoke_Emitter")
    if m:
        fx["chimney"] = dict(pos=m.location + Vector((0, 0, 0.5)), radius=num(m, ("radius",), 3.6))
    fx["anvil_ignis"] = dict(pos=mk["VFX_Anvil_Sparks"].location.copy())
    fx["anvil_hammer"] = dict(pos=mk["VFX_Forge_Sparks"].location.copy())
    m = mk.get("VFX_Quench_Steam")
    if m:
        fx["quench"] = dict(pos=m.location.copy(), size=size_rbx(m) or (1.4, 0.2, 1.4))
    W = ctx["wheel"]
    wc = W["center"]
    fx["wheel_in"] = dict(pos=Vector((wc.x, wc.y - W["dy"], W["wz"] + 0.2)))     # a montante (sul): pas entram
    fx["wheel_out"] = dict(pos=Vector((wc.x, wc.y + W["dy"], W["wz"] + 0.2)))    # a jusante (norte): pas saem
    fx["wheel_mist"] = dict(pos=mk["VFX_Wheel_Splash"].location.copy())
    ctx["fx"] = fx
    ctx["vents"] = []
    ctx["smokes"] = []
    ctx["log"].append("forja: lareira %s, chamine z%.1f r%.1f, bigorna do Ignis %s, pilao %s, tempera %s" % (
        "ok" if "hearth" in fx else "-", VL.R(fx["chimney"]["pos"])[1] if "chimney" in fx else -1,
        fx["chimney"]["radius"] if "chimney" in fx else 0,
        tuple(round(x, 1) for x in VL.R(fx["anvil_ignis"]["pos"])),
        tuple(round(x, 1) for x in VL.R(fx["anvil_hammer"]["pos"])), "ok" if "quench" in fx else "-"))


def collect(EV):
    mk = EV.markers()
    ctx = dict(groups={}, sources=[], portals=[], log=[], mk=mk)
    build_wheel(ctx, mk, EV)
    build_hammer(ctx, mk, EV)
    build_portals(ctx, EV)
    fx_points(ctx, mk)
    ctx["waterfalls"] = waterfalls(EV)
    ctx["flows"] = flows()
    ctx["log"].append("quedas: %s; correntes: %s" % (
        ", ".join("%s(l=%.1f h=%.1f)" % (w["name"], w["width"], w["top"].z - w["base"].z) for w in ctx["waterfalls"]),
        ", ".join("%s(%.0f)" % (f["name"], (f["b"] - f["a"]).length) for f in ctx["flows"])))
    ctx["log"].append("pecas moveis: %d caixas com chanfro minusculo viraram caixas limpas" % ctx.get("unbevel", 0))
    refs = []
    for n in ("VFX_Waterwheel_Rotate", "NPC_Ignis", "PORTAL_Naruto"):
        if n in mk:
            o = mk[n]
            R3 = o.matrix_world.to_3x3().normalized()
            refs.append(dict(kind="marker", name=n, pos=EV.rbx(o.location), x=EV.rbx(R3.col[0]), y=EV.rbx(R3.col[1])))
    ctx["refs"] = refs
    ctx["exact"] = sorted({m.name for s in ctx["sources"] for m in bpy.data.objects[s[0]].data.materials
                           if m and EV.is_glow(m.name)})
    # sem carrinho de mina: os campos ficam neutros (o cliente so cria carrinho com o molde MineCart, que a montagem
    # da vila apaga)
    ctx["cart"] = dict(path=[], rest=0.0, far=0.0, weigh=None, loc=Vector((0, 0, 0)), yaw=0.0)
    return ctx


# ------------------------------------------------------------------ Luau: o do export_vfx com trocas conferidas
def _swap(src, old, new, label, count=1):
    k = src.count(old)
    if k != count:
        raise RuntimeError("export_vm_vfx: trecho '%s' do export_vfx mudou (%d ocorrencias, esperado %d): revise a troca"
                           % (label, k, count))
    return src.replace(old, new)


def _cut(src, start, end, new, label):
    a = src.find(start)
    b = src.find(end, a + len(start)) if a >= 0 else -1
    if a < 0 or b < 0 or src.count(start) != 1:
        raise RuntimeError("export_vm_vfx: bloco '%s' do export_vfx mudou: revise o recorte" % label)
    return src[:a] + new + src[b + len(end):]


CART_NEW = """-- ---------------------------------------------------------------- (lobby Vila Medieval: SEM carrinho de mina)
-- o molde antigo sai do ReplicatedStorage (o cliente so cria carrinho se ele existir) e pecas de carrinho vao para
-- ServerStorage
do local old = CFG:FindFirstChild("MineCart"); if old then old:Destroy() end end
for _, cp in ipairs(cartParts) do cp[1].Parent = ORIG end
CFG:SetAttribute("VFX_Lobby", "VilaMedieval")
"""

PULSE_NEW = """    if string.find(n, "__Forge_Glow_VM", 1, true) then
      kind = "ember"                                     -- boca da fornalha, leito e linguas da chamine (VM_Frg_*)
    elseif string.find(n, "__Lantern_Glow", 1, true) then
      kind = "lantern"
    end
"""

LIGHT_NEW = """    if string.sub(n, 1, 9) == "L_Portal_" then
      kind, event = "portal", "portal:" .. string.sub(n, 10)
    elseif string.sub(n, 1, 13) == "L_Hearth_Fire" or n == "L_VM_Night_Chimney" then
      kind = "fire"                                      -- boca da fornalha (a luz mais forte) e camara da chamine
    elseif string.sub(n, 1, 11) == "L_VM_ShopIn" then
      kind = nil                                         -- interior da loja: luz fixa
    end
"""

IGNIS_HOOK = """local lastRigStrike = -1e9
local impactRemote = CFG:WaitForChild("IgnisImpact", 10)
if impactRemote and impactRemote:IsA("RemoteEvent") then
  lastRigStrike = os.clock()
  impactRemote.OnClientEvent:Connect(function(power)
    lastRigStrike = os.clock()
    fire("ignis", tonumber(power) or 1)
  end)
end"""


def setup_lua(EV, data):
    s = EV.SETUP_LUA
    s = _cut(s, "-- ---------------------------------------------------------------- molde do carrinho (o cliente clona)",
             "tpl.Parent = CFG\n", CART_NEW, "molde do carrinho")
    s = _cut(s, '    if string.find(n, "__Crystal_", 1, true) then', '      kind = "lantern"\n    end\n', PULSE_NEW,
             "pulsos das pecas estaticas")
    s = _cut(s, '    if string.sub(n, 1, 9) == "L_Portal_" then', '      kind = nil\n    end\n', LIGHT_NEW,
             "luzes com flicker")
    s = _swap(s, "accel = Vector3.new(0, -40, 3)", "accel = Vector3.new(0, -40, 3 * DATA.wheelFlowZ)", "respingo")
    s = _swap(s, "accel = Vector3.new(0, -40, 2)", "accel = Vector3.new(0, -40, 2 * DATA.wheelFlowZ)", "pa")
    s = _swap(s, "VFX e MOVIMENTO do Lobby Vila-Forja - MONTAGEM",
              "VFX e MOVIMENTO do lobby VILA MEDIEVAL - MONTAGEM (export_vm_vfx.py sobre o SETUP_LUA do export_vfx)",
              "titulo")
    s = _swap(s, '(#cartParts > 0) and "malha" or "Parts")', '"nenhum (vila)")', "log final")
    s = _swap(s, "--@DATA@", data, "dados")
    return _names(s)


def client_lua(EV, data):
    s = EV.CLIENT_LUA
    s = _swap(s, "local lastRigStrike = -1e9", IGNIS_HOOK, "gancho IgnisImpact")
    s = _swap(s, "VFX e MOVIMENTO do Lobby Vila-Forja - ANIMACAO NO CLIENTE",
              "VFX e MOVIMENTO do lobby VILA MEDIEVAL - ANIMACAO NO CLIENTE (LocalScript VFX_Lobby_Forja_Client; com o "
              "gancho do RemoteEvent IgnisImpact)", "titulo")
    s = _swap(s, "--@DATA@", data, "dados")
    return _names(s)


def _names(s):
    for a, b in (("vfx_lobby_forja_client.lua", CLIENT_FILE), ("vfx_lobby_forja.lua", SETUP_FILE),
                 ("montar_lobby_forja.lua", "montar_lobby_vila_medieval.lua"), ("export_all.py", "export_vm.py"),
                 ("gerado por export_vfx.py", "gerado por export_vm_vfx.py (+ export_vfx.py)")):
        s = s.replace(a, b)
    return s.replace("@VERSION@", "vfx-forja-2")


def data_setup(EV, ctx, movers):
    d = EV.lua_data_setup(ctx, movers)
    d = _swap(d, "DATA.wheelWidth = 3.4", "DATA.wheelWidth = %s\nDATA.wheelFlowZ = -1  -- a levada corre para o norte "
              "(-Z): respingos a jusante" % EV.fnum(2 * ctx["wheel"]["half"]), "largura da roda")
    lines = [ln for ln in d.split("\n") if not ln.startswith("DATA.cartRest")]
    return "\n".join(lines)


def read_export_id(out):
    p = os.path.join(out, DATA_FILE)
    try:
        return json.load(open(p, encoding="utf-8")).get("export_id")
    except (OSError, ValueError):
        return None


def main(out, export_id=None):
    ER, EV = _ev()
    EV.OUT = out
    os.makedirs(out, exist_ok=True)
    EV.TX.ensure()
    ctx = collect(EV)
    ctx["export_id"] = export_id or read_export_id(out)
    movers = EV.export_meshes(ctx)
    setup = setup_lua(EV, data_setup(EV, ctx, movers))
    client = client_lua(EV, EV.lua_data_client(ctx))
    for fn, src in ((SETUP_FILE, setup), (CLIENT_FILE, client)):
        with open(os.path.join(out, fn), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(src)
        ctx["log"].append("%s: %d linhas" % (fn, src.count("\n")))
    EV.cleanup()
    for line in ctx["log"]:
        print("[export_vm_vfx]", line)
    print("EXPORT VFX VM OK movers=%d portais=%d quedas=%d correntes=%d EXPORT_ID %s -> %s" % (
        len(movers), len(ctx["portals"]), len(ctx["waterfalls"]), len(ctx["flows"]), ctx["export_id"] or "-",
        os.path.join(out, ctx.get("fbx") or "")))
    return ctx


if __name__ == "__main__":
    _argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    main(os.path.abspath(_argv[0]) if _argv else os.path.join(HERE, "export"))
