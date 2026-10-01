# export_vfx.py - VFX e MOVIMENTO do Lobby Vila-Forja para o Roblox
# uso: blender -b lobby_forja_mineradora.blend --python export_all.py      (RECOMENDADO: estatico + VFX no mesmo passe)
#      blender -b lobby_forja_mineradora.blend --python export_vfx.py      (so o VFX; le o EXPORT_ID do lobby_data.json)
#      FM_VFX_OUT=<pasta> desvia a saida (padrao: a mesma pasta do export_roblox, ./export)
# saida em ./export/:
#   LOBBY_VFX_MOVING_<ID6>.fbx    (ID6 = EXPORT_ID do estatico; sem ele, LOBBY_VFX_MOVING.fbx). Orcamento: 16k tris e
#                                 30 MeshParts (ER.BUDGET vfx_*); FM_BUDGET=strict (padrao) falha sem gravar se passar.
#                                 pecas moveis: roda d'agua + eixo baixo (coroa, cames), eixo alto (pinhao + engrenagem
#                                 da parede da forja), engrenagem menor da parede, martinete, fole (se o forge separar a
#                                 tampa), a versao FIXA do que ficou parado nessas malhas e o carrinho de mina.
#                                 "VFX_<grupo>__<material>", 1 material por malha (com a textura de detalhe EMBUTIDA,
#                                 como o export estatico), origem no centro do bbox.
#   vfx_lobby_forja.lua           MONTAGEM (Command Bar uma vez, ou Script em ServerScriptService)
#   vfx_lobby_forja_client.lua    ANIMACAO (LocalScript em StarterPlayer > StarterPlayerScripts)
#
# Por que um FBX extra: no export estatico a roda, as engrenagens e o martinete estao fundidos com pecas fixas
# (mancais, calhas, paredes). Aqui o script separa as ILHAS de malha que giram das que ficam paradas; a montagem
# guarda as malhas estaticas originais em ServerStorage (reversivel) e poe as versoes separadas no lugar.
# A troca e por OBJETO + FAMILIA de material (Wood_*, Metal_*...), nao pelo nome exato da variante.
# Espirais dos portais: nao ha geometria aqui. A montagem poe um SurfaceGui na face do disco (a textura da espiral
# que o montar aplicou) e o cliente gira as ImageLabels.
import sys, os, math, random, json, glob
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy, bmesh
from mathutils import Vector, Matrix
import fm_layout as L
import fm_lib
import fm_parts
import fm_mat_textures as TX
import export_roblox as ER

OUT = os.environ.get("FM_VFX_OUT") or ER.OUT
VERSION = "vfx-forja-2"
TMP_COLL = "_VFX_TMP"
META_TRIS, META_PARTS = 16000, 30   # orcamento do LOBBY_VFX_MOVING.fbx

# ------------------------------------------------------------------ geometria da casa da roda
# Valores do fm_water, usados SO se os marcadores nao trouxerem as props (VFX_Waterwheel_Rotate: half_w, R, pivot;
# VFX_TripHammer: pivot, crown_c/crown_r, pinion_c/pinion_r, cam_len). A classificacao confere a razao de dentes
# (2,0 +- 0,1) e as 2 ilhas do martinete e ABORTA se nao bater: mudanca na casa da roda nao passa calada.
WHEEL_HALF_W = 1.7             # meia largura da roda (Wd/2); +0,75 de folga
UZ = 15.5                      # eixo alto (pinhao)
GEAR_DX = 2.4                  # gx = MILL.x0 + 2.4 (roda de coroa e pinhao)
GEAR_RC, GEAR_RP, TOOTH = 2.9, 1.3, 0.25
CAM_LEN = 2.0
HAMMER_PIV = (5.0, 9.0)        # pivo do martinete: (wy + 5, z 9)
HAMMER_REST = 0.03             # rad acima da pose modelada: cabeca assenta na bigorna e o came so encosta no cabo
HAMMER_LIFT = 0.16             # rad de subida maxima
GEAR_RATIO = (2.0, 0.1)
# perfil do martinete em fracao do intervalo entre cames (3 cames = 120 graus):
# came passa (0-15) -> cabo sobe seguindo o came (15-64) -> segura -> cai rapido (66-72) = GOLPE -> quique
HAMMER_PROFILE = {"rise0": 15 / 120, "rise1": 64 / 120, "fall0": 66 / 120, "hit": 72 / 120, "bounce": 80 / 120}
# fole (kind 'pump'): angulo = rest + lift * (0.5 - 0.5 cos(k w_roda t)); no pico (fole fechado) dispara 'foles'.
# Padroes = manivela no eixo da roda (1 golpe por volta) e 12 graus; o VFX_Bellows_Hinge manda (lift/angle_deg, k).
PUMP_REST, PUMP_LIFT, PUMP_K = 0.0, math.radians(12.0), 1

# ------------------------------------------------------------------ portais
# rad/s no plano do disco (sinal = sentido); a ImageLabel interna (0,55) gira PORTAL_INNER x mais rapido
PORTAL_SPIN = {"Naruto": -0.9, "DragonBall": 1.25, "ShadowGarden": -0.55, "DemonSlayer": 1.05,
               "OnePiece": -0.75, "OnePunchMan": 1.45}
PORTAL_INNER = 2.3
PORTAL_PAL = {  # sRGB: disco, bracos/particulas, nucleo (so para particulas e para o fallback sem textura)
    "Naruto": ((255, 110, 16), (255, 196, 96), (255, 244, 214)),
    "DragonBall": ((30, 120, 240), (150, 214, 255), (236, 248, 255)),
    "ShadowGarden": ((118, 38, 214), (208, 158, 255), (244, 232, 255)),
    "DemonSlayer": ((206, 28, 40), (255, 150, 138), (255, 234, 226)),
    "OnePiece": ((24, 92, 226), (138, 204, 255), (228, 246, 255)),
    "OnePunchMan": ((232, 175, 0), (255, 236, 120), (255, 250, 225)),
}

CART_MARGIN = 2.9              # meio carrinho + folga para nao encostar nos carrinhos estacionados
CART_Z = L.FLOOR + 0.3         # mesma cota dos carrinhos do fm_mine
EXPORT_GROUPS = ER.GROUPS      # colecoes exportadas (onde procurar cachoeiras, agua, aros)
SMOKE_VILLAGE = 4              # chamines da vila com fumaca (as mais visiveis da praca), nao todas


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


def lstr(s):
    return '"%s"' % str(s).replace("\\", "\\\\").replace('"', '\\"')


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


def pget(ob, names, default=None, vec=False):
    """prop de marcador por varios nomes possiveis; vec=True -> Vector (aceita lista/array do Blender)"""
    if ob is None:
        return default
    for n in names:
        if n in ob.keys():
            v = ob[n]
            if vec:
                try:
                    t = tuple(float(x) for x in v)
                    if len(t) == 3:
                        return Vector(t)
                except TypeError:
                    continue
                continue
            try:
                return float(v)
            except (TypeError, ValueError):
                continue
    return default


def is_glow(m):
    return ER.rbx_rule(m)[0] == "Neon"


def coarse(m):
    """familia GROSSA do material para a troca estatico -> VFX (Wood_Dark_B -> Wood, Metal_Rust -> Metal).
    Materiais que brilham (Neon) ficam pelo nome exato: tem pulso proprio e nunca giram junto."""
    if is_glow(m):
        return m
    return m.split("_")[0]


def fine_ok(obj_name):
    """a troca pode ser pela familia da VARIANTE (Wood_Dark_B -> Wood_Dark) quando o export estatico nao funde
    materiais pequenos no vizinho nesse objeto (sem ER._fold, ou objeto em ER.NO_FOLD_OBJ). Senao a face de um Metal_Iron
    pode estar dentro da malha estatica Metal_Dark: ai so a familia GROSSA (Metal_*) garante que nada some."""
    return not hasattr(ER, "_fold") or obj_name in getattr(ER, "NO_FOLD_OBJ", ())


def src_key(m, fine):
    """chave de troca do material: nome exato (brilho), familia da variante (fine) ou familia grossa"""
    if is_glow(m):
        return m
    return fm_lib.family_of(m) if fine else coarse(m)


def bbox_of(pts):
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return mn, mx


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
        i.mn, i.mx = bbox_of(cos)
        i.mats = {matname(mats, f.material_index) for f in faces}
        out.append(i)
    return out


def faces_obj(name, faces, src_mats, only_mats=None, remap=None, uv=None):
    """copia faces (de um bmesh fonte, com a UVMap) para um objeto novo multi-material.
    only_mats filtra por material; remap troca material (variante minoritaria -> majoritaria nas pecas moveis)."""
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("UVMap") if uv is not None else None   # sem UV: export_roblox projeta
    vmap = {}
    mlist = []
    for f in faces:
        m = matname(src_mats, f.material_index)
        if only_mats is not None and m not in only_mats:
            continue
        m = (remap or {}).get(m, m)
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
        if uv is not None:
            for ln, lo in zip(nf.loops, f.loops):
                ln[uvl].uv = lo[uv].uv
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


def unbevel_boxes(ob, max_frac=0.16):
    """PECAS MOVEIS: caixa com chanfro minusculo (dente, raio, pa, came: 0,03-0,05 stud) vira caixa limpa
    (12 tris em vez de ~44). A estatica original fica guardada, entao nao ha com o que comparar; o chanfro grande
    (cabeca do martinete, cubos) passa do limite de area e fica como esta."""
    if ob is None:
        return 0
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.verts.ensure_lookup_table()
    bm.verts.index_update()
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
    boxes, dead = [], set()
    for faces in groups.values():
        if len(faces) < 10 or len({f.material_index for f in faces}) != 1:
            continue
        areas = sorted(((f.calc_area(), f) for f in faces), key=lambda x: -x[0])
        tot = sum(a for a, _ in areas)
        A = areas[0][1].normal.copy()
        B = next((f.normal.copy() for a, f in areas[1:] if abs(f.normal.dot(A)) < 0.05), None)
        if B is None or tot <= 0:
            continue
        C = A.cross(B).normalized()
        B = C.cross(A).normalized()
        axes = (A, B, C)
        main = [a for a, f in areas if any(abs(f.normal.dot(ax)) > 0.9995 for ax in axes)]
        if len(main) != 6 or tot - sum(main) > max_frac * tot:
            continue
        vs = {v for f in faces for v in f.verts}
        lo = [min(v.co.dot(ax) for v in vs) for ax in axes]
        hi = [max(v.co.dot(ax) for v in vs) for ax in axes]
        boxes.append((axes, lo, hi, faces[0].material_index))
        dead |= vs
    if not boxes:
        bm.free()
        return 0
    bmesh.ops.delete(bm, geom=list(dead), context="VERTS")
    uvl = bm.loops.layers.uv.get("UVMap")
    mats = me.materials
    new_faces = []
    for axes, lo, hi, mi in boxes:
        cv = {}
        for i in (0, 1):
            for j in (0, 1):
                for k in (0, 1):
                    p = axes[0] * (hi[0] if i else lo[0]) + axes[1] * (hi[1] if j else lo[1]) + axes[2] * (hi[2] if k else lo[2])
                    cv[(i, j, k)] = bm.verts.new(p)
        quads = [((0, 0, 0), (0, 1, 0), (0, 1, 1), (0, 0, 1)), ((1, 0, 0), (1, 0, 1), (1, 1, 1), (1, 1, 0)),
                 ((0, 0, 0), (0, 0, 1), (1, 0, 1), (1, 0, 0)), ((0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)),
                 ((0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)), ((0, 0, 1), (0, 1, 1), (1, 1, 1), (1, 0, 1))]
        mname = matname(mats, mi)
        tk = fm_lib.tex_key(mname)
        inv = 1.0 / (fm_lib.tex_tile(tk) if tk else 4.0)
        fs = []
        for q in quads:
            f = bm.faces.new([cv[c] for c in q])
            f.material_index = mi
            fs.append(f)
        bmesh.ops.recalc_face_normals(bm, faces=fs)
        if uvl is not None:
            for f in fs:
                e = max(f.edges, key=lambda e: e.calc_length())
                u = (e.verts[1].co - e.verts[0].co).normalized()
                v = f.normal.cross(u)
                for lp in f.loops:
                    lp[uvl].uv = (lp.vert.co.dot(u) * inv, lp.vert.co.dot(v) * inv)
        new_faces += fs
    bm.to_mesh(me)
    bm.free()
    return len(boxes)


def face_mats(isls, mats):
    return {matname(mats, f.material_index) for i in isls for f in i.faces}


def majority_remap(isls, mats):
    """pecas moveis: variantes da mesma familia (Wood_Light / Wood_Light_B) viram a variante com mais faces
    -> menos MeshParts no FBX de movimento (a diferenca de tom numa peca girando nao se le)"""
    cnt = {}
    for i in isls:
        for f in i.faces:
            m = matname(mats, f.material_index)
            cnt[m] = cnt.get(m, 0) + 1
    best = {}
    for m, n in cnt.items():
        fam = fm_lib.family_of(m)
        if fam not in best or n > cnt[best[fam]]:
            best[fam] = m
    return {m: best[fm_lib.family_of(m)] for m in cnt}


def ext_mats(ob, aff):
    """todos os materiais do objeto que caem nas familias afetadas (o que a montagem vai esconder e a copia FIXA
    tem que repor). Familia da variante quando o estatico nao funde materiais nesse objeto (copia fixa menor),
    senao familia grossa."""
    fine = fine_ok(ob.name)
    fams = {src_key(m, fine) for m in aff}
    return {m.name for m in ob.data.materials if m and src_key(m.name, fine) in fams}, sorted(fams)


def fold_tiny(isls, mats, min_tris=40):
    """pecas moveis GERADAS aqui (carrinho): material com menos de min_tris vira o material dominante da peca
    (1 MeshPart a menos por detalhe de 12 tris)"""
    cnt = {}
    for i in isls:
        for f in i.faces:
            m = matname(mats, f.material_index)
            cnt[m] = cnt.get(m, 0) + len(f.verts) - 2
    if not cnt:
        return {}
    top = max(cnt, key=lambda m: cnt[m])
    return {m: (top if n < min_tris else m) for m, n in cnt.items()}


def add_obj(ctx, gname, ob, **g):
    if gname not in ctx["groups"]:
        g.setdefault("objs", [])
        ctx["groups"][gname] = g
    if ob is not None:
        grp = ctx["groups"][gname]
        if grp["kind"] in ("spin", "hammer"):
            ctx["unbevel"] = ctx.get("unbevel", 0) + unbevel_boxes(ob)
        grp["objs"].append(ob)


def upper_center(mk, wc):
    """centro do pinhao (eixo alto): props do VFX_TripHammer ou o valor do fm_water"""
    return pget(mk.get("VFX_TripHammer"), ("pinion_c", "pinhao_c", "pinion", "pinhao"),
                Vector((L.MILL[0] + GEAR_DX, wc.y, UZ)), vec=True)


def is_shaft(i, c, rmax=0.85, minlen=2.0):
    """ilha e um trecho de EIXO coaxial ao eixo X que passa por c (longo em X, fino, todo a <= rmax do eixo): gira
    junto (um eixo octogonal parado ao lado da engrenagem girando se le). Mancais e colares sao curtos: ficam."""
    e = i.mx - i.mn
    return e.x >= minlen and max(e.y, e.z) <= 2 * rmax + 0.1 and \
        all(math.hypot(p.y - c.y, p.z - c.z) <= rmax for p in i.cos)


def bbox_faces(ob, mats, zmin=-1e9, zmax=1e9):
    """bbox (mundo) das faces de um conjunto de materiais, opcionalmente so as que ficam numa faixa de z"""
    if ob is None:
        return None
    if isinstance(mats, str):
        mats = {mats}
    mw = ob.matrix_world
    names = [m.name if m else "" for m in ob.data.materials]
    pts = []
    for p in ob.data.polygons:
        if p.material_index >= len(names) or names[p.material_index] not in mats:
            continue
        cs = [mw @ ob.data.vertices[v].co for v in p.vertices]
        if all(zmin <= c.z <= zmax for c in cs):
            pts.extend(cs)
    return bbox_of(pts) if pts else None


def objs_prefix(prefix):
    return [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(prefix)]


def bbox_prefix(prefix, mats):
    box = None
    for o in objs_prefix(prefix):
        r = bbox_faces(o, mats)
        if r:
            box = r if box is None else (Vector(map(min, box[0], r[0])), Vector(map(max, box[1], r[1])))
    return box


# ------------------------------------------------------------------ 1. roda d'agua
def build_wheel(ctx, mk):
    m = mk["VFX_Waterwheel_Rotate"]
    wc = pget(m, ("pivot", "center"), None, vec=True) or m.location.copy()
    rpm = pget(m, ("rpm",), 6.0)
    w = 2 * math.pi * rpm / 60.0
    R = pget(m, ("R", "radius", "raio"), float(L.WHEEL_R))
    half = pget(m, ("half_w", "halfw", "half_width"), WHEEL_HALF_W) + 0.75
    ob = bpy.data.objects["WATER_Waterwheel"]
    pin_c = upper_center(mk, wc)
    bm = world_bm(ob)
    uv = bm.loops.layers.uv.get("UVMap")
    isl = islands(ob, bm)
    rot, up, fix = [], [], []
    for i in isl:
        ok = all(abs(p.x - wc.x) <= half and math.hypot(p.y - wc.y, p.z - wc.z) <= R + 0.6 for p in i.cos)
        if ok or is_shaft(i, wc):
            rot.append(i)                 # roda + eixo baixo (sai da roda e entra na casa)
        elif is_shaft(i, pin_c):
            up.append(i)                  # eixo alto (parede da forja -> pinhao): gira com o pinhao
        else:
            fix.append(i)
    mats = ob.data.materials
    aff = face_mats(rot + up, mats)
    ext, fams = ext_mats(ob, aff)
    ctx["log"].append("roda: %d ilhas giram (eixo alto: %d), %d fixas; familias trocadas %s" % (
        len(rot), len(up), len(fix), fams))
    o_rot = faces_obj("VFX_Roda_src", [f for i in rot for f in i.faces], mats, remap=majority_remap(rot, mats), uv=uv)
    o_up = faces_obj("VFX_RodaEixoAlto_src", [f for i in up for f in i.faces], mats, uv=uv) if up else None
    o_fix = faces_obj("VFX_RodaFixa_src", [f for i in fix for f in i.faces], mats, ext, uv=uv)
    bm.free()
    # sentido: a roda e de baixo (undershot); o rio corre para -Y, entao o fundo da roda anda para -Y
    # => rotacao em torno de -X (Blender e Roblox compartilham o eixo X)
    add_obj(ctx, "roda", o_rot, name="VFX_Roda", kind="spin", assembly="RodaDagua", pivot=wc, axis=Vector((-1, 0, 0)),
            speed=w)
    add_obj(ctx, "fixa", o_fix, name="VFX_Fixa", kind="fixed", assembly="Fixas")
    ctx["pending_up"] = [o_up] if o_up else []           # entra no grupo eixo_alto quando a casa da roda o criar
    ctx["sources"].append(("WATER_Waterwheel", fams, ["roda", "fixa"] + (["eixo_alto"] if o_up else [])))
    # pas: 16 a cada 22,5 graus a partir de 0 (fm_water); a borda externa (raio R) toca a agua em z = rio
    wz = mk["VFX_Wheel_Splash"].location.z if "VFX_Wheel_Splash" in mk else 2.8
    s = max(-1.0, min(1.0, (wz - wc.z) / R))
    a_in = math.atan2(s, math.sqrt(1 - s * s))        # lado +Y (montante): a pa entra
    a_out = math.atan2(s, -math.sqrt(1 - s * s))      # lado -Y (jusante): a pa sai
    ctx["wheel"] = dict(center=wc, R=R, w=w, rpm=rpm, paddles=16, a_in=a_in, a_out=a_out)


# ------------------------------------------------------------------ 2. casa da roda: coroa + cames, pinhao, martinete
def build_wheelhouse(ctx, mk):
    wc = ctx["wheel"]["center"]
    w = ctx["wheel"]["w"]
    wy, az = wc.y, wc.z
    mh = mk["VFX_TripHammer"]
    head = mh.location.copy()
    hx = head.x
    gx = L.MILL[0] + GEAR_DX
    crown_c = pget(mh, ("crown_c", "coroa_c", "crown", "coroa"), Vector((gx, wy, az)), vec=True)
    pin_c = pget(mh, ("pinion_c", "pinhao_c", "pinion", "pinhao"), Vector((gx, wy, UZ)), vec=True)
    rc = pget(mh, ("crown_r", "coroa_r"), GEAR_RC)
    rp = pget(mh, ("pinion_r", "pinhao_r"), GEAR_RP)
    cam_len = pget(mh, ("cam_len", "came"), CAM_LEN)
    piv = pget(mh, ("pivot", "pivo"), Vector((hx, wy + HAMMER_PIV[0], HAMMER_PIV[1])), vec=True)
    gx = crown_c.x
    uz = pin_c.z
    ob = bpy.data.objects["BLD_WheelHouse"]
    bm = world_bm(ob)
    uv = bm.loops.layers.uv.get("UVMap")
    isl = islands(ob, bm)
    low, pin, ham, fix = [], [], [], []
    teeth_c = teeth_p = 0
    for i in isl:
        if any(is_glow(m) for m in i.mats):
            fix.append(i)
            continue
        # trechos de eixo (baixo: roda -> coroa -> cames; alto: pinhao -> parede)
        if is_shaft(i, crown_c):
            low.append(i)
            continue
        if is_shaft(i, pin_c):
            pin.append(i)
            continue
        ext = i.mx - i.mn
        # engrenagens: fatia fina em x = gx
        if all(abs(p.x - gx) <= 0.8 for p in i.cos) and max(ext) <= 7.0:
            dl = math.hypot(i.c.y - crown_c.y, i.c.z - crown_c.z)
            dh = math.hypot(i.c.y - pin_c.y, i.c.z - pin_c.z)
            in_c = all(math.hypot(p.y - crown_c.y, p.z - crown_c.z) <= rc + 0.95 for p in i.cos)
            in_p = all(math.hypot(p.y - pin_c.y, p.z - pin_c.z) <= rp + 0.95 for p in i.cos)
            if dl < 0.35 and in_c:
                low.append(i)
            elif dh < 0.35 and in_p:
                pin.append(i)
            elif in_c or in_p:
                # dente: fica com a engrenagem cujo raio de dente bate melhor
                if in_c and (not in_p or abs(dl - (rc + TOOTH)) <= abs(dh - (rp + TOOTH))):
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
                all(math.hypot(p.y - wy, p.z - az) <= cam_len + 0.6 for p in i.cos):
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
    ext_, fams = ext_mats(ob, aff)
    ratio = (teeth_c / teeth_p) if teeth_p else 0.0
    ctx["log"].append("casa da roda: eixo baixo %d ilhas (%d dentes), pinhao %d (%d dentes, razao %.2f), martinete %d"
                      % (len(low), teeth_c, len(pin), teeth_p, ratio, len(ham)))
    if abs(ratio - GEAR_RATIO[0]) > GEAR_RATIO[1] or len(ham) != 2:
        raise RuntimeError("casa da roda mudou: razao de dentes %.2f (esperado %.1f+-%.1f) e martinete com %d ilhas "
                           "(esperado 2). Grave as props do VFX_TripHammer (pivot, crown_c/crown_r, pinion_c/pinion_r) "
                           "ou ajuste a classificacao do export_vfx.py" % (ratio, GEAR_RATIO[0], GEAR_RATIO[1], len(ham)))
    o_low = faces_obj("VFX_EixoBaixo_src", [f for i in low for f in i.faces], mats, remap=majority_remap(low, mats), uv=uv)
    o_pin = faces_obj("VFX_Pinhao_src", [f for i in pin for f in i.faces], mats, remap=majority_remap(pin, mats), uv=uv)
    o_ham = faces_obj("VFX_Martinete_src", [f for i in ham for f in i.faces], mats, remap=majority_remap(ham, mats), uv=uv)
    o_fix = faces_obj("VFX_CasaFixa_src", [f for i in fix for f in i.faces], mats, ext_, uv=uv)
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
    # o eixo baixo tem o MESMO movimento da roda (mesmo eixo, mesma velocidade): vai no mesmo grupo
    if (crown_c - wc).cross(Vector((1, 0, 0))).length > 0.3:
        raise RuntimeError("coroa fora do eixo da roda (%s x %s)" % (tuple(crown_c), tuple(wc)))
    add_obj(ctx, "roda", o_low)
    add_obj(ctx, "eixo_alto", o_pin, name="VFX_EixoAlto", kind="spin", assembly="CasaDaRoda", pivot=pin_c.copy(),
            axis=Vector((1, 0, 0)), speed=w * ratio)
    for o in ctx.pop("pending_up", []):
        add_obj(ctx, "eixo_alto", o)
    add_obj(ctx, "martinete", o_ham, name="VFX_Martinete", kind="hammer", assembly="CasaDaRoda", pivot=piv, axis=ax,
            speed=w, cam_phase=cam_phase, cams=ncam, rest=HAMMER_REST, lift=HAMMER_LIFT, event="martinete")
    add_obj(ctx, "fixa", o_fix)
    ctx["sources"].append(("BLD_WheelHouse", fams, ["roda", "eixo_alto", "martinete", "fixa"]))
    ctx["hammer"] = dict(head=head, piv=piv)
    ctx["upper"] = dict(c=pin_c.copy(), speed=w * ratio, teeth=teeth_p)


# ------------------------------------------------------------------ 3. engrenagens da parede da forja (eixo alto)
def build_wall_gears(ctx):
    ob = bpy.data.objects.get("FORGE_Wall_Gears")
    up = ctx.get("upper")
    if ob is None or up is None or ob.type != "MESH":
        # juntadas num objeto maior (ala): trocar a malha estatica da ala inteira custaria milhares de tris na copia
        # fixa -> ficam paradas. O forge tem que manter FORGE_Wall_Gears como objeto proprio.
        ctx["log"].append("AVISO engrenagens da parede: objeto FORGE_Wall_Gears ausente (juntado em outro?) -> ficam "
                          "PARADAS; mantenha FORGE_Wall_Gears separado no fm_forge")
        return
    bm = world_bm(ob)
    uv = bm.loops.layers.uv.get("UVMap")
    isl = islands(ob, bm)
    mats = ob.data.materials
    # centros: ilhas redondas no plano YZ (disco, aro, cubo) -> agrupadas por centro do BBOX (a media dos vertices
    # do aro em tubo sai 0,1-0,15 fora do eixo por causa da costura: pivo torto = engrenagem bamboleando)
    def bc(i):
        return (i.mn + i.mx) / 2
    centers = []
    for i in isl:
        e = i.mx - i.mn
        q = bc(i)
        if e.x <= 1.6 and e.y > 0.4 and abs(e.y - e.z) <= 0.12 * max(e.y, e.z):
            for c in centers:
                if abs(c["c"].y - q.y) < 0.3 and abs(c["c"].z - q.z) < 0.3 and abs(c["c"].x - q.x) < 1.0:
                    c["body"].append(i)
                    c["r"] = max(c["r"], max(e.y, e.z) / 2)
                    break
            else:
                centers.append(dict(c=q, body=[i], r=max(e.y, e.z) / 2, teeth=[], parts=[]))
    centers = [c for c in centers if len(c["body"]) >= 2]
    used = set()
    for c in centers:
        c["c"] = sum((bc(i) for i in c["body"]), Vector()) / len(c["body"])
        for i in c["body"]:
            used.add(id(i))

    def dist(i, c):
        q = bc(i)
        return math.hypot(q.y - c["c"].y, q.z - c["c"].z)

    def teeth_ring(c):
        # dentes = o anel MAIS EXTERNO com >= 6 ilhas a mesma distancia do centro (raios ficam mais para dentro)
        ds = sorted(((dist(i, c), i) for i in c["parts"] + c["teeth"]), key=lambda x: x[0])
        rings = []
        for d, i in ds:
            if rings and d - rings[-1][-1][0] <= 0.08:
                rings[-1].append((d, i))
            else:
                rings.append([(d, i)])
        big = [r for r in rings if len(r) >= 6]
        allp = c["parts"] + c["teeth"]
        c["teeth"] = [i for _, i in big[-1]] if big else []
        c["parts"] = [i for i in allp if i not in c["teeth"]]
        c["tr"] = sum(d for d, _ in big[-1]) / len(big[-1]) if big else None

    deferred = []
    for i in isl:
        if id(i) in used:
            continue
        cand = []
        for c in centers:
            if abs(i.c.x - c["c"].x) > 1.0 or any(abs(p.x - c["c"].x) > 1.2 for p in i.cos):
                continue
            dmax = max(math.hypot(p.y - c["c"].y, p.z - c["c"].z) for p in i.cos)
            # 1,2 x o aro: pega os dentes, deixa de fora a guarda de chapa (r 3,5) e o mancal
            if dmax <= c["r"] * 1.2 + 0.1:
                cand.append((dmax, c))
        if len(cand) == 1:
            cand[0][1]["parts"].append(i)
            used.add(id(i))
        elif cand:
            deferred.append((i, cand))
    for c in centers:
        teeth_ring(c)
    for i, cand in deferred:
        # dente na zona de engrenamento (perto dos dois centros): fica com a engrenagem cujo anel de dentes bate
        fit = [(abs(dist(i, c) - c["tr"]), c) for _, c in cand if c.get("tr") is not None and abs(dist(i, c) - c["tr"]) <= 0.15]
        c = min(fit, key=lambda x: x[0])[1] if fit else min(cand, key=lambda x: x[0])[1]
        c["parts"].append(i)
        used.add(id(i))
    for c in centers:
        teeth_ring(c)
    drv = [c for c in centers if abs(c["c"].y - up["c"].y) < 0.4 and abs(c["c"].z - up["c"].z) < 0.4]
    if not drv:
        bm.free()
        ctx["log"].append("engrenagens da parede: nenhuma no eixo alto (y %.1f z %.1f) -> ficam paradas" % (up["c"].y, up["c"].z))
        return
    d0 = drv[0]
    groups = [(d0, "eixo_alto", Vector((1, 0, 0)), up["speed"])]
    for c in centers:
        if c is d0:
            continue
        dist = (c["c"] - d0["c"]).length
        if abs(dist - (c["r"] + d0["r"])) > max(1.0, 0.25 * dist) or not c["teeth"] or not d0["teeth"]:
            continue
        groups.append((c, "engrenagem_parede", Vector((-1, 0, 0)), up["speed"] * len(d0["teeth"]) / len(c["teeth"])))
    moving = [i for c, _, _, _ in groups for i in c["body"] + c["parts"] + c["teeth"]]
    aff = face_mats(moving, mats)
    ext_, fams = ext_mats(ob, aff)
    for c, gname, axis, speed in groups:
        isls = c["body"] + c["parts"] + c["teeth"]
        o = faces_obj("VFX_%s_parede_src" % gname, [f for i in isls for f in i.faces], mats,
                      remap=majority_remap(isls, mats), uv=uv)
        if gname == "eixo_alto":
            add_obj(ctx, gname, o)
        else:
            add_obj(ctx, gname, o, name="VFX_EngrenagemParede", kind="spin", assembly="ForjaEngrenagens", pivot=c["c"].copy(),
                    axis=axis, speed=speed)
    mid = {id(i) for i in moving}
    o_fix = faces_obj("VFX_ParedeFixa_src", [f for i in isl if id(i) not in mid for f in i.faces], mats, ext_, uv=uv)
    add_obj(ctx, "fixa", o_fix)
    bm.free()
    ctx["sources"].append(("FORGE_Wall_Gears", fams, [g[1] for g in groups] + ["fixa"]))
    ctx["log"].append("engrenagens da parede: %s" % ", ".join("%s r%.1f %d dentes %.2f rad/s" % (g[1], g[0]["r"], len(g[0]["teeth"]), g[3])
                                                              for g in groups))


# ------------------------------------------------------------------ 4. fole (tampa separada pelo forge)
def build_bellows(ctx, mk):
    ob = bpy.data.objects.get("FORGE_Bellows_Top")
    hm = mk.get("VFX_Bellows_Hinge")
    if ob is None or hm is None or ob.type != "MESH":
        ctx["log"].append("fole: %s -> sem bombeamento" % ("FORGE_Bellows_Top ausente" if ob is None else "sem VFX_Bellows_Hinge"))
        return
    piv = pget(hm, ("pivot", "pivo"), None, vec=True) or hm.location.copy()
    axis = pget(hm, ("axis", "eixo"), None, vec=True)
    if axis is None or axis.length < 1e-6:
        axis = hm.matrix_world.to_3x3().normalized().col[0]
    axis = axis.normalized()
    lift = pget(hm, ("lift",), None)
    if lift is None:
        ad = pget(hm, ("angle_deg", "angulo"), None)
        lift = math.radians(ad) if ad is not None else PUMP_LIFT
    bm = world_bm(ob)
    uv = bm.loops.layers.uv.get("UVMap")
    cen = sum((v.co for v in bm.verts), Vector()) / max(1, len(bm.verts))
    # angulo positivo FECHA o fole: a tampa desce a partir da pose modelada (aberta) e o couro entra no pedestal;
    # abrir alem da pose deixaria um vao embaixo do couro. O sopro (evento 'foles') e o fundo do curso.
    if (Matrix.Rotation(0.05, 3, axis) @ (cen - piv)).z > (cen - piv).z:
        axis = -axis
    mats = ob.data.materials
    fine = fine_ok(ob.name)
    allm = {m.name for m in mats if m}
    o = faces_obj("VFX_Foles_src", list(bm.faces), mats, uv=uv)
    bm.free()
    add_obj(ctx, "foles", o, name="VFX_Foles", kind="pump", assembly="ForjaFoles", pivot=piv, axis=axis,
            speed=ctx["wheel"]["w"], rest=pget(hm, ("rest",), PUMP_REST), lift=abs(lift),
            k=pget(hm, ("k", "golpes", "cycles"), PUMP_K), event="foles")
    ctx["sources"].append(("FORGE_Bellows_Top", sorted({src_key(m, fine) for m in allm}), ["foles"]))
    ctx["log"].append("fole: FORGE_Bellows_Top bombeia (pivo %s, eixo %s, curso %.1f graus, %s por volta da roda)" % (
        tuple(round(x, 2) for x in piv), tuple(round(x, 2) for x in axis), math.degrees(abs(lift)),
        fnum(pget(hm, ("k", "golpes", "cycles"), PUMP_K))))


# ------------------------------------------------------------------ 5. portais: disco (SurfaceGui na montagem) + aro
def build_portals(ctx):
    for key in L.PORTAL_KEYS:
        sw = bpy.data.objects.get("PORTAL_%s_Swirl" % key)
        if sw is None:
            continue
        mw = sw.matrix_world
        cs = [mw @ v.co for v in sw.data.vertices]
        mn, mx = bbox_of(cs)
        c = (mn + mx) / 2
        R = max(mx.x - mn.x, mx.z - mn.z) / 2
        thick = mx.y - mn.y
        pal = PORTAL_PAL.get(key)
        if pal is None:
            col = fm_lib.MATS.get("P_%s_Swirl" % key, ((1, 1, 1),))[0]
            base = [int(255 * min(1, x) ** 0.45) for x in col]
            pal = (base, [min(255, int(x * 0.5 + 128)) for x in base], [min(255, int(x * 0.15 + 220)) for x in base])
        smat = sw.data.materials[0].name if sw.data.materials and sw.data.materials[0] else ""
        textured = smat in TX.SWIRL_TEX or smat in fm_lib.SWIRLS
        # aro Neon da geometria do portal (fm_portals): faces que brilham num anel em volta do disco
        rims = []
        for o in bpy.data.objects:
            if o.type != "MESH" or o is sw or not o.name.startswith("PORTAL_%s" % key):
                continue
            names = [m.name if m else "" for m in o.data.materials]
            tot, hit = {}, {}
            omw = o.matrix_world
            for p in o.data.polygons:
                m = names[p.material_index] if p.material_index < len(names) else ""
                if not m or not is_glow(m) or m in fm_lib.SWIRLS or m in TX.SWIRL_TEX:
                    continue
                tot[m] = tot.get(m, 0) + 1
                q = omw @ p.center
                r = math.hypot(q.x - c.x, q.z - c.z)
                if 0.85 * R <= r <= 1.5 * R and abs(q.y - c.y) <= 2.5:
                    hit[m] = hit.get(m, 0) + 1
            for m, n in hit.items():
                if n >= 4 and n >= 0.5 * tot[m]:
                    rims.append("%s__%s" % (o.name, m))
        ctx["portals"].append(dict(key=key, center=c, R=R, thick=thick, normal=Vector((0, -1, 0)), pal=pal,
                                   idx=L.PORTAL_KEYS.index(key), swirl="PORTAL_%s_Swirl" % key, textured=textured,
                                   spin=PORTAL_SPIN.get(key, 0.9), rims=sorted(rims)))
    ctx["log"].append("portais: %d (disco com textura: %d; aros Neon: %s)" % (
        len(ctx["portals"]), sum(1 for p in ctx["portals"] if p["textured"]),
        ", ".join("%s=%d" % (p["key"], len(p["rims"])) for p in ctx["portals"])))


# ------------------------------------------------------------------ 6. carrinho de mina ocasional (mina -> forja)
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
    i0 = max(0, next(i for i in range(len(s)) if s[i] >= s_rest - 4.0) - 1)
    i1 = min(len(s) - 1, next((i for i in range(len(s)) if s[i] >= s_far + 4.0), len(s) - 1))
    path = [Vector((p.x, p.y, CART_Z)) for p in fine[i0:i1 + 1]]
    base = s[i0]
    p0 = point_at(fine, s, s_rest)
    ta = point_at(fine, s, s_rest + 1.2) - point_at(fine, s, s_rest - 1.2)
    yaw = math.atan2(ta.y, ta.x)
    loc = (p0.x, p0.y, CART_Z)
    rng = random.Random(11)
    body = fm_lib.MB("VFX_Carrinho_src", tmp_coll(), rng)
    fm_parts.mine_cart(body, loc, yaw, None, rng)
    o_body = body.finish()
    ld = fm_lib.MB("VFX_CarrinhoCarga_src", tmp_coll(), rng)
    F = fm_parts.Frame(loc[0], loc[1], loc[2], yaw)
    # carga de uma cor so (1 MeshPart): o azul le como "minerio" de longe, igual aos carrinhos parados
    fm_parts.crystal_cluster(ld, F.p(0, 0, 2.9), 0.75, "Crystal_Blue", rng, 6)
    fm_parts.crystal_cluster(ld, F.p(0.75, 0.45, 2.85), 0.55, "Crystal_Blue", rng, 3)
    o_load = ld.finish()
    # carrinho: variantes da mesma familia viram a majoritaria e detalhes minusculos viram o material dominante
    bmc = world_bm(o_body)
    uvc = bmc.loops.layers.uv.get("UVMap")
    ic = islands(o_body, bmc)
    rm = majority_remap(ic, o_body.data.materials)
    tiny = fold_tiny(ic, o_body.data.materials)
    rm = {m: tiny.get(r, r) for m, r in rm.items()}
    o_body2 = faces_obj("VFX_Carrinho_m", [f for i in ic for f in i.faces], o_body.data.materials, remap=rm, uv=uvc)
    bmc.free()
    add_obj(ctx, "carrinho", o_body2, name="VFX_Carrinho", kind="cart")
    add_obj(ctx, "carga", o_load, name="VFX_CarrinhoCarga", kind="load")
    ctx["cart"] = dict(path=path, rest=s_rest - base, far=s_far - base, weigh=(s_weigh - base) if s_weigh else None,
                       loc=Vector(loc), yaw=yaw)


# ------------------------------------------------------------------ 7. agua: quedas (ilhas de Water_Fall) e correntes
def export_objs():
    out = []
    for g in EXPORT_GROUPS:
        col = bpy.data.collections.get(g)
        if col:
            out.extend(o for o in col.all_objects if o.type == "MESH" and not o.name.startswith(ER.SKIP_PREFIX))
    return out


def fit_beam(top, base, od, pts, lip):
    """curva do Beam da queda (a mesma Bezier do Roblox: P1 = A0 + A0.eixo*c0 com eixo = para fora, P2 = A1 - A1.eixo*c1
    com eixo = para cima) ajustada para correr SEMPRE na frente da malha da agua (>= 0,25 stud), senao o Beam some
    dentro da cortina na metade de baixo. Devolve c0, c1 e os afastamentos o0 (bocal) e o1 (base) ao longo de 'out'."""
    fall = top.z - base.z
    bands = {}
    for p in pts:
        k = int((top.z - p.z) // 1.0)
        bands[k] = max(bands.get(k, -1e9), (p - top).dot(od))

    def front(z):
        return bands.get(int((top.z - z) // 1.0), -1e9)
    kb = int((top.z - base.z - 1.2) // 1.0)
    for k in list(bands):
        if k > kb:
            del bands[k]          # faixas do poco nao contam
    ks = sorted(bands)
    for a, b in zip(ks, ks[1:]):
        for k in range(a + 1, b):
            bands[k] = max(bands[a], bands[b])   # faixa sem vertice (cortina reta): a mais avancada das vizinhas
    c1 = -min(max(fall * 0.3, 2.0), 24.0)
    c0a = min(max(lip * 1.4, 0.8), 6.0)
    up = Vector((0, 0, 1))
    for o1 in (0.35, 0.6, 0.9, 1.3, 1.8, 2.5, 3.2):
        for c0 in [c0a + 0.5 * k for k in range(13)]:
            P = (top + od * 0.35, top + od * (0.35 + c0), base + od * o1 - up * c1, base + od * o1)
            ok = True
            for s in range(1, 40):
                t = s / 40.0
                q = P[0] * (1 - t) ** 3 + P[1] * 3 * t * (1 - t) ** 2 + P[2] * 3 * t * t * (1 - t) + P[3] * t ** 3
                # o primeiro stud (curva do bocal) e a ultima faixa (espuma/escoamento no poco, que avanca na
                # horizontal) ficam por conta do ZOffset e da nevoa
                if base.z + 1.2 < q.z < top.z - 1.0 and (q - top).dot(od) < front(q.z) + 0.25:
                    ok = False
                    break
            if ok:
                return dict(c0=c0, c1=c1, o0=0.35, o1=o1)
    return dict(c0=c0a + 6.0, c1=c1, o0=0.35, o1=3.2)


def waterfall_info(mk):
    """uma queda por ILHA de Water_Fall (todas as cachoeiras exportadas, inclusive as novas) + nome do marcador
    VFX_Waterfall_* mais proximo"""
    wmk = [(n[14:], mk[n].location) for n in sorted(mk) if n.startswith("VFX_Waterfall_")]
    falls = []
    for o in export_objs():
        names = [x.name if x else "" for x in o.data.materials]
        idx = {i for i, n in enumerate(names) if n.startswith("Water_Fall")}
        if not idx:
            continue
        bm = world_bm(o)
        for i in islands(o, bm):
            fs = [f for f in i.faces if f.material_index in idx]
            if len(fs) < 4:
                continue
            pts = [v.co.copy() for f in fs for v in f.verts]
            zt = max(p.z for p in pts)
            zb = min(p.z for p in pts)
            if zt - zb < 3.0:
                continue
            tp = [p for p in pts if p.z >= zt - 0.8]
            bp = [p for p in pts if p.z <= zb + 0.8]
            top = sum(tp, Vector()) / len(tp)
            base = sum(bp, Vector()) / len(bp)
            od = Vector((base.x - top.x, base.y - top.y, 0))
            od = od.normalized() if od.length > 0.2 else Vector((0, -1, 0))
            side = Vector((-od.y, od.x, 0))
            wv = [p.dot(side) for p in bp]
            width = (max(wv) - min(wv)) / 0.7 if len(wv) > 1 else 6.0   # Water_Fall e a faixa central (70%)
            lip = max(0.0, (base - top).dot(od))
            f = dict(top=top, base=base, width=max(3.0, width), out=od, lip=lip, obj=o.name)
            f.update(fit_beam(top, base, od, pts, lip))
            falls.append(f)
        bm.free()
    used = {}
    for f in sorted(falls, key=lambda f: -f["top"].z):
        best = min(wmk, key=lambda m: math.hypot(m[1].x - f["base"].x, m[1].y - f["base"].y)) if wmk else None
        nm = best[0] if best and math.hypot(best[1].x - f["base"].x, best[1].y - f["base"].y) < 30 else "Queda"
        used[nm] = used.get(nm, 0) + 1
        f["name"] = nm if used[nm] == 1 else "%s_%d" % (nm, used[nm])
    return sorted(falls, key=lambda f: f["name"])


def flow_info():
    """superficies de agua corrente (faces de topo de 'Water' no rio e no canal): o rio corre para -Y; o canal do
    ledge corre para o vertedouro (SPILL_X), dos dois lados"""
    flows = []
    for name in ("WATER_Pool_River", "WATER_Canal_Ledge"):
        o = bpy.data.objects.get(name)
        if o is None:
            continue
        names = [x.name if x else "" for x in o.data.materials]
        mw = o.matrix_world
        nm = mw.to_3x3().inverted().transposed()
        for p in o.data.polygons:
            if p.material_index >= len(names) or names[p.material_index] != "Water":
                continue
            n = (nm @ p.normal).normalized()
            if n.z < 0.95 or p.area < 30:
                continue
            cs = [mw @ o.data.vertices[v].co for v in p.vertices]
            mn, mx = bbox_of(cs)
            dx, dy = mx.x - mn.x, mx.y - mn.y
            z = mx.z + 0.08
            if max(dx, dy) < 1.4 * min(dx, dy):
                continue                                   # tanque (quadrado): agua parada
            if dy >= dx:                                   # rio e bica do vertedouro: correm para -Y
                xm = (mn.x + mx.x) / 2
                flows.append(dict(name="Rio" if name == "WATER_Pool_River" else "Vertedouro",
                                  a=Vector((xm, mx.y - 0.5, z)), b=Vector((xm, mn.y + 0.5, z)), width=dx - 0.4,
                                  speed=4.0))             # studs/s
            else:                                          # canal: dos extremos para o vertedouro
                ym = (mn.y + mx.y) / 2
                sx = L.SPILL_X
                if mn.x < sx - 6:
                    flows.append(dict(name="Canal_Oeste", a=Vector((mn.x + 0.5, ym, z)), b=Vector((sx - 3.0, ym, z)),
                                      width=dy - 0.4, speed=2.5))
                if mx.x > sx + 6:
                    flows.append(dict(name="Canal_Leste", a=Vector((mx.x - 0.5, ym, z)), b=Vector((sx + 3.0, ym, z)),
                                      width=dy - 0.4, speed=2.5))
    return flows


# ------------------------------------------------------------------ 8. pontos dos efeitos (forja, vila, cristais)
def marker_box(m):
    """(pos, size Roblox = (x, altura, profundidade y)) de um marcador com prop size (lista x,y,z do Blender)"""
    sz = pget(m, ("size", "tamanho"), None, vec=True)
    if sz is None:
        return m.location.copy(), None
    return m.location.copy(), (abs(sz.x), abs(sz.z), abs(sz.y))


def vent_points(mk):
    """respiros do telhado da forja (fumaca fina): marcadores VFX_Smoke_Vent_* do forge, se houver; senao o topo de
    cada chamine de chapa (FORGE_Roof_Vents*), as venezianas da torre de respiro (FORGE_Vent_Tower) e o lanternim do
    salao (FORGE_Hall_Roof); se o forge juntou esses objetos na ala/salao, os brilhos Forge_Glow_Soft no alto dos
    telhados FORGE_* (cada aglomerado pequeno = um respiro)"""
    out = []
    for n in sorted(mk):
        if n.startswith(("VFX_Smoke_Vent", "VFX_Vent_Smoke", "VFX_Roof_Vent")):
            m = mk[n]
            pos, size = marker_box(m)
            out.append(dict(pos=pos, size=size or (1.4, 0.3, 1.4), rate=float(m.get("rate", 1.3))))
    if out:
        return out
    for o in objs_prefix("FORGE_Roof_Vents"):
        mw = o.matrix_world
        cl = []
        for v in o.data.vertices:
            p = mw @ v.co
            for c in cl:
                if math.hypot(p.x - c[0].x, p.y - c[0].y) < 3.0:
                    c[1].append(p)
                    break
            else:
                cl.append((p, [p]))
        for c0, ps in cl:
            zt = max(p.z for p in ps)
            top = [p for p in ps if p.z >= zt - 1.2]
            cx = sum(p.x for p in top) / len(top)
            cy = sum(p.y for p in top) / len(top)
            out.append(dict(pos=Vector((cx, cy, zt - 0.2)), size=(1.4, 0.3, 1.4), rate=1.4))
    for prefix, rate in (("FORGE_Vent_Tower", 1.2), ("FORGE_Hall_Roof", 1.0)):
        for o in objs_prefix(prefix):
            r = bbox_faces(o, "Forge_Glow_Soft")
            if r:
                mn, mx = r
                out.append(dict(pos=Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, (mn.z + mx.z) / 2)),
                                size=(mx.x - mn.x + 0.8, mx.z - mn.z, mx.y - mn.y + 0.8), rate=rate))
    if out:
        return out
    # objetos juntados: aglomerados de Forge_Glow_Soft no alto dos telhados FORGE_* que sejam o PONTO MAIS ALTO do
    # lugar (respiro/lanternim: so o chapeu por cima, <= 3 studs). Janela de oitao tem telhado em cima: fica de fora.
    zmin = L.FLOOR + 14.0
    cl = []
    verts = []
    for o in objs_prefix("FORGE_"):
        mw = o.matrix_world
        names = [m.name if m else "" for m in o.data.materials]
        gi = names.index("Forge_Glow_Soft") if "Forge_Glow_Soft" in names else -1
        vw = [mw @ v.co for v in o.data.vertices]
        verts.extend(p for p in vw if p.z >= zmin)
        if gi < 0:
            continue
        for p in o.data.polygons:
            if p.material_index != gi:
                continue
            q = mw @ p.center
            if q.z < zmin:
                continue
            for c in cl:
                if math.hypot(q.x - c[0].x, q.y - c[0].y) < 7.0:
                    c[1].append(q)
                    break
            else:
                cl.append((q, [q]))
    for c0, ps in cl:
        mn, mx = bbox_of(ps)
        if max(mx.x - mn.x, mx.y - mn.y) > 12.0:
            continue
        cx, cy = (mn.x + mx.x) / 2, (mn.y + mx.y) / 2
        rr = max(1.5, max(mx.x - mn.x, mx.y - mn.y) / 2 + 0.5)
        above = [p.z for p in verts if math.hypot(p.x - cx, p.y - cy) <= rr]
        ztop = max(above) if above else mx.z
        if ztop > mx.z + 3.0:
            continue
        out.append(dict(pos=Vector((cx, cy, ztop + 0.2)),
                        size=(max(1.4, mx.x - mn.x + 0.6), 0.3, max(1.4, mx.y - mn.y + 0.6)), rate=1.2))
    return sorted(out, key=lambda v: -v["pos"].z)[:5]


def village_smokes(mk):
    """fumaca fina em so SMOKE_VILLAGE chamines da vila: loja + as cabanas mais proximas da praca, alternando os lados"""
    ms = [(n, mk[n]) for n in sorted(mk) if n.startswith("VFX_Smoke_")]
    px, py = L.PLAZA_C
    shop = [x for x in ms if x[0] == "VFX_Smoke_Shop"]
    cab = sorted((x for x in ms if x[0] != "VFX_Smoke_Shop"),
                 key=lambda x: math.hypot(x[1].location.x - px, x[1].location.y - py))
    west = [x for x in cab if x[1].location.x < px]
    east = [x for x in cab if x[1].location.x >= px]
    pick = list(shop)
    while len(pick) < SMOKE_VILLAGE and (west or east):
        for side in (west, east):
            if side and len(pick) < SMOKE_VILLAGE:
                pick.append(side.pop(0))
    return [dict(marker=n, pos=m.location.copy(), rate=float(m.get("rate", 2))) for n, m in pick]


def fx_points(ctx, mk):
    fx = {}
    # lareira: marcador do forge (centro do leito de brasas; size = largura x profundidade x ALTURA das chamas)
    # > bbox das chamas Fire_Glow_Core + Fire_Glow_Mid > marcador sem size. O emissor e uma lamina no leito (as chamas
    # nascem nas brasas e sobem); a altura vira escala de velocidade/tamanho no Luau.
    m = mk.get("VFX_Hearth_Fire")
    pos, size = marker_box(m) if m else (None, None)
    height = None
    if size is not None:
        height = size[1]
        size = (max(1.0, size[0] * 0.85), 0.4, max(1.0, size[2] * 0.7))
    else:
        hb = bbox_prefix("FORGE_Hearth", {"Fire_Glow_Core", "Fire_Glow_Mid"})
        core = bbox_prefix("FORGE_Hearth", {"Fire_Glow_Core"})
        if hb:
            mn, mx = hb
            z0 = (core[0].z if core else mn.z) + 0.35
            pos = Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, z0))
            size = (max(1.0, (mx.x - mn.x) * 0.8), 0.4, max(1.0, (mx.y - mn.y) * 0.7))
            height = max(2.5, mx.z - z0 + 1.5)
        elif m:
            size = (8.0, 0.4, 3.0)
    if pos is not None:
        fx["hearth"] = dict(pos=pos, size=size, height=height or 3.5)
    # torre-chamine: marcador (segue CHIMNEY_TOP), conferido com o topo real da torre
    cm = mk.get("VFX_Chimney_Smoke_Emitter")
    tower = bpy.data.objects.get("FORGE_Chimney_Tower")
    ttop = None
    rad = L.CHIMNEY_R - 2.4
    if tower:
        mw = tower.matrix_world
        cx, cy = L.CHIMNEY
        # a coroa pode abrir alem do raio do fuste (coroa nova: r ~13-14 com CHIMNEY_R 10): 2x o raio pega o topo
        # real sem pegar os canos que o forge junta no mesmo objeto (mais baixos)
        pts = [mw @ v.co for v in tower.data.vertices]
        pts = [p for p in pts if math.hypot(p.x - cx, p.y - cy) <= 2.0 * L.CHIMNEY_R]
        ttop = max(p.z for p in pts) if pts else None
        ring = bbox_faces(tower, "Forge_Emissive", zmin=(ttop - 4) if ttop else -1e9)
        if ring:
            rad = max(3.0, (ring[1].x - ring[0].x) / 2 - 1.2)
        elif ttop is not None:
            rtop = max(math.hypot(p.x - cx, p.y - cy) for p in pts if p.z >= ttop - 1.0)
            rad = max(3.0, min(L.CHIMNEY_R, rtop) - 2.4)
    if cm is not None:
        p = cm.location.copy()
        if ttop is not None and abs(p.z - ttop) > 4.0:
            ctx["log"].append("AVISO: VFX_Chimney_Smoke_Emitter em z%.1f, topo da torre em z%.1f -> usando o topo" % (p.z, ttop))
            p.z = ttop
        fx["chimney"] = dict(pos=p + Vector((0, 0, 0.5)), radius=rad)
    elif ttop is not None:
        fx["chimney"] = dict(pos=Vector((L.CHIMNEY[0], L.CHIMNEY[1], ttop + 0.5)), radius=rad)
    # bigorna do Ignis: marcador do forge > brasa Ember_Glow da FORGE_Anvil > marcador antigo
    if "VFX_Anvil_Sparks" in mk:
        fx["anvil_ignis"] = dict(pos=mk["VFX_Anvil_Sparks"].location.copy())
    else:
        ab = bbox_prefix("FORGE_Anvil", {"Ember_Glow", "Metal_Heated"})
        fx["anvil_ignis"] = dict(pos=Vector(((ab[0].x + ab[1].x) / 2, (ab[0].y + ab[1].y) / 2, ab[1].z + 0.1)) if ab else
                                 mk["VFX_Forge_Sparks"].location - Vector((0, 0, 2.2)))
    # tempera: marcador do forge > agua do balde/cocho na fachada da forja
    if "VFX_Quench_Steam" in mk:
        qp, qs = marker_box(mk["VFX_Quench_Steam"])
        fx["quench"] = dict(pos=qp, size=qs or (1.4, 0.2, 1.4))
    else:
        # a ilha de agua (balde/cocho) mais perto da bigorna do Ignis, nao a uniao de todas
        best = None
        for o in objs_prefix("FORGE_"):
            names = [m.name if m else "" for m in o.data.materials]
            if "Water" not in names:
                continue
            bm = world_bm(o)
            wi = names.index("Water")
            for i in islands(o, bm):
                pts = [v.co.copy() for f in i.faces if f.material_index == wi for v in f.verts]
                if not pts:
                    continue
                mn, mx = bbox_of(pts)
                d = math.hypot((mn.x + mx.x) / 2 - L.ANVIL[0], (mn.y + mx.y) / 2 - L.ANVIL[1])
                if best is None or d < best[0]:
                    best = (d, mn, mx)
            bm.free()
        if best:
            _, mn, mx = best
            fx["quench"] = dict(pos=Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mx.z + 0.1)),
                                size=(max(0.6, mx.x - mn.x), 0.2, max(0.6, mx.y - mn.y)))
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
    ctx["vents"] = vent_points(mk)
    ctx["smokes"] = village_smokes(mk)
    ctx["waterfalls"] = waterfall_info(mk)
    ctx["flows"] = flow_info()
    ctx["log"].append("forja: lareira %s, chamine z%.1f r%.1f, bigorna %s, tempera %s, respiros %d" % (
        "ok" if "hearth" in fx else "-", fx["chimney"]["pos"].z if "chimney" in fx else -1,
        fx["chimney"]["radius"] if "chimney" in fx else 0, tuple(round(x, 1) for x in fx["anvil_ignis"]["pos"]),
        "ok" if "quench" in fx else "-", len(ctx["vents"])))
    ctx["log"].append("vila: fumaca em %s" % ", ".join(s["marker"][10:] for s in ctx["smokes"]))
    ctx["log"].append("cachoeiras: " + ", ".join("%s(l=%.1f h=%.1f)" % (w["name"], w["width"], w["top"].z - w["base"].z)
                                                   for w in ctx["waterfalls"]))
    ctx["log"].append("correntes: " + ", ".join("%s(%.0f studs)" % (f["name"], (f["b"] - f["a"]).length) for f in ctx["flows"]))


# ------------------------------------------------------------------ coleta geral
def collect():
    mk = markers()
    ctx = dict(groups={}, sources=[], portals=[], log=[], mk=mk)
    build_wheel(ctx, mk)
    build_wheelhouse(ctx, mk)
    build_wall_gears(ctx)
    build_bellows(ctx, mk)
    build_portals(ctx)
    build_cart(ctx, mk)
    fx_points(ctx, mk)
    ctx["log"].append("pecas moveis: %d caixas com chanfro minusculo viraram caixas limpas" % ctx.get("unbevel", 0))
    refs = []
    for n in ("VFX_Waterwheel_Rotate", "NPC_Ignis", "RAIL_Start_Mine", "PORTAL_Naruto"):
        if n in mk:
            o = mk[n]
            R3 = o.matrix_world.to_3x3().normalized()
            refs.append(dict(kind="marker", name=n, pos=rbx(o.location), x=rbx(R3.col[0]), y=rbx(R3.col[1])))
    ctx["refs"] = refs
    ctx["exact"] = sorted({m.name for s in ctx["sources"] for m in bpy.data.objects[s[0]].data.materials
                           if m and is_glow(m.name)})
    return ctx


# ------------------------------------------------------------------ exportacao (FBX + dados)
def join_meshes(name, meshes):
    bm = bmesh.new()
    for me in meshes:
        bm.from_mesh(me)
    nm = bpy.data.meshes.new(name)
    bm.to_mesh(nm)
    bm.free()
    return nm


def export_meshes(ctx):
    """cada grupo: junta os objetos-fonte, divide por material (mesmo split/UV do export_roblox), 1 malha por
    material com o material de exportacao (textura embutida). Devolve os movers."""
    movers = []
    made = []
    for gname, g in ctx["groups"].items():
        splits = []
        for ob in g.get("objs", []):
            if ob is None:
                continue
            for _n, nm, mname in ER.split_object(ob):
                splits.append((nm, mname))
        # pecas que se movem: variantes da mesma familia viram a variante com mais tris NO GRUPO (o eixo Wood_Dark da
        # casa e a roda Wood_Dark_B saem numa MeshPart so); a copia fixa guarda a variante exata
        remap = {}
        if g["kind"] != "fixed":
            cnt = {}
            for nm, mname in splits:
                cnt[mname] = cnt.get(mname, 0) + len(nm.polygons)
            best = {}
            for m, n in cnt.items():
                fam = fm_lib.family_of(m)
                if fam not in best or n > cnt[best[fam]]:
                    best[fam] = m
            remap = {m: best[fm_lib.family_of(m)] for m in cnt}
        per = {}
        for nm, mname in splits:
            per.setdefault(remap.get(mname, mname), []).append(nm)
        for mname, mes in sorted(per.items()):
            name = "%s__%s" % (g["name"], mname)
            nm = mes[0] if len(mes) == 1 else join_meshes(name, mes)
            for me in mes:
                if me is not nm:
                    bpy.data.meshes.remove(me)
            nm.name = name
            if not nm.vertices:
                continue
            mn, mx = bbox_of([v.co for v in nm.vertices])
            c = (mn + mx) / 2
            sz = mx - mn
            nm.transform(Matrix.Translation(-c))
            nm.materials.clear()
            em = ER.export_material(mname)
            if em is not None:
                nm.materials.append(em)
            o = bpy.data.objects.new(name, nm)
            o.location = c
            tmp_coll().objects.link(o)
            made.append(o)
            movers.append(dict(name=name, group=gname, home=rbx(c), size=(sz.x, sz.z, sz.y), tris=len(nm.polygons),
                               mat=mname))
    per = {}
    for m in movers:
        per[m["group"]] = per.get(m["group"], [0, 0])
        per[m["group"]][0] += 1
        per[m["group"]][1] += m["tris"]
    ctx["log"].append("grupos (malhas/tris): " + ", ".join("%s=%d/%d" % (k, v[0], v[1]) for k, v in sorted(per.items())))
    # orcamento (o mesmo do export_roblox, quando ele declara): FM_BUDGET=strict (padrao) falha sem gravar nada
    bud = getattr(ER, "BUDGET", {}) or {}
    max_tris, max_parts = int(bud.get("vfx_tris", META_TRIS)), int(bud.get("vfx_meshes", META_PARTS))
    tris = sum(m["tris"] for m in movers)
    ok = tris <= max_tris and len(made) <= max_parts
    ctx["log"].append("META %s: %d/%d tris, %d/%d MeshParts" % ("OK" if ok else "ESTOURADA", tris, max_tris,
                                                               len(made), max_parts))
    if not ok and os.environ.get("FM_BUDGET", "strict").lower() != "warn":
        for line in ctx["log"]:
            print("[export_vfx]", line)
        print("EXPORT VFX FALHOU: LOBBY_VFX_MOVING passou do orcamento (%d/%d tris, %d/%d MeshParts). Nada foi gravado. "
              "FM_BUDGET=warn grava mesmo assim." % (tris, max_tris, len(made), max_parts))
        sys.stdout.flush()
        os._exit(3)
    # nome novo a cada passe (ID6 = EXPORT_ID, como os LOBBY_<colecao>_<ID6>.fbx): o 3D Importer nao reusa cache
    eid = ctx.get("export_id")
    fn = "LOBBY_VFX_MOVING_%s.fbx" % eid[:6] if eid else "LOBBY_VFX_MOVING.fbx"
    for old in glob.glob(os.path.join(OUT, "LOBBY_VFX_MOVING*.fbx")):
        os.remove(old)
    path = os.path.join(OUT, fn)
    ctx["fbx"] = fn
    bpy.ops.object.select_all(action="DESELECT")
    for o in made:
        o.select_set(True)
    if made:
        bpy.context.view_layer.objects.active = made[0]
        bpy.ops.export_scene.fbx(filepath=path, use_selection=True, axis_forward="-Z", axis_up="Y",
                                 apply_scale_options="FBX_SCALE_ALL", mesh_smooth_type="FACE", path_mode="COPY",
                                 embed_textures=True, add_leaf_bones=False, bake_anim=False,
                                 use_mesh_modifiers=True, object_types={"MESH"})
        nmat = len({s.material_slots[0].material.name for s in made if s.material_slots and s.material_slots[0].material})
        ctx["log"].append("FBX %s: %d malhas, %d tris, %d materiais de exportacao, %d KB" % (
            fn, len(made), tris, nmat, os.path.getsize(path) // 1024))
    return movers


def mat_table(movers):
    """cor = a mesma cor calibrada do montar (ER.rbx_color); x = textura de detalhe (so usada sem peca-modelo)"""
    rows = {}
    for m in movers:
        mname = m["mat"]
        if mname in rows:
            continue
        mat = bpy.data.materials.get(mname)
        rm, tr, sh = ER.rbx_rule(mname)
        rows[mname] = (ER.rbx_color(mname, mat), rm, tr, ER.tex_of(mname))
    return rows


def read_export_id():
    """EXPORT_ID do passe estatico (export_roblox): variavel do modulo (mesmo processo, export_all) ou o JSON"""
    for k in ("EXPORT_ID", "export_id", "LAST_EXPORT_ID"):
        v = getattr(ER, k, None)
        if isinstance(v, str) and v:
            return v
    p = os.path.join(OUT, "lobby_data.json")
    if os.path.exists(p):
        try:
            d = json.load(open(p, encoding="utf-8"))
        except (ValueError, OSError):
            return None
        for k in ("export_id", "EXPORT_ID", "exportId"):
            if isinstance(d.get(k), str) and d[k]:
                return d[k]
        meta = d.get("meta") or {}
        for k in ("export_id", "EXPORT_ID"):
            if isinstance(meta.get(k), str) and meta[k]:
                return meta[k]
    return None


def lua_data_setup(ctx, movers):
    Lg = []
    A = Lg.append
    A("local DATA = {}")
    A("DATA.version = %s" % lstr(VERSION))
    A("DATA.exportId = %s  -- EXPORT_ID do passe estatico (montar_lobby_forja.lua grava em root:GetAttribute('EXPORT_ID'))"
      % (lstr(ctx["export_id"]) if ctx.get("export_id") else "nil"))
    A("DATA.fbx = %s  -- FBX de movimento DESTE passe (3D Importer)" % lstr(ctx.get("fbx") or "LOBBY_VFX_MOVING.fbx"))
    A("-- referencias para achar a transformacao do lobby (posicao canonica = export_roblox, Roblox = (x, z, -y))")
    A("DATA.refs = {")
    for r in ctx["refs"]:
        A("  {name = %s, pos = %s, x = %s, y = %s}," % (lstr(r["name"]), lv3(r["pos"]), lv3(r["x"]), lv3(r["y"])))
    A("}")
    A("-- pecas do LOBBY_VFX_MOVING.fbx: {nome, grupo, centro do bbox (canonico), tamanho (Roblox)}")
    A("DATA.movers = {")
    for m in movers:
        A("  {%s, %s, %s, %s}," % (lstr(m["name"]), lstr(m["group"]), lv3(m["home"]), lv3(m["size"])))
    A("}")
    A("-- malhas estaticas trocadas: objeto + familias de material, da variante (Wood_Dark: pega Wood_Dark_B) quando o")
    A("-- export estatico nao funde materiais nesse objeto, senao GROSSAS (Wood, Metal); materiais que brilham")
    A("-- (DATA.exact) contam pelo nome exato. So troca se TODOS os grupos existirem (tudo ou nada).")
    A("DATA.sources = {")
    for obj, fams, groups in ctx["sources"]:
        A("  {name = %s, fams = {%s}, groups = {%s}}," % (lstr(obj), ", ".join(lstr(f) for f in fams),
                                                        ", ".join(lstr(g) for g in groups)))
    A("}")
    A("DATA.exact = {%s}" % ", ".join("[%s] = true" % lstr(m) for m in ctx["exact"]))
    A("DATA.groups = {")
    for gname, g in ctx["groups"].items():
        f = ["kind = %s" % lstr(g["kind"])]
        if g.get("assembly"):
            f.append("assembly = %s" % lstr(g["assembly"]))
        if g["kind"] in ("spin", "hammer", "pump"):
            f.append("pivot = %s" % lv3(rbx(g["pivot"])))
            f.append("axis = %s" % lv3(rbx(g["axis"])))
            f.append("speed = %s" % fnum(g["speed"]))
        if g["kind"] == "hammer":
            f.append("camPhase = %s, cams = %d, rest = %s, lift = %s, event = %s" % (
                fnum(g["cam_phase"]), g["cams"], fnum(g["rest"]), fnum(g["lift"]), lstr(g["event"])))
        if g["kind"] == "pump":
            f.append("rest = %s, lift = %s, k = %s, event = %s" % (fnum(g["rest"]), fnum(g["lift"]), fnum(g["k"]),
                                                                  lstr(g["event"])))
        A("  [%s] = {%s}," % (lstr(gname), ", ".join(f)))
    A("}")
    A("-- cor calibrada do montar (mesma do export_roblox), Material, transparencia, textura de detalhe")
    A("DATA.mats = {")
    for k, (c, m, t, x) in sorted(mat_table(movers).items()):
        A("  [%s] = {c = %s, m = Enum.Material.%s, t = %s, x = %s}," % (lstr(k), lc3(c), m, fnum(t),
                                                                       lstr(x) if x else "nil"))
    A("}")
    A("DATA.texRules = {%s}" % ", ".join("{%s, %s}" % (lstr(p), lstr(k)) for p, k in fm_lib.TEX_RULES))
    A("DATA.portals = {")
    for p in ctx["portals"]:
        A("  {key = %s, idx = %d, center = %s, normal = %s, radius = %s, thick = %s, swirl = %s, spin = %s," % (
            lstr(p["key"]), p["idx"], lv3(rbx(p["center"])), lv3(rbx(p["normal"])), fnum(p["R"]), fnum(p["thick"]),
            lstr(p["swirl"]), fnum(p["spin"])))
        A("   rims = {%s}, disc = %s, arm = %s, core3 = %s}," % (", ".join(lstr(r) for r in p["rims"]),
                                                              lc3(p["pal"][0]), lc3(p["pal"][1]), lc3(p["pal"][2])))
    A("}")
    A("DATA.portalInner = %s" % fnum(PORTAL_INNER))
    fx = ctx["fx"]
    A("DATA.fx = {")
    for k in sorted(fx):
        e = fx[k]
        f = ["pos = %s" % lv3(rbx(e["pos"]))]
        if e.get("size"):
            f.append("size = %s" % lv3(e["size"]))       # (largura x, altura, profundidade y) = Size do Roblox
        if "radius" in e:
            f.append("radius = %s" % fnum(e["radius"]))
        if "height" in e:
            f.append("height = %s" % fnum(e["height"]))
        A("  %s = {%s}," % (k, ", ".join(f)))
    A("}")
    A("DATA.vents = {")
    for v in ctx["vents"]:
        A("  {pos = %s, size = %s, rate = %s}," % (lv3(rbx(v["pos"])), lv3(v["size"]), fnum(v["rate"])))
    A("}")
    A("DATA.smokes = {")
    for s in ctx["smokes"]:
        A("  {marker = %s, pos = %s, rate = %s}," % (lstr(s["marker"]), lv3(rbx(s["pos"])), fnum(s["rate"])))
    A("}")
    A("DATA.wheelWidth = 3.4")
    A("DATA.waterfalls = {")
    for w in ctx["waterfalls"]:
        A("  {name = %s, top = %s, base = %s, width = %s, out = %s, lip = %s, c0 = %s, c1 = %s, o0 = %s, o1 = %s}," % (
            lstr(w["name"]), lv3(rbx(w["top"])), lv3(rbx(w["base"])), fnum(w["width"]), lv3(rbx(w["out"])),
            fnum(w["lip"]), fnum(w["c0"]), fnum(w["c1"]), fnum(w["o0"]), fnum(w["o1"])))
    A("}")
    A("DATA.flows = {")
    for f in ctx["flows"]:
        A("  {name = %s, a = %s, b = %s, width = %s, speed = %s}," % (
            lstr(f["name"]), lv3(rbx(f["a"])), lv3(rbx(f["b"])), fnum(f["width"]), fnum(f["speed"])))
    A("}")
    c = ctx["cart"]
    A("DATA.cartRest = CFrame.new(%s) * CFrame.Angles(0, %s, 0)" % (lv3(rbx(c["loc"]))[12:-1], fnum(c["yaw"])))
    return "\n".join(Lg)


def lua_data_client(ctx):
    c = ctx["cart"]
    Lg = []
    A = Lg.append
    A("local DATA = {}")
    A("DATA.version = %s" % lstr(VERSION))
    A("DATA.exportId = %s" % (lstr(ctx["export_id"]) if ctx.get("export_id") else "nil"))
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
    A("DATA.ignis = {cycle = 4.4, hits = {{0, 0.7}, {0.75, 0.7}, {1.5, 1.35}}, quenchEvery = 3, pos = %s}" % lv3(
        rbx(ctx["fx"]["anvil_ignis"]["pos"])))
    w = ctx["wheel"]
    A("-- pas da roda: a pa k esta no angulo k*step - w*t (plano da roda); entra na agua em aIn e sai em aOut")
    A("DATA.wheel = {speed = %s, step = %s, aIn = %s, aOut = %s, pos = %s}" % (
        fnum(w["w"]), fnum(2 * math.pi / w["paddles"]), fnum(w["a_in"]), fnum(w["a_out"]), lv3(rbx(w["center"]))))
    A("DATA.portals = {")
    for p in ctx["portals"]:
        A("  {key = %s, idx = %d, center = %s}," % (lstr(p["key"]), p["idx"], lv3(rbx(p["center"]))))
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


def main(export_id=None):
    os.makedirs(OUT, exist_ok=True)
    TX.ensure()
    ctx = collect()
    ctx["export_id"] = export_id or read_export_id()
    movers = export_meshes(ctx)
    write_lua(ctx, movers)
    cleanup()
    for line in ctx["log"]:
        print("[export_vfx]", line)
    print("[export_vfx] EXPORT_ID %s" % (ctx["export_id"] or "(nenhum: o montar ainda nao grava; conferencia desligada)"))
    print("EXPORT VFX OK movers=%d portais=%d cachoeiras=%d correntes=%d respiros=%d -> %s" % (
        len(movers), len(ctx["portals"]), len(ctx["waterfalls"]), len(ctx["flows"]), len(ctx["vents"]),
        os.path.join(OUT, ctx.get("fbx") or "")))
    return ctx


# =====================================================================================================================
# LUAU: MONTAGEM
# =====================================================================================================================
SETUP_LUA = r'''--[[
vfx_lobby_forja.lua   (gerado por export_vfx.py - @VERSION@ - nao editar a mao: ajuste export_vfx.py e reexporte)
VFX e MOVIMENTO do Lobby Vila-Forja - MONTAGEM

ORDEM (tudo do MESMO passe do export_all.py: o EXPORT_ID confere e este script ABORTA se nao bater)
  1. importar LOBBY_*.fbx e rodar montar_lobby_forja.lua (colisoes, marcadores, luzes, cores, EXPORT_ID, RICO);
  2. importar export/LOBBY_VFX_MOVING_<ID6>.fbx (DATA.fbx, o do MESMO passe) com o 3D Importer (pode cair em
     qualquer lugar do workspace: este script acha as pecas pelo nome e as coloca na posicao certa, mesmo com o lobby
     deslocado ou girado);
  3. rodar ESTE script na Command Bar (ou como Script em ServerScriptService) e salvar o place.
     Pode rodar de novo (idempotente). Nao ha nenhum loop por frame no servidor.
  E SEMPRE: vfx_lobby_forja_client.lua como LocalScript em StarterPlayer > StarterPlayerScripts.

O QUE ESTE SCRIPT CRIA
  <lobby>.VFX              pecas invisiveis com ParticleEmitters, Beams e o SurfaceGui das espirais: fogo da lareira,
                           pluma da torre (nucleo escuro, corpo, topo claro, brasas, faiscas), fumaca fina dos
                           respiros e de 4 chamines da vila, faiscas da bigorna, vapor da tempera, respingos da roda,
                           cachoeiras (Beam com estrias + nevoa/espuma), ondulacao do rio e do canal, portais
                           (espiral em SurfaceGui, particulas sugadas, pulso), brilhos dos cristais
  <lobby>.VFX_MOVING       modelos (streaming atomico) com as pecas moveis do LOBBY_VFX_MOVING.fbx
  ReplicatedStorage.LOBBY_FORJA_VFX       config (VFX_RootCF), molde do carrinho (MineCart), BindableEvent Evento
  ServerStorage.LOBBY_FORJA_VFX_ORIGINAIS malhas estaticas trocadas pelas versoes separadas (para desfazer, devolva)
  Tags: FORJA_Spin, FORJA_Hammer, FORJA_Pump, FORJA_Swirl, FORJA_Pulse, FORJA_Flicker, FORJA_Burst, FORJA_Emitter

GANCHOS
  Rig real do Ignis: tag "FORJA_Ignis" no Model; KeyframeMarker "Golpe" (parametro opcional = forca) dispara as
  faiscas. Sem rig, o cliente usa um ritmo interno (toc-toc-TOC) e a tempera chia a cada 3 ciclos.
  Qualquer LocalScript: ReplicatedStorage.LOBBY_FORJA_VFX.Evento:Fire("ignis", 1.5)
  eventos: "ignis", "tempera", "martinete", "foles", "roda:entra", "roda:sai", "portal:<Nome>", "carga"
]]

local CollectionService = game:GetService("CollectionService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerStorage = game:GetService("ServerStorage")
local RunService = game:GetService("RunService")

local ROOT_NAMES = {"LOBBY_FORJA", "LOBBY_FORJA_PREVIEW"} -- o primeiro que existir no workspace
-- texturas de agua que o jogo ja usa (StylizedWater da Vila da Folha / Vale Capsule); troque aqui se quiser outras
local TEX_AGUA = {
  linhas = "rbxassetid://123614169905314",     -- rede de linhas claras: ondulacao do rio e do canal
  cachoeira = "rbxassetid://108982815970120",  -- estrias: quedas
}
-- sentido das texturas dos Beams: 1 = corre de Attachment0 (bocal/montante) para Attachment1 (base/jusante), a mesma
-- convencao das cachoeiras do StylizedWater; se a agua aparecer SUBINDO no Studio, troque para -1
local SENTIDO_AGUA = 1
-- espirais: vazio = usa a textura que o montar aplicou no disco PORTAL_<Nome>_Swirl (TextureID ou SurfaceAppearance)
local SWIRL_IMG = {Naruto = "", DragonBall = "", ShadowGarden = "", DemonSlayer = "", OnePiece = "", OnePunchMan = ""}

if RunService:IsRunning() and not RunService:IsServer() then
  warn("[VFX Forja] vfx_lobby_forja.lua e a MONTAGEM (Command Bar ou Script de servidor), nao um LocalScript")
  return
end

--@DATA@

local function log(fmt, ...) print("[VFX Forja] " .. string.format(fmt, ...)) end
local function warnf(fmt, ...) warn("[VFX Forja] " .. string.format(fmt, ...)) end

-- ---------------------------------------------------------------- raiz, passe de exportacao e transformacao
local root
for _, n in ipairs(ROOT_NAMES) do
  root = workspace:FindFirstChild(n)
  if root then break end
end
if not root then
  warnf("lobby nao encontrado no workspace (%s)", table.concat(ROOT_NAMES, ", "))
  return
end
local rootId = root:GetAttribute("EXPORT_ID")
if rootId ~= DATA.exportId then
  warnf("EXPORT_ID nao confere: lobby = %s, VFX = %s. O estatico (LOBBY_*.fbx + montar_lobby_forja.lua) e o VFX "
    .. "(LOBBY_VFX_MOVING.fbx + este script) tem que sair do MESMO export_all.py. Nada foi alterado.",
    tostring(rootId), tostring(DATA.exportId))
  return
end
if rootId == nil then log("montar sem EXPORT_ID: conferencia de passe desligada (reexporte com o export_all.py)") end
local RICO = root:GetAttribute("RICO") == true

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
-- nome sem o sufixo que o 3D Importer poe em nomes repetidos ('.001', ' (1)')
local function norm(n) return (string.gsub(string.gsub(n, "%.%d+$", ""), " %(%d+%)$", "")) end
-- material do nome "<objeto>__<material>[_k][_gX_Y]" (fatias _k e celulas _gX_Y do export estatico)
local function matOf(name)
  local s = string.match(norm(name), "__(.+)$")
  if not s then return nil end
  s = string.gsub(s, "_g%-?%d+_%-?%d+$", "")
  s = string.gsub(s, "_%d+$", "")
  s = string.gsub(s, "_g%-?%d+_%-?%d+$", "")
  return s
end
local function objOf(name) return string.match(norm(name), "^(.-)__") end
local function coarse(m)
  if not m then return nil end
  if DATA.exact[m] then return m end
  return string.match(m, "^([^_]+)") or m
end
local function famKey(m) return m and (string.match(m, "^(.-)_[A-Z]$") or m) end
local function texKey(m)
  if not m then return nil end
  for _, r in ipairs(DATA.texRules) do
    if string.sub(m, 1, #r[1]) == r[1] then return r[2] end
  end
  return nil
end
local function lerMapa(d)
  local ok, v = pcall(function() return d.TextureID end)
  if ok and v and v ~= "" then return v end
  local sa = d:FindFirstChildOfClass("SurfaceAppearance")
  if sa then
    local ok2, v2 = pcall(function() return sa.ColorMap end)
    if ok2 and v2 and v2 ~= "" then return v2 end
    local ok3, v3 = pcall(function() return sa.ColorMapContent.Uri end)
    if ok3 and v3 and v3 ~= "" then return v3 end
  end
  return nil
end

-- ---------------------------------------------------------------- pecas moveis (LOBBY_VFX_MOVING.fbx)
local wanted, ours = {}, {}
for _, m in ipairs(DATA.movers) do
  wanted[m[1]] = {group = m[2], home = m[3], size = m[4]}
  ours[objOf(m[1])] = true
end
-- so mexe em MeshParts deste exportador (grupos atuais + nomes da versao vfx-forja-1)
local LEGACY = {"VFX_RodaDagua", "VFX_CasaRoda", "VFX_Espiral_", "VFX_Carrinho"}
local function isOurs(name)
  local o = objOf(name)
  if not o then return false end
  if ours[o] then return true end
  for _, pre in ipairs(LEGACY) do
    if string.sub(o, 1, #pre) == pre then return true end
  end
  return false
end
local function sorted3(v)
  local t = {v.X, v.Y, v.Z}
  table.sort(t)
  return t
end
local function sizeErr(a, b)
  local s, w = sorted3(a), sorted3(b)
  return math.abs(s[1] - w[1]) + math.abs(s[2] - w[2]) + math.abs(s[3] - w[3]), 0.06 * (w[1] + w[2] + w[3]) + 0.3
end
local found, cands = {}, {}
-- nome exato E tamanho do bbox (mesmo nome com outro tamanho = peca de outro passe -> vira candidata)
local function scan(container, parked)
  for _, d in ipairs(container:GetDescendants()) do
    if d:IsA("MeshPart") and string.sub(d.Name, 1, 4) == "VFX_" and isOurs(d.Name) then
      local w = wanted[d.Name]
      local e, tol
      if w then e, tol = sizeErr(d.Size, w.size) end
      if w and e <= tol then
        if not found[d.Name] then
          found[d.Name] = d
        elseif found[d.Name] ~= d and not parked then
          d.Parent = ORIG -- duplicata (FBX importado duas vezes)
        end
      elseif not parked then
        table.insert(cands, d)
      end
    end
  end
end
scan(workspace)
scan(CFG)
scan(ORIG, true) -- pecas guardadas por uma montagem anterior (FBX incompleto na vez passada)
-- nome exato nao achado: mesmo objeto + mesma familia de material + mesmo tamanho (variante renomeada)
local nRen = 0
for _, m in ipairs(DATA.movers) do
  if not found[m[1]] then
    local o, f = objOf(m[1]), coarse(matOf(m[1]))
    local best, be, tol
    for i, d in ipairs(cands) do
      if objOf(d.Name) == o and coarse(matOf(d.Name)) == f then
        local e, t = sizeErr(d.Size, m[4])
        if not be or e < be then best, be, tol = i, e, t end
      end
    end
    if best and be <= tol then
      local d = table.remove(cands, best)
      d.Name = m[1]
      found[m[1]] = d
      nRen += 1
    end
  end
end
local nStale = 0
for _, d in ipairs(cands) do
  d.Parent = ORIG -- peca VFX de outro passe (nome/tamanho nao batem): fora da cena
  nStale += 1
end
if nRen > 0 then log("%d pecas moveis casadas por objeto + familia + tamanho (variante renomeada)", nRen) end
if nStale > 0 then warnf("%d MeshParts VFX_ de outro passe guardadas em ServerStorage (importe %s)", nStale, DATA.fbx) end

local groupCount, groupTotal = {}, {}
for _, m in ipairs(DATA.movers) do
  groupTotal[m[2]] = (groupTotal[m[2]] or 0) + 1
  if found[m[1]] then groupCount[m[2]] = (groupCount[m[2]] or 0) + 1 end
end
local function groupOk(g) return groupTotal[g] ~= nil and groupCount[g] == groupTotal[g] end

-- aparencia: copia de uma peca estatica com o mesmo material (cor, Material, textura: identica ao que o montar
-- aplicou, inclusive no modo RICO); sem peca-modelo, usa DATA.mats + a textura de uma peca da mesma familia
local looks, looksFam, texParts = {}, {}, {}
local function addLook(d)
  if not d:IsA("MeshPart") or wanted[d.Name] or string.sub(d.Name, 1, 4) == "VFX_" then return end
  local m = matOf(d.Name)
  if not m then return end
  looks[m] = looks[m] or d
  local fk = famKey(m)
  looksFam[fk] = looksFam[fk] or d
  local tk = texKey(m)
  if tk and not texParts[tk] and d:FindFirstChildOfClass("SurfaceAppearance") then texParts[tk] = d end
end
for _, d in ipairs(root:GetDescendants()) do addLook(d) end
for _, d in ipairs(ORIG:GetDescendants()) do addLook(d) end
local function applyLook(p, mat)
  p.Anchored = true
  p.CanCollide = false
  p.CanTouch = false
  p.CanQuery = false
  for _, c in ipairs(p:GetChildren()) do
    if c:IsA("SurfaceAppearance") then c:Destroy() end
  end
  local e = DATA.mats[mat]
  local src = looks[mat] or looksFam[famKey(mat)]
  if src then
    p.Color = src.Color
    p.Material = src.Material
    p.MaterialVariant = src.MaterialVariant
    p.Transparency = src.Transparency
    p.Reflectance = src.Reflectance
    p.CastShadow = src.CastShadow
    local sa = src:FindFirstChildOfClass("SurfaceAppearance")
    if sa then sa:Clone().Parent = p end
    p.TextureID = src.TextureID
  elseif e then
    p.Color = e.c
    p.Material = e.m
    p.Transparency = e.t
    local tp = RICO and e.x and texParts[e.x]
    local sa = tp and tp:FindFirstChildOfClass("SurfaceAppearance")
    if sa then sa:Clone().Parent = p end
    p.TextureID = ""
  else
    p.TextureID = ""
  end
end

-- fontes: esconde as malhas estaticas (objeto + familia) SO se TODAS as pecas de maquina existirem (tudo ou nada:
-- a malha FIXA e compartilhada; meia troca deixaria peca duplicada ou buraco)
local machineGroups, machineOk, missing = {}, true, {}
for _, s in ipairs(DATA.sources) do
  for _, g in ipairs(s.groups) do
    machineGroups[g] = true
    if groupTotal[g] and not groupOk(g) then
      machineOk = false
      missing[g] = groupTotal[g] - (groupCount[g] or 0)
    end
  end
end
if machineOk then
  for _, s in ipairs(DATA.sources) do
    local fams = {}
    for _, f in ipairs(s.fams) do fams[f] = true end
    local moved = 0
    for _, d in ipairs(root:GetDescendants()) do
      local m = d:IsA("MeshPart") and not wanted[d.Name] and objOf(d.Name) == s.name and matOf(d.Name)
      -- fams: familia GROSSA (Metal) ou da variante (Metal_Dark), conforme o export estatico funde materiais ou nao
      if m and (fams[coarse(m)] or fams[famKey(m)]) then
        d.Parent = ORIG
        moved += 1
      end
    end
    log("%s: %d malhas estaticas guardadas em ServerStorage (familias %s)", s.name, moved, table.concat(s.fams, ", "))
  end
else
  local t = {}
  for g, n in pairs(missing) do table.insert(t, g .. " (faltam " .. n .. ")") end
  warnf("%s incompleto: %s. Roda, engrenagens, martinete e fole ficam ESTATICOS "
    .. "(importe o FBX deste mesmo export e rode de novo)", DATA.fbx, table.concat(t, ", "))
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
local nMov = 0
for name, part in pairs(found) do
  local w = wanted[name]
  local g = DATA.groups[w.group]
  clearTags(part)
  applyLook(part, matOf(name))
  local home = rootCF * CFrame.new(w.home)
  part.CFrame = home
  if not g then
    part.Parent = MOVF
  elseif g.kind == "cart" or g.kind == "load" then
    table.insert(cartParts, {part, g.kind == "load"})
  elseif machineGroups[w.group] and not machineOk then
    part.Parent = ORIG -- maquina incompleta: nao mostra meia roda
  else
    part.Parent = assembly(g.assembly or "Pecas")
    nMov += 1
    if g.kind == "spin" then
      setMotion(part, home, g)
      CollectionService:AddTag(part, "FORJA_Spin")
    elseif g.kind == "hammer" then
      setMotion(part, home, g)
      part:SetAttribute("VFX_CamPhase", g.camPhase)
      part:SetAttribute("VFX_Cams", g.cams)
      part:SetAttribute("VFX_Rest", g.rest)
      part:SetAttribute("VFX_Lift", g.lift)
      part:SetAttribute("VFX_Event", g.event)
      CollectionService:AddTag(part, "FORJA_Hammer")
    elseif g.kind == "pump" then
      setMotion(part, home, g)
      part:SetAttribute("VFX_Rest", g.rest)
      part:SetAttribute("VFX_Lift", g.lift)
      part:SetAttribute("VFX_K", g.k)
      part:SetAttribute("VFX_Event", g.event)
      CollectionService:AddTag(part, "FORJA_Pump")
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

-- peca invisivel; posC canonico (ou cfW = CFrame do mundo); lookC = direcao da face Front (canonica)
local function host(name, posC, size, lookC, cfW)
  local p = Instance.new("Part")
  p.Name = name
  p.Size = size
  if cfW then
    p.CFrame = cfW
  else
    local cf = CFrame.new(posC)
    if lookC then cf = CFrame.lookAt(posC, posC + lookC) end
    p.CFrame = WCF(cf)
  end
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
local function attW(parent, name, cfC) -- CFrame canonico -> mundo
  local a = Instance.new("Attachment")
  a.Name = name
  a.Parent = parent
  a.WorldCFrame = WCF(cfC)
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
local function beam(parent, name, a0, a1, p)
  local b = Instance.new("Beam")
  b.Name = name
  b.Attachment0 = a0
  b.Attachment1 = a1
  b.FaceCamera = false
  b.Segments = p.segments or 12
  b.Texture = p.tex
  b.TextureMode = Enum.TextureMode.Wrap
  b.TextureLength = p.len or 6
  b.TextureSpeed = (p.speed or 1) * SENTIDO_AGUA
  b.Width0 = p.w0
  b.Width1 = p.w1 or p.w0
  b.CurveSize0 = p.c0 or 0
  b.CurveSize1 = p.c1 or 0
  b.LightEmission = p.emission or 0
  b.LightInfluence = p.influence or 1
  b.Color = CS(p.color or RGB(255, 255, 255))
  b.Transparency = NS(p.transp or 0)
  b.ZOffset = p.zoff or 0
  b.Parent = parent
  return b
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
local nEm, nBeam = 0, 0
local function count(n) nEm += n end

-- ---------------------------------------------------------------- FORJA (quente)
if FX.hearth then
  -- lamina no leito de brasas; hk = altura das chamas (props do VFX_Hearth_Fire) / 3,5 studs do ajuste original
  local hk = math.clamp((FX.hearth.height or 3.5) / 3.5, 0.7, 1.8)
  local sk = 0.6 + 0.4 * hk
  local h = host("Lareira_Fogo", FX.hearth.pos, FX.hearth.size)
  -- continuo + rajada a cada golpe do fole ("foles")
  emitter(h, "Chamas", {tex = TEX.dot, color = {{0, RGB(255, 246, 196)}, {0.25, RGB(255, 196, 78)}, {0.6, RGB(255, 112, 32)}, {1, RGB(150, 34, 12)}},
    size = {{0, 1.3 * sk}, {0.35, 2.2 * sk}, {1, 0.35}}, transp = {{0, 0.45}, {0.18, 0.08}, {0.75, 0.45}, {1, 1}},
    life = {0.55, 1.05}, rate = 30, speed = {2.5 * hk, 5 * hk}, spread = 12, accel = Vector3.new(0, 3.5 * hk, 0), drag = 0.6,
    emission = 1, bright = 2, rot = {0, 360}, rotspeed = {-40, 40}, zoff = 0.4, maxd = 320, event = "foles", count = 6})
  emitter(h, "Linguas", {tex = TEX.fire, color = {{0, RGB(255, 226, 150)}, {0.5, RGB(255, 132, 40)}, {1, RGB(190, 46, 18)}},
    size = {{0, 2.2 * sk}, {0.5, 3.0 * sk}, {1, 0.8}}, transp = {{0, 0.55}, {0.3, 0.2}, {1, 1}},
    life = {0.4, 0.8}, rate = 10, speed = {3 * hk, 6 * hk}, spread = 8, emission = 0.9, bright = 1.6, rot = {-25, 25}, maxd = 320})
  emitter(h, "Brasas", {tex = TEX.dot, color = RGB(255, 168, 60), size = {{0, 0.3}, {1, 0}}, transp = {{0, 0}, {0.8, 0.2}, {1, 1}},
    life = {0.9, 1.8}, rate = 5, speed = {2.5 * hk, 5 * hk}, spread = 25, accel = Vector3.new(0, 2, 1.4), drag = 0.4,
    emission = 1, bright = 3, maxd = 260, event = "foles", count = 6})
  count(3)
end
-- pluma da torre: nucleo escuro + corpo cinza que deriva + topo claro e transparente; brasas e faiscas
if FX.chimney then
  local r = FX.chimney.radius
  local h = host("Chamine_Pluma", FX.chimney.pos, Vector3.new(r * 1.3, 1, r * 1.3))
  emitter(h, "Nucleo", {tex = TEX.smoke, color = {{0, RGB(40, 36, 34)}, {1, RGB(72, 66, 62)}},
    size = {{0, 6}, {1, 18}}, transp = {{0, 1}, {0.05, 0.12}, {0.6, 0.4}, {1, 1}}, life = {4.5, 6.5}, rate = 3,
    speed = {8, 11}, spread = 6, accel = Vector3.new(1.2, 0.8, 0), drag = 0.3, influence = 1, rot = {0, 360},
    rotspeed = {-14, 14}, maxd = 3000})
  emitter(h, "Corpo", {tex = TEX.smoke, color = {{0, RGB(96, 90, 86)}, {0.5, RGB(128, 122, 118)}, {1, RGB(160, 156, 154)}},
    size = {{0, 10}, {0.4, 18}, {1, 28}}, transp = {{0, 1}, {0.08, 0.32}, {0.6, 0.5}, {1, 1}}, life = {7, 10}, rate = 3.5,
    speed = {6, 9}, spread = 10, accel = Vector3.new(2, 1.5, 0), drag = 0.25, influence = 1, rot = {0, 360},
    rotspeed = {-10, 10}, maxd = 3000})
  local top = host("Chamine_PlumaTopo", FX.chimney.pos + Vector3.new(0, 7, 0), Vector3.new(r * 1.8, 2, r * 1.8))
  emitter(top, "Topo", {tex = TEX.smoke, color = {{0, RGB(178, 174, 172)}, {1, RGB(216, 214, 214)}},
    size = {{0, 14}, {1, 40}}, transp = {{0, 1}, {0.15, 0.62}, {0.7, 0.78}, {1, 1}}, life = {9, 12}, rate = 1.6,
    speed = {4, 6}, spread = 14, accel = Vector3.new(2.6, 1.0, 0), drag = 0.2, influence = 1, rot = {0, 360},
    rotspeed = {-8, 8}, maxd = 3000})
  emitter(h, "Brasas", {tex = TEX.dot, color = {{0, RGB(255, 214, 120)}, {1, RGB(255, 96, 24)}}, size = {{0, 0.55}, {1, 0}},
    transp = {{0, 0}, {0.8, 0.2}, {1, 1}}, life = {2, 3.5}, rate = 4, speed = {9, 15}, spread = 22,
    accel = Vector3.new(1.5, -3, 0), drag = 0.5, emission = 1, bright = 3, maxd = 900})
  emitter(h, "Faiscas", {tex = TEX.dot, color = {{0, RGB(255, 236, 170)}, {1, RGB(255, 120, 30)}}, size = {{0, 0.4}, {1, 0.05}},
    transp = {{0, 0}, {1, 1}}, life = {0.8, 1.4}, rate = 2, speed = {18, 26}, spread = 18, accel = Vector3.new(0, -12, 0),
    drag = 0.8, emission = 1, bright = 4, orient = Enum.ParticleOrientation.VelocityParallel, squash = 1.6, maxd = 900,
    event = "foles", count = 10})
  count(5)
end
-- fumaca fina nos respiros do telhado da forja
for i, v in ipairs(DATA.vents) do
  local h = host("Respiro_" .. i, v.pos, v.size)
  emitter(h, "Fumaca", {tex = TEX.smoke, color = {{0, RGB(150, 146, 142)}, {1, RGB(180, 178, 176)}},
    size = {{0, 1.4}, {1, 6}}, transp = {{0, 1}, {0.12, 0.55}, {1, 1}}, life = {4, 6}, rate = v.rate, speed = {2, 3.5},
    spread = 12, accel = Vector3.new(1.2, 0.6, 0), drag = 0.3, influence = 1, rot = {0, 360}, rotspeed = {-12, 12}, maxd = 600})
  count(1)
end
local function anvilFX(name, posC, event, sparks, speedMax, peak, loop)
  local h = host(name, posC, Vector3.new(0.6, 0.2, 0.6))
  local a = att(h, "Topo")
  emitter(a, "Faiscas", {tex = TEX.dot, color = {{0, RGB(255, 250, 214)}, {0.4, RGB(255, 192, 82)}, {1, RGB(255, 108, 30)}},
    size = {{0, 0.28}, {1, 0.06}}, transp = {{0, 0}, {0.7, 0.1}, {1, 1}}, life = {0.3, 0.75}, speed = {speedMax * 0.5, speedMax},
    spread = 75, accel = Vector3.new(0, -60, 0), drag = 1.4, emission = 1, bright = 4,
    orient = Enum.ParticleOrientation.VelocityParallel, squash = 2, event = event, count = sparks})
  emitter(a, "Brilho", {tex = TEX.dot, color = RGB(255, 204, 128), size = {{0, 2.2}, {1, 5}}, transp = {{0, 0.35}, {1, 1}},
    life = {0.16}, speed = {0}, emission = 1, bright = 3, event = event, count = 1})
  if loop then
    -- faiscas miudas em loop: a bigorna nunca fica "morta" entre os golpes
    emitter(a, "FaiscasLoop", {tex = TEX.dot, color = {{0, RGB(255, 236, 180)}, {1, RGB(255, 120, 36)}},
      size = {{0, 0.18}, {1, 0.04}}, transp = {{0, 0}, {1, 1}}, life = {0.25, 0.55}, rate = loop, speed = {5, 10},
      spread = 60, accel = Vector3.new(0, -50, 0), drag = 1.2, emission = 1, bright = 3,
      orient = Enum.ParticleOrientation.VelocityParallel, squash = 1.5, maxd = 220})
  end
  flashLight(h, RGB(255, 160, 70), 14, peak, event)
  count(loop and 3 or 2)
  return h, a
end
anvilFX("Bigorna_Ignis", FX.anvil_ignis.pos, "ignis", 14, 26, 4, 2.5)
local _, ah = anvilFX("Bigorna_Martinete", FX.anvil_hammer.pos, "martinete", 9, 18, 3)
emitter(ah, "Po", {tex = TEX.smoke, color = RGB(128, 118, 108), size = {{0, 0.8}, {1, 2.6}}, transp = {{0, 0.5}, {1, 1}},
  life = {0.6, 1.1}, speed = {2, 4}, spread = 80, accel = Vector3.new(0, 1, 0), drag = 2, influence = 1,
  event = "martinete", count = 4})
count(1)
if FX.quench then
  local q = host("Tempera_Vapor", FX.quench.pos, FX.quench.size)
  emitter(q, "Vapor", {tex = TEX.smoke, color = RGB(236, 240, 244), size = {{0, 0.8}, {1, 3.6}},
    transp = {{0, 1}, {0.15, 0.55}, {1, 1}}, life = {1.6, 2.6}, rate = 1.5, speed = {1.5, 3}, spread = 18,
    accel = Vector3.new(0.4, 1.4, 0), drag = 0.6, influence = 0.8, rot = {0, 360}, rotspeed = {-30, 30}, maxd = 260})
  emitter(q, "Chiado", {tex = TEX.smoke, color = RGB(246, 248, 250), size = {{0, 1.2}, {1, 5.5}},
    transp = {{0, 0.35}, {1, 1}}, life = {1.2, 2.2}, speed = {3, 6}, spread = 25, accel = Vector3.new(0.4, 2.5, 0),
    drag = 0.8, influence = 0.8, rot = {0, 360}, rotspeed = {-40, 40}, event = "tempera", count = 14})
  count(2)
end

-- ---------------------------------------------------------------- AGUA (frio): roda, quedas, correntes
do
  local ww = DATA.wheelWidth
  local o = host("Roda_Respingo", FX.wheel_out.pos, Vector3.new(ww + 0.4, 0.4, 1.6))
  emitter(o, "Gotas", {tex = TEX.dot, color = RGB(226, 242, 255), size = {{0, 0.45}, {1, 0.2}}, transp = {{0, 0.15}, {1, 1}},
    life = {0.5, 0.9}, rate = 10, speed = {6, 11}, spread = 30, accel = Vector3.new(0, -40, 3), drag = 0.5,
    emission = 0.3, influence = 0.6, orient = Enum.ParticleOrientation.VelocityParallel, squash = 0.8, maxd = 300})
  -- rajada sincronizada com a pa que sai da agua (evento do cliente, pela fase da roda)
  emitter(o, "Pa", {tex = TEX.dot, color = RGB(236, 248, 255), size = {{0, 0.55}, {1, 0.2}}, transp = {{0, 0.1}, {1, 1}},
    life = {0.5, 0.9}, speed = {7, 12}, spread = 25, accel = Vector3.new(0, -40, 2), drag = 0.5, emission = 0.3,
    influence = 0.6, orient = Enum.ParticleOrientation.VelocityParallel, squash = 0.8, event = "roda:sai", count = 9})
  local i = host("Roda_Entrada", FX.wheel_in.pos, Vector3.new(ww + 0.4, 0.4, 1.6))
  emitter(i, "Gotas", {tex = TEX.dot, color = RGB(226, 242, 255), size = {{0, 0.4}, {1, 0.15}}, transp = {{0, 0.2}, {1, 1}},
    life = {0.35, 0.6}, rate = 4, speed = {3, 6}, spread = 40, accel = Vector3.new(0, -40, 0), drag = 0.5,
    emission = 0.3, influence = 0.6, maxd = 300})
  emitter(i, "Pa", {tex = TEX.dot, color = RGB(236, 248, 255), size = {{0, 0.5}, {1, 0.15}}, transp = {{0, 0.1}, {1, 1}},
    life = {0.35, 0.6}, speed = {4, 8}, spread = 45, accel = Vector3.new(0, -40, 0), drag = 0.5, emission = 0.3,
    influence = 0.6, event = "roda:entra", count = 6})
  local m = host("Roda_Nevoa", FX.wheel_mist.pos, Vector3.new(ww + 1, 0.5, 4))
  emitter(m, "Espuma", {tex = TEX.smoke, color = RGB(240, 248, 255), size = {{0, 1.5}, {1, 4.5}}, transp = {{0, 0.5}, {1, 1}},
    life = {1.2, 2}, rate = 4, speed = {1, 2.5}, spread = 40, drag = 1, influence = 0.7, rot = {0, 360}, maxd = 300})
  count(5)
end
-- cachoeiras: 2 Beams com estrias (corpo + brilho) seguindo a queda + nevoa e espuma na base
for _, wf in ipairs(DATA.waterfalls) do
  local w = wf.width
  local out = wf.out
  local lat = UP:Cross(out).Unit
  -- curva ajustada no export (fit_beam): corre na frente da cortina de agua do bocal ate a base
  local top = wf.top + out * (wf.o0 or 0.35)
  local base = wf.base + out * (wf.o1 or 0.35)
  local fall = top.Y - base.Y
  local hb = host("Queda_" .. wf.name, (top + base) / 2, Vector3.new(1, 1, 1))
  local a0 = attW(hb, "Topo", CFrame.fromMatrix(top, out, lat))
  local a1 = attW(hb, "Base", CFrame.fromMatrix(base, UP, lat))
  local c0 = wf.c0 or math.clamp(wf.lip * 1.4, 0.8, 6)
  local c1 = wf.c1 or -math.clamp(fall * 0.3, 2, 24)
  beam(hb, "Agua", a0, a1, {tex = TEX_AGUA.cachoeira, len = 6, speed = 1.2, w0 = w, w1 = w * 1.08, c0 = c0, c1 = c1,
    emission = 0.3, influence = 0.7, color = {{0, RGB(214, 240, 255)}, {1, RGB(176, 222, 246)}},
    transp = {{0, 0.3}, {0.08, 0.06}, {0.9, 0.1}, {1, 0.45}}, zoff = 0.3, segments = 16})
  beam(hb, "Brilho", a0, a1, {tex = TEX_AGUA.cachoeira, len = 9, speed = 2, w0 = w * 0.6, w1 = w * 0.7, c0 = c0 * 1.05,
    c1 = c1 * 0.95, emission = 0.45, influence = 0.4, color = RGB(255, 255, 255), transp = {{0, 0.5}, {1, 0.7}},
    zoff = 0.5, segments = 16})
  nBeam += 2
  local b = host("Queda_" .. wf.name .. "_Base", base + Vector3.new(0, 0.3, 0), Vector3.new(w + 1.5, 0.6, 3), wf.out)
  emitter(b, "Nevoa", {tex = TEX.smoke, color = RGB(236, 245, 255), size = {{0, math.clamp(w * 0.45, 3, 7)}, {1, math.clamp(w * 1.15, 6, 14)}},
    transp = {{0, 0.72}, {0.3, 0.55}, {1, 1}}, life = {2.5, 4}, rate = math.clamp(w * 0.35, 1.5, 4), speed = {1.5, 3.5},
    spread = 45, accel = Vector3.new(0, 0.6, 0), drag = 0.6, influence = 0.8, rot = {0, 360}, rotspeed = {-10, 10}, maxd = 650})
  emitter(b, "Espuma", {tex = TEX.smoke, color = RGB(250, 253, 255), size = {{0, 1.4}, {1, 3.2}}, transp = {{0, 0.25}, {1, 1}},
    life = {0.6, 1.1}, rate = math.clamp(w * 1.4, 5, 12), speed = {4, 8}, spread = 35, accel = Vector3.new(0, -18, 0),
    drag = 0.8, influence = 0.7, rot = {0, 360}, maxd = 450})
  count(2)
end
-- rio (-Y) e canal (para o vertedouro): ondulacao rolando no sentido do fluxo (Beam deitado na agua)
for _, f in ipairs(DATA.flows) do
  local dir = (f.b - f.a).Unit
  local lat = UP:Cross(dir).Unit
  local h = host("Corrente_" .. f.name, (f.a + f.b) / 2, Vector3.new(1, 1, 1))
  local a0 = attW(h, "Montante", CFrame.fromMatrix(f.a, dir, lat))
  local a1 = attW(h, "Jusante", CFrame.fromMatrix(f.b, dir, lat))
  beam(h, "Ondulacao", a0, a1, {tex = TEX_AGUA.linhas, len = 16, speed = f.speed / 16, w0 = f.width, emission = 0.12,
    influence = 0.9, color = RGB(236, 248, 255), transp = {{0, 1}, {0.04, 0.6}, {0.96, 0.6}, {1, 1}}, segments = 2,
    zoff = 0.05})
  nBeam += 1
end

-- ---------------------------------------------------------------- PORTAIS: espiral em SurfaceGui + sugadas + aro
local nSwirl, nSug, nRim = 0, 0, 0
for _, p in ipairs(DATA.portals) do
  local key, R, n = p.key, p.radius, p.normal
  local u = UP:Cross(n).Unit
  local v = n:Cross(u).Unit
  local discs = {}
  for _, d in ipairs(root:GetDescendants()) do
    if d:IsA("MeshPart") and string.sub(d.Name, 1, #p.swirl + 2) == p.swirl .. "__" then table.insert(discs, d) end
  end
  -- disco modelado: gira no mesmo relogio (leitura de tras e de lado; de frente o SurfaceGui cobre)
  for _, d in ipairs(discs) do
    clearTags(d)
    d:SetAttribute("VFX_Home", d.CFrame)
    d:SetAttribute("VFX_Pivot", W(p.center))
    d:SetAttribute("VFX_Axis", WV(n).Unit)
    d:SetAttribute("VFX_Speed", p.spin)
    d:SetAttribute("VFX_Phase", 0)
    d:SetAttribute("VFX_Portal", key)
    CollectionService:AddTag(d, "FORJA_Spin")
  end
  -- espiral: SurfaceGui na face voltada ao jogador, sem luz do sol (brilha de dia); 2 ImageLabels girando
  local img = SWIRL_IMG[key] or ""
  if img == "" and discs[1] then img = lerMapa(discs[1]) or "" end
  if img ~= "" then
    local h = host("Portal_" .. key .. "_Espiral", p.center + n * (p.thick / 2 + 0.08), Vector3.new(R * 2.04, R * 2.04, 0.05), n)
    local sg = Instance.new("SurfaceGui")
    sg.Name = "Espiral"
    sg.Face = Enum.NormalId.Front
    sg.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
    sg.PixelsPerStud = 32
    sg.LightInfluence = 0
    sg.Brightness = 2.4
    sg.MaxDistance = 700
    sg.ClipsDescendants = false
    sg.Parent = h
    local function label(name, scale, transp, z)
      local l = Instance.new("ImageLabel")
      l.Name = name
      l.BackgroundTransparency = 1
      l.AnchorPoint = Vector2.new(0.5, 0.5)
      l.Position = UDim2.fromScale(0.5, 0.5)
      l.Size = UDim2.fromScale(scale, scale)
      l.Image = img
      l.ImageTransparency = transp
      l.ZIndex = z
      l.Parent = sg
      return l
    end
    label("Externa", 1, 0, 1)
    label("Interna", 0.55, 0.22, 2)
    h:SetAttribute("VFX_Speed", p.spin)
    h:SetAttribute("VFX_InnerMul", DATA.portalInner)
    h:SetAttribute("VFX_Portal", key)
    h:SetAttribute("VFX_Bright", 2.4)
    CollectionService:AddTag(h, "FORJA_Swirl")
    nSwirl += 1
  else
    warnf("portal %s: disco sem textura de espiral (rode o montar com a textura ou preencha SWIRL_IMG) - so o disco gira", key)
  end
  -- particulas sugadas: presas no disco que gira (nascem no aro e correm para o centro, na cor do portal)
  local ringHost = discs[1]
  local ph = host("Portal_" .. key, p.center, Vector3.new(1, 1, 1))
  if not ringHost then ringHost = ph end
  for _, c in ipairs(ringHost:GetChildren()) do
    if c:IsA("Attachment") and string.sub(c.Name, 1, 7) == "Sugada_" then c:Destroy() end
  end
  local f = p.thick / 2 + 0.45
  local wc, wn, wu, wv = W(p.center), WV(n).Unit, WV(u).Unit, WV(v).Unit
  for k = 0, 2 do
    local ang = math.pi * 2 * k / 3 + 0.4
    local pos = wc + (wu * math.cos(ang) + wv * math.sin(ang)) * R * 0.92 + wn * f
    local a = Instance.new("Attachment")
    a.Name = "Sugada_" .. k
    a.Parent = ringHost
    a.WorldCFrame = CFrame.lookAt(pos, wc + wn * f)
    emitter(a, "Sugadas", {tex = TEX.star, color = {{0, p.arm}, {1, p.core3}}, size = {{0, 0.15}, {0.2, 0.75}, {1, 0.1}},
      transp = {{0, 1}, {0.15, 0.1}, {1, 0.35}}, life = {1.15}, rate = 5, speed = {R * 0.92 / 1.15 * 0.95},
      spread = 6, dir = Enum.NormalId.Front, emission = 1, bright = 2, zoff = 0.3, maxd = 450})
    count(1)
    nSug += 1
  end
  local fa = att(ph, "Frente", CFrame.lookAt(n * 0.35, n * 1.35)) -- espaco local do host = canonico
  emitter(fa, "Pulso", {tex = TEX.ring, color = p.core3, size = {{0, 3}, {1, 2 * R * 1.2}}, transp = {{0, 0.15}, {1, 1}},
    life = {1.1}, speed = {0.3}, dir = Enum.NormalId.Front, orient = Enum.ParticleOrientation.VelocityPerpendicular,
    emission = 1, bright = 2, event = "portal:" .. key, count = 1})
  count(1)
  -- aro Neon (geometria do portal): pulsa junto com o portal
  local rimSet = {}
  for _, r in ipairs(p.rims) do rimSet[r] = true end
  for _, d in ipairs(root:GetDescendants()) do
    if d:IsA("MeshPart") then
      local base = string.match(d.Name, "^(.-)_%d+$")
      if rimSet[d.Name] or (base and rimSet[base]) then
        clearTags(d)
        d:SetAttribute("VFX_Kind", "portalrim")
        d:SetAttribute("VFX_Event", "portal:" .. key)
        d:SetAttribute("VFX_BaseColor", d.Color)
        CollectionService:AddTag(d, "FORJA_Pulse")
        nRim += 1
      end
    end
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

-- ---------------------------------------------------------------- VILA: fumaca fina em poucas chamines
for _, s in ipairs(DATA.smokes) do
  local mkp = markers and markers:FindFirstChild(s.marker)
  local rate = (mkp and tonumber(mkp:GetAttribute("rate"))) or s.rate or 2
  local nm = "Chamine_" .. string.sub(s.marker, 11)
  local h
  if mkp and mkp:IsA("BasePart") then
    h = host(nm, nil, Vector3.new(0.8, 0.3, 0.8), nil, CFrame.new(mkp.Position))
  else
    h = host(nm, s.pos, Vector3.new(0.8, 0.3, 0.8))
  end
  emitter(h, "Fumaca", {tex = TEX.smoke, color = {{0, RGB(150, 146, 142)}, {1, RGB(186, 184, 182)}},
    size = {{0, 1.2}, {1, 5}}, transp = {{0, 1}, {0.12, 0.5}, {1, 1}}, life = {5, 7}, rate = rate, speed = {2, 3.2},
    spread = 8, accel = Vector3.new(1.2, 0.4, 0), drag = 0.3, influence = 1, rot = {0, 360}, rotspeed = {-12, 12}, maxd = 700})
  count(1)
end

-- ---------------------------------------------------------------- tags das pecas estaticas (pulsos e flicker)
local nPulse, nLight = 0, 0
for _, d in ipairs(root:GetDescendants()) do
  if d:IsA("MeshPart") and d.Parent ~= ORIG and not CollectionService:HasTag(d, "FORJA_Spin") then
    local n = d.Name
    local kind, event, amp
    if string.find(n, "__Crystal_", 1, true) then
      kind = "crystal"
    elseif string.find(n, "__Metal_Heated", 1, true) then
      kind = "heat"
      if string.sub(n, 1, 12) == "FORGE_Anvil_" then event = "ignis"
      elseif string.sub(n, 1, 15) == "BLD_WheelHouse_" then event = "martinete" end
    elseif string.find(n, "__Ember_Glow", 1, true) then
      kind = "heat"
      if string.sub(n, 1, 12) == "FORGE_Anvil_" then event = "ignis" end
    elseif string.find(n, "__Fire_Glow_", 1, true) then
      kind = "ember"
    elseif string.sub(n, 1, 6) == "FORGE_" and (string.find(n, "__Forge_Glow_Soft", 1, true) or string.find(n, "__Forge_Emissive", 1, true)) then
      kind, amp = "ember", 0.5
    elseif string.find(n, "__Lantern_Glow", 1, true) then
      kind = "lantern"
    end
    if kind and CollectionService:HasTag(d, "FORJA_Pulse") and d:GetAttribute("VFX_Kind") == "portalrim" then
      kind = nil -- aro de portal ja marcado acima
    end
    if kind then
      if CollectionService:HasTag(d, "FORJA_Pulse") then CollectionService:RemoveTag(d, "FORJA_Pulse") end
      d:SetAttribute("VFX_Kind", kind)
      d:SetAttribute("VFX_Event", event or "")
      d:SetAttribute("VFX_Amp", amp or 1)
      d:SetAttribute("VFX_BaseColor", d:GetAttribute("VFX_BaseColor") or d.Color)
      CollectionService:AddTag(d, "FORJA_Pulse")
      nPulse += 1
    end
  elseif (d:IsA("PointLight") or d:IsA("SpotLight")) and d.Parent and d.Parent.Parent and d.Parent.Parent.Name == "LIGHTS" then
    local n = d.Parent.Name
    local kind, event = "lantern", ""
    if string.sub(n, 1, 9) == "L_Portal_" then
      kind, event = "portal", "portal:" .. string.sub(n, 10)
    elseif string.sub(n, 1, 12) == "L_HearthLamp" then
      kind = "lantern"                                   -- lanternas ao lado da boca: nao sao fogo
    elseif n == "L_Hearth_Fire" then
      kind, event = "fire", "foles"                      -- respira com o fole (1,3x no golpe)
    elseif string.sub(n, 1, 8) == "L_Hearth" or string.sub(n, 1, 9) == "L_Furnace" or n == "L_DS_Oni"
      or string.sub(n, 1, 12) == "L_DS_Brazier" or string.sub(n, 1, 13) == "L_Tower_Crown" then
      kind = "fire"                                      -- (rever L_DS_* quando o Demon Slayer for redesenhado)
    elseif n == "L_Mine_Chamber" or n == "L_Mine_Tunnel" or n == "L_Shed_Light" then
      kind = "crystal"
    elseif n == "L_Hall_Fill" or n == "L_Shop_Fill" or n == "L_Konoha_Gate" then
      kind = nil
    end
    if CollectionService:HasTag(d, "FORJA_Flicker") then CollectionService:RemoveTag(d, "FORJA_Flicker") end
    if kind then
      d:SetAttribute("VFX_Kind", kind)
      d:SetAttribute("VFX_Event", event)
      d:SetAttribute("VFX_Base", d:GetAttribute("VFX_Base") or d.Brightness)
      CollectionService:AddTag(d, "FORJA_Flicker")
      nLight += 1
    end
  end
end

CFG:SetAttribute("VFX_Version", DATA.version)
CFG:SetAttribute("VFX_ExportId", DATA.exportId or "")
CFG:SetAttribute("VFX_RootCF", rootCF)
CFG:SetAttribute("VFX_Root", root:GetFullName())
CFG:SetAttribute("VFX_Ready", true)
log("pronto (%s): referencia %s | %d pecas moveis%s, %d emissores, %d beams, %d espirais, %d sugadas, %d aros, %d pulsos, %d luzes, carrinho %s",
  DATA.version, refName, nMov, machineOk and "" or " (maquinas ESTATICAS: FBX incompleto)", nEm, nBeam, nSwirl, nSug,
  nRim, nPulse, nLight, (#cartParts > 0) and "malha" or "Parts")
'''

# =====================================================================================================================
# LUAU: CLIENTE
# =====================================================================================================================
CLIENT_LUA = r'''--[[
vfx_lobby_forja_client.lua   (gerado por export_vfx.py - @VERSION@ - nao editar a mao)
VFX e MOVIMENTO do Lobby Vila-Forja - ANIMACAO NO CLIENTE

ONDE COLOCAR: LocalScript em StarterPlayer > StarterPlayerScripts.
Precisa da montagem (vfx_lobby_forja.lua) feita antes: ela deixa ReplicatedStorage.LOBBY_FORJA_VFX e as tags.

O que faz (tudo local, nada replica para o servidor; relogio = workspace:GetServerTimeNow, todos veem a mesma fase):
  - gira a roda d'agua + eixo baixo, o eixo alto (pinhao + engrenagem da parede) e a engrenagem menor, bate o
    martinete (faiscas no golpe), bombeia o fole (rajada de chamas, faiscas na torre e clarao na lareira no pico);
  - respingos da roda sincronizados com as pas que entram e saem da agua;
  - espirais dos portais: gira as 2 ImageLabels do SurfaceGui (interna 2,3x) + o disco; pulso de brilho, aro e anel;
  - carrinho de mina ocasional: sai do patio da mina, para na balanca, descarrega no portao da forja e volta;
  - golpes do Ignis (ritmo interno ou KeyframeMarker "Golpe" no rig com a tag FORJA_Ignis) e chiado da tempera;
  - pulsos: cristais, metal quente, brasas, chamas, aros dos portais; flicker das lanternas e do fogo.
Desempenho: 1 conexao PreRender com BulkMoveTo so para o que esta perto da camera; pulsos a 20 Hz, luzes a 15 Hz,
liga/desliga de emissores a 2 Hz. Streaming: registra/desregistra por tag (CollectionService), sem WaitForChild
no workspace. Respeita GuiService.ReducedMotionEnabled. CFG:SetAttribute("VFX_Pause", true) congela tudo.
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
if CFG:GetAttribute("VFX_Version") and CFG:GetAttribute("VFX_Version") ~= DATA.version then
  warn(string.format("[VFX Forja] montagem %s e cliente %s: rode os dois do mesmo export", tostring(CFG:GetAttribute("VFX_Version")), DATA.version))
end
local cfgId = CFG:GetAttribute("VFX_ExportId")
if cfgId and cfgId ~= "" and DATA.exportId and cfgId ~= DATA.exportId then
  warn(string.format("[VFX Forja] montagem do passe %s e cliente do passe %s: o trilho do carrinho e a fase das pas "
    .. "podem nao bater (use os dois .lua do mesmo export_all.py)", cfgId, DATA.exportId))
end
local rootCF = CFG:GetAttribute("VFX_RootCF")
if typeof(rootCF) ~= "CFrame" then rootCF = CFrame.new() end

local TAU = math.pi * 2
local SPIN_DIST, HAMMER_DIST, CART_DIST, SWIRL_DIST, WHEEL_DIST = 340, 220, 420, 520, 260
local PULSE_DIST = {crystal = 230, heat = 200, ember = 450, lantern = 200, portalrim = 480}
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

-- ---------------------------------------------------------------- eventos (faiscas, claroes, rajadas)
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

-- ---------------------------------------------------------------- rotores (roda, engrenagens, discos dos portais)
local spins = {}
watch("FORJA_Spin", function(p)
  if not p:IsA("BasePart") or not p:IsDescendantOf(workspace) or spins[p] then return end
  local home, pivot, axis = p:GetAttribute("VFX_Home"), p:GetAttribute("VFX_Pivot"), p:GetAttribute("VFX_Axis")
  if typeof(home) ~= "CFrame" or typeof(pivot) ~= "Vector3" or typeof(axis) ~= "Vector3" then return end
  spins[p] = {pivot = pivot, pivotCF = CFrame.new(pivot), axis = axis.Unit, rel = CFrame.new(-pivot) * home,
    speed = p:GetAttribute("VFX_Speed") or 0, phase = p:GetAttribute("VFX_Phase") or 0, portal = p:GetAttribute("VFX_Portal")}
end, function(p) spins[p] = nil end)

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

-- ---------------------------------------------------------------- fole: angulo = rest + lift * (0.5 - 0.5 cos(k w t))
local pumps, pumpGroups = {}, {}
watch("FORJA_Pump", function(p)
  if not p:IsA("BasePart") or not p:IsDescendantOf(workspace) then return end
  local home, pivot, axis = p:GetAttribute("VFX_Home"), p:GetAttribute("VFX_Pivot"), p:GetAttribute("VFX_Axis")
  if typeof(home) ~= "CFrame" or typeof(pivot) ~= "Vector3" or typeof(axis) ~= "Vector3" then return end
  local ev = p:GetAttribute("VFX_Event") or "foles"
  local g = pumpGroups[ev]
  if not g then
    g = {w = (p:GetAttribute("VFX_K") or 2) * (p:GetAttribute("VFX_Speed") or 0.63), rest = p:GetAttribute("VFX_Rest") or 0,
      lift = p:GetAttribute("VFX_Lift") or 0.14, lastPh = nil, angle = 0, pivot = pivot}
    pumpGroups[ev] = g
  end
  pumps[p] = {group = g, pivotCF = CFrame.new(pivot), axis = axis.Unit, rel = CFrame.new(-pivot) * home}
end, function(p) pumps[p] = nil end)

-- ---------------------------------------------------------------- espirais dos portais (SurfaceGui)
local swirls = {}
watch("FORJA_Swirl", function(h)
  if not h:IsA("BasePart") or not h:IsDescendantOf(workspace) then return end
  local sg = h:FindFirstChildOfClass("SurfaceGui")
  if not sg then return end
  swirls[h] = {pos = h.Position, sg = sg, ext = sg:FindFirstChild("Externa"), int = sg:FindFirstChild("Interna"),
    speed = h:GetAttribute("VFX_Speed") or 0.9, mul = h:GetAttribute("VFX_InnerMul") or 2.3,
    bright = h:GetAttribute("VFX_Bright") or sg.Brightness, portal = h:GetAttribute("VFX_Portal") or ""}
end, function(h) swirls[h] = nil end)

-- ---------------------------------------------------------------- pulsos de cor e luzes
local pulses, lights, emitters = {}, {}, {}
watch("FORJA_Pulse", function(p)
  if not p:IsA("BasePart") or not p:IsDescendantOf(workspace) then return end
  local base = p:GetAttribute("VFX_BaseColor")
  if typeof(base) ~= "Color3" then base = p.Color end
  local kind = p:GetAttribute("VFX_Kind") or "crystal"
  pulses[p] = {kind = kind, event = p:GetAttribute("VFX_Event") or "", base = base, hi = base:Lerp(WHITE, 0.45),
    amp = p:GetAttribute("VFX_Amp") or 1, pos = p.Position, seed = seedOf(p.Position), maxd = PULSE_DIST[kind] or 220}
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

-- ---------------------------------------------------------------- relogios (portais, Ignis, pas da roda)
local portalW = {}
for _, p in ipairs(DATA.portals) do portalW[p.key] = {pos = rootCF * p.center, idx = p.idx, last = nil} end
local PORTAL_PERIOD = 3.6
local ignisPos = rootCF * DATA.ignis.pos
local lastIgnis, ignisCycles = nil, 0
local WH = DATA.wheel
local wheelPos = rootCF * WH.pos
local lastIn, lastOut

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

  -- fole (no pico do curso: rajada nas chamas/brasas, faiscas na torre, clarao na lareira)
  for ev, g in pairs(pumpGroups) do
    local ph = angleAt(g.w, t)
    local near = (g.pivot - cp).Magnitude < HAMMER_DIST
    if g.lastPh and near and dt < 0.5 then
      if (g.lastPh < math.pi and ph >= math.pi) then fire(ev, 1) end
    end
    g.lastPh = ph
    g.near = near
    g.angle = g.rest + g.lift * (0.5 - 0.5 * math.cos(ph))
  end
  for p, h in pairs(pumps) do
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

  -- espirais: mesmo relogio do disco (Rotation positiva = horario visto de frente = giro negativo em volta da normal)
  for _, s in pairs(swirls) do
    if (s.pos - cp).Magnitude < SWIRL_DIST then
      local sp = s.speed * motion
      if s.ext then s.ext.Rotation = (-math.deg(angleAt(sp, t))) % 360 end
      if s.int then s.int.Rotation = (-math.deg(angleAt(sp * s.mul, t))) % 360 end
      s.sg.Brightness = s.bright * (1 + 0.45 * (flash["portal:" .. s.portal] or 0))
    end
  end

  -- pas da roda: a pa k esta em k*step - w*t; entra na agua em aIn e sai em aOut
  if (wheelPos - cp).Magnitude < WHEEL_DIST then
    local th = angleAt(WH.speed, t)
    local nIn = math.floor((th + WH.aIn) / WH.step)
    local nOut = math.floor((th + WH.aOut) / WH.step)
    if lastIn and nIn ~= lastIn and dt < 0.5 then fire("roda:entra", 1) end
    if lastOut and nOut ~= lastOut and dt < 0.5 then fire("roda:sai", 1) end
    lastIn, lastOut = nIn, nOut
  else
    lastIn, lastOut = nil, nil
  end

  -- portais: pulso de luz + anel + aro + brilho da espiral
  for key, pw in pairs(portalW) do
    local ph = (t + pw.idx * 0.55) % PORTAL_PERIOD
    if pw.last and ph < pw.last and (pw.pos - cp).Magnitude < 480 then fire("portal:" .. key, 1) end
    pw.last = ph
  end
  -- Ignis: ritmo interno enquanto o rig nao manda "Golpe"; a tempera chia a cada quenchEvery ciclos
  if os.clock() - lastRigStrike > 12 and (ignisPos - cp).Magnitude < 260 then
    local tc = t % DATA.ignis.cycle
    if lastIgnis then
      for _, hit in ipairs(DATA.ignis.hits) do
        local ht = hit[1]
        if (lastIgnis < ht and tc >= ht) or (tc < lastIgnis and (lastIgnis < ht or tc >= ht)) then fire("ignis", hit[2]) end
      end
      if tc < lastIgnis then
        ignisCycles += 1
        if ignisCycles % DATA.ignis.quenchEvery == 0 then fire("tempera", 1) end
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
          local f0 = math.clamp(0.9 + 0.22 * math.noise(tn * 1.6, e.seed, 0.3) * flick, 0.7, 1)
          local f = 1 - e.amp * (1 - f0)
          c = Color3.new(e.base.R * f, e.base.G * f, e.base.B * f)
        elseif e.kind == "lantern" then
          local f = math.clamp(0.96 + 0.1 * math.noise(tn * 5.5, e.seed, 0.7) * flick, 0.85, 1)
          c = Color3.new(e.base.R * f, e.base.G * f, e.base.B * f)
        elseif e.kind == "portalrim" then
          c = e.base:Lerp(WHITE, math.clamp(0.08 + 0.1 * math.sin(tn * 2.6 + e.seed) + 0.55 * (flash[e.event] or 0), 0, 1))
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
          f *= 1 + 0.3 * (flash[e.event] or 0)
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
