# export_vfx.py - VFX e MOVIMENTO do Lobby Vila-Forja para o Roblox
# uso: blender -b lobby_forja_mineradora.blend --python export_vfx.py
#      (rode depois do export_roblox.py; FM_VFX_OUT=<pasta> desvia a saida, padrao ./export)
# saida em ./export/:
#   LOBBY_VFX_MOVING.fbx          pecas moveis: roda d'agua (rotor + parte fixa), engrenagens e cames, martinete,
#                                 espirais dos portais, carrinho de mina. Mesmo padrao do export_roblox:
#                                 "<objeto>__<material>[_k]", 1 material por malha, origem no centro.
#   vfx_lobby_forja.lua           MONTAGEM (Command Bar uma vez, ou Script em ServerScriptService)
#   vfx_lobby_forja_client.lua    ANIMACAO (LocalScript em StarterPlayer > StarterPlayerScripts)
#
# Por que um FBX extra: no export estatico a roda, as engrenagens e o martinete estao fundidos com pecas fixas
# (mancais, calhas, paredes, chanfros). Aqui o script separa as ILHAS de malha que giram das que ficam paradas,
# e a montagem guarda as malhas estaticas originais em ServerStorage (reversivel) e poe as versoes separadas no
# lugar. O que nao se move continua identico.
import sys, os, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy, bmesh
from mathutils import Vector, Matrix
import fm_layout as L
import fm_lib
import fm_parts
import export_roblox as ER

OUT = os.environ.get("FM_VFX_OUT") or os.path.join(HERE, "export")
VERSION = "vfx-forja-1"
TMP_COLL = "_VFX_TMP"

# ------------------------------------------------------------------ constantes do fm_water (locais das funcoes)
WHEEL_HALF_W = 1.7 + 0.75      # meia largura da roda (Wd/2) + folga: tudo dentro gira
UZ = 15.5                      # eixo alto (pinhao) na casa da roda
GEAR_DX = 2.4                  # gx = MILL.x0 + 2.4 (roda de coroa e pinhao)
GEAR_RC, GEAR_RP, TOOTH = 2.9, 1.3, 0.25
CAM_LEN = 2.0
HAMMER_PIV = (5.0, 9.0)        # pivo do martinete: (wy + 5, z 9)
HAMMER_REST = 0.03             # rad acima da pose modelada: cabeca assenta na bigorna e o came so encosta no cabo
HAMMER_LIFT = 0.16             # rad de subida maxima
# perfil do martinete em fracao do intervalo entre cames (3 cames = 120 graus):
# came passa (0-15) -> cabo sobe seguindo o came (15-64) -> segura -> cai rapido (66-72) = GOLPE -> quique
# (cai antes do proximo came chegar: o cabo nunca atravessa os cames)
HAMMER_PROFILE = {"rise0": 15 / 120, "rise1": 64 / 120, "fall0": 66 / 120, "hit": 72 / 120, "bounce": 80 / 120}

PORTAL_SPIN = 0.85             # rad/s dos bracos (sentido que "suga" para o centro)
PORTAL_INNER = 2.3             # multiplicador do clone interno (vortice: centro gira mais rapido)
PORTAL_PAL = {  # sRGB: disco saturado, bracos claros, nucleo quase branco (no Roblox nao ha shader de espiral)
    "Naruto": ((232, 52, 96), (255, 178, 204), (255, 238, 244)),
    "DragonBall": ((255, 146, 18), (255, 232, 150), (255, 251, 228)),
    "ShadowGarden": ((118, 38, 214), (208, 158, 255), (244, 232, 255)),
    "DemonSlayer": ((206, 28, 40), (255, 150, 138), (255, 234, 226)),
    "OnePiece": ((24, 92, 226), (138, 204, 255), (228, 246, 255)),
    "OnePunchMan": ((16, 168, 236), (176, 242, 255), (236, 252, 255)),
}

CART_MARGIN = 2.9              # meio carrinho + folga para nao encostar nos carrinhos estacionados
CART_Z = L.FLOOR + 0.3         # mesma cota dos carrinhos do fm_mine


# ------------------------------------------------------------------ utilitarios
def rbx(v):
    return ER.to_rbx(v)


def fnum(x):
    s = ("%.3f" % x).rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


def lv3(v):
    return "Vector3.new(%s, %s, %s)" % tuple(fnum(x) for x in v)


def lc3(c):
    return "Color3.fromRGB(%d, %d, %d)" % tuple(int(x) for x in c)


def tmp_coll():
    c = bpy.data.collections.get(TMP_COLL)
    if c is None:
        c = bpy.data.collections.new(TMP_COLL)
        bpy.context.scene.collection.children.link(c)
    return c


def ensure_mat(name, srgb_col):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
        lin = [((x / 255.0 + 0.055) / 1.055) ** 2.4 if x / 255.0 > 0.04045 else x / 255.0 / 12.92 for x in srgb_col]
        m.diffuse_color = (*lin, 1.0)
    return m


def matname(mats, i):
    if i < len(mats) and mats[i] is not None:
        return mats[i].name
    return "Default"


def markers():
    c = bpy.data.collections.get("15_GAMEPLAY_MARKERS")
    return {o.name: o for o in c.objects} if c else {}


class Isl:
    __slots__ = ("faces", "cos", "c", "mn", "mx", "mats")


def world_bm(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bm.transform(ob.matrix_world)
    bm.verts.ensure_lookup_table()
    bm.verts.index_update()
    return bm


def islands(ob, bm):
    """ilhas de malha conexas (cada primitiva do MB e uma ilha: caixa, cilindro, viga...)"""
    par = list(range(len(bm.verts)))

    def find(i):
        while par[i] != i:
            par[i] = par[par[i]]
            i = par[i]
        return i
    for e in bm.edges:
        a, b = find(e.verts[0].index), find(e.verts[1].index)
        if a != b:
            par[a] = b
    groups = {}
    for f in bm.faces:
        groups.setdefault(find(f.verts[0].index), []).append(f)
    mats = ob.data.materials
    out = []
    for faces in groups.values():
        vs = {}
        for f in faces:
            for v in f.verts:
                vs[v.index] = v.co
        cos = [c.copy() for c in vs.values()]
        i = Isl()
        i.faces = faces
        i.cos = cos
        i.c = sum(cos, Vector()) / len(cos)
        i.mn = Vector((min(p.x for p in cos), min(p.y for p in cos), min(p.z for p in cos)))
        i.mx = Vector((max(p.x for p in cos), max(p.y for p in cos), max(p.z for p in cos)))
        i.mats = {matname(mats, f.material_index) for f in faces}
        out.append(i)
    return out


def faces_obj(name, faces, src_mats, only_mats=None):
    """copia faces (de um bmesh fonte) para um objeto novo multi-material; only_mats filtra por material"""
    bm = bmesh.new()
    vmap = {}
    mlist = []
    for f in faces:
        m = matname(src_mats, f.material_index)
        if only_mats is not None and m not in only_mats:
            continue
        vs = []
        for v in f.verts:
            nv = vmap.get(v.index)
            if nv is None:
                nv = bm.verts.new(v.co)
                vmap[v.index] = nv
            vs.append(nv)
        try:
            nf = bm.faces.new(vs)
        except ValueError:
            continue
        if m not in mlist:
            mlist.append(m)
        nf.material_index = mlist.index(m)
    if not bm.faces:
        bm.free()
        return None
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for m in mlist:
        me.materials.append(bpy.data.materials.get(m) or ensure_mat(m, (200, 200, 200)))
    ob = bpy.data.objects.new(name, me)
    tmp_coll().objects.link(ob)
    return ob


def face_mats(isls, mats):
    return {matname(mats, f.material_index) for i in isls for f in i.faces}


def bbox_faces(ob, mat, zmin=-1e9, zmax=1e9):
    """bbox (mundo) das faces de um material, opcionalmente so as que ficam numa faixa de z"""
    if ob is None:
        return None
    mw = ob.matrix_world
    names = [m.name if m else "" for m in ob.data.materials]
    pts = []
    for p in ob.data.polygons:
        if p.material_index >= len(names) or names[p.material_index] != mat:
            continue
        cs = [mw @ ob.data.vertices[v].co for v in p.vertices]
        if all(zmin <= c.z <= zmax for c in cs):
            pts.extend(cs)
    if not pts:
        return None
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return mn, mx


# ------------------------------------------------------------------ 1. roda d'agua
def build_wheel(ctx, mk):
    m = mk["VFX_Waterwheel_Rotate"]
    wc = m.location.copy()
    rpm = float(m.get("rpm", 6))
    w = 2 * math.pi * rpm / 60.0
    ob = bpy.data.objects["WATER_Waterwheel"]
    bm = world_bm(ob)
    isl = islands(ob, bm)
    R = L.WHEEL_R
    rot, fix = [], []
    for i in isl:
        ok = all(abs(p.x - wc.x) <= WHEEL_HALF_W and math.hypot(p.y - wc.y, p.z - wc.z) <= R + 0.6 for p in i.cos)
        (rot if ok else fix).append(i)
    mats = ob.data.materials
    aff = face_mats(rot, mats)
    ctx["log"].append("roda: %d ilhas giram, %d fixas; materiais afetados %s" % (len(rot), len(fix), sorted(aff)))
    o_rot = faces_obj("VFX_RodaDagua", [f for i in rot for f in i.faces], mats)
    o_fix = faces_obj("VFX_RodaDaguaFixa", [f for i in fix for f in i.faces], mats, aff)
    bm.free()
    # sentido: a roda e de baixo (undershot); o rio corre para -Y, entao o fundo da roda anda para -Y
    # => rotacao em torno de -X (Blender e Roblox compartilham o eixo X)
    axis_b = Vector((-1, 0, 0))
    ctx["groups"]["roda"] = dict(obj=o_rot, kind="spin", assembly="RodaDagua", pivot=wc, axis=axis_b, speed=w)
    ctx["groups"]["roda_fixa"] = dict(obj=o_fix, kind="fixed", assembly="RodaDagua")
    ctx["sources"].append(("WATER_Waterwheel", sorted(aff), ["roda", "roda_fixa"]))
    ctx["wheel"] = dict(center=wc, R=R, w=w, rpm=rpm)


# ------------------------------------------------------------------ 2. casa da roda: coroa + cames, pinhao, martinete
def build_wheelhouse(ctx, mk):
    wc = ctx["wheel"]["center"]
    w = ctx["wheel"]["w"]
    wy, az = wc.y, wc.z
    gx = L.MILL[0] + GEAR_DX
    head = mk["VFX_TripHammer"].location.copy()
    hx = head.x
    piv = Vector((hx, wy + HAMMER_PIV[0], HAMMER_PIV[1]))
    ob = bpy.data.objects["BLD_WheelHouse"]
    bm = world_bm(ob)
    isl = islands(ob, bm)
    low, pin, ham, fix = [], [], [], []
    teeth_c = teeth_p = 0
    for i in isl:
        if "Metal_Heated" in i.mats:
            fix.append(i)
            continue
        ext = i.mx - i.mn
        # engrenagens: fatia fina em x = gx
        if all(abs(p.x - gx) <= 0.8 for p in i.cos) and max(ext) <= 7.0:
            dl = math.hypot(i.c.y - wy, i.c.z - az)
            dh = math.hypot(i.c.y - wy, i.c.z - UZ)
            in_c = all(math.hypot(p.y - wy, p.z - az) <= GEAR_RC + 0.95 for p in i.cos)
            in_p = all(math.hypot(p.y - wy, p.z - UZ) <= GEAR_RP + 0.95 for p in i.cos)
            if dl < 0.35 and in_c:
                low.append(i)
            elif dh < 0.35 and in_p:
                pin.append(i)
            elif in_c or in_p:
                # dente: fica com a engrenagem cujo raio de dente bate melhor
                if in_c and (not in_p or abs(dl - (GEAR_RC + TOOTH)) <= abs(dh - (GEAR_RP + TOOTH))):
                    low.append(i)
                    teeth_c += 1
                else:
                    pin.append(i)
                    teeth_p += 1
            else:
                fix.append(i)
            continue
        # cames no eixo baixo
        if all(abs(p.x - hx) <= 0.8 for p in i.cos) and ext.x < 2.0 and \
                all(math.hypot(p.y - wy, p.z - az) <= CAM_LEN + 0.6 for p in i.cos):
            low.append(i)
            continue
        # martinete: cabo + cabeca (tudo entre a cabeca e o pivo, acima da bigorna)
        if all(hx - 1.0 <= p.x <= hx + 1.0 and head.y - 1.1 <= p.y <= piv.y + 1.2 and
               head.z - 2.1 <= p.z <= piv.z + 0.6 for p in i.cos) and i.mx.z >= head.z - 0.5:
            ham.append(i)
            continue
        fix.append(i)
    mats = ob.data.materials
    moving = low + pin + ham
    aff = face_mats(moving, mats)
    ratio = (teeth_c / teeth_p) if teeth_p else 2.0
    ctx["log"].append("casa da roda: eixo baixo %d ilhas (%d dentes), pinhao %d (%d dentes, razao %.2f), martinete %d"
                      % (len(low), teeth_c, len(pin), teeth_p, ratio, len(ham)))
    if len(ham) != 2 or teeth_c == 0 or teeth_p == 0:
        ctx["log"].append("AVISO: classificacao da casa da roda fora do esperado (confira o render de verificacao)")
    o_low = faces_obj("VFX_CasaRodaEixo", [f for i in low for f in i.faces], mats)
    o_pin = faces_obj("VFX_CasaRodaPinhao", [f for i in pin for f in i.faces], mats)
    o_ham = faces_obj("VFX_CasaRodaMartinete", [f for i in ham for f in i.faces], mats)
    o_fix = faces_obj("VFX_CasaRodaFixa", [f for i in fix for f in i.faces], mats, aff)
    bm.free()
    # fase dos cames: angulo do eixo (w*t) em que um came aponta para baixo (-90 graus no plano YZ)
    cams = [i for i in low if all(abs(p.x - hx) <= 0.8 for p in i.cos)]
    ncam = max(1, len(cams))
    a0 = math.atan2(cams[0].c.z - az, cams[0].c.y - wy) if cams else 0.0
    cam_phase = (a0 + math.pi / 2) % (2 * math.pi / ncam)
    # sinal do eixo do martinete: angulo positivo = cabeca sobe
    ax = Vector((1, 0, 0))
    if (Matrix.Rotation(0.05, 3, ax) @ (head - piv)).z < (head - piv).z:
        ax = -ax
    ctx["groups"]["eixo_baixo"] = dict(obj=o_low, kind="spin", assembly="CasaDaRoda", pivot=wc.copy(),
                                       axis=Vector((-1, 0, 0)), speed=w)
    ctx["groups"]["pinhao"] = dict(obj=o_pin, kind="spin", assembly="CasaDaRoda", pivot=Vector((gx, wy, UZ)),
                                   axis=Vector((1, 0, 0)), speed=w * ratio)
    ctx["groups"]["martinete"] = dict(obj=o_ham, kind="hammer", assembly="CasaDaRoda", pivot=piv, axis=ax,
                                      speed=w, cam_phase=cam_phase, cams=ncam, rest=HAMMER_REST, lift=HAMMER_LIFT,
                                      event="martinete")
    ctx["groups"]["casa_fixa"] = dict(obj=o_fix, kind="fixed", assembly="CasaDaRoda")
    ctx["sources"].append(("BLD_WheelHouse", sorted(aff), ["eixo_baixo", "pinhao", "martinete", "casa_fixa"]))
    ctx["hammer"] = dict(head=head, piv=piv)


# ------------------------------------------------------------------ 3. espirais dos portais (geometria: o Roblox nao tem o shader)
def ribbon(mb, pts, widths, y0, th, m):
    """fita achatada no plano XZ (normal Y), espessura th, centrada em y0"""
    rings = []
    n = len(pts)
    for i, p in enumerate(pts):
        a = pts[max(i - 1, 0)]
        b = pts[min(i + 1, n - 1)]
        t = Vector((b.x - a.x, 0, b.z - a.z)).normalized()
        s = Vector((-t.z, 0, t.x))
        w = widths[i] / 2
        ring = [mb.bm.verts.new((p.x + s.x * u, y0 + v, p.z + s.z * u)) for u, v in
                ((-w, -th / 2), (w, -th / 2), (w, th / 2), (-w, th / 2))]
        rings.append(ring)
    for r0, r1 in zip(rings, rings[1:]):
        for j in range(4):
            k = (j + 1) % 4
            mb.bm.faces.new((r0[j], r0[k], r1[k], r1[j]))
    mb.bm.faces.new(list(reversed(rings[0])))
    mb.bm.faces.new(rings[-1])
    mb._post([v for r in rings for v in r], m, None, 0, 1)


def build_portals(ctx):
    for key in L.PORTAL_KEYS:
        sw = bpy.data.objects.get("PORTAL_%s_Swirl" % key)
        if sw is None:
            continue
        mw = sw.matrix_world
        cs = [mw @ v.co for v in sw.data.vertices]
        mn = Vector((min(p.x for p in cs), min(p.y for p in cs), min(p.z for p in cs)))
        mx = Vector((max(p.x for p in cs), max(p.y for p in cs), max(p.z for p in cs)))
        c = (mn + mx) / 2
        R = max(mx.x - mn.x, mx.z - mn.z) / 2
        thick = mx.y - mn.y
        pal = PORTAL_PAL.get(key)
        if pal is None:
            col = fm_lib.MATS.get("P_%s_Swirl" % key, ((1, 1, 1),))[0]
            base = [int(255 * min(1, x) ** 0.45) for x in col]
            pal = (base, [min(255, int(x * 0.5 + 128)) for x in base], [min(255, int(x * 0.15 + 220)) for x in base])
        plain = len(sw.data.polygons) <= 200 and len(sw.data.materials) <= 1
        info = dict(key=key, center=c, R=R, normal=Vector((0, -1, 0)), pal=pal, idx=L.PORTAL_KEYS.index(key),
                    swirl="PORTAL_%s_Swirl" % key, arms=None)
        if plain:
            m_arm = "VFXP_%s_Braco" % key
            m_core = "VFXP_%s_Nucleo" % key
            ensure_mat(m_arm, pal[1])
            ensure_mat(m_core, pal[2])
            mb = fm_lib.MB("VFX_Espiral_%s" % key, tmp_coll(), random.Random(7))
            th = 0.07
            r0, r1 = 0.14 * R, 0.95 * R
            turns = 0.62
            b = math.log(r1 / r0) / (turns * 2 * math.pi)
            ns = 13
            for side in (-1, 1):      # frente (-Y, para os jogadores) e verso
                y0 = c.y + side * (thick / 2 + 0.04 + th / 2)
                for k in range(3):
                    th0 = 2 * math.pi * k / 3
                    pts, ws = [], []
                    for i in range(ns + 1):
                        f = i / ns
                        r = r0 * (r1 / r0) ** f
                        a = th0 + math.log(r / r0) / b
                        pts.append(Vector((c.x + r * math.cos(a), y0, c.z + r * math.sin(a))))
                        wdt = R * (0.05 + 0.15 * f)
                        if f > 0.8:
                            wdt *= max(0.15, 1.0 - (f - 0.8) / 0.2 * 0.85)
                        if f < 0.12:
                            wdt *= 0.45 + f / 0.12 * 0.55
                        ws.append(wdt)
                    ribbon(mb, pts, ws, y0, th, m_arm)
                if side > 0:
                    continue          # verso: so os bracos (aro e nucleo so na frente)
                # aro fino (le como borda luminosa) e nucleo
                ring = [Vector((c.x + 0.975 * R * math.cos(a), y0, c.z + 0.975 * R * math.sin(a)))
                        for a in [2 * math.pi * i / 28 for i in range(29)]]
                mb.sweep(ring, [(-0.05 * R, -th / 2), (0.05 * R, -th / 2), (0.05 * R, th / 2), (-0.05 * R, th / 2)],
                         m_arm, True, up=(0, 1, 0), caps=False)
                mb.cyl(0.17 * R, th, (c.x, y0, c.z), (math.radians(90), 0, 0), m_core, 12, bevel=0.0)
            ob = mb.finish(recalc=True)
            info["arms"] = "VFX_Espiral_%s__%s" % (key, m_arm)
            info["core"] = "VFX_Espiral_%s__%s" % (key, m_core)
            ctx["groups"]["espiral_%s" % key] = dict(obj=ob, kind="spin", assembly="Portal_%s" % key, pivot=c,
                                                      axis=Vector((0, -1, 0)), speed=PORTAL_SPIN, portal=key,
                                                      inner=True, no_shadow=True, split_core=m_core,
                                                      core_group="nucleo_%s" % key)
            ctx["groups"]["nucleo_%s" % key] = dict(obj=None, kind="core", assembly="Portal_%s" % key, portal=key,
                                                    no_shadow=True)
        ctx["portals"].append(info)
    ctx["log"].append("portais: %d (espirais geradas: %d)" % (len(ctx["portals"]),
                                                              sum(1 for p in ctx["portals"] if p["arms"])))


# ------------------------------------------------------------------ 4. carrinho de mina ocasional (mina -> forja)
def project_s(p, fine, s):
    best = None
    for i in range(len(fine) - 1):
        a, b = fine[i], fine[i + 1]
        ab = b - a
        l2 = ab.x * ab.x + ab.y * ab.y
        t = 0.0 if l2 == 0 else max(0.0, min(1.0, ((p.x - a.x) * ab.x + (p.y - a.y) * ab.y) / l2))
        qx, qy = a.x + ab.x * t, a.y + ab.y * t
        d = math.hypot(p.x - qx, p.y - qy)
        if best is None or d < best[0]:
            best = (d, s[i] + t * (s[i + 1] - s[i]))
    return best


def point_at(fine, s, x):
    x = max(0.0, min(s[-1], x))
    for i in range(len(fine) - 1):
        if s[i + 1] >= x:
            f = 0.0 if s[i + 1] == s[i] else (x - s[i]) / (s[i + 1] - s[i])
            return fine[i].lerp(fine[i + 1], f)
    return fine[-1].copy()


def build_cart(ctx, mk):
    import fm_mine
    pts = fm_mine.rail_path(fm_mine.tunnel_frame())
    fine = fm_lib.resample(pts, 1.0)
    s = [0.0]
    for a, b in zip(fine, fine[1:]):
        s.append(s[-1] + (b - a).length)
    # trechos ocupados pelos carrinhos estacionados (vertices de RAIL_Mine_Carts projetados no trilho)
    occ = []
    ob = bpy.data.objects.get("RAIL_Mine_Carts")
    if ob:
        mw = ob.matrix_world
        vals = []
        for v in ob.data.vertices:
            r = project_s(mw @ v.co, fine, s)
            if r and r[0] < 3.0:
                vals.append(r[1])
        vals.sort()
        for x in vals:
            if occ and x - occ[-1][1] <= 1.2:
                occ[-1][1] = x
            else:
                occ.append([x, x])
    free = []
    last = 0.0
    for a, b in occ:
        if a - last > 1.0:
            free.append((last, a))
        last = b
    if s[-1] - last > 1.0:
        free.append((last, s[-1]))
    cand = [f for f in free if f[1] - f[0] >= 25.0] or free
    fa, fb = cand[-1]                         # trecho livre mais perto da forja
    s_rest = fa + (CART_MARGIN if fa > 0 else 2.0)
    s_far = fb - (CART_MARGIN if fb < s[-1] else 2.0)
    s_weigh = None
    if "RAIL_Weigh_Station" in mk:
        r = project_s(mk["RAIL_Weigh_Station"].location, fine, s)
        if r and s_rest + 8 < r[1] < s_far - 8:
            s_weigh = r[1]
    ctx["log"].append("carrinho: ocupados %s -> anda de s=%.1f a s=%.1f (parada na balanca %s) de %.1f"
                      % ([(round(a, 1), round(b, 1)) for a, b in occ], s_rest, s_far,
                         "s=%.1f" % s_weigh if s_weigh else "-", s[-1]))
    # trecho do trilho exportado para o Luau (so o que o carrinho percorre)
    i0 = max(0, next(i for i in range(len(s)) if s[i] >= s_rest - 4.0) - 1)
    i1 = min(len(s) - 1, next((i for i in range(len(s)) if s[i] >= s_far + 4.0), len(s) - 1))
    path = [Vector((p.x, p.y, CART_Z)) for p in fine[i0:i1 + 1]]
    base = s[i0]
    # pose de repouso
    p0 = point_at(fine, s, s_rest)
    ta = point_at(fine, s, s_rest + 1.2) - point_at(fine, s, s_rest - 1.2)
    yaw = math.atan2(ta.y, ta.x)
    loc = (p0.x, p0.y, CART_Z)
    rng = random.Random(11)
    body = fm_lib.MB("VFX_Carrinho", tmp_coll(), rng)
    fm_parts.mine_cart(body, loc, yaw, None, rng)
    o_body = body.finish()
    ld = fm_lib.MB("VFX_CarrinhoCarga", tmp_coll(), rng)
    F = fm_parts.Frame(loc[0], loc[1], loc[2], yaw)
    fm_parts.crystal_cluster(ld, F.p(0, 0, 2.9), 0.75, "Crystal_Blue", rng, 6)
    fm_parts.crystal_cluster(ld, F.p(0.75, 0.45, 2.85), 0.55, "Crystal_Purple", rng, 3)
    o_load = ld.finish()
    ctx["groups"]["carrinho"] = dict(obj=o_body, kind="cart")
    ctx["groups"]["carga"] = dict(obj=o_load, kind="load")
    ctx["cart"] = dict(path=path, rest=s_rest - base, far=s_far - base, weigh=(s_weigh - base) if s_weigh else None,
                       loc=Vector(loc), yaw=yaw)


# ------------------------------------------------------------------ 5. pontos dos efeitos
def waterfall_info(mk):
    col = bpy.data.collections.get("05_WATER_SYSTEM")
    objs = [o for o in col.all_objects if o.type == "MESH"] if col else []
    out = []
    for name in sorted(n for n in mk if n.startswith("VFX_Waterfall_")):
        m = mk[name].location
        pts = []
        for o in objs:
            names = [x.name if x else "" for x in o.data.materials]
            if "Water_Fall" not in names:
                continue
            mw = o.matrix_world
            for p in o.data.polygons:
                if p.material_index >= len(names) or names[p.material_index] != "Water_Fall":
                    continue
                cw = mw @ p.center
                if math.hypot(cw.x - m.x, cw.y - m.y) <= 10.0:
                    pts.extend(mw @ o.data.vertices[v].co for v in p.vertices)
        if not pts:
            out.append(dict(name=name[14:], top=m + Vector((0, 0, 6)), base=m - Vector((0, 0, 6)), width=6.0,
                            out=Vector((0, -1, 0))))
            continue
        zt = max(p.z for p in pts)
        zb = min(p.z for p in pts)
        tp = [p for p in pts if p.z >= zt - 0.8]
        bp = [p for p in pts if p.z <= zb + 0.8]
        top = sum(tp, Vector()) / len(tp)
        base = sum(bp, Vector()) / len(bp)
        o = Vector((base.x - top.x, base.y - top.y, 0))
        o = o.normalized() if o.length > 0.2 else Vector((0, -1, 0))
        side = Vector((-o.y, o.x, 0))
        wv = [p.dot(side) for p in bp]
        width = (max(wv) - min(wv)) / 0.7 if len(wv) > 1 else 6.0   # Water_Fall e a faixa central (70%)
        out.append(dict(name=name[14:], top=top, base=base, width=max(3.0, width), out=o))
    return out


def fx_points(ctx, mk):
    fx = {}
    hb = bbox_faces(bpy.data.objects.get("FORGE_Hearth"), "Forge_Emissive", zmax=L.FL + 2.45)
    if hb:
        mn, mx = hb
        fx["hearth"] = dict(pos=Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mx.z + 0.2)),
                            size=(mx.x - mn.x - 0.6, 0.4, mx.y - mn.y - 0.6))
    else:
        p = mk["VFX_Hearth_Fire"].location
        fx["hearth"] = dict(pos=p, size=(8.0, 0.4, 3.0))
    hc = bbox_faces(bpy.data.objects.get("FORGE_Hearth"), "Forge_Emissive", zmin=23.0)
    if hc:
        mn, mx = hc
        fx["hearth_chimney"] = dict(pos=Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mx.z + 0.3)),
                                    size=(mx.x - mn.x, 0.4, mx.y - mn.y))
    fx["chimney"] = dict(pos=mk["VFX_Chimney_Smoke_Emitter"].location + Vector((0, 0, 0.5)), radius=L.CHIMNEY_R - 2.4)
    ab = bbox_faces(bpy.data.objects.get("FORGE_Anvil"), "Metal_Heated")
    fx["anvil_ignis"] = dict(pos=((ab[0] + ab[1]) / 2 + Vector((0, 0, (ab[1].z - ab[0].z) / 2 + 0.1))) if ab else
                             mk["VFX_Forge_Sparks"].location - Vector((0, 0, 2.2)))
    hb2 = bbox_faces(bpy.data.objects.get("BLD_WheelHouse"), "Metal_Heated")
    fx["anvil_hammer"] = dict(pos=((hb2[0] + hb2[1]) / 2 + Vector((0, 0, (hb2[1].z - hb2[0].z) / 2 + 0.1))) if hb2 else
                              ctx["hammer"]["head"] - Vector((0, 0, 1.5)))
    wc = ctx["wheel"]["center"]
    R = ctx["wheel"]["R"]
    wz = mk["VFX_Wheel_Splash"].location.z
    dy = math.sqrt(max(0.0, R * R - (wc.z - wz) ** 2))
    fx["wheel_out"] = dict(pos=Vector((wc.x, wc.y - dy, wz + 0.2)))      # pas saem da agua (lado jusante)
    fx["wheel_in"] = dict(pos=Vector((wc.x, wc.y + dy, wz + 0.2)))       # pas entram
    fx["wheel_mist"] = dict(pos=mk["VFX_Wheel_Splash"].location.copy())
    if "MINE_Interior_Zone" in mk:
        fx["mine"] = dict(pos=mk["MINE_Interior_Zone"].location + Vector((0, 0, 4.0)), size=(20.0, 8.0, 20.0))
    sb = None
    shed = bpy.data.objects.get("BLD_Crystal_Shed")
    for mname in ("Crystal_Blue", "Crystal_Purple"):
        r = bbox_faces(shed, mname)
        if r:
            sb = r if sb is None else (Vector(map(min, sb[0], r[0])), Vector(map(max, sb[1], r[1])))
    if sb:
        d = sb[1] - sb[0]
        fx["shed"] = dict(pos=(sb[0] + sb[1]) / 2, size=(max(2.0, d.x), max(2.0, d.z), max(2.0, d.y)))
    ctx["fx"] = fx
    ctx["waterfalls"] = waterfall_info(mk)
    ctx["log"].append("cachoeiras: " + ", ".join("%s(l=%.1f h=%.1f)" % (w["name"], w["width"], w["top"].z - w["base"].z)
                                                   for w in ctx["waterfalls"]))


# ------------------------------------------------------------------ coleta geral
def collect():
    mk = markers()
    ctx = dict(groups={}, sources=[], portals=[], log=[], mk=mk)
    build_wheel(ctx, mk)
    build_wheelhouse(ctx, mk)
    build_portals(ctx)
    build_cart(ctx, mk)
    fx_points(ctx, mk)
    refs = []
    for n in ("VFX_Waterwheel_Rotate", "NPC_Ignis", "RAIL_Start_Mine", "PORTAL_Naruto"):
        if n in mk:
            o = mk[n]
            R3 = o.matrix_world.to_3x3().normalized()
            refs.append(dict(kind="marker", name=n, pos=rbx(o.location), x=rbx(R3.col[0]), y=rbx(R3.col[1])))
    ctx["refs"] = refs
    return ctx


# ------------------------------------------------------------------ exportacao (FBX + dados)
def export_meshes(ctx):
    """divide cada grupo por material (mesmo split do export_roblox), grava o FBX e devolve a lista de movers"""
    movers = []
    made = []
    for gname, g in ctx["groups"].items():
        ob = g.get("obj")
        if ob is None:
            continue
        for name, nm, mname in ER.split_object(ob):
            cs = [v.co for v in nm.vertices]
            if not cs:
                continue
            mn = Vector((min(c.x for c in cs), min(c.y for c in cs), min(c.z for c in cs)))
            mx = Vector((max(c.x for c in cs), max(c.y for c in cs), max(c.z for c in cs)))
            home = rbx((mn + mx) / 2)
            cen = sum(cs, Vector()) / len(cs)
            nm.transform(Matrix.Translation(-cen))
            o = bpy.data.objects.new(name, nm)
            o.location = cen
            tmp_coll().objects.link(o)
            made.append(o)
            grp = gname
            if g.get("split_core") and mname == g["split_core"]:
                grp = g["core_group"]
            movers.append((name, grp, home, len(nm.polygons), mname))
    per = {}
    for m in movers:
        k = m[1].split("_")[0]
        per[k] = per.get(k, 0) + m[3]
    ctx["log"].append("tris por grupo: " + ", ".join("%s=%d" % kv for kv in sorted(per.items())))
    path = os.path.join(OUT, "LOBBY_VFX_MOVING.fbx")
    bpy.ops.object.select_all(action="DESELECT")
    for o in made:
        o.select_set(True)
    if made:
        bpy.context.view_layer.objects.active = made[0]
        bpy.ops.export_scene.fbx(filepath=path, use_selection=True, axis_forward="-Z", axis_up="Y",
                                 apply_scale_options="FBX_SCALE_ALL", mesh_smooth_type="FACE", path_mode="COPY",
                                 embed_textures=False, add_leaf_bones=False, bake_anim=False,
                                 use_mesh_modifiers=True, object_types={"MESH"})
        ctx["log"].append("FBX %s: %d malhas, %d tris, %d KB" % (os.path.basename(path), len(made),
                                                                sum(m[3] for m in movers), os.path.getsize(path) // 1024))
    return movers


def mat_table(movers, ctx):
    rows = {}
    pal = {}
    for p in ctx["portals"]:
        pal["VFXP_%s_Braco" % p["key"]] = p["pal"][1]
        pal["VFXP_%s_Nucleo" % p["key"]] = p["pal"][2]
    for m in movers:
        mname = m[4]
        if mname in rows:
            continue
        if mname in pal:
            rows[mname] = (pal[mname], "Neon", "Neon", 0.0)
            continue
        mat = bpy.data.materials.get(mname)
        if mat is None:
            continue
        styl, rich, tr = ER.rbx_material(mname)
        rows[mname] = (ER.srgb(ER.base_color(mat)), styl, rich, tr)
    return rows


def lua_data_setup(ctx, movers):
    Lg = []
    A = Lg.append
    A("local DATA = {}")
    A("DATA.version = %r" % VERSION)
    A("-- referencias para achar a transformacao do lobby (posicao canonica = export_roblox, Roblox = (x, z, -y))")
    A("DATA.refs = {")
    for r in ctx["refs"]:
        A("  {name = %r, pos = %s, x = %s, y = %s}," % (r["name"], lv3(r["pos"]), lv3(r["x"]), lv3(r["y"])))
    A("}")
    A("-- pecas do LOBBY_VFX_MOVING.fbx: {nome, grupo, centro do bbox (canonico)}")
    A("DATA.movers = {")
    for name, grp, home, tris, mname in movers:
        A("  {%r, %r, %s}," % (name, grp, lv3(home)))
    A("}")
    A("-- malhas estaticas substituidas quando TODAS as pecas dos grupos existem")
    A("DATA.sources = {")
    for obj, mats, groups in ctx["sources"]:
        A("  {name = %r, mats = {%s}, groups = {%s}}," % (obj, ", ".join(repr(m) for m in mats),
                                                        ", ".join(repr(g) for g in groups)))
    A("}")
    A("DATA.groups = {")
    for gname, g in ctx["groups"].items():
        f = ["kind = %r" % g["kind"]]
        if g.get("assembly"):
            f.append("assembly = %r" % g["assembly"])
        if g["kind"] in ("spin", "hammer"):
            f.append("pivot = %s" % lv3(rbx(g["pivot"])))
            f.append("axis = %s" % lv3(rbx(g["axis"])))
            f.append("speed = %s" % fnum(g["speed"]))
        if g["kind"] == "hammer":
            f.append("camPhase = %s, cams = %d, rest = %s, lift = %s, event = %r" % (
                fnum(g["cam_phase"]), g["cams"], fnum(g["rest"]), fnum(g["lift"]), g["event"]))
        if g.get("portal"):
            f.append("portal = %r" % g["portal"])
        if g.get("inner"):
            f.append("inner = true, innerScale = 0.55, innerSpeed = %s" % fnum(PORTAL_INNER))
        if g.get("no_shadow"):
            f.append("noShadow = true")
        A("  [%r] = {%s}," % (gname, ", ".join(f)))
    A("}")
    A("DATA.mats = {")
    for k, (c, m, r, t) in sorted(mat_table(movers, ctx).items()):
        A("  [%r] = {c = %s, m = Enum.Material.%s, r = Enum.Material.%s, t = %s}," % (k, lc3(c), m, r, fnum(t)))
    A("}")
    A("DATA.portals = {")
    for p in ctx["portals"]:
        A("  {key = %r, idx = %d, center = %s, normal = %s, radius = %s, swirl = %r, arms = %s, core = %s," % (
            p["key"], p["idx"], lv3(rbx(p["center"])), lv3(rbx(p["normal"])), fnum(p["R"]), p["swirl"],
            repr(p["arms"]) if p["arms"] else "nil", repr(p.get("core")) if p.get("core") else "nil"))
        A("   disc = %s, arm = %s, core3 = %s}," % (lc3(p["pal"][0]), lc3(p["pal"][1]), lc3(p["pal"][2])))
    A("}")
    fx = ctx["fx"]
    A("DATA.fx = {")
    for k in sorted(fx):
        e = fx[k]
        f = ["pos = %s" % lv3(rbx(e["pos"]))]
        if "size" in e:
            sx, sy, sz = e["size"]                  # (largura x, altura, profundidade y) no Blender
            f.append("size = %s" % lv3((sx, sy, sz)))
        if "radius" in e:
            f.append("radius = %s" % fnum(e["radius"]))
        A("  %s = {%s}," % (k, ", ".join(f)))
    A("}")
    A("DATA.wheelWidth = 3.4")
    A("DATA.waterfalls = {")
    for w in ctx["waterfalls"]:
        A("  {name = %r, top = %s, base = %s, width = %s, out = %s}," % (
            w["name"], lv3(rbx(w["top"])), lv3(rbx(w["base"])), fnum(w["width"]), lv3(rbx(w["out"]))))
    A("}")
    c = ctx["cart"]
    A("DATA.cartRest = CFrame.new(%s) * CFrame.Angles(0, %s, 0)" % (lv3(rbx(c["loc"]))[12:-1], fnum(c["yaw"])))
    return "\n".join(Lg)


def lua_data_client(ctx):
    c = ctx["cart"]
    Lg = []
    A = Lg.append
    A("local DATA = {}")
    A("DATA.version = %r" % VERSION)
    A("-- trilho percorrido pelo carrinho (canonico; o cliente aplica VFX_RootCF)")
    A("DATA.path = {")
    row = []
    for p in c["path"]:
        row.append(lv3(rbx(p)))
        if len(row) == 3:
            A("  " + ", ".join(row) + ",")
            row = []
    if row:
        A("  " + ", ".join(row) + ",")
    A("}")
    A("DATA.cart = {rest = %s, weigh = %s, far = %s, cycle = 48, vOut = 6, vBack = 7.5, acc = 3," % (
        fnum(c["rest"]), fnum(c["weigh"]) if c["weigh"] is not None else "nil", fnum(c["far"])))
    A("  stopWeigh = 3, stopFar = 4.5, unloadAt = 1.6, reloadAt = 2.2}")
    A("DATA.hammer = {rise0 = %s, rise1 = %s, fall0 = %s, hit = %s, bounce = %s}" % tuple(
        fnum(HAMMER_PROFILE[k]) for k in ("rise0", "rise1", "fall0", "hit", "bounce")))
    A("DATA.ignis = {cycle = 4.4, hits = {{0, 0.7}, {0.75, 0.7}, {1.5, 1.35}}, pos = %s}" % lv3(
        rbx(ctx["fx"]["anvil_ignis"]["pos"])))
    A("DATA.portals = {")
    for p in ctx["portals"]:
        A("  {key = %r, idx = %d, center = %s}," % (p["key"], p["idx"], lv3(rbx(p["center"]))))
    A("}")
    return "\n".join(Lg)


def write_lua(ctx, movers):
    setup = SETUP_LUA.replace("--@DATA@", lua_data_setup(ctx, movers)).replace("@VERSION@", VERSION)
    client = CLIENT_LUA.replace("--@DATA@", lua_data_client(ctx)).replace("@VERSION@", VERSION)
    for fn, src in (("vfx_lobby_forja.lua", setup), ("vfx_lobby_forja_client.lua", client)):
        with open(os.path.join(OUT, fn), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(src)
        ctx["log"].append("%s: %d linhas" % (fn, src.count("\n")))


def cleanup():
    c = bpy.data.collections.get(TMP_COLL)
    if c:
        for o in list(c.objects):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if me and me.users == 0:
                bpy.data.meshes.remove(me)
        bpy.data.collections.remove(c)


def main():
    os.makedirs(OUT, exist_ok=True)
    ctx = collect()
    movers = export_meshes(ctx)
    write_lua(ctx, movers)
    cleanup()
    for line in ctx["log"]:
        print("[export_vfx]", line)
    print("EXPORT VFX OK movers=%d portais=%d cachoeiras=%d" % (len(movers), len(ctx["portals"]),
                                                               len(ctx["waterfalls"])))


# =====================================================================================================================
# LUAU: MONTAGEM
# =====================================================================================================================
SETUP_LUA = r'''--[[
vfx_lobby_forja.lua   (gerado por export_vfx.py - @VERSION@ - nao editar a mao: ajuste export_vfx.py e reexporte)
VFX e MOVIMENTO do Lobby Vila-Forja - MONTAGEM

ONDE COLOCAR
  A) Command Bar do Studio (recomendado), UMA vez, depois de:
       1. importar LOBBY_*.fbx e rodar montar_lobby_forja.lua (colisoes, marcadores, luzes);
       2. importar export/LOBBY_VFX_MOVING.fbx com o 3D Importer (pode cair em qualquer lugar do workspace: este
          script acha as pecas pelo nome e as coloca na posicao certa, mesmo com o lobby deslocado ou girado).
     Depois salve o place: emissores, luzes, tags e atributos ficam gravados. Pode rodar de novo (idempotente).
  B) Ou como Script (nao LocalScript) em ServerScriptService: monta tudo ao iniciar o servidor.
     Nao ha nenhum loop por frame no servidor.
  E SEMPRE: vfx_lobby_forja_client.lua como LocalScript em StarterPlayer > StarterPlayerScripts. Ele gira a roda,
  as engrenagens e as espirais, bate o martinete, move o carrinho e faz pulsos/flicker - tudo no cliente.

O QUE ESTE SCRIPT CRIA
  <lobby>.VFX              pecas invisiveis com ParticleEmitters e luzes: fogo da lareira, fumaca da chamine,
                           faiscas das bigornas, respingos da roda, nevoa/espuma/fios das quedas, vortice e
                           particulas sugadas dos portais, brilhos dos cristais
  <lobby>.VFX_MOVING       modelos (streaming atomico) com as pecas moveis do LOBBY_VFX_MOVING.fbx
  ReplicatedStorage.LOBBY_FORJA_VFX       config (VFX_RootCF), molde do carrinho (MineCart), BindableEvent Evento
  ServerStorage.LOBBY_FORJA_VFX_ORIGINAIS malhas estaticas trocadas pelas versoes separadas (para desfazer, devolva)
  Tags (CollectionService): FORJA_Spin, FORJA_Hammer, FORJA_Pulse, FORJA_Flicker, FORJA_Burst, FORJA_Emitter

GANCHOS
  Rig real do Ignis: ponha a tag "FORJA_Ignis" no Model; um KeyframeMarker "Golpe" na animacao do martelo dispara
  as faiscas (parametro opcional = forca). Sem rig, o cliente usa um ritmo interno (toc-toc-TOC).
  Qualquer LocalScript: ReplicatedStorage.LOBBY_FORJA_VFX.Evento:Fire("ignis", 1.5)
  eventos: "ignis", "martinete", "portal:<Nome>", "carga"
]]

local CollectionService = game:GetService("CollectionService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerStorage = game:GetService("ServerStorage")
local RunService = game:GetService("RunService")

local ROOT_NAMES = {"LOBBY_FORJA", "LOBBY_FORJA_PREVIEW"} -- o primeiro que existir no workspace
local RICO = false          -- mesmo valor do montar_lobby_forja.lua (so usado quando nao ha peca original para copiar)
local RECOLOR_SWIRL = true  -- disco das espirais mais saturado, para os bracos claros lerem (sem textura no Roblox)

if RunService:IsRunning() and not RunService:IsServer() then
  warn("[VFX Forja] vfx_lobby_forja.lua e a MONTAGEM (Command Bar ou Script de servidor), nao um LocalScript")
  return
end

--@DATA@

local function log(fmt, ...) print("[VFX Forja] " .. string.format(fmt, ...)) end
local function warnf(fmt, ...) warn("[VFX Forja] " .. string.format(fmt, ...)) end

-- ---------------------------------------------------------------- raiz e transformacao do lobby
local root
for _, n in ipairs(ROOT_NAMES) do
  root = workspace:FindFirstChild(n)
  if root then break end
end
if not root then
  warnf("lobby nao encontrado no workspace (%s)", table.concat(ROOT_NAMES, ", "))
  return
end

local markers = root:FindFirstChild("GAMEPLAY_MARKERS")
local rootCF, refName
for _, r in ipairs(DATA.refs) do
  local p = markers and markers:FindFirstChild(r.name)
  if p and p:IsA("BasePart") then
    rootCF = p.CFrame * CFrame.fromMatrix(r.pos, r.x, r.y):Inverse()
    refName = r.name
    break
  end
end
if not rootCF then
  -- sem marcadores: usa o disco do portal Naruto (centro canonico conhecido)
  local p = root:FindFirstChild("PORTAL_Naruto_Swirl__P_Naruto_Swirl", true)
  local pc = DATA.portals[1] and DATA.portals[1].center
  if p and pc then
    rootCF = p.CFrame * CFrame.new(-pc)
    refName = p.Name
  else
    rootCF = CFrame.new()
    refName = "origem"
    warnf("nenhuma referencia achada (rode montar_lobby_forja.lua antes); usando a origem")
  end
end
for _, r in ipairs(DATA.refs) do
  local p = markers and markers:FindFirstChild(r.name)
  if p and p:IsA("BasePart") and r.name ~= refName then
    local err = ((rootCF * r.pos) - p.Position).Magnitude
    if err > 1 then warnf("marcador %s fora do lugar esperado (%.1f studs) - confira", r.name, err) end
  end
end
local function W(v) return rootCF * v end
local function WV(v) return rootCF:VectorToWorldSpace(v) end
local function WCF(cf) return rootCF * cf end

local function folder(parent, name, class)
  local f = parent:FindFirstChild(name)
  if not f then
    f = Instance.new(class or "Folder")
    f.Name = name
    f.Parent = parent
  end
  return f
end
local VFXF = folder(root, "VFX")
VFXF:ClearAllChildren()
local MOVF = folder(root, "VFX_MOVING")
local ORIG = folder(ServerStorage, "LOBBY_FORJA_VFX_ORIGINAIS")
local CFG = folder(ReplicatedStorage, "LOBBY_FORJA_VFX")
local EV = CFG:FindFirstChild("Evento")
if not EV then
  EV = Instance.new("BindableEvent")
  EV.Name = "Evento"
  EV.Parent = CFG
end

local function clearTags(inst)
  for _, t in ipairs(CollectionService:GetTags(inst)) do
    if string.sub(t, 1, 6) == "FORJA_" then CollectionService:RemoveTag(inst, t) end
  end
end
local function matOf(name)
  return string.match(name, "__(.-)_%d+$") or string.match(name, "__(.+)$")
end

-- ---------------------------------------------------------------- pecas moveis (LOBBY_VFX_MOVING.fbx)
local wanted = {}
for _, m in ipairs(DATA.movers) do wanted[m[1]] = {group = m[2], home = m[3]} end
local found = {}
local function scan(container)
  for _, d in ipairs(container:GetDescendants()) do
    if d:IsA("MeshPart") and wanted[d.Name] then
      if found[d.Name] and found[d.Name] ~= d then
        d.Parent = ORIG -- duplicata (FBX importado duas vezes)
      else
        found[d.Name] = d
      end
    end
  end
end
scan(workspace)
scan(CFG)
local groupCount, groupTotal = {}, {}
for _, m in ipairs(DATA.movers) do
  groupTotal[m[2]] = (groupTotal[m[2]] or 0) + 1
  if found[m[1]] then groupCount[m[2]] = (groupCount[m[2]] or 0) + 1 end
end
local function groupOk(g) return groupTotal[g] ~= nil and groupCount[g] == groupTotal[g] end

-- aparencia: copia de uma peca original com o mesmo material (fica identica ao que o montar aplicou)
local looks = {}
for _, d in ipairs(root:GetDescendants()) do
  if d:IsA("MeshPart") and not wanted[d.Name] then
    local m = matOf(d.Name)
    if m and not looks[m] then looks[m] = d end
  end
end
for _, d in ipairs(ORIG:GetDescendants()) do
  if d:IsA("MeshPart") then
    local m = matOf(d.Name)
    if m and not looks[m] then looks[m] = d end
  end
end
local function applyLook(p, mat)
  p.Anchored = true
  p.CanCollide = false
  p.CanTouch = false
  p.CanQuery = false
  local e = DATA.mats[mat]
  local src = looks[mat]
  if src and not string.find(mat, "^VFXP_") then
    p.Color = src.Color
    p.Material = src.Material
    p.MaterialVariant = src.MaterialVariant
    p.Transparency = src.Transparency
    p.Reflectance = src.Reflectance
  elseif e then
    p.Color = e.c
    p.Material = RICO and e.r or e.m
    p.Transparency = e.t
  end
  p.TextureID = ""
end

-- fontes completas: esconde as malhas estaticas originais; incompletas: nao anima (evita peca duplicada)
local sourceOk = {}
local byName = {}
for _, d in ipairs(root:GetDescendants()) do
  if d:IsA("MeshPart") and not wanted[d.Name] then
    local base = string.match(d.Name, "^(.-)_%d+$")
    for _, key in ipairs({d.Name, base}) do
      if key then
        byName[key] = byName[key] or {}
        table.insert(byName[key], d)
      end
    end
  end
end
for _, s in ipairs(DATA.sources) do
  local ok = true
  for _, g in ipairs(s.groups) do
    if groupTotal[g] and not groupOk(g) then ok = false end
  end
  sourceOk[s.name] = ok
  if ok then
    local moved = 0
    for _, mat in ipairs(s.mats) do
      for _, d in ipairs(byName[s.name .. "__" .. mat] or {}) do
        if d.Parent ~= ORIG then
          d.Parent = ORIG
          moved += 1
        end
      end
    end
    log("%s: %d malhas originais guardadas em ServerStorage (substituidas pelas pecas separadas)", s.name, moved)
  else
    warnf("%s: LOBBY_VFX_MOVING.fbx incompleto; a peca fica estatica (importe o FBX e rode de novo)", s.name)
  end
end
local groupSource = {}
for _, s in ipairs(DATA.sources) do
  for _, g in ipairs(s.groups) do groupSource[g] = s.name end
end

local assemblies = {}
local function assembly(name)
  local m = assemblies[name]
  if not m then
    m = MOVF:FindFirstChild(name)
    if not m then
      m = Instance.new("Model")
      m.Name = name
      m.Parent = MOVF
    end
    pcall(function() m.ModelStreamingMode = Enum.ModelStreamingMode.Atomic end)
    assemblies[name] = m
  end
  return m
end

local function setMotion(p, home, g)
  p:SetAttribute("VFX_Home", home)
  p:SetAttribute("VFX_Pivot", W(g.pivot))
  p:SetAttribute("VFX_Axis", WV(g.axis).Unit)
  p:SetAttribute("VFX_Speed", g.speed)
  p:SetAttribute("VFX_Phase", 0)
end

local cartParts = {}
local portalArms, portalCore = {}, {}
local nMov = 0
for name, part in pairs(found) do
  local w = wanted[name]
  local g = DATA.groups[w.group]
  local mat = matOf(name)
  clearTags(part)
  applyLook(part, mat)
  local home = rootCF * CFrame.new(w.home)
  part.CFrame = home
  part.CastShadow = not (g and g.noShadow)
  if not g then
    part.Parent = MOVF
  elseif g.kind == "cart" or g.kind == "load" then
    table.insert(cartParts, {part, g.kind == "load"})
  elseif groupSource[w.group] and not sourceOk[groupSource[w.group]] then
    part.Parent = ORIG -- fonte incompleta: nao mostra meia roda
  else
    part.Parent = assembly(g.assembly)
    nMov += 1
    if g.kind == "spin" then
      setMotion(part, home, g)
      if g.portal then part:SetAttribute("VFX_Portal", g.portal) end
      if g.inner then
        part:SetAttribute("VFX_Inner", true)
        part:SetAttribute("VFX_InnerScale", g.innerScale)
        part:SetAttribute("VFX_InnerSpeed", g.innerSpeed)
        portalArms[g.portal] = part
      end
      CollectionService:AddTag(part, "FORJA_Spin")
    elseif g.kind == "hammer" then
      setMotion(part, home, g)
      part:SetAttribute("VFX_CamPhase", g.camPhase)
      part:SetAttribute("VFX_Cams", g.cams)
      part:SetAttribute("VFX_Rest", g.rest)
      part:SetAttribute("VFX_Lift", g.lift)
      part:SetAttribute("VFX_Event", g.event)
      CollectionService:AddTag(part, "FORJA_Hammer")
    elseif g.kind == "core" then
      portalCore[g.portal] = part
    end
  end
end

-- ---------------------------------------------------------------- molde do carrinho (o cliente clona)
local oldTpl = CFG:FindFirstChild("MineCart")
local tpl = Instance.new("Model")
tpl.Name = "MineCart"
local restCF = WCF(DATA.cartRest)
local function mkPart(parent, name, size, cf, color, material, shape)
  local p = Instance.new("Part")
  p.Name = name
  if shape then p.Shape = shape end
  p.Size = size
  p.CFrame = cf
  p.Color = color
  p.Material = material
  p.Anchored = true
  p.CanCollide = false
  p.CanTouch = false
  p.CanQuery = false
  p.TopSurface = Enum.SurfaceType.Smooth
  p.BottomSurface = Enum.SurfaceType.Smooth
  p.Parent = parent
  return p
end
if #cartParts > 0 then
  for _, cp in ipairs(cartParts) do
    cp[1].Parent = tpl
    cp[1]:SetAttribute("VFX_Load", cp[2])
  end
else
  -- sem o FBX: carrinho simples em Parts
  local iron, dark = Color3.fromRGB(88, 88, 94), Color3.fromRGB(52, 52, 56)
  mkPart(tpl, "Chassi", Vector3.new(3.4, 0.35, 2.2), restCF * CFrame.new(0, 0.8, 0), dark, Enum.Material.Metal)
  mkPart(tpl, "Cacamba", Vector3.new(3.2, 1.6, 2.5), restCF * CFrame.new(0, 1.85, 0), iron, Enum.Material.Metal)
  for sx = -1, 1, 2 do
    for sz = -1, 1, 2 do
      mkPart(tpl, "Roda", Vector3.new(0.3, 1.24, 1.24), restCF * CFrame.new(sx * 1.1, 0.4, sz * 1.25) *
        CFrame.Angles(0, math.pi / 2, 0), dark, Enum.Material.Metal, Enum.PartType.Cylinder)
    end
  end
  for i = 1, 3 do
    local c = mkPart(tpl, "Cristal", Vector3.new(0.7, 1.4 + i * 0.2, 0.7), restCF * CFrame.new(-0.8 + i * 0.45, 3.0, 0.25 * (i - 2)) *
      CFrame.Angles(0.2 * (i - 2), 0, 0.25), Color3.fromRGB(56, 145, 255), Enum.Material.Neon)
    c:SetAttribute("VFX_Load", true)
  end
end
tpl.WorldPivot = restCF
tpl:SetAttribute("VFX_RestCF", restCF)
if oldTpl then oldTpl:Destroy() end
tpl.Parent = CFG

-- ---------------------------------------------------------------- utilitarios de particulas
local TEX = {
  dot = "rbxasset://textures/particles/explosion01_implosion_main.dds",   -- ponto macio
  ring = "rbxasset://textures/particles/explosion01_shockwave_main.dds",  -- anel
  smoke = "rbxasset://textures/particles/smoke_main.dds",
  fire = "rbxasset://textures/particles/fire_main.dds",
  star = "rbxasset://textures/particles/sparkles_main.dds",
  vortex = "rbxasset://textures/particles/forcefield_vortex_main.dds",
}
local function RGB(r, g, b) return Color3.fromRGB(r, g, b) end
local function NS(t)
  if type(t) == "number" then return NumberSequence.new(t) end
  local k = {}
  for _, p in ipairs(t) do table.insert(k, NumberSequenceKeypoint.new(p[1], p[2])) end
  return NumberSequence.new(k)
end
local function CS(t)
  if typeof(t) == "Color3" then return ColorSequence.new(t) end
  local k = {}
  for _, p in ipairs(t) do table.insert(k, ColorSequenceKeypoint.new(p[1], p[2])) end
  return ColorSequence.new(k)
end
local function NR(t) return NumberRange.new(t[1], t[2] or t[1]) end

local function host(name, posC, size, lookC)
  local p = Instance.new("Part")
  p.Name = name
  p.Size = size
  local cf = CFrame.new(posC)
  if lookC then cf = CFrame.lookAt(posC, posC + lookC) end
  p.CFrame = WCF(cf)
  p.Anchored = true
  p.CanCollide = false
  p.CanTouch = false
  p.CanQuery = false
  p.CastShadow = false
  p.Transparency = 1
  p.Locked = true
  p.Parent = VFXF
  return p
end
local function att(parent, name, cf)
  local a = Instance.new("Attachment")
  a.Name = name
  a.CFrame = cf or CFrame.new()
  a.Parent = parent
  return a
end
local function emitter(parent, name, p)
  local e = Instance.new("ParticleEmitter")
  e.Name = name
  e.Texture = p.tex or TEX.dot
  e.Color = CS(p.color or RGB(255, 255, 255))
  e.Size = NS(p.size or 1)
  e.Transparency = NS(p.transp or 0)
  e.Lifetime = NR(p.life)
  e.Rate = p.rate or 0
  e.Speed = NR(p.speed or {0})
  e.SpreadAngle = Vector2.new(p.spread or 0, p.spread2 or p.spread or 0)
  e.Acceleration = p.accel and WV(p.accel) or Vector3.zero
  e.Drag = p.drag or 0
  e.LightEmission = p.emission or 0
  e.LightInfluence = p.influence or 0
  e.Brightness = p.bright or 1
  e.Rotation = NR(p.rot or {0})
  e.RotSpeed = NR(p.rotspeed or {0})
  e.EmissionDirection = p.dir or Enum.NormalId.Top
  e.Shape = Enum.ParticleEmitterShape.Box
  e.ShapeStyle = Enum.ParticleEmitterShapeStyle.Volume
  e.Orientation = p.orient or Enum.ParticleOrientation.FacingCamera
  if p.squash then e.Squash = NS(p.squash) end
  e.ZOffset = p.zoff or 0
  e.LockedToPart = p.locked or false
  e.Parent = parent
  if (p.rate or 0) > 0 then
    e:SetAttribute("VFX_MaxDist", p.maxd or 400)
    CollectionService:AddTag(e, "FORJA_Emitter")
  end
  if p.event then
    e:SetAttribute("VFX_Event", p.event)
    e:SetAttribute("VFX_Count", p.count or 8)
    CollectionService:AddTag(e, "FORJA_Burst")
  end
  return e
end
local function flashLight(parent, color, range, peak, event)
  local l = Instance.new("PointLight")
  l.Name = "Clarao"
  l.Color = color
  l.Range = range
  l.Brightness = 0
  l.Shadows = false
  l:SetAttribute("VFX_Kind", "flash")
  l:SetAttribute("VFX_Event", event)
  l:SetAttribute("VFX_Base", peak)
  l.Parent = parent
  CollectionService:AddTag(l, "FORJA_Flicker")
  return l
end
local UP = Vector3.new(0, 1, 0)
local FX = DATA.fx
local nEm = 0
local function count(n) nEm += n end

-- ---------------------------------------------------------------- FORJA (quente)
if FX.hearth then
  local h = host("Lareira_Fogo", FX.hearth.pos, FX.hearth.size)
  emitter(h, "Chamas", {tex = TEX.dot, color = {{0, RGB(255, 246, 196)}, {0.25, RGB(255, 196, 78)}, {0.6, RGB(255, 112, 32)}, {1, RGB(150, 34, 12)}},
    size = {{0, 1.3}, {0.35, 2.2}, {1, 0.35}}, transp = {{0, 0.45}, {0.18, 0.08}, {0.75, 0.45}, {1, 1}},
    life = {0.55, 1.05}, rate = 30, speed = {2.5, 5}, spread = 12, accel = Vector3.new(0, 3.5, 0), drag = 0.6,
    emission = 1, bright = 2, rot = {0, 360}, rotspeed = {-40, 40}, zoff = 0.4, maxd = 320})
  emitter(h, "Linguas", {tex = TEX.fire, color = {{0, RGB(255, 226, 150)}, {0.5, RGB(255, 132, 40)}, {1, RGB(190, 46, 18)}},
    size = {{0, 2.2}, {0.5, 3.0}, {1, 0.8}}, transp = {{0, 0.55}, {0.3, 0.2}, {1, 1}},
    life = {0.4, 0.8}, rate = 10, speed = {3, 6}, spread = 8, emission = 0.9, bright = 1.6, rot = {-25, 25}, maxd = 320})
  emitter(h, "Brasas", {tex = TEX.dot, color = RGB(255, 168, 60), size = {{0, 0.3}, {1, 0}}, transp = {{0, 0}, {0.8, 0.2}, {1, 1}},
    life = {0.9, 1.8}, rate = 5, speed = {2.5, 5}, spread = 25, accel = Vector3.new(0, 2, 1.4), drag = 0.4,
    emission = 1, bright = 3, maxd = 260})
  count(3)
end
if FX.chimney then
  local r = FX.chimney.radius
  local h = host("Chamine_Fumaca", FX.chimney.pos, Vector3.new(r, 1, r))
  emitter(h, "Fumaca", {tex = TEX.smoke, color = {{0, RGB(66, 58, 54)}, {0.5, RGB(94, 88, 84)}, {1, RGB(142, 138, 136)}},
    size = {{0, 5}, {0.25, 10}, {1, 28}}, transp = {{0, 1}, {0.06, 0.3}, {0.55, 0.45}, {1, 1}},
    life = {9, 13}, rate = 4.5, speed = {7, 10}, spread = 8, accel = Vector3.new(1.4, 0.3, -0.65), drag = 0.25,
    influence = 1, rot = {0, 360}, rotspeed = {-12, 12}, maxd = 3000})
  emitter(h, "Fagulhas", {tex = TEX.dot, color = RGB(255, 150, 50), size = {{0, 0.45}, {1, 0}}, transp = {{0, 0}, {1, 1}},
    life = {1.5, 3}, rate = 3, speed = {9, 14}, spread = 20, accel = Vector3.new(1.5, -2, -0.6), drag = 0.5,
    emission = 1, bright = 3, maxd = 700})
  count(2)
end
if FX.hearth_chimney then
  local h = host("Lareira_Fumaca", FX.hearth_chimney.pos, FX.hearth_chimney.size)
  emitter(h, "Fumaca", {tex = TEX.smoke, color = {{0, RGB(120, 114, 110)}, {1, RGB(172, 168, 166)}},
    size = {{0, 1.6}, {1, 7}}, transp = {{0, 1}, {0.1, 0.55}, {1, 1}}, life = {4, 6}, rate = 1.8, speed = {3, 5},
    spread = 10, accel = Vector3.new(0.8, 0.3, -0.35), influence = 1, rot = {0, 360}, rotspeed = {-15, 15}, maxd = 500})
  count(1)
end
local function anvilFX(name, posC, event, sparks, speedMax, peak)
  local h = host(name, posC, Vector3.new(0.6, 0.2, 0.6))
  local a = att(h, "Topo")
  emitter(a, "Faiscas", {tex = TEX.dot, color = {{0, RGB(255, 250, 214)}, {0.4, RGB(255, 192, 82)}, {1, RGB(255, 108, 30)}},
    size = {{0, 0.28}, {1, 0.06}}, transp = {{0, 0}, {0.7, 0.1}, {1, 1}}, life = {0.3, 0.75}, speed = {speedMax * 0.5, speedMax},
    spread = 75, accel = Vector3.new(0, -60, 0), drag = 1.4, emission = 1, bright = 4,
    orient = Enum.ParticleOrientation.VelocityParallel, squash = 2, event = event, count = sparks})
  emitter(a, "Brilho", {tex = TEX.dot, color = RGB(255, 204, 128), size = {{0, 2.2}, {1, 5}}, transp = {{0, 0.35}, {1, 1}},
    life = {0.16}, speed = {0}, emission = 1, bright = 3, event = event, count = 1})
  flashLight(h, RGB(255, 160, 70), 14, peak, event)
  count(2)
  return h, a
end
anvilFX("Bigorna_Ignis", FX.anvil_ignis.pos, "ignis", 14, 26, 4)
local _, ah = anvilFX("Bigorna_Martinete", FX.anvil_hammer.pos, "martinete", 9, 18, 3)
emitter(ah, "Po", {tex = TEX.smoke, color = RGB(128, 118, 108), size = {{0, 0.8}, {1, 2.6}}, transp = {{0, 0.5}, {1, 1}},
  life = {0.6, 1.1}, speed = {2, 4}, spread = 80, accel = Vector3.new(0, 1, 0), drag = 2, influence = 1,
  event = "martinete", count = 4})
count(1)

-- ---------------------------------------------------------------- AGUA (frio): roda e quedas
do
  local ww = DATA.wheelWidth
  local o = host("Roda_Respingo", FX.wheel_out.pos, Vector3.new(ww + 0.4, 0.4, 1.6))
  emitter(o, "Gotas", {tex = TEX.dot, color = RGB(226, 242, 255), size = {{0, 0.45}, {1, 0.2}}, transp = {{0, 0.15}, {1, 1}},
    life = {0.5, 0.9}, rate = 22, speed = {6, 11}, spread = 30, accel = Vector3.new(0, -40, 3), drag = 0.5,
    emission = 0.3, influence = 0.6, orient = Enum.ParticleOrientation.VelocityParallel, squash = 0.8, maxd = 300})
  local i = host("Roda_Entrada", FX.wheel_in.pos, Vector3.new(ww + 0.4, 0.4, 1.6))
  emitter(i, "Gotas", {tex = TEX.dot, color = RGB(226, 242, 255), size = {{0, 0.4}, {1, 0.15}}, transp = {{0, 0.2}, {1, 1}},
    life = {0.35, 0.6}, rate = 10, speed = {3, 6}, spread = 40, accel = Vector3.new(0, -40, 0), drag = 0.5,
    emission = 0.3, influence = 0.6, maxd = 300})
  local m = host("Roda_Nevoa", FX.wheel_mist.pos, Vector3.new(ww + 1, 0.5, 4))
  emitter(m, "Espuma", {tex = TEX.smoke, color = RGB(240, 248, 255), size = {{0, 1.5}, {1, 4.5}}, transp = {{0, 0.5}, {1, 1}},
    life = {1.2, 2}, rate = 4, speed = {1, 2.5}, spread = 40, drag = 1, influence = 0.7, rot = {0, 360}, maxd = 300})
  count(3)
end
for _, wf in ipairs(DATA.waterfalls) do
  local w = wf.width
  local h = (wf.top - wf.base).Magnitude
  local b = host("Queda_" .. wf.name .. "_Base", wf.base + Vector3.new(0, 0.3, 0), Vector3.new(w + 1.5, 0.6, 3), wf.out)
  emitter(b, "Nevoa", {tex = TEX.smoke, color = RGB(236, 245, 255), size = {{0, math.clamp(w * 0.45, 3, 7)}, {1, math.clamp(w * 1.15, 6, 14)}},
    transp = {{0, 0.72}, {0.3, 0.55}, {1, 1}}, life = {2.5, 4}, rate = math.clamp(w * 0.35, 1.5, 4), speed = {1.5, 3.5},
    spread = 45, accel = Vector3.new(0, 0.6, 0), drag = 0.6, influence = 0.8, rot = {0, 360}, rotspeed = {-10, 10}, maxd = 650})
  emitter(b, "Espuma", {tex = TEX.smoke, color = RGB(250, 253, 255), size = {{0, 1.4}, {1, 3.2}}, transp = {{0, 0.25}, {1, 1}},
    life = {0.6, 1.1}, rate = math.clamp(w * 1.4, 5, 12), speed = {4, 8}, spread = 35, accel = Vector3.new(0, -18, 0),
    drag = 0.8, influence = 0.7, rot = {0, 360}, maxd = 450})
  local t = host("Queda_" .. wf.name .. "_Fios", wf.top + wf.out * 0.7, Vector3.new(w * 0.75, 0.3, 0.5), wf.out)
  emitter(t, "Fios", {tex = TEX.dot, color = RGB(220, 238, 255), size = {{0, 0.55}, {1, 0.3}}, transp = {{0, 0.4}, {0.8, 0.55}, {1, 1}},
    life = {math.min(1.6, math.sqrt(2 * h / 40))}, rate = math.clamp(w * 1.2, 4, 10), speed = {3, 6}, spread = 4, spread2 = 10,
    dir = Enum.NormalId.Bottom, accel = Vector3.new(0, -40, 0) + wf.out * 1.5, emission = 0.4, influence = 0.5,
    orient = Enum.ParticleOrientation.VelocityParallel, squash = 2.5, maxd = 450})
  count(3)
end

-- ---------------------------------------------------------------- PORTAIS (acentos)
for _, p in ipairs(DATA.portals) do
  local key = p.key
  local R = p.radius
  local n = p.normal
  local armPart = portalArms[key]
  -- disco original: gira junto (se ganhou detalhe no Blender, aparece girando) e fica mais saturado
  local swirlParts = {}
  for _, d in ipairs(root:GetDescendants()) do
    if d:IsA("MeshPart") and string.sub(d.Name, 1, #p.swirl + 2) == p.swirl .. "__" then table.insert(swirlParts, d) end
  end
  local g = DATA.groups["espiral_" .. key]
  for _, d in ipairs(swirlParts) do
    clearTags(d)
    d:SetAttribute("VFX_Home", d.CFrame)
    d:SetAttribute("VFX_Pivot", W(p.center))
    d:SetAttribute("VFX_Axis", WV(n).Unit)
    d:SetAttribute("VFX_Speed", g and g.speed or 0.85)
    d:SetAttribute("VFX_Phase", 0)
    d:SetAttribute("VFX_Portal", key)
    CollectionService:AddTag(d, "FORJA_Spin")
    if RECOLOR_SWIRL and armPart then d.Color = p.disc end
  end
  -- base do plano do portal (canonico = espaco local das pecas, que tem a orientacao da raiz)
  local u = UP:Cross(n).Unit
  local v = n:Cross(u).Unit
  -- particulas sugadas: presas no disco que gira (nascem ao longo do aro e correm para o centro)
  local ringHost = armPart or swirlParts[1]
  if ringHost then
    for _, c in ipairs(ringHost:GetChildren()) do
      if c:IsA("Attachment") and string.sub(c.Name, 1, 7) == "Sugada_" then c:Destroy() end
    end
    local f = 0.45
    for k = 0, 1 do
      local ang = math.pi * k
      local lp = u * (math.cos(ang) * R * 0.92) + v * (math.sin(ang) * R * 0.92) + n * f
      local a = att(ringHost, "Sugada_" .. k, CFrame.lookAt(lp, n * f))
      emitter(a, "Sugadas", {tex = TEX.star, color = {{0, p.arm}, {1, p.core3}}, size = {{0, 0.15}, {0.2, 0.75}, {1, 0.1}},
        transp = {{0, 1}, {0.15, 0.1}, {1, 0.35}}, life = {1.15}, rate = 6, speed = {R * 0.92 / 1.15 * 0.95},
        spread = 6, dir = Enum.NormalId.Front, emission = 1, bright = 2, zoff = 0.3, maxd = 450})
      count(1)
    end
  end
  local h = host("Portal_" .. key, p.center, Vector3.new(1, 1, 1))
  local fa = att(h, "Frente", CFrame.lookAt(n * 0.35, n * 1.35))
  emitter(fa, "Vortice", {tex = TEX.vortex, color = p.arm, size = {{0, 2 * R * 0.95}, {1, 2 * R * 0.55}},
    transp = {{0, 1}, {0.25, 0.45}, {0.75, 0.55}, {1, 1}}, life = {2.4, 3}, rate = 1.1, speed = {0.2},
    dir = Enum.NormalId.Front, orient = Enum.ParticleOrientation.VelocityPerpendicular, emission = 1, bright = 1.5,
    rot = {0, 360}, rotspeed = {60, 100}, zoff = 0.2, maxd = 450})
  emitter(fa, "Pulso", {tex = TEX.ring, color = p.core3, size = {{0, 3}, {1, 2 * R * 1.2}}, transp = {{0, 0.15}, {1, 1}},
    life = {1.1}, speed = {0.3}, dir = Enum.NormalId.Front, orient = Enum.ParticleOrientation.VelocityPerpendicular,
    emission = 1, bright = 2, event = "portal:" .. key, count = 1})
  count(2)
  local core = portalCore[key]
  if core then
    core:SetAttribute("VFX_Kind", "portalcore")
    core:SetAttribute("VFX_Event", "portal:" .. key)
    core:SetAttribute("VFX_BaseColor", core.Color)
    CollectionService:AddTag(core, "FORJA_Pulse")
  end
end

-- ---------------------------------------------------------------- CRISTAIS (frio)
local function sparkles(name, e, rate)
  local h = host(name, e.pos, e.size)
  emitter(h, "Brilhos", {tex = TEX.star, color = {{0, RGB(150, 212, 255)}, {1, RGB(176, 124, 255)}},
    size = {{0, 0}, {0.3, 0.7}, {1, 0}}, transp = {{0, 0.2}, {1, 1}}, life = {0.8, 1.6}, rate = rate, speed = {0.2, 0.6},
    spread = 180, emission = 1, bright = 2, rotspeed = {-90, 90}, maxd = 220})
  count(1)
end
if FX.mine then sparkles("Mina_Brilhos", FX.mine, 5) end
if FX.shed then sparkles("Galpao_Brilhos", FX.shed, 2.5) end

-- ---------------------------------------------------------------- tags das pecas estaticas (pulsos e flicker)
local nPulse, nLight = 0, 0
for _, d in ipairs(root:GetDescendants()) do
  if d:IsA("MeshPart") and d.Parent ~= ORIG then
    local n = d.Name
    local kind, event
    if string.find(n, "__Crystal_", 1, true) then
      kind = "crystal"
    elseif string.find(n, "__Metal_Heated", 1, true) then
      kind = "heat"
      if string.sub(n, 1, 12) == "FORGE_Anvil_" then event = "ignis"
      elseif string.sub(n, 1, 15) == "BLD_WheelHouse_" then event = "martinete" end
    elseif string.find(n, "__Forge_Emissive", 1, true) and string.sub(n, 1, 6) == "FORGE_" then
      kind = "ember"
    elseif string.find(n, "__Lantern_Glow", 1, true) then
      kind = "lantern"
    end
    if kind then
      if CollectionService:HasTag(d, "FORJA_Pulse") then CollectionService:RemoveTag(d, "FORJA_Pulse") end
      d:SetAttribute("VFX_Kind", kind)
      d:SetAttribute("VFX_Event", event or "")
      d:SetAttribute("VFX_BaseColor", d.Color)
      CollectionService:AddTag(d, "FORJA_Pulse")
      nPulse += 1
    end
  elseif (d:IsA("PointLight") or d:IsA("SpotLight")) and d.Parent and d.Parent.Parent and d.Parent.Parent.Name == "LIGHTS" then
    local n = d.Parent.Name
    local kind, event = "lantern", ""
    if string.sub(n, 1, 9) == "L_Portal_" then
      kind, event = "portal", "portal:" .. string.sub(n, 10)
    elseif string.sub(n, 1, 8) == "L_Hearth" or string.sub(n, 1, 9) == "L_Furnace" or string.sub(n, 1, 12) == "L_DS_Brazier" then
      kind = "fire"
    elseif n == "L_Mine_Chamber" or n == "L_Mine_Tunnel" or n == "L_Shed_Light" then
      kind = "crystal"
    elseif n == "L_Hall_Fill" or n == "L_Shop_Fill" or n == "L_Konoha_Gate" then
      kind = nil
    end
    if CollectionService:HasTag(d, "FORJA_Flicker") then CollectionService:RemoveTag(d, "FORJA_Flicker") end
    if kind then
      d:SetAttribute("VFX_Kind", kind)
      d:SetAttribute("VFX_Event", event)
      d:SetAttribute("VFX_Base", d.Brightness)
      CollectionService:AddTag(d, "FORJA_Flicker")
      nLight += 1
    end
  end
end

CFG:SetAttribute("VFX_Version", DATA.version)
CFG:SetAttribute("VFX_RootCF", rootCF)
CFG:SetAttribute("VFX_Root", root:GetFullName())
CFG:SetAttribute("VFX_Ready", true)
log("pronto (%s): referencia %s | %d pecas moveis, %d emissores, %d pulsos, %d luzes com flicker, carrinho %s",
  DATA.version, refName, nMov, nEm, nPulse, nLight, (#cartParts > 0) and "malha" or "Parts")
'''

# =====================================================================================================================
# LUAU: CLIENTE
# =====================================================================================================================
CLIENT_LUA = r'''--[[
vfx_lobby_forja_client.lua   (gerado por export_vfx.py - @VERSION@ - nao editar a mao)
VFX e MOVIMENTO do Lobby Vila-Forja - ANIMACAO NO CLIENTE

ONDE COLOCAR: LocalScript em StarterPlayer > StarterPlayerScripts.
Precisa da montagem (vfx_lobby_forja.lua) feita antes: ela deixa ReplicatedStorage.LOBBY_FORJA_VFX e as tags.

O que faz (tudo local, nada replica para o servidor):
  - gira a roda d'agua, a coroa, os cames e o pinhao (mesmo relogio: workspace:GetServerTimeNow, todos os
    jogadores veem a mesma fase) e bate o martinete com faiscas no golpe;
  - gira as espirais dos portais + clone interno mais rapido (vortice), pulso de luz/anel periodico;
  - carrinho de mina ocasional: sai do patio da mina, para na balanca, descarrega no portao da forja e volta;
  - golpes do Ignis (ritmo interno ou KeyframeMarker "Golpe" no rig marcado com a tag FORJA_Ignis);
  - pulsos: cristais, metal quente, brasas da forja, nucleo dos portais; flicker sutil das lanternas e do fogo.
Desempenho: 1 conexao PreRender com BulkMoveTo so para o que esta perto da camera; pulsos a 20 Hz, luzes a 15 Hz,
liga/desliga de emissores a 2 Hz. Streaming: registra/desregistra por tag (CollectionService), sem WaitForChild
no workspace. Respeita GuiService.ReducedMotionEnabled.
]]

local RunService = game:GetService("RunService")
local CollectionService = game:GetService("CollectionService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local GuiService = game:GetService("GuiService")

if not RunService:IsClient() then return end

--@DATA@

local CFG = ReplicatedStorage:WaitForChild("LOBBY_FORJA_VFX", 60)
if not CFG then
  warn("[VFX Forja] ReplicatedStorage.LOBBY_FORJA_VFX nao existe: rode vfx_lobby_forja.lua (montagem) antes")
  return
end
local rootCF = CFG:GetAttribute("VFX_RootCF")
if typeof(rootCF) ~= "CFrame" then rootCF = CFrame.new() end

local TAU = math.pi * 2
local SPIN_DIST, HAMMER_DIST, CART_DIST = 340, 220, 420
local PULSE_DIST = {crystal = 230, heat = 200, ember = 450, lantern = 200, portalcore = 480}
local LIGHT_DIST = {lantern = 170, fire = 260, crystal = 220, portal = 480, flash = 260}
local HOT = Color3.fromRGB(255, 196, 120)
local WHITE = Color3.new(1, 1, 1)

local reduced = false
local function readReduced()
  local ok, v = pcall(function() return GuiService.ReducedMotionEnabled end)
  reduced = ok and v == true
end
readReduced()
pcall(function() GuiService:GetPropertyChangedSignal("ReducedMotionEnabled"):Connect(readReduced) end)

local localFolder = Instance.new("Folder")
localFolder.Name = "FORJA_VFX_LOCAL"
localFolder.Parent = workspace

local function angleAt(speed, t)
  if speed == 0 then return 0 end
  local period = TAU / math.abs(speed)
  return speed * (t % period)
end
local function seedOf(v) return (v.X * 0.137 + v.Y * 0.071 + v.Z * 0.113) % 97 + 0.37 end
local function watch(tag, add, remove)
  CollectionService:GetInstanceAddedSignal(tag):Connect(add)
  CollectionService:GetInstanceRemovedSignal(tag):Connect(remove)
  for _, inst in ipairs(CollectionService:GetTagged(tag)) do task.spawn(add, inst) end
end
local function posOf(inst)
  if inst:IsA("BasePart") then return inst.Position end
  if inst:IsA("Attachment") then return inst.WorldPosition end
  local p = inst.Parent
  if p then return posOf(p) end
  return Vector3.zero
end

-- ---------------------------------------------------------------- eventos (faiscas, claroes)
local bursts, flash = {}, {}
local function fire(ev, strength)
  strength = strength or 1
  local cam = workspace.CurrentCamera
  local cp = cam and cam.CFrame.Position or Vector3.zero
  for em, b in pairs(bursts) do
    if b.event == ev and em.Parent and (b.pos - cp).Magnitude < 300 then
      em:Emit(math.max(1, math.floor(b.count * strength + 0.5)))
    end
  end
  flash[ev] = math.max(flash[ev] or 0, math.min(1.5, strength))
end
watch("FORJA_Burst", function(e)
  if not e:IsA("ParticleEmitter") or not e:IsDescendantOf(workspace) then return end
  bursts[e] = {event = e:GetAttribute("VFX_Event") or "", count = e:GetAttribute("VFX_Count") or 8, pos = posOf(e)}
end, function(e) bursts[e] = nil end)
local EV = CFG:FindFirstChild("Evento")
if EV and EV:IsA("BindableEvent") then
  EV.Event:Connect(function(name, strength) if type(name) == "string" then fire(name, tonumber(strength) or 1) end end)
end

-- ---------------------------------------------------------------- rotores (roda, engrenagens, espirais)
local spins = {}
watch("FORJA_Spin", function(p)
  if not p:IsA("BasePart") or not p:IsDescendantOf(workspace) or spins[p] then return end
  local home, pivot, axis = p:GetAttribute("VFX_Home"), p:GetAttribute("VFX_Pivot"), p:GetAttribute("VFX_Axis")
  if typeof(home) ~= "CFrame" or typeof(pivot) ~= "Vector3" or typeof(axis) ~= "Vector3" then return end
  local e = {part = p, pivot = pivot, pivotCF = CFrame.new(pivot), axis = axis.Unit, rel = CFrame.new(-pivot) * home,
    speed = p:GetAttribute("VFX_Speed") or 0, phase = p:GetAttribute("VFX_Phase") or 0, portal = p:GetAttribute("VFX_Portal")}
  if p:GetAttribute("VFX_Inner") then
    local c = p:Clone()
    for _, t in ipairs(CollectionService:GetTags(c)) do CollectionService:RemoveTag(c, t) end
    c:ClearAllChildren()
    local k = p:GetAttribute("VFX_InnerScale") or 0.55
    c.Size = Vector3.new(p.Size.X * k, p.Size.Y * k, p.Size.Z * 1.45)
    c.Transparency = math.clamp(p.Transparency + 0.2, 0, 0.9)
    c.CastShadow = false
    c.Name = p.Name .. "_Interno"
    c.CFrame = home
    c.Parent = localFolder
    e.inner = c
    e.innerMul = p:GetAttribute("VFX_InnerSpeed") or 2.3
  end
  spins[p] = e
end, function(p)
  local e = spins[p]
  if e and e.inner then e.inner:Destroy() end
  spins[p] = nil
end)

-- ---------------------------------------------------------------- martinete
local H = DATA.hammer
local function smooth(x) x = math.clamp(x, 0, 1) return x * x * (3 - 2 * x) end
local function hammerLift(u)
  if u < H.rise0 then return 0 end
  if u < H.rise1 then return smooth((u - H.rise0) / (H.rise1 - H.rise0)) end
  if u < H.fall0 then return 1 end
  if u < H.hit then local f = (u - H.fall0) / (H.hit - H.fall0) return 1 - f * f end
  if u < H.bounce then return 0.08 * math.sin(math.pi * (u - H.hit) / (H.bounce - H.hit)) end
  return 0
end
local hammers, hammerGroups = {}, {}
watch("FORJA_Hammer", function(p)
  if not p:IsA("BasePart") or not p:IsDescendantOf(workspace) then return end
  local home, pivot, axis = p:GetAttribute("VFX_Home"), p:GetAttribute("VFX_Pivot"), p:GetAttribute("VFX_Axis")
  if typeof(home) ~= "CFrame" or typeof(pivot) ~= "Vector3" or typeof(axis) ~= "Vector3" then return end
  local ev = p:GetAttribute("VFX_Event") or "martinete"
  local g = hammerGroups[ev]
  if not g then
    g = {speed = p:GetAttribute("VFX_Speed") or 0.6, camPhase = p:GetAttribute("VFX_CamPhase") or 0,
      cams = math.max(1, p:GetAttribute("VFX_Cams") or 3), rest = p:GetAttribute("VFX_Rest") or 0,
      lift = p:GetAttribute("VFX_Lift") or 0.15, lastU = nil, angle = 0, pivot = pivot}
    hammerGroups[ev] = g
  end
  hammers[p] = {group = g, pivotCF = CFrame.new(pivot), axis = axis.Unit, rel = CFrame.new(-pivot) * home}
end, function(p) hammers[p] = nil end)

-- ---------------------------------------------------------------- pulsos de cor e luzes
local pulses, lights, emitters = {}, {}, {}
watch("FORJA_Pulse", function(p)
  if not p:IsA("BasePart") or not p:IsDescendantOf(workspace) then return end
  local base = p:GetAttribute("VFX_BaseColor")
  if typeof(base) ~= "Color3" then base = p.Color end
  local kind = p:GetAttribute("VFX_Kind") or "crystal"
  local hi = base:Lerp(WHITE, 0.45)
  pulses[p] = {kind = kind, event = p:GetAttribute("VFX_Event") or "", base = base, hi = hi, pos = p.Position,
    seed = seedOf(p.Position), maxd = PULSE_DIST[kind] or 220}
end, function(p) pulses[p] = nil end)
watch("FORJA_Flicker", function(l)
  if not l:IsA("Light") or not l:IsDescendantOf(workspace) then return end
  local kind = l:GetAttribute("VFX_Kind") or "lantern"
  local pos = posOf(l)
  lights[l] = {kind = kind, event = l:GetAttribute("VFX_Event") or "", base = l:GetAttribute("VFX_Base") or l.Brightness,
    pos = pos, seed = seedOf(pos), maxd = LIGHT_DIST[kind] or 200}
end, function(l) lights[l] = nil end)
watch("FORJA_Emitter", function(e)
  if not e:IsA("ParticleEmitter") or not e:IsDescendantOf(workspace) then return end
  emitters[e] = {pos = posOf(e), maxd = e:GetAttribute("VFX_MaxDist") or 400}
end, function(e) emitters[e] = nil end)

-- ---------------------------------------------------------------- Ignis: rig real (marker "Golpe") ou ritmo interno
local lastRigStrike = -1e9
local function hookAnimator(animator)
  local function hookTrack(track)
    track:GetMarkerReachedSignal("Golpe"):Connect(function(param)
      lastRigStrike = os.clock()
      fire("ignis", tonumber(param) or 1)
    end)
  end
  animator.AnimationPlayed:Connect(hookTrack)
  for _, tr in ipairs(animator:GetPlayingAnimationTracks()) do hookTrack(tr) end
end
watch("FORJA_Ignis", function(model)
  task.spawn(function()
    for _ = 1, 20 do
      local an = model:FindFirstChildWhichIsA("Animator", true)
      if an then hookAnimator(an) return end
      task.wait(0.5)
    end
  end)
end, function() end)

-- ---------------------------------------------------------------- carrinho de mina
local cart
local function setupCart()
  local tpl = CFG:FindFirstChild("MineCart")
  if not tpl or #DATA.path < 2 then return end
  local restCF = tpl:GetAttribute("VFX_RestCF")
  if typeof(restCF) ~= "CFrame" then restCF = tpl:GetPivot() end
  local m = tpl:Clone()
  m.Name = "Carrinho_Local"
  m.Parent = localFolder
  local c = {model = m, parts = {}, offs = {}, load = {}, loaded = nil, pts = {}, cum = {}, idx = 1}
  for _, d in ipairs(m:GetDescendants()) do
    if d:IsA("BasePart") then
      table.insert(c.parts, d)
      table.insert(c.offs, restCF:ToObjectSpace(d.CFrame))
      if d:GetAttribute("VFX_Load") then table.insert(c.load, d) end
      d.CanCollide = false
      d.CanQuery = false
      d.CanTouch = false
    end
  end
  for i, p in ipairs(DATA.path) do
    c.pts[i] = rootCF * p
    c.cum[i] = (i == 1) and 0 or (c.cum[i - 1] + (c.pts[i] - c.pts[i - 1]).Magnitude)
  end
  c.up = rootCF.UpVector
  if c.parts[1] then
    local dust = Instance.new("ParticleEmitter")
    dust.Name = "Po"
    dust.Texture = "rbxasset://textures/particles/smoke_main.dds"
    dust.Color = ColorSequence.new(Color3.fromRGB(150, 138, 124))
    dust.Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 1.2), NumberSequenceKeypoint.new(1, 3.5)})
    dust.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.45), NumberSequenceKeypoint.new(1, 1)})
    dust.Lifetime = NumberRange.new(0.8, 1.4)
    dust.Speed = NumberRange.new(2, 4)
    dust.SpreadAngle = Vector2.new(70, 70)
    dust.Drag = 2
    dust.Rate = 0
    dust.LightInfluence = 1
    dust.Parent = c.parts[1]
    c.dust = dust
  end
  -- linha do tempo do ciclo
  local C = DATA.cart
  local function moveDur(d, v, a)
    if d <= v * v / a then return 2 * math.sqrt(d / a) end
    return d / v + v / a
  end
  local segs = {}
  local function mv(s0, s1, v) table.insert(segs, {kind = "move", s0 = s0, s1 = s1, v = v, dur = moveDur(math.abs(s1 - s0), v, C.acc)}) end
  local function st(s, dur, tag) table.insert(segs, {kind = "stop", s0 = s, s1 = s, dur = dur, tag = tag}) end
  if C.weigh then
    mv(C.rest, C.weigh, C.vOut)
    st(C.weigh, C.stopWeigh, "balanca")
    mv(C.weigh, C.far, C.vOut)
  else
    mv(C.rest, C.far, C.vOut)
  end
  st(C.far, C.stopFar, "descarga")
  mv(C.far, C.rest, C.vBack)
  local used = 0
  for _, s in ipairs(segs) do used += s.dur end
  table.insert(segs, {kind = "stop", s0 = C.rest, s1 = C.rest, dur = math.max(4, C.cycle - used), tag = "carga"})
  local t0 = 0
  for _, s in ipairs(segs) do s.t0 = t0 t0 += s.dur end
  c.segs = segs
  c.cycle = t0
  c.idx = 1
  cart = c
end
local function trapezoid(d, v, a, tau)
  local ta = v / a
  if d <= v * ta then
    local tt = math.sqrt(d / a)
    if tau < tt then return 0.5 * a * tau * tau end
    local r = math.max(0, 2 * tt - tau)
    return d - 0.5 * a * r * r
  end
  local T = d / v + ta
  if tau < ta then return 0.5 * a * tau * tau end
  if tau < T - ta then return 0.5 * a * ta * ta + v * (tau - ta) end
  local r = math.max(0, T - tau)
  return d - 0.5 * a * r * r
end
local function cartPos(c, s)
  local pts, cum = c.pts, c.cum
  local n = #pts
  s = math.clamp(s, 0, cum[n])
  local i = math.clamp(c.idx, 1, n - 1)
  while i > 1 and cum[i] > s do i -= 1 end
  while i < n - 1 and cum[i + 1] < s do i += 1 end
  c.idx = i
  local span = cum[i + 1] - cum[i]
  local f = span > 0 and (s - cum[i]) / span or 0
  return pts[i]:Lerp(pts[i + 1], f)
end
local function cartCF(c, s)
  local p = cartPos(c, s)
  local fwd = cartPos(c, s + 1.2) - cartPos(c, s - 1.2)
  fwd = fwd - c.up * fwd:Dot(c.up)
  if fwd.Magnitude < 1e-3 then fwd = rootCF.RightVector end
  return CFrame.fromMatrix(p, fwd.Unit, c.up)
end
local function cartState(c, t)
  local tc = t % c.cycle
  for _, s in ipairs(c.segs) do
    if tc < s.t0 + s.dur then
      local tau = tc - s.t0
      if s.kind == "stop" then return s.s0, s, tau end
      local d = math.abs(s.s1 - s.s0)
      local x = trapezoid(d, s.v, DATA.cart.acc, tau)
      return s.s0 + (s.s1 > s.s0 and x or -x), s, tau
    end
  end
  local last = c.segs[#c.segs]
  return last.s0, last, last.dur
end
local function cartLoaded(c, seg, tau)
  -- carregado na ida; descarrega no portao da forja; recarrega parado no patio da mina
  local after = false
  for _, s in ipairs(c.segs) do
    if s == seg then break end
    if s.tag == "descarga" then after = true end
  end
  if seg.tag == "descarga" then return tau < DATA.cart.unloadAt end
  if seg.tag == "carga" then return tau >= DATA.cart.reloadAt end
  return not after
end
task.spawn(function()
  for _ = 1, 30 do
    if CFG:FindFirstChild("MineCart") then setupCart() return end
    task.wait(1)
  end
end)

-- ---------------------------------------------------------------- relogios (portais e Ignis)
local portalW = {}
for _, p in ipairs(DATA.portals) do portalW[p.key] = {pos = rootCF * p.center, idx = p.idx, last = nil} end
local PORTAL_PERIOD = 3.6
local ignisPos = rootCF * DATA.ignis.pos
local lastIgnis

-- ---------------------------------------------------------------- laco
local moveParts, moveCFs = {}, {}
local accPulse, accLight, accEm = 0, 0, 0
local okStep, step = pcall(function() return RunService.PreRender end)
if not okStep or not step then step = RunService.RenderStepped end
step:Connect(function(dt)
  if CFG:GetAttribute("VFX_Pause") then return end
  local cam = workspace.CurrentCamera
  if not cam then return end
  local cp = cam.CFrame.Position
  local t = workspace:GetServerTimeNow()
  local tn = t % 3600 -- ruido/seno com numeros pequenos (math.noise perde precisao com ~1e9)
  local motion = reduced and 0.35 or 1
  table.clear(moveParts)
  table.clear(moveCFs)
  local n = 0

  -- rotores
  for p, e in pairs(spins) do
    if (e.pivot - cp).Magnitude < SPIN_DIST then
      local sp = e.speed * (e.portal and motion or 1)
      n += 1
      moveParts[n] = p
      moveCFs[n] = e.pivotCF * CFrame.fromAxisAngle(e.axis, e.phase + angleAt(sp, t)) * e.rel
      if e.inner then
        n += 1
        moveParts[n] = e.inner
        moveCFs[n] = e.pivotCF * CFrame.fromAxisAngle(e.axis, e.phase + angleAt(sp * e.innerMul, t)) * e.rel
      end
    end
  end

  -- martinete (fase vem do eixo da roda: 1 golpe por came)
  for ev, g in pairs(hammerGroups) do
    local span = TAU / g.cams
    local u = ((angleAt(g.speed, t) - g.camPhase) % span) / span
    local near = (g.pivot - cp).Magnitude < HAMMER_DIST
    if g.lastU and near then
      local crossed = (g.lastU < H.hit and u >= H.hit) or (u < g.lastU and g.lastU < H.hit)
      if crossed and dt < 0.5 then fire(ev, 1) end
    end
    g.lastU = u
    g.near = near
    g.angle = g.rest + g.lift * hammerLift(u)
  end
  for p, h in pairs(hammers) do
    if h.group.near then
      n += 1
      moveParts[n] = p
      moveCFs[n] = h.pivotCF * CFrame.fromAxisAngle(h.axis, h.group.angle) * h.rel
    end
  end

  -- carrinho
  if cart then
    local s, seg, tau = cartState(cart, t)
    local cf = cartCF(cart, s)
    if (cf.Position - cp).Magnitude < CART_DIST then
      for i, part in ipairs(cart.parts) do
        n += 1
        moveParts[n] = part
        moveCFs[n] = cf * cart.offs[i]
      end
      local loaded = cartLoaded(cart, seg, tau)
      if loaded ~= cart.loaded then
        if cart.loaded ~= nil and cart.dust then cart.dust:Emit(8) end
        cart.loaded = loaded
        for _, part in ipairs(cart.load) do part.Transparency = loaded and 0 or 1 end
      end
    end
  end

  if n > 0 then workspace:BulkMoveTo(moveParts, moveCFs, Enum.BulkMoveMode.FireCFrameChanged) end

  -- portais: pulso de luz + anel
  for key, pw in pairs(portalW) do
    local ph = (t + pw.idx * 0.55) % PORTAL_PERIOD
    if pw.last and ph < pw.last and (pw.pos - cp).Magnitude < 480 then fire("portal:" .. key, 1) end
    pw.last = ph
  end
  -- Ignis: ritmo interno enquanto o rig nao manda "Golpe"
  if os.clock() - lastRigStrike > 12 and (ignisPos - cp).Magnitude < 260 then
    local tc = t % DATA.ignis.cycle
    if lastIgnis then
      for _, hit in ipairs(DATA.ignis.hits) do
        local ht = hit[1]
        if (lastIgnis < ht and tc >= ht) or (tc < lastIgnis and (lastIgnis < ht or tc >= ht)) then fire("ignis", hit[2]) end
      end
    end
    lastIgnis = tc
  else
    lastIgnis = nil
  end

  -- decaimento dos claroes
  local k = math.exp(-dt * 7)
  for ev, v in pairs(flash) do
    v *= k
    flash[ev] = (v > 0.01) and v or nil
  end

  -- claroes (todo frame, sao poucos)
  for l, e in pairs(lights) do
    if e.kind == "flash" then l.Brightness = e.base * (flash[e.event] or 0) end
  end

  -- pulsos de cor (20 Hz)
  accPulse += dt
  if accPulse >= 0.05 then
    accPulse = 0
    local flick = reduced and 0.3 or 1
    for p, e in pairs(pulses) do
      if (e.pos - cp).Magnitude < e.maxd then
        local c
        if e.kind == "crystal" then
          local s = 0.5 + 0.5 * math.sin(tn * 1.9 + e.seed)
          c = e.base:Lerp(e.hi, (0.08 + 0.34 * s * s) * (reduced and 0.5 or 1))
        elseif e.kind == "heat" then
          local br = 0.5 + math.noise(tn * 0.9, e.seed, 0.5)
          c = e.base:Lerp(HOT, math.clamp(0.06 + 0.14 * br + 0.8 * (flash[e.event] or 0), 0, 1))
        elseif e.kind == "ember" then
          local f = math.clamp(0.9 + 0.22 * math.noise(tn * 1.6, e.seed, 0.3) * flick, 0.7, 1)
          c = Color3.new(e.base.R * f, e.base.G * f, e.base.B * f)
        elseif e.kind == "lantern" then
          local f = math.clamp(0.96 + 0.1 * math.noise(tn * 5.5, e.seed, 0.7) * flick, 0.85, 1)
          c = Color3.new(e.base.R * f, e.base.G * f, e.base.B * f)
        elseif e.kind == "portalcore" then
          c = e.base:Lerp(WHITE, math.clamp(0.15 + 0.15 * math.sin(tn * 2.6 + e.seed) + 0.6 * (flash[e.event] or 0), 0, 1))
        end
        if c then p.Color = c end
      end
    end
  end

  -- flicker das luzes (15 Hz)
  accLight += dt
  if accLight >= 0.066 then
    accLight = 0
    local flick = reduced and 0.3 or 1
    for l, e in pairs(lights) do
      if e.kind ~= "flash" and (e.pos - cp).Magnitude < e.maxd then
        local f = 1
        if e.kind == "lantern" then
          f = 1 + (0.12 * math.noise(tn * 2.1, e.seed, 0.2) + 0.06 * math.noise(tn * 9.3, e.seed, 0.8)) * flick
        elseif e.kind == "fire" then
          f = 1 + (0.3 * math.noise(tn * 3.3, e.seed, 0.4) + 0.16 * math.noise(tn * 11, e.seed, 0.9)) * flick
        elseif e.kind == "crystal" then
          f = 1 + 0.15 * math.sin(tn * 1.9 + e.seed)
        elseif e.kind == "portal" then
          f = 1 + 0.1 * math.sin(tn * 2.2 + e.seed) + 0.9 * (flash[e.event] or 0)
        end
        l.Brightness = e.base * f
      end
    end
  end

  -- emissores continuos longe da camera ficam desligados (2 Hz)
  accEm += dt
  if accEm >= 0.5 then
    accEm = 0
    for em, e in pairs(emitters) do
      local on = (e.pos - cp).Magnitude < e.maxd
      if em.Enabled ~= on then em.Enabled = on end
    end
  end
end)
'''


if __name__ == "__main__":
    main()
