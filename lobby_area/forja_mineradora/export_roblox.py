# export_roblox.py - prepara o lobby para o Roblox Studio
# uso: blender -b lobby_forja_mineradora.blend --python export_roblox.py [-- <pasta_saida>]
#      (ou FM_EXPORT_DIR=<pasta>; padrao ./export)
#      FM_BUDGET=strict (padrao): se algum dono ou meta global passar do orcamento, imprime o relatorio e FALHA sem
#                                 gravar nada (codigo de saida 3); FM_BUDGET=warn grava assim mesmo e so avisa.
# saida:
#   LOBBY_<colecao>_<ID6>.fbx malhas visuais: 1 material (VARIANTE) por malha, <= 18k tris, pedacos grandes fatiados em
#                            celulas de 128 studs, origem no CENTRO DO BBOX, UVMap em studs/TILE e texturas embutidas.
#                            ID6 = EXPORT_ID (crc32 dos nomes): nome novo a cada mudanca -> o 3D Importer nao reusa cache.
#                            Os LOBBY_<colecao>*.fbx anteriores sao apagados.
#   lobby_data.json          malhas (centro/tamanho/sombra/dono), materiais, colisoes (COL_), marcadores, luzes, orcamento
#   montar_lobby_forja.lua   Command Bar: confere a importacao (relatorio por FBX), alinha, aplica cor/Material/textura
#                            por variante, sombra por malha, streaming (SKYLINE persistente + modelos atomicos),
#                            camera (cascas que ocluem), colisoes, marcadores, luzes (NightOnly), chao distante,
#                            rede de seguranca (VOID_CATCH) e, opcional, o Lighting do lobby
import sys, os, json, math, zlib, glob, re, colorsys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fm_pv3
fm_pv3.load()       # portais v3: materiais (MATS/RBX_CAL) e textura da espiral de cada portal
import numpy as np
import bpy, bmesh
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
import fm_lib
import fm_mat_textures as TX
# traducao dos materiais (Enum.Material, cor calibrada, sombra) mora no fm_lib; estes nomes ficam aqui por
# compatibilidade (export_vfx.py e ferramentas antigas importam daqui)
from fm_lib import RBX_RULES, RBX_KEYWORDS, RBX_CAL, rbx_rule, rbx_color, rbx_material
from fm_lib import rbx_base_color as base_color, to_srgb as srgb, family_of as family


def mat_color(mname):
    """cor do Roblox de um material, usando a cor do proprio material quando ele nao esta registrado em MATS"""
    return rbx_color(mname, bpy.data.materials.get(mname))

_argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = (_argv[0] if _argv and __name__ == "__main__" else None) or os.environ.get("FM_EXPORT_DIR") or \
    os.path.join(HERE, "export")
BUDGET_MODE = os.environ.get("FM_BUDGET", "strict").lower()
MAX_TRIS = 18000
MAX_AXIS = 2000.0            # guarda generica: nenhum pedaco com eixo > 2000 studs (limite da MeshPart: 2048)
CELL = 128.0                 # fatiamento espacial dos pedacos grandes (frustum/streaming)
CELL_TRIGGER = 160.0         # pedaco com bbox > 160 studs em X ou Y e fatiado em celulas de CELL
CELL_MIN_TRIS = 1500         # ... se tiver tris que valham o corte (pedaco leve e barato mesmo fora do frustum)
CELL_KEEP_TRIS = 600         # celula com menos tris que isso junta com a celula grande mais proxima do mesmo pedaco
VARIANT_MIN_TRIS = 1500      # variante (Stone_Light_C...) com menos tris no lobby inteiro volta para a base da familia
GROUPS = ["02_TERRAIN", "03_FORGE", "04_MINE", "05_WATER_SYSTEM", "06_PORTALS", "07_BUILDINGS", "08_PROPS",
          "09_VEGETATION", "10_RAILS"]
SKIP_PREFIX = ("COL_", "SCALE_", "BLK_", "SKY_", "VFX_", "NPC_")   # NPC_: o proxy do Ignis ocupa o lugar do rig
SKIP_NAMES = {"TER_Far_Valley_Plane"}
# vale distante: exporta so as silhuetas; o plano (2400 studs, coplanar com o chao) vira a Part FAR_GROUND no Lua
FAR_VALLEY = "TER_Far_Valley"
FAR_GROUND = {"size": [2048, 2, 2048], "top_z": -69.0, "material": "Far_Haze"}
VOID_CATCH = {"size": [2048, 4, 2048], "y": -25.0}

# ------------------------------------------------------------------ donos e orcamento (brief fix2)
OWNERS = [("FORGE_", "forge"), ("NPC_", "forge"), ("PORTAL_", "portals"), ("KONOHA_", "portals"),
          ("BLD_", "architecture"), ("TER_", "terrain"), ("VEG_", "vegetation"), ("WATER_", "scene_lighting"),
          ("SKY_", "scene_lighting"), ("PROP_", "props"), ("MINE_", "props"), ("RAIL_", "props")]
# cotas redistribuidas na integracao da rodada 2 (tetos GLOBAIS inalterados): arquitetura/terreno usam em
# MeshParts a folga que forja/portais/vegetacao deixaram; colisoes sao Parts invisiveis ancoradas (custo baixo)
# portais v3 (2026-09-24): 5 portais novos com dressing proprio de escada; a folga vem da forja e da cena (MeshParts)
BUDGET_OWNER = {"forge": (120000, 116), "portals": (90000, 150), "architecture": (135000, 170),
                "terrain": (128000, 118), "vegetation": (50000, 70), "scene_lighting": (38000, 36),
                "props": (58000, 90)}
BUDGET = {"static_tris": 624000, "static_meshes": 750, "vfx_tris": 16000, "vfx_meshes": 30, "total_tris": 640000,
          "total_meshes": 780, "materials": 130, "shadow_meshes": 350, "day_lights": 45, "col": 820}

# ------------------------------------------------------------------ fold de materiais pequenos (menos MeshParts)
FOLD_AREA = 60.0             # studs^2 por objeto: abaixo disso o material vai para o vizinho dominante
FOLD_DIST = 100.0            # distancia maxima de cor (sRGB) para o fold automatico de mesmo Enum.Material
FOLD_DIST_NEON = 70.0        # Neon so funde com Neon de cor parecida
CAP_DIST = 90.0              # teto global de materiais: distancia maxima de cor (sRGB) do remapeamento
FOLD_TO = {                  # destinos explicitos (valem mesmo com Enum/cor diferentes), por preferencia
    "Metal_Valve_Red": ("Metal_Dark", "Metal_Burnt", "Metal_Iron"),
    "Metal_Copper": ("Metal_Dark", "Metal_Burnt", "Metal_Iron"),
    "Metal_Brass": ("Metal_Iron", "Metal_Dark", "Metal_Burnt"),
    "Metal_Blade": ("Metal_Iron", "Metal_Dark"),
    "Cloth_Navy": ("Wood_Dark",), "Leather": ("Wood_Dark",), "Leather_Bellows": ("Leather", "Wood_Dark"),
    "Cloth_Canvas": ("Rope", "Wood_Light", "Wood_Plank"),
    "P_OP_Red": ("Cloth_Red",), "P_OP_Sail": ("Cloth_Canvas", "Rope"),
    "Leaf_Succulent": ("Leaf_Moss",), "P_Moss": ("Leaf_Moss", "Grass"), "P_Gravel": ("Dirt", "Stone_Dark"),
    "P_Shadow_Cloth": ("P_Shadow_Trim", "P_Shadow_Stone"), "P_Naruto_Orange": ("P_Naruto_Red",),
    "P_DS_Checker": ("P_DS_Char", "P_DS_Black"), "Hair_Red": ("Cloth_Red",), "Skin": ("Wood_Light",),
    "Fire_Glow_Outer": ("Fire_Glow_Mid", "Fire_Glow_Core", "Forge_Emissive"),
}
GLOBAL_SMALL_TRIS = 400      # material com menos tris que isso no lobby inteiro segue o FOLD_TO mesmo com area grande
FOLD_PROTECT = ("Flower_", "Emblem_", "Water", "Foam", "Crystal_", "Lantern_", "Window_Warm", "Forge_", "P_DB_Ball",
                "P_DB_Star")
NO_FOLD_OBJ = ("WATER_Waterwheel", "BLD_WheelHouse")     # fontes do export_vfx (trocadas pelas pecas moveis)
CORE_OF = {"Crystal_Blue": "Crystal_Blue_Core", "Crystal_Purple": "Crystal_Purple_Core"}

# ------------------------------------------------------------------ streaming / sombra / camera
CARVED = ("Carved", "Rosto", "Hokage", "Sculpt", "Monument")
SKYLINE_WHOLE = ("TER_Mountains_Peaks", "TER_Far_Valley")          # silhuetas: ficam inteiras (sem celulas)
SKYLINE_MODEL = ("TER_Mountains_Peaks", "TER_Mountains_Near", "TER_Far_Valley", "VEG_Mountain_Forest", "VEG_Deadwood")
BACKGROUND = ("TER_Mountains_", "TER_Far_Valley", "VEG_Mountain_Forest", "VEG_Deadwood")
SHADOW_DIST = 220.0
SHADOW_MIN = 12.0            # diagonal minima (studs) de uma MeshPart que projeta sombra ...
SHADOW_MIN_TRIS = 200        # ... e volume de detalhe minimo (ou diagonal >= SHADOW_BIG: parede grande e simples)
SHADOW_BIG = 30.0
# cascas visuais que a camera NAO pode atravessar (viram CanCollide/CanQuery no grupo 'SoVisual', que nao colide com
# os personagens): paredes/tetos dos interiores, tunel e camara da mina, penhascos e canion
SHELL_OBJ = ("FORGE_Hall_Walls", "FORGE_Hall_Roof", "FORGE_Wing_", "FORGE_Chimney_Tower", "FORGE_Loft",
             "FORGE_Furnace_Interior", "FORGE_Bellows_House", "BLD_Shop", "BLD_Cabin_", "BLD_WheelHouse",
             "MINE_Tunnel", "MINE_Chamber", "MINE_Entrance_Portal", "TER_Cliff_West", "TER_Cliff_East",
             "KONOHA_Canyon_Walls", "KONOHA_Gorge_Side")
SHELL_FAMILY = ("Stone_", "Wood_", "Plaster", "Roof", "Cliff_Rock", "Metal_", "Dirt", "Grass")
SHELL_MIN = 8.0
# COL com tag CollectionService 'CamOccluder' (para um PlayerModule com Popper que respeite a tag):
# area -> altura minima da caixa (paredes); caixas altas acima do piso contam como teto
CAM_COL_AREAS = {"Forge": 5.0, "ForgeInt": 5.0, "ForgeLoft": 5.0, "Shop": 5.0, "Cabin": 5.0,
                 "WheelHouse": 5.0, "Mine": 5.0, "WestCliff": 8.0, "EastCliff": 8.0, "Konoha": 8.0}

# ------------------------------------------------------------------ luzes
NIGHT_ONLY = ("L_Path_", "L_StairFoot_", "L_Bridge_", "L_Jetty", "L_SpawnStair", "L_MineGate_", "L_Stall_",
              "L_Konoha_Toro", "L_P_Naruto_Toro", "L_P_Naruto_Chochin", "L_DS_Eave", "L_Cabin_West_", "L_Cabin_East_",
              # lanternas externas que tambem nao aparecem de dia (meta <= 40 luzes ativas)
              "L_Konoha_0", "L_Shop_Door", "L_WheelHouse_Door")
LIGHT_SKIP = ("L_Hall_9_", "L_Hall_16_")      # o Neon da lanterna ja le
SHADOW_LIGHTS = ("L_Hearth_Fire",)
LIGHT_KEEP = ("L_Hearth_Fire", "L_Portal_", "L_Mine_Chamber", "L_Mine_Crystal")   # nunca rebaixadas pelo cluster
CLUSTER_R, CLUSTER_MAX = 20.0, 6

# Blender (x, y, z) -> FBX(-Z fwd, Y up) -> Roblox (x, z, -y). Mesmo mapeamento para colisoes/marcadores/luzes.
# O montar_lobby_forja.lua CONFERE isso na importacao (ALINHAR) e corrige rotacao/deslocamento/escala do importador.
T = Matrix(((1, 0, 0), (0, 0, 1), (0, -1, 0)))


def to_rbx(v):
    v = T @ Vector(v)
    return [round(v.x, 3), round(v.y, 3), round(v.z, 3)]


def tex_of(name):
    return fm_lib.tex_key(name)


def owner_of(name):
    for p, o in OWNERS:
        if name.startswith(p):
            return o
    return "outros"


def is_carved(name):
    return name.startswith(("TER_", "KONOHA_")) and any(k in name for k in CARVED)


def skyline_whole(name):
    return name.startswith(SKYLINE_WHOLE) or is_carved(name)


def skyline_model(name):
    return name.startswith(SKYLINE_MODEL) or is_carved(name)


def atomic_model(name):
    """Model Atomic (streaming sem pecas pela metade): forja inteira, cada construcao, cada portal, portao de Konoha"""
    if name.startswith("FORGE_"):
        return "FORGE"
    if name.startswith("BLD_"):
        return name
    if name.startswith("PORTAL_"):
        return "PORTAL_" + name.split("_")[1]
    if name.startswith("KONOHA_Great_Gate"):
        return "KONOHA_Great_Gate"
    return ""


# ------------------------------------------------------------------ geometria
def _uv_fallback(bm, uvl, name):
    """malha sem UVMap (objeto feito fora do MB): projecao CUBICA em coordenadas de mundo, em studs/TILE"""
    tk = tex_of(name)
    inv = 1.0 / (fm_lib.tex_tile(tk) if tk else 4.0)
    for f in bm.faces:
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        a, b = [(1, 2), (0, 2), (0, 1)][ax]
        for lp in f.loops:
            co = lp.vert.co
            lp[uvl].uv = (co[a] * inv, co[b] * inv)


def _uv_disc(bm, uvl):
    """espiral do portal: UV planar do disco (0..1). Normal = eixo MAIS FINO do bbox (o disco tem frente e verso,
    a soma das normais se anula), virada para -Y do mundo (frente dos portais); 'cima' do mundo = v."""
    if not bm.verts:
        return
    lo = Vector((min(v.co.x for v in bm.verts), min(v.co.y for v in bm.verts), min(v.co.z for v in bm.verts)))
    hi = Vector((max(v.co.x for v in bm.verts), max(v.co.y for v in bm.verts), max(v.co.z for v in bm.verts)))
    ext = hi - lo
    ax = min(range(3), key=lambda i: ext[i])
    nrm = Vector((0, 0, 0))
    nrm[ax] = 1.0
    if ax == 1:
        nrm = Vector((0, -1, 0))
    c = (lo + hi) / 2
    up = Vector((0, 0, 1)) - nrm * nrm.z
    if up.length < 1e-3:
        up = Vector((0, 1, 0))
    up.normalize()
    side = up.cross(nrm).normalized()
    R = max(((v.co - c) - nrm * (v.co - c).dot(nrm)).length for v in bm.verts) or 1.0
    for f in bm.faces:
        for lp in f.loops:
            d = lp.vert.co - c
            lp[uvl].uv = (0.5 + d.dot(side) / (2 * R), 0.5 + d.dot(up) / (2 * R))


def _islands(faces):
    """ilhas conexas (por vertice) de uma lista de faces"""
    par = {}

    def find(a):
        while par[a] != a:
            par[a] = par[par[a]]
            a = par[a]
        return a
    for f in faces:
        ids = [v.index for v in f.verts]
        for i in ids:
            par.setdefault(i, i)
        r0 = find(ids[0])
        for i in ids[1:]:
            r = find(i)
            if r != r0:
                par[r] = r0
    out = {}
    for f in faces:
        out.setdefault(find(f.verts[0].index), []).append(f)
    return list(out.values())


def _is_tip(faces):
    """ponta de cristal: ilha com >= 5 vertices colapsados num ponto (cone de raio ~0,02 do fm_parts)"""
    vs = list({v for f in faces for v in f.verts})
    if len(vs) > 64:
        return False
    for a in vs:
        k = sum(1 for b in vs if (a.co - b.co).length < 0.08)
        if k >= 5:
            return True
    return False


def _area(faces):
    return sum(f.calc_area() for f in faces)


def _fold(obname, by_mat, log, small=()):
    """materiais com menos de FOLD_AREA studs^2 no objeto vao para o vizinho dominante (FOLD_TO ou mesmo
    Enum.Material com cor parecida; Neon so em Neon de cor parecida). Materiais quase sem uso no lobby inteiro
    (small) seguem o FOLD_TO explicito mesmo com area grande. Nunca: Glass, transparentes, espirais, flores,
    emblemas, agua, cristais, lanternas."""
    if obname.startswith(NO_FOLD_OBJ) or len(by_mat) < 2:
        return by_mat
    area = {m: _area(fs) for m, fs in by_mat.items()}
    info = {m: (rbx_rule(m), mat_color(m)) for m in by_mat}

    def fixed(m):          # nunca sai do lugar
        (rm, tr, sh), _ = info[m]
        return rm == "Glass" or tr > 0 or m in fm_lib.SWIRLS or m.startswith(FOLD_PROTECT)

    def target_ok(m):      # pode receber
        (rm, tr, sh), _ = info[m]
        return rm != "Glass" and tr == 0 and m not in fm_lib.SWIRLS
    alive = set(by_mat)
    to = {}
    for m in sorted(by_mat, key=lambda k: area[k]):
        if fixed(m):
            continue
        rm = info[m][0][0]
        cm = info[m][1]
        tgt = None
        if area[m] >= FOLD_AREA:
            if m not in small:
                continue
            # quase sem uso no lobby: so o destino explicito, se existir no objeto
            cands = [o for o in alive if o != m and target_ok(o)]
            for want in FOLD_TO.get(m, ()):
                hit = [o for o in cands if o == want or family(o) == want]
                if hit:
                    tgt = max(hit, key=lambda o: area[o])
                    break
            if tgt:
                to[m] = tgt
                alive.discard(m)
            continue
        cands = [o for o in alive if o != m and area[o] > area[m] and target_ok(o)]
        if FOLD_TO.get(m):
            for want in FOLD_TO[m]:
                hit = [o for o in cands if o == want or family(o) == want]
                if hit:
                    tgt = max(hit, key=lambda o: area[o])
                    break
        if tgt is not None:
            pass
        elif rm == "Neon":
            # brilho so vai para outro brilho de cor parecida (brasa -> fogo); lanterna/cristal nunca se movem
            same = [o for o in cands if info[o][0][0] == "Neon" and math.dist(info[o][1], cm) <= FOLD_DIST_NEON]
            if same:
                tgt = max(same, key=lambda o: area[o])
        else:
            cands = [o for o in cands if info[o][0][0] != "Neon" and not o.startswith(FOLD_PROTECT)]
            for want in FOLD_TO.get(m, ()) + FOLD_TO.get(family(m), ()):
                hit = [o for o in cands if o == want or family(o) == want]
                if hit:
                    tgt = max(hit, key=lambda o: area[o])
                    break
            if tgt is None:
                same = [o for o in cands if info[o][0][0] == rm and
                        math.dist(info[o][1], cm) <= FOLD_DIST]
                if same:
                    tgt = max(same, key=lambda o: area[o])
        if tgt:
            to[m] = tgt
            alive.discard(m)
    if not to:
        return by_mat
    out = {}
    for m, fs in by_mat.items():
        t = m
        seen = set()
        while t in to and t not in seen:
            seen.add(t)
            t = to[t]
        out.setdefault(t, []).extend(fs)
    for m, t in to.items():
        log.append((obname, m, round(area[m], 1), t))
    return out


def _bbox(faces):
    vs = {v for f in faces for v in f.verts}
    xs = [v.co.x for v in vs]
    ys = [v.co.y for v in vs]
    zs = [v.co.z for v in vs]
    return Vector((min(xs), min(ys), min(zs))), Vector((max(xs), max(ys), max(zs)))


def _cells(faces):
    """fatiamento espacial: pedaco com bbox > CELL_TRIGGER em X ou Y (e >= CELL_MIN_TRIS) -> celulas de CELL pelo
    centroide da face; celulas leves (< CELL_KEEP_TRIS) juntam com a celula grande mais proxima"""
    lo, hi = _bbox(faces)
    if len(faces) < CELL_MIN_TRIS or ((hi.x - lo.x) <= CELL_TRIGGER and (hi.y - lo.y) <= CELL_TRIGGER):
        return [(None, faces)]
    cells = {}
    for f in faces:
        c = f.calc_center_median()
        k = (int(math.floor(c.x / CELL)) + 16, int(math.floor(c.y / CELL)) + 16)
        cells.setdefault(k, []).append(f)
    big = [k for k, fs in cells.items() if len(fs) >= CELL_KEEP_TRIS]
    if not big:
        big = [max(cells, key=lambda k: len(cells[k]))]
    out = {k: list(cells[k]) for k in big}
    for k, fs in cells.items():
        if k in out:
            continue
        tgt = min(big, key=lambda b: (max(abs(b[0] - k[0]), abs(b[1] - k[1])), -len(cells[b])))
        out[tgt].extend(fs)
    if len(out) == 1:
        return [(None, faces)]
    return sorted(out.items())


def _halve(chunks):
    """fatia ate cada pedaco caber em MAX_TRIS e MAX_AXIS (guarda generica do limite de 2048 da MeshPart)"""
    def bad(c):
        if len(c) > MAX_TRIS:
            return True
        lo, hi = _bbox(c)
        return max(hi.x - lo.x, hi.y - lo.y) > MAX_AXIS and len(c) > 1
    while any(bad(c) for c in chunks):
        new = []
        for c in chunks:
            if not bad(c):
                new.append(c)
                continue
            cs = [f.calc_center_median() for f in c]
            xs = [p.x for p in cs]
            ys = [p.y for p in cs]
            axis = 0 if (max(xs) - min(xs)) >= (max(ys) - min(ys)) else 1
            order = sorted(range(len(c)), key=lambda i: cs[i][axis])
            h = len(order) // 2
            new.append([c[i] for i in order[:h]])
            new.append([c[i] for i in order[h:]])
        chunks = new
    return chunks


def split_object(ob, fold=False, cells=False, cores=False, fold_log=None, remap=None, small=None):
    """retorna lista de (nome, mesh, material) - um por material (variante), fatiado se passar de MAX_TRIS ou de
    MAX_AXIS. Copia a UVMap do MB; sem UV -> projecao cubica de mundo; espirais -> UV do disco.
    Com os padroes (usados pelo export_vfx) o comportamento e o de sempre; o export estatico liga:
      fold  = materiais pequenos no vizinho dominante;  cells = celulas de 128 studs nos pedacos grandes;
      cores = pontas dos cristais viram *_Core (Neon)."""
    res = []
    me = ob.data
    mw = ob.matrix_world
    bm_all = bmesh.new()
    bm_all.from_mesh(me)
    bm_all.transform(mw)
    bmesh.ops.triangulate(bm_all, faces=bm_all.faces[:])
    bm_all.verts.index_update()
    bm_all.normal_update()
    uv_src = bm_all.loops.layers.uv.get("UVMap") or bm_all.loops.layers.uv.active
    far_valley = ob.name.startswith(FAR_VALLEY)
    plane_v = set()
    if far_valley:
        # plano gigante (2400 studs, coplanar com o FAR_GROUND) -> Part FAR_GROUND no Lua; sai com as bordas
        for f in bm_all.faces:
            if abs(f.normal.z) > 0.9 and f.calc_area() > 1e4:
                plane_v.update(v.index for v in f.verts)
    by_mat = {}
    for f in bm_all.faces:
        mi = f.material_index
        mname = me.materials[mi].name if mi < len(me.materials) and me.materials[mi] else "Default"
        if far_valley:
            if family(mname) in ("Grass_Dark", "Grass"):
                continue       # plano antigo do vale
            if plane_v and all(v.index in plane_v for v in f.verts):
                continue
        mname = fm_lib.alias(mname)
        if remap:
            mname = remap.get(mname, mname)
        by_mat.setdefault(mname, []).append(f)
    if cores:
        for m in list(by_mat):
            core = CORE_OF.get(m)
            if not core:
                continue
            keep, tips = [], []
            for isl in _islands(by_mat[m]):
                (tips if _is_tip(isl) else keep).extend(isl)
            if tips:
                by_mat[core] = by_mat.get(core, []) + tips
                if keep:
                    by_mat[m] = keep
                else:
                    del by_mat[m]
    if fold:
        by_mat = _fold(ob.name, by_mat, fold_log if fold_log is not None else [], small or ())
    for mname, faces in sorted(by_mat.items()):
        groups = _cells(faces) if (cells and not skyline_whole(ob.name)) else [(None, faces)]
        for cell, cfaces in groups:
            chunks = _halve([cfaces])
            for k, c in enumerate(chunks):
                bm = bmesh.new()
                uvl = bm.loops.layers.uv.new("UVMap")
                vmap = {}
                for f in c:
                    vs = []
                    for v in f.verts:
                        if v.index not in vmap:
                            vmap[v.index] = bm.verts.new(v.co)
                        vs.append(vmap[v.index])
                    try:
                        nf = bm.faces.new(vs)
                    except ValueError:
                        continue
                    if uv_src is not None:
                        for ln, lo in zip(nf.loops, f.loops):
                            ln[uvl].uv = lo[uv_src].uv
                bm.verts.index_update()
                bm.normal_update()
                if mname in fm_lib.SWIRLS or mname in TX.SWIRL_TEX:
                    _uv_disc(bm, uvl)
                elif uv_src is None:
                    _uv_fallback(bm, uvl, mname)
                name = "%s__%s" % (ob.name, mname)
                if cell is not None:
                    name += "_g%d_%d" % cell
                if len(chunks) > 1:
                    name += "_%d" % k
                nm = bpy.data.meshes.new(name)
                bm.to_mesh(nm)
                bm.free()
                res.append((name, nm, mname))
    bm_all.free()
    return res


# ------------------------------------------------------------------ materiais do FBX (texturas embutidas)
_EXP_MATS = {}


def export_material(mname):
    """material do FBX: familias texturizadas recebem a PNG de detalhe ligada DIRETO no Base Color (o exportador
    FBX so enxerga textura ligada direto); espirais recebem a PNG da espiral. Demais: o proprio material."""
    tk = tex_of(mname)
    swirl = mname if mname in TX.SWIRL_TEX else None
    if not tk and not swirl:
        m = bpy.data.materials.get(mname)
        if m is None:
            m = bpy.data.materials.new(mname)
            c = fm_lib.S(*rbx_color(mname))
            m.diffuse_color = (*c, 1.0)
        return m
    key = swirl or tk
    if key in _EXP_MATS:
        return _EXP_MATS[key]
    p = TX.swirl_path(swirl) if swirl else TX.path(tk)
    img = bpy.data.images.load(p, check_existing=False)
    img.name = "RBX_" + os.path.basename(p)
    m = bpy.data.materials.new("RBX_" + (("SWIRL_" + swirl) if swirl else ("TEX_" + tk)))
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bs = nt.nodes.new("ShaderNodeBsdfPrincipled")
    im = nt.nodes.new("ShaderNodeTexImage")
    im.image = img
    nt.links.new(im.outputs["Color"], bs.inputs["Base Color"])
    nt.links.new(bs.outputs[0], out.inputs[0])
    _EXP_MATS[key] = m
    return m


# ------------------------------------------------------------------ colisoes
def _col_box(o):
    mw = o.matrix_world
    R = mw.to_3x3().normalized()
    h = Vector([abs(s) / 2 for s in o.scale])
    c = mw.translation.copy()
    corners = [c + R @ Vector((sx * h.x, sy * h.y, sz * h.z)) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
    return {"o": o, "name": o.name, "kind": o.get("col_kind", "Block"), "c": c, "R": R, "h": h, "corners": corners,
            "lo": Vector((min(p.x for p in corners), min(p.y for p in corners), min(p.z for p in corners))),
            "hi": Vector((max(p.x for p in corners), max(p.y for p in corners), max(p.z for p in corners)))}


def _inside(p, b, tol=0.05):
    q = b["R"].transposed() @ (p - b["c"])
    return abs(q.x) <= b["h"].x + tol and abs(q.y) <= b["h"].y + tol and abs(q.z) <= b["h"].z + tol


def _same_rot(a, b):
    return all(abs(a["R"][i][j] - b["R"][i][j]) < 1e-4 for i in range(3) for j in range(3))


def _try_merge(a, b, tol=0.05):
    """une duas caixas de mesmo tipo/rotacao com secao identica que se tocam/sobrepoem num eixo (uniao exata)"""
    if a["kind"] != b["kind"] or not _same_rot(a, b):
        return None
    qa = a["R"].transposed() @ a["c"]
    qb = a["R"].transposed() @ b["c"]
    for ax in range(3):
        o1, o2 = [i for i in range(3) if i != ax]
        if abs(a["h"][o1] - b["h"][o1]) > tol or abs(a["h"][o2] - b["h"][o2]) > tol:
            continue
        if abs(qa[o1] - qb[o1]) > tol or abs(qa[o2] - qb[o2]) > tol:
            continue
        a0, a1 = qa[ax] - a["h"][ax], qa[ax] + a["h"][ax]
        b0, b1 = qb[ax] - b["h"][ax], qb[ax] + b["h"][ax]
        if b0 > a1 + tol or a0 > b1 + tol:
            continue
        lo, hi = min(a0, b0), max(a1, b1)
        q = qa.copy()
        q[ax] = (lo + hi) / 2
        h = a["h"].copy()
        h[ax] = (hi - lo) / 2
        return q, h, ax
    return None


def collisions(log):
    """COL_ -> caixas do Roblox. Descarta as totalmente contidas em outra do mesmo tipo (tolerancia 0,05; Block e Floor
    contam como caixa, Ramp so com Ramp) e une vizinhas de mesmo tipo com secao identica (uniao exata)."""
    boxes = [_col_box(o) for o in bpy.data.objects if o.name.startswith("COL_") and o.type == "MESH"]
    boxes.sort(key=lambda b: b["name"])
    dropped = []
    for b in boxes:
        if b.get("gone"):
            continue
        for a in boxes:
            if a is b or a.get("gone") or (a["kind"] == "Ramp") != (b["kind"] == "Ramp"):   # Block ~ Floor
                continue
            if not (a["lo"].x - 0.05 <= b["lo"].x and a["lo"].y - 0.05 <= b["lo"].y and a["lo"].z - 0.05 <= b["lo"].z
                    and b["hi"].x <= a["hi"].x + 0.05 and b["hi"].y <= a["hi"].y + 0.05 and
                    b["hi"].z <= a["hi"].z + 0.05):
                continue
            if all(_inside(p, a) for p in b["corners"]):
                b["gone"] = True
                dropped.append((b["name"], a["name"]))
                break
    live = [b for b in boxes if not b.get("gone")]
    merged = []
    changed = True
    while changed:
        changed = False
        i = 0
        while i < len(live):
            a = live[i]
            j = i + 1
            while j < len(live):
                b = live[j]
                if any(b["lo"][k] > a["hi"][k] + 0.05 or a["lo"][k] > b["hi"][k] + 0.05 for k in range(3)):
                    j += 1
                    continue
                r = _try_merge(a, b)
                if r is None:
                    j += 1
                    continue
                q, h, ax = r
                a["c"] = a["R"] @ q
                a["h"] = h
                cs = [a["c"] + a["R"] @ Vector((sx * h.x, sy * h.y, sz * h.z))
                      for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
                a["corners"] = cs
                a["lo"] = Vector((min(p.x for p in cs), min(p.y for p in cs), min(p.z for p in cs)))
                a["hi"] = Vector((max(p.x for p in cs), max(p.y for p in cs), max(p.z for p in cs)))
                merged.append((b["name"], a["name"]))
                del live[j]
                changed = True
            i += 1
    # caixa coberta pela UNIAO de outras (nenhuma sozinha a contem): amostra uma grade dentro dela (passo <= 0,75
    # stud) e descarta se todo ponto cai dentro de alguma outra caixa viva do mesmo tipo -> colisao identica
    covered = []
    for b in sorted(live, key=lambda b: (b["h"].x * b["h"].y * b["h"].z, b["name"])):
        near = [a for a in live if a is not b and not a.get("gone") and
                (a["kind"] == "Ramp") == (b["kind"] == "Ramp") and
                not any(a["lo"][k] > b["hi"][k] + 0.05 or b["lo"][k] > a["hi"][k] + 0.05 for k in range(3))]
        if len(near) < 2:
            continue
        axes = [np.linspace(-b["h"][k], b["h"][k], max(2, min(24, int(math.ceil(2 * b["h"][k] / 0.75)) + 1)))
                for k in range(3)]
        g = np.stack(np.meshgrid(*axes, indexing="ij"), -1).reshape(-1, 3)
        R = np.array(b["R"])
        P = g @ R.T + np.array(b["c"])
        ok = np.zeros(len(P), dtype=bool)
        for a in near:
            Ra = np.array(a["R"])
            q = (P - np.array(a["c"])) @ Ra
            ok |= np.all(np.abs(q) <= np.array(a["h"]) + 0.05, axis=1)
            if ok.all():
                break
        if ok.all():
            b["gone"] = True
            covered.append(b["name"])
    live = [b for b in live if not b.get("gone")]
    log["col_dropped"] = dropped
    log["col_merged"] = merged
    log["col_covered"] = covered
    out = []
    for b in live:
        R = b["R"]
        area = re.sub(r"^COL_(.*)_\d+$", r"\1", b["name"])
        height = b["hi"].z - b["lo"].z
        thr = CAM_COL_AREAS.get(area)
        cam = False
        if thr is not None and b["kind"] == "Block":
            ext = b["hi"] - b["lo"]
            cam = height >= thr or (area not in ("WestCliff", "EastCliff", "Konoha") and b["lo"].z >= 7.5
                                    and max(ext.x, ext.y) >= 6.0)
        out.append({"name": b["name"], "kind": b["kind"], "pos": to_rbx(b["c"]), "x": to_rbx(R.col[0]),
                    "y": to_rbx(R.col[1]), "size": [round(2 * b["h"].x, 3), round(2 * b["h"].y, 3),
                                                    round(2 * b["h"].z, 3)], "cam": cam})
    return out


def col_bvh():
    verts, polys = [], []
    for o in bpy.data.objects:
        if o.type != "MESH" or not o.name.startswith("COL_"):
            continue
        mw = o.matrix_world
        base = len(verts)
        verts += [mw @ v.co for v in o.data.vertices]
        polys += [[base + i for i in p.vertices] for p in o.data.polygons]
    return BVHTree.FromPolygons(verts, polys) if polys else None


def ground_z(bvh, x, y, z, up=2.5, down=8.0):
    if bvh is None:
        return None
    hit = bvh.ray_cast(Vector((x, y, z + up)), Vector((0, 0, -1)), up + down)
    return hit[0].z if hit[0] is not None else None


def headroom(bvh, x, y, z, h=6.0):
    hit = bvh.ray_cast(Vector((x, y, z + 0.3)), Vector((0, 0, 1)), h)
    return hit[0] is None


def safe_points(bvh, markers):
    """pontos seguros da rede de quedas: spawn, RESPAWN_*/SAFE_* e os pes das escadas/patamares (sobre COL)"""
    pts = []
    for m in markers:
        if m["name"].startswith(("SPAWN_", "RESPAWN_", "SAFE_")):
            pts.append({"name": m["name"], "pos": m["pos"]})
    try:
        import fm_layout as L
    except Exception:
        L = None
    cand = [("SAFE_Spawn", (0.0, -104.0), 0.0), ("SAFE_Avenida", (0.0, -80.0), 0.0), ("SAFE_Praca", (0.0, -40.0), 4.0),
            ("SAFE_Margem_Leste", (96.0, -18.0), 4.0), ("SAFE_Estrada_Oeste", (-44.0, 0.0), 4.0),
            ("SAFE_Loja", (20.0, -38.0), 4.0), ("SAFE_Konoha_Ponte", (-99.5, 190.0), 30.0)]
    if L:
        for i, px in enumerate(L.PORTAL_X):
            cand.append(("SAFE_Escada1_%d" % i, (px, L.FLIGHT1_Y0 - 3.0), L.FLOOR))
            cand.append(("SAFE_Ledge_%d" % i, (px, L.MID_FRONT_Y + 3.0), L.MID))
            cand.append(("SAFE_Terraco_%d" % i, (px, L.FLIGHT2_Y1 + 5.0), L.TERR))
        for i, (x, y) in enumerate(L.KONOHA_PATH):
            cand.append(("SAFE_Konoha_%d" % i, (x, y), L.TERR))
        mx, my = L.MINE_MOUTH
        cand.append(("SAFE_Mina", (mx - 9.0 * math.cos(L.MINE_DIR), my - 9.0 * math.sin(L.MINE_DIR)), L.FLOOR))
    for name, (x, y), z in cand:
        g = ground_z(bvh, x, y, z, up=12.0, down=24.0)
        if g is None or abs(g - z) > 12.0 or not headroom(bvh, x, y, g):
            continue
        pts.append({"name": name, "pos": to_rbx((x, y, g))})
    return pts


# ------------------------------------------------------------------ luzes
def lights():
    out = []
    for o in sorted(bpy.data.objects, key=lambda o: o.name):
        if o.type != "LIGHT" or o.data.type not in ("POINT", "SPOT") or o.name.startswith(LIGHT_SKIP):
            continue
        e = o.data.energy
        rng0 = min(60, 8 + math.sqrt(e) * 1.1)
        br0 = min(4.0, 0.6 + e / 800.0)
        rng_, br = min(20.0, rng0 * 0.35), min(1.5, br0 * 0.5)
        if o.name.startswith("L_Portal_"):
            rng_, br = 14.0, 1.0
        L = {"name": o.name, "type": o.data.type, "pos": to_rbx(o.location), "color": srgb(o.data.color),
             "range": round(rng_, 1), "brightness": round(br, 2),
             "shadows": o.name.startswith(SHADOW_LIGHTS), "night": o.name.startswith(NIGHT_ONLY), "_loc": o.location}
        if o.data.type == "SPOT":
            d = o.matrix_world.to_3x3() @ Vector((0, 0, -1))
            L["dir"] = to_rbx(d.normalized())
            L["angle"] = round(min(180.0, math.degrees(o.data.spot_size)), 1)
        out.append(L)
    # meta: <= CLUSTER_MAX luzes ativas por cluster de CLUSTER_R studs (as mais fracas viram NightOnly)
    keep = [l for l in out if not l["night"]]
    keep.sort(key=lambda l: (not (l["name"].startswith(LIGHT_KEEP) or l["name"].endswith("_Pad")), -l["brightness"],
                             -l["range"]))
    acc = []
    demoted = []
    for l in keep:
        near = sum(1 for a in acc if (a["_loc"] - l["_loc"]).length <= CLUSTER_R)
        protected = l["name"].startswith(LIGHT_KEEP) or l["name"].endswith("_Pad")
        if near >= CLUSTER_MAX and not protected:
            l["night"] = True
            demoted.append(l["name"])
        else:
            acc.append(l)
    for l in out:
        del l["_loc"]
    return out, demoted


# ------------------------------------------------------------------ sol do Roblox = sol do Blender
def sun_setup():
    """ClockTime e GeographicLatitude que fazem Lighting:GetSunDirection() apontar para o sol da cena.
    Modelo do Roblox (G3D LightingParameters, conferido no Studio: 15,4 h / lat 22 -> (-0,777; 0,629; -0,026)):
      sol = (sin a * cos t, -cos a * cos t, -sin t), a = 2 pi ClockTime / 24, t = 23,5 graus - latitude."""
    suns = [o for o in bpy.data.objects if o.type == "LIGHT" and o.data.type == "SUN"]
    sun = bpy.data.objects.get("SUN_Key") or (max(suns, key=lambda o: o.data.energy) if suns else None)
    if sun is not None:
        d = (sun.matrix_world.to_3x3() @ Vector((0, 0, 1))).normalized()     # da cena PARA o sol
        r = Vector(to_rbx(d)).normalized()
    else:
        r = Vector((-0.77, 0.50, 0.41)).normalized()
    t = -math.asin(max(-1.0, min(1.0, r.z)))
    lat = 23.5 - math.degrees(t)
    ct = max(1e-6, math.cos(t))
    a = math.atan2(r.x / ct, -r.y / ct)
    clock = (a / (2 * math.pi) * 24.0) % 24.0
    chk = Vector((math.sin(a) * ct, -math.cos(a) * ct, -math.sin(t)))
    return round(clock, 3), round(max(-90.0, min(90.0, lat)), 3), [round(x, 4) for x in r], (chk - r).length


def lighting_cfg(clock, lat):
    return {
        "Lighting": {"GeographicLatitude": lat, "ClockTime": clock, "EnvironmentDiffuseScale": 0.4,
                     "EnvironmentSpecularScale": 0.5, "Brightness": 2.5, "ExposureCompensation": 0.0,
                     "ShadowSoftness": 0.2, "OutdoorAmbient": [118, 128, 152], "Ambient": [90, 92, 104],
                     "ColorShift_Top": [255, 236, 210]},
        "ColorCorrectionEffect": {"Saturation": 0.15, "Contrast": 0.12, "TintColor": [255, 246, 236]},
        "BloomEffect": {"Threshold": 1.3, "Intensity": 0.6, "Size": 28},
        "Atmosphere": {"Density": 0.34, "Offset": 0.05, "Haze": 1.8, "Glare": 0.1, "Color": [199, 214, 235],
                       "Decay": [106, 128, 168]},
    }


LIGHTING_LOBBY = lighting_cfg(14.2, 64.0)     # (valor de modulo; o export recalcula pelo sol da cena)


# ------------------------------------------------------------------ export
def piece_flags(obname, mname, c, sz, tris):
    """sombra so onde le (perto, fora do fundo/interiores, peca que faz sombra visivel) + flags de camera/skyline"""
    rm, tr, sh = rbx_rule(mname)
    shadow = bool(sh)
    if math.hypot(c.x, c.y) > SHADOW_DIST or obname.startswith(BACKGROUND) or is_carved(obname):
        shadow = False
    if "_Interior" in obname:                      # BLD_*_Interior, FORGE_Interior_Props, FORGE_Furnace_Interior
        shadow = False
    if sz.length <= SHADOW_MIN or (tris < SHADOW_MIN_TRIS and sz.length < SHADOW_BIG):
        shadow = False
    flags = ""
    dims = sorted((sz.x, sz.y, sz.z))
    if obname.startswith(SHELL_OBJ) and mname.startswith(SHELL_FAMILY) and dims[1] >= SHELL_MIN and \
            sz.z >= 5.0 and rm not in ("Neon", "Glass"):
        flags += "o"
    if skyline_model(obname):
        flags += "k"
    return shadow, flags


def export_objects(g):
    col = bpy.data.collections.get(g)
    if not col:
        return []
    objs = [o for o in col.all_objects if o.type == "MESH" and not o.name.startswith(SKIP_PREFIX)
            and o.name not in SKIP_NAMES]
    return sorted(objs, key=lambda o: o.name)


def variant_remap():
    """variantes pouco usadas no lobby inteiro (< VARIANT_MIN_TRIS) voltam para a base da familia: menos materiais
    e menos MeshParts, sem mudar o que se ve (as variantes sao tons proximos da base)"""
    tot = {}
    for g in GROUPS:
        for o in export_objects(g):
            if o.name.startswith(NO_FOLD_OBJ):
                continue
            ms = o.data.materials
            for p in o.data.polygons:
                mi = p.material_index
                n = fm_lib.alias(ms[mi].name) if mi < len(ms) and ms[mi] else "Default"
                tot[n] = tot.get(n, 0) + len(p.vertices) - 2
    remap = {}
    for n, t in tot.items():
        base = fm_lib.VARIANT_OF.get(n)
        if base and base != n and base in fm_lib.MATS and t < VARIANT_MIN_TRIS:
            remap[n] = base
    small = {n for n, t in tot.items() if t < GLOBAL_SMALL_TRIS}
    return remap, small


def collect(log, extra=None):
    """divide todas as malhas visuais em pedacos (sem gravar nada). extra = remapeamento global de materiais
    (teto de materiais), somado ao das variantes pouco usadas."""
    tmp = bpy.data.collections.new("_EXPORT_TMP")
    bpy.context.scene.collection.children.link(tmp)
    pieces = []
    fold_log = []
    remap, small = variant_remap()
    log["remap"] = dict(remap)
    if extra:
        remap.update(extra)
        for k in list(remap):          # cadeias (variante -> base -> vizinho) resolvidas num passo
            t, seen = remap[k], {k}
            while t in remap and t not in seen:
                seen.add(t)
                t = remap[t]
            remap[k] = t
    for g in GROUPS:
        for o in export_objects(g):
            rm = None if o.name.startswith(NO_FOLD_OBJ) else remap
            for name, nm, mname in split_object(o, fold=True, cells=True, cores=True, fold_log=fold_log, remap=rm,
                                                small=small):
                if not nm.vertices:
                    bpy.data.meshes.remove(nm)
                    continue
                xs = [v.co.x for v in nm.vertices]
                ys = [v.co.y for v in nm.vertices]
                zs = [v.co.z for v in nm.vertices]
                lo = Vector((min(xs), min(ys), min(zs)))
                hi = Vector((max(xs), max(ys), max(zs)))
                c = (lo + hi) / 2          # origem no CENTRO DO BBOX = MeshPart.Position no Roblox
                sz = hi - lo
                nm.transform(Matrix.Translation(-c))
                em = export_material(mname)
                if em is not None:
                    nm.materials.append(em)
                ob = bpy.data.objects.new(name, nm)
                ob.location = c
                tmp.objects.link(ob)
                shadow, flags = piece_flags(o.name, mname, c, sz, len(nm.polygons))
                pieces.append({"ob": ob, "name": name, "group": g, "obj": o.name, "material": mname,
                               "tris": len(nm.polygons), "center_rbx": to_rbx(c),
                               "size_rbx": [round(sz.x, 3), round(sz.z, 3), round(sz.y, 3)],
                               "owner": owner_of(o.name), "shadow": shadow, "flags": flags,
                               "model": atomic_model(o.name)})
    log["fold"] = fold_log
    return tmp, pieces


def discard(tmp, pieces):
    for p in pieces:
        if "ob" in p:
            me = p["ob"].data
            bpy.data.objects.remove(p["ob"], do_unlink=True)
            bpy.data.meshes.remove(me)
    bpy.data.collections.remove(tmp)


def same_hue(a, b):
    """duas cores sRGB (0-255) podem ser trocadas pelo teto de materiais? Cinzas entre si sim; cor saturada so com
    cor de matiz parecido (<= 25 graus); cinza com cor saturada nao"""
    ha, sa, _ = colorsys.rgb_to_hsv(*[x / 255.0 for x in a])
    hb, sb, _ = colorsys.rgb_to_hsv(*[x / 255.0 for x in b])
    if sa < 0.18 and sb < 0.18:
        return True
    if min(sa, sb) < 0.18:
        return max(sa, sb) < 0.3
    d = abs(ha - hb)
    return min(d, 1.0 - d) <= 25.0 / 360.0


def material_cap(pieces, limit):
    """teto GLOBAL de materiais (a meta nao e de nenhum dono): se o lobby passar de 'limit', os materiais menos usados
    vao para o material mais parecido de mesmo Enum.Material (cor sRGB a <= CAP_DIST; Neon so em Neon a <=
    FOLD_DIST_NEON) que tenha pelo menos o mesmo uso. Nunca: Glass, transparentes, espirais, FOLD_PROTECT e os
    materiais das fontes do export_vfx (NO_FOLD_OBJ). Retorna {material: destino}."""
    tris, locked = {}, set()
    for p in pieces:
        tris[p["material"]] = tris.get(p["material"], 0) + p["tris"]
        if p["obj"].startswith(NO_FOLD_OBJ):
            locked.add(p["material"])
    if len(tris) <= limit:
        return {}
    info = {m: (rbx_rule(m), mat_color(m)) for m in tris}

    def free(m):
        (rm, tr, sh), _ = info[m]
        return not (rm == "Glass" or tr > 0 or m in fm_lib.SWIRLS or m in TX.SWIRL_TEX or m.startswith(FOLD_PROTECT))
    extra = {}
    n = len(tris)
    for m in sorted(tris, key=lambda k: (tris[k], k)):
        if n <= limit:
            break
        if m in locked or not free(m):
            continue
        (rm, tr, sh), c = info[m]
        lim = FOLD_DIST_NEON if rm == "Neon" else CAP_DIST
        cands = [o for o in tris if o != m and o not in extra and free(o) and info[o][0][0] == rm and
                 tris[o] >= tris[m] and math.dist(info[o][1], c) <= lim and same_hue(info[o][1], c)]
        if not cands:
            continue
        extra[m] = min(cands, key=lambda o: (math.dist(info[o][1], c), -tris[o], o))
        n -= 1
    return extra


def cap_shadows(pieces, limit):
    """teto GLOBAL de MeshParts com sombra: se passar, as de menor prioridade (tamanho / distancia do centro)
    deixam de projetar sombra. Retorna os nomes cortados."""
    on = [p for p in pieces if p["shadow"]]
    if len(on) <= limit:
        return []

    def prio(p):
        c = p["center_rbx"]
        return Vector(p["size_rbx"]).length / (1.0 + math.hypot(c[0], c[2]) / 110.0)
    on.sort(key=lambda p: (prio(p), p["name"]))
    cut = on[:len(on) - limit]
    for p in cut:
        p["shadow"] = False
    return [p["name"] for p in cut]


def budget_report(pieces, n_mats, n_col, day_lights):
    per = {}
    for p in pieces:
        t = per.setdefault(p["owner"], [0, 0])
        t[0] += p["tris"]
        t[1] += 1
    tris = sum(p["tris"] for p in pieces)
    lines = ["ORCAMENTO por dono (tris / MeshParts; limite entre parenteses)"]
    over = []
    for o in sorted(set(per) | set(BUDGET_OWNER)):
        t, m = per.get(o, (0, 0))
        bt, bm = BUDGET_OWNER.get(o, (None, None))
        bad = bt is not None and (t > bt or m > bm)
        if bad:
            over.append(o)
        lines.append("  %-15s %7d (%s)  %4d (%s)%s" % (o, t, bt if bt else "-", m, bm if bm else "-",
                                                       "  <-- ESTOUROU" if bad else ""))
    shadow = sum(1 for p in pieces if p["shadow"])
    glob_ = [("tris estaticos", tris, BUDGET["static_tris"]), ("MeshParts estaticas", len(pieces), BUDGET["static_meshes"]),
             ("tris total (+ reserva VFX %d)" % BUDGET["vfx_tris"], tris + BUDGET["vfx_tris"], BUDGET["total_tris"]),
             ("MeshParts total (+ reserva VFX %d)" % BUDGET["vfx_meshes"], len(pieces) + BUDGET["vfx_meshes"],
              BUDGET["total_meshes"]),
             ("materiais", n_mats, BUDGET["materials"]), ("MeshParts com sombra", shadow, BUDGET["shadow_meshes"]),
             ("luzes ativas de dia", day_lights, BUDGET["day_lights"]), ("COL", n_col, BUDGET["col"])]
    lines.append("METAS GLOBAIS")
    for k, v, lim in glob_:
        bad = v > lim
        if bad:
            over.append(k)
        lines.append("  %-38s %7d / %-7d%s" % (k, v, lim, "  <-- ESTOUROU" if bad else ""))
    return lines, over, per


def main():
    TX.ensure()
    log = {}
    tmp, pieces = collect(log)
    extra = material_cap(pieces, BUDGET["materials"])
    if extra:
        # teto de materiais: refaz a divisao com o remapeamento (as faces remapeadas juntam com as do destino)
        discard(tmp, pieces)
        tmp, pieces = collect(log, extra)
    log["mat_cap"] = extra
    log["shadow_cut"] = cap_shadows(pieces, BUDGET["shadow_meshes"])
    names = sorted(p["name"] for p in pieces)
    export_id = "%08x" % (zlib.crc32("\n".join(names).encode("utf-8")) & 0xffffffff)
    id6 = export_id[:6]
    used = {}
    for p in pieces:
        used[p["material"]] = used.get(p["material"], 0) + 1
    cols = collisions(log)
    bvh = col_bvh()
    # marcadores (NPC_/PLAYER_ assentados na COL de baixo)
    markers = []
    snapped = []
    for o in sorted(bpy.data.objects, key=lambda o: o.name):
        if o.type == "EMPTY" and any(o.users_collection) and o.users_collection[0].name == "15_GAMEPLAY_MARKERS":
            R = o.matrix_world.to_3x3().normalized()
            props = {}
            for k, v in o.items():
                if isinstance(v, (bool, int, float, str)):
                    props[k] = v
                else:
                    try:
                        props[k] = list(v)
                    except TypeError:
                        props[k] = str(v)
            loc = o.location.copy()
            if o.name.startswith(("NPC_", "PLAYER_")):
                g = ground_z(bvh, loc.x, loc.y, loc.z, up=2.5, down=2.5)
                if g is not None and abs(g - loc.z) > 1e-3:
                    snapped.append((o.name, round(loc.z, 3), round(g, 3)))
                    loc.z = g
            markers.append({"name": o.name, "pos": to_rbx(loc), "x": to_rbx(R.col[0]), "y": to_rbx(R.col[1]),
                            "props": props})
    log["snapped"] = snapped
    if not any(m["name"].startswith("SPAWN") for m in markers):
        try:
            import fm_layout
            sp = fm_layout.SPAWN
        except Exception:
            sp = (0.0, -104.0, 0.0)
        markers.append({"name": "SPAWN_Lobby", "pos": to_rbx((sp[0], sp[1], sp[2] + 3.0)),
                        "x": to_rbx((1, 0, 0)), "y": to_rbx((0, 1, 0)),
                        "props": {"kind": "spawn", "note": "chegada do lobby, de frente para a avenida (+Y Blender)"}})
    lts, demoted = lights()
    day = sum(1 for l in lts if not l["night"])
    lines, over, per = budget_report(pieces, len(used), len(cols), day)
    clock, lat, sun_r, sun_err = sun_setup()
    for ln in lines:
        print(ln)
    if over and BUDGET_MODE != "warn":
        print("EXPORT FALHOU: orcamento estourado (%s). Nada foi gravado. FM_BUDGET=warn grava mesmo assim."
              % ", ".join(over))
        discard(tmp, pieces)
        sys.stdout.flush()
        os._exit(3)
    os.makedirs(OUT, exist_ok=True)
    data = {"mapping": "Roblox = (x_blender, z_blender, -y_blender); 1 BU = 1 stud; malha: origem = centro do bbox",
            "export_id": export_id, "fbx": {}, "meshes": [], "materials": {}, "textures": {}, "collisions": cols,
            "markers": markers, "lights": lts, "far_ground": None, "void_catch": None, "safe_points": [],
            "sun_rbx": sun_r, "lighting_lobby": lighting_cfg(clock, lat), "budget": {"lines": lines, "over": over}}
    # FBX por grupo (nome novo por EXPORT_ID; apaga os anteriores do mesmo grupo)
    for g in GROUPS:
        made = [p for p in pieces if p["group"] == g]
        fn = "LOBBY_%s_%s.fbx" % (g, id6)
        for old in glob.glob(os.path.join(OUT, "LOBBY_%s*.fbx" % g)):
            b = os.path.basename(old)
            if b != fn and re.match(r"^LOBBY_%s(_[0-9a-f]{6})?\.fbx$" % re.escape(g), b):
                os.remove(old)
        if not made:
            continue
        bpy.ops.object.select_all(action="DESELECT")
        for p in made:
            p["ob"].select_set(True)
        bpy.context.view_layer.objects.active = made[0]["ob"]
        path = os.path.join(OUT, fn)
        bpy.ops.export_scene.fbx(filepath=path, use_selection=True, axis_forward="-Z", axis_up="Y",
                                 apply_scale_options="FBX_SCALE_ALL", mesh_smooth_type="FACE", path_mode="COPY",
                                 embed_textures=True, add_leaf_bones=False, bake_anim=False,
                                 use_mesh_modifiers=True, object_types={"MESH"})
        data["fbx"][g] = fn
        print("FBX", fn, len(made), "malhas", sum(p["tris"] for p in made), "tris", os.path.getsize(path) // 1024, "KB")
    for p in pieces:
        me = p["ob"].data
        bpy.data.objects.remove(p["ob"], do_unlink=True)
        bpy.data.meshes.remove(me)
        del p["ob"]
        data["meshes"].append(p)
    bpy.data.collections.remove(tmp)
    for mname in sorted(used):
        m = bpy.data.materials.get(mname)
        rm, tr, sh = rbx_rule(mname)
        swirl = mname if mname in TX.SWIRL_TEX else None
        data["materials"][mname] = {"color": rbx_color(mname, m), "material": rm, "transparency": tr,
                                    "shadow": sh, "family": family(mname), "tex": tex_of(mname),
                                    "swirl": swirl, "meshes": used[mname]}
    for k, (fn, tile) in sorted(TX.TEXTURES.items()):
        data["textures"][k] = {"file": "textures/" + fn, "studs_per_tile": tile}
    for k, (fn, arm, core) in sorted(TX.SWIRL_TEX.items()):
        data["textures"][k] = {"file": "textures/" + fn, "uv": "disco 0..1", "portal": TX.SWIRL_SPEC[k]["portal"],
                               "arm": list(arm), "core": list(core)}
    fg = dict(FAR_GROUND)
    fg["color"] = rbx_color(FAR_GROUND["material"])
    fg["pos"] = to_rbx((0, 0, FAR_GROUND["top_z"] - FAR_GROUND["size"][1] / 2))
    data["far_ground"] = fg
    data["void_catch"] = {"size": VOID_CATCH["size"], "pos": [0.0, VOID_CATCH["y"], 0.0]}
    data["safe_points"] = safe_points(bvh, markers)
    json.dump(data, open(os.path.join(OUT, "lobby_data.json"), "w"), indent=1)
    write_lua(data)
    # relatorio
    n_cam = sum(1 for c in cols if c["cam"])
    n_occ = sum(1 for p in data["meshes"] if "o" in p["flags"])
    print("VARIANTES pouco usadas (< %d tris) -> base: %s" % (VARIANT_MIN_TRIS, log["remap"]))
    print("FOLD: %d materiais pequenos fundidos no vizinho dominante" % len(log["fold"]))
    for f in log["fold"][:12]:
        print("   %s: %s (%.1f studs2) -> %s" % f)
    print("TETO DE MATERIAIS (%d): %s" % (BUDGET["materials"], log["mat_cap"] or "nao precisou"))
    print("TETO DE SOMBRA (%d): %d MeshParts perderam a sombra %s" % (
        BUDGET["shadow_meshes"], len(log["shadow_cut"]), log["shadow_cut"][:12]))
    print("COL: %d contidas descartadas, %d cobertas pela uniao de outras, %d unidas a vizinhas; %d com tag "
          "CamOccluder" % (len(log["col_dropped"]), len(log["col_covered"]), len(log["col_merged"]), n_cam))
    for a, b in log["col_dropped"]:
        print("   descartada %s (dentro de %s)" % (a, b))
    if log["col_covered"]:
        print("   cobertas: %s" % ", ".join(log["col_covered"]))
    print("CAMERA: %d cascas visuais ocluem a camera (grupo SoVisual)" % n_occ)
    print("MARCADORES assentados na COL:", log["snapped"])
    print("LUZES: %d exportadas, %d ativas de dia, %d NightOnly (%d rebaixadas pelo cluster %s)" % (
        len(lts), day, len(lts) - day, len(demoted), demoted))
    print("SOL: ClockTime %.3f  GeographicLatitude %.3f  -> GetSunDirection esperado %s (erro do modelo %.1e)" % (
        clock, lat, sun_r, sun_err))
    print("SEGURANCA: %d pontos seguros para o VOID_CATCH" % len(data["safe_points"]))
    print("EXPORT OK id=%s malhas=%d tris=%d materiais=%d col=%d marcadores=%d luzes=%d (dia %d) sombra=%d -> %s" % (
        export_id, len(data["meshes"]), sum(p["tris"] for p in data["meshes"]), len(data["materials"]),
        len(cols), len(markers), len(lts), day, sum(1 for p in data["meshes"] if p["shadow"]), OUT))
    if over:
        print("AVISO: orcamento estourado (%s) - gravado porque FM_BUDGET=warn" % ", ".join(over))


# ------------------------------------------------------------------ Lua
def lua_val(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, (list, tuple)):
        return "{" + ",".join(lua_val(x) for x in v) + "}"
    s = str(v).replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
    return "'" + s + "'"


def lua_str(s):
    return lua_val(str(s))


def write_lua(data):
    L = []
    A = L.append
    A("-- montar_lobby_forja.lua  (gerado por export_roblox.py - nao editar a mao)  EXPORT_ID %s" % data["export_id"])
    A("-- 1) Importe os FBX LOBBY_*_%s.fbx (3D Importer) para dentro de workspace.LOBBY_FORJA. Deixe o importador" %
      data["export_id"][:6])
    A("--    subir as TEXTURAS embutidas. ESPERE as texturas processarem (as MeshParts ficam BRANCAS por alguns")
    A("--    minutos) antes de 'corrigir' cor: o branco some sozinho.")
    A("-- 2) Rode este script na Command Bar. Ele:")
    A("--    - CONFERE a importacao: achadas/esperadas por FBX, malhas faltando, MeshParts com eixo > 2048, texturas;")
    A("--      normaliza nomes trocados pelo importador ('.001', ' (1)');")
    A("--    - ALINHA cada MeshPart na posicao certa (aborta se algum FBX tiver < 90% das malhas);")
    A("--    - aplica cor/Material por VARIANTE, sombra POR MALHA (longe/fundo/interior nao projetam), fidelidade")
    A("--      (Box / Automatic; SKYLINE em Performance), streaming (SKYLINE persistente, modelos atomicos);")
    A("--    - camera: as cascas dos interiores/penhascos ocluem a camera (grupo 'SoVisual', que nao colide com os")
    A("--      personagens: o Script LOBBY_FORJA_Servidor poe os personagens no grupo 'Personagens');")
    A("--    - cria COLISOES invisiveis (tag CamOccluder nas paredes/tetos), MARCADORES, LUZES (NightOnly desligadas),")
    A("--      chao distante, VOID_CATCH (rede de seguranca de quedas) e, opcional, o Lighting do lobby.")
    A("-- Recomendado no Workspace: StreamingEnabled = true, StreamingTargetRadius = 1024, StreamingMinRadius = 128.")
    A("-- Rodar de novo e seguro (idempotente). Ids de textura encontrados sao impressos: cole em TEX para fixar.")
    A("local EXPORT_ID = %s" % lua_str(data["export_id"]))
    A("local ROOT_OFFSET = Vector3.new(0, 0, 0)  -- desloca o lobby INTEIRO (malhas alinhadas + colisoes + marcadores + luzes)")
    A("local ALINHAR = true      -- reposiciona as MeshParts pelos centros exportados (corrige o importador)")
    A("local RICO = false        -- true = texturas de detalhe (SurfaceAppearance Overlay) nas familias pedra/madeira/telha/rocha/grama/reboco/terra")
    A("local LISO = false        -- true = tudo SmoothPlastic (menos Neon/Metal/Glass), sem os materiais ricos do modo hibrido")
    A("local CAMERA_CASCAS = true  -- true = cascas visuais ocluem a camera (CanCollide/CanQuery no grupo SoVisual)")
    A("local APLICAR_LIGHTING = false  -- true = aplica o Lighting recomendado do lobby (GLOBAL: prefira o perfil em AreaAtmosphere)")
    A("local root = workspace:FindFirstChild('LOBBY_FORJA') or Instance.new('Model', workspace)")
    A("root.Name = 'LOBBY_FORJA'")
    A("root:SetAttribute('EXPORT_ID', EXPORT_ID); root:SetAttribute('RICO', RICO)")
    A("local CS = game:GetService('CollectionService')")
    A("local PS = game:GetService('PhysicsService')")
    A("local function folder(n) local f = root:FindFirstChild(n) or Instance.new('Folder'); f.Name = n; f.Parent = root; return f end")
    A("local COLF, MKF, LTF = folder('COLLISION'), folder('GAMEPLAY_MARKERS'), folder('LIGHTS')")
    A("local function cf(p, x, y) local px = Vector3.new(p[1],p[2],p[3]) + ROOT_OFFSET")
    A("  local vx = Vector3.new(x[1],x[2],x[3]); local vy = Vector3.new(y[1],y[2],y[3])")
    A("  return CFrame.fromMatrix(px, vx, vy) end")
    A("local function grupo(n) pcall(function() if not PS:IsCollisionGroupRegistered(n) then PS:RegisterCollisionGroup(n) end end) end")
    A("grupo('SoVisual'); grupo('Personagens')")
    A("pcall(function() PS:CollisionGroupSetCollidable('SoVisual', 'Personagens', false) end)")
    # texturas
    A("-- ids das texturas (rbxassetid://...). Vazio = usa o que o 3D Importer subiu (lido das MeshParts).")
    A("-- Alternativa: suba as PNG de textures/ pelo Asset Manager e cole os ids aqui.")
    A("local TEX = {")
    for k, v in sorted(data["textures"].items()):
        A("  [%s] = '',  -- %s%s" % (lua_str(k), v["file"], (" (%s studs por repeticao)" % v["studs_per_tile"])
                                     if "studs_per_tile" in v else " (espiral, UV do disco)"))
    A("}")
    # materiais
    A("-- material/variante -> c = cor calibrada no Studio, m = Enum.Material (hibrido), t = transparencia,")
    A("--   s = CastShadow da familia, x = textura de detalhe, w = espiral")
    A("local MAT = {")
    for k, v in sorted(data["materials"].items()):
        A("  [%s] = {c = Color3.fromRGB(%d,%d,%d), m = Enum.Material.%s, t = %s, s = %s, x = %s, w = %s}," % (
            lua_str(k), v["color"][0], v["color"][1], v["color"][2], v["material"], v["transparency"],
            lua_val(v["shadow"]), lua_str(v["tex"]) if v["tex"] else "nil",
            lua_str(v["swirl"]) if v["swirl"] else "nil"))
    A("}")
    A("local KEEP = {[Enum.Material.Neon]=true, [Enum.Material.Metal]=true, [Enum.Material.Glass]=true, [Enum.Material.CorrodedMetal]=true}")
    A("local function norm(n) n = string.gsub(n, '%.%d+$', ''); n = string.gsub(n, ' %(%d+%)$', ''); return n end")
    A("local function matOf(name)")
    A("  local s = string.match(name, '__(.+)$'); if not s then return nil end")
    A("  if MAT[s] then return MAT[s], s end")
    A("  s = string.gsub(string.gsub(s, '_%d+$', ''), '_g%d+_%d+$', '')  -- fatias _k e celulas _gX_Y")
    A("  if MAT[s] then return MAT[s], s end")
    A("  local best, bl = nil, 0   -- tolerante: maior prefixo conhecido (variantes/materiais novos)")
    A("  for k, v in pairs(MAT) do if #k > bl and string.sub(s, 1, #k) == k then best, bl = v, #k end end")
    A("  return best, s")
    A("end")
    # malhas esperadas
    gidx = {g: i + 1 for i, g in enumerate(GROUPS)}
    A("-- FBX: indice -> arquivo")
    A("local FBX = {%s}" % ", ".join("[%d]=%s" % (gidx[g], lua_str(data["fbx"].get(g, "LOBBY_%s.fbx" % g)))
                                     for g in GROUPS))
    A("-- malhas exportadas: nome = {centro X,Y,Z, tamanho X,Y,Z, FBX, sombra, material, flags, modelo}")
    A("--   flags: o = casca que oclui a camera, k = SKYLINE (persistente, RenderFidelity Performance)")
    A("--   modelo: Model Atomic (streaming sem pecas pela metade)")
    A("local MESH = {")
    for m in data["meshes"]:
        A("  [%s]={%s,%s,%s,%s,%s,%s,%d,%s,%s,%s,%s}," % (
            lua_str(m["name"]), *m["center_rbx"], *m["size_rbx"], gidx[m["group"]], lua_val(m["shadow"]),
            lua_str(m["material"]), lua_str(m["flags"]), lua_str(m["model"])))
    A("}")
    A(LUA_CHECK)
    A(LUA_ALIGN)
    A(LUA_APPLY)
    # colisoes
    A("-- colisoes: {nome, tipo, pos, eixoX, eixoY, tamanho, camera}")
    A("local COL = {")
    for c in data["collisions"]:
        A("  {%s,%s,{%s,%s,%s},{%s,%s,%s},{%s,%s,%s},{%s,%s,%s},%s}," % (
            lua_str(c["name"]), lua_str(c["kind"]), *c["pos"], *c["x"], *c["y"], *c["size"], lua_val(c["cam"])))
    A("}")
    A("COLF:ClearAllChildren()")
    A("for _, c in ipairs(COL) do")
    A("  local p = Instance.new('Part'); p.Name = c[1]; p.Anchored = true; p.CanCollide = true")
    A("  p.Transparency = 1; p.CastShadow = false; p.CanTouch = false; p.Material = Enum.Material.SmoothPlastic")
    A("  p.Size = Vector3.new(c[6][1], c[6][2], c[6][3]); p.CFrame = cf(c[3], c[4], c[5])")
    A("  p:SetAttribute('kind', c[2]); if c[7] then CS:AddTag(p, 'CamOccluder') end; p.Parent = COLF")
    A("end")
    # marcadores
    A("local MK = {")
    for m in data["markers"]:
        props = ",".join("[%s]=%s" % (lua_str(k), lua_val(v)) for k, v in m["props"].items()
                         if not isinstance(v, (list, tuple)))
        A("  {%s,{%s,%s,%s},{%s,%s,%s},{%s,%s,%s},{%s}}," % (lua_str(m["name"]), *m["pos"], *m["x"], *m["y"], props))
    A("}")
    A("MKF:ClearAllChildren()")
    A("for _, m in ipairs(MK) do")
    A("  local p = Instance.new('Part'); p.Name = m[1]; p.Anchored = true; p.CanCollide = false; p.CanQuery = false")
    A("  p.CanTouch = false; p.CastShadow = false; p.Transparency = 1; p.Size = Vector3.new(1,1,1); p.CFrame = cf(m[2], m[3], m[4])")
    A("  for k, v in pairs(m[5]) do p:SetAttribute(k, v) end")
    A("  p.Parent = MKF")
    A("end")
    # luzes
    A("-- luzes: {nome, tipo, pos, cor, alcance, brilho, sombra, noturna, direcao(spot), angulo(spot)}")
    A("-- noturna = Enabled false + atributo NightOnly (o ciclo dia/noite liga: for _, l in LIGHTS:GetDescendants() ...)")
    A("local LT = {")
    for l in data["lights"]:
        extra = ""
        if l["type"] == "SPOT":
            extra = ",{%s,%s,%s},%s" % (*l["dir"], l["angle"])
        A("  {%s,%s,{%s,%s,%s},{%d,%d,%d},%s,%s,%s,%s%s}," % (
            lua_str(l["name"]), lua_str(l["type"]), *l["pos"], *l["color"], l["range"], l["brightness"],
            lua_val(l["shadows"]), lua_val(l["night"]), extra))
    A("}")
    A("LTF:ClearAllChildren()")
    A("local nDia = 0")
    A("for _, l in ipairs(LT) do")
    A("  local a = Instance.new('Part'); a.Name = l[1]; a.Anchored = true; a.CanCollide = false; a.CanQuery = false")
    A("  a.CanTouch = false; a.CastShadow = false; a.Transparency = 1; a.Size = Vector3.new(0.5,0.5,0.5)")
    A("  local pos = Vector3.new(l[3][1], l[3][2], l[3][3]) + ROOT_OFFSET")
    A("  if l[2] == 'SPOT' and l[9] then a.CFrame = CFrame.lookAt(pos, pos + Vector3.new(l[9][1], l[9][2], l[9][3])) else a.CFrame = CFrame.new(pos) end")
    A("  local pl = Instance.new(l[2] == 'SPOT' and 'SpotLight' or 'PointLight')")
    A("  pl.Color = Color3.fromRGB(l[4][1], l[4][2], l[4][3]); pl.Range = l[5]; pl.Brightness = l[6]; pl.Shadows = l[7]")
    A("  pl.Enabled = not l[8]; if l[8] then a:SetAttribute('NightOnly', true); pl:SetAttribute('NightOnly', true) else nDia += 1 end")
    A("  if l[2] == 'SPOT' then pl.Face = Enum.NormalId.Front; if l[10] then pl.Angle = l[10] end end")
    A("  pl.Parent = a; a.Parent = LTF")
    A("end")
    # chao distante
    fg = data["far_ground"]
    A("-- chao do vale distante (o plano de 2400 studs do Blender NAO e exportado: era coplanar e dava z-fighting)")
    A("do local g = root:FindFirstChild('FAR_GROUND') or Instance.new('Part'); g.Name = 'FAR_GROUND'")
    A("  g.Anchored = true; g.CanCollide = false; g.CanTouch = false; g.CanQuery = false; g.CastShadow = false")
    A("  g.Size = Vector3.new(%s,%s,%s); g.Position = Vector3.new(%s,%s,%s) + ROOT_OFFSET" % (
        *fg["size"], *fg["pos"]))
    A("  g.Color = Color3.fromRGB(%d,%d,%d); g.Material = Enum.Material.SmoothPlastic" % tuple(fg["color"]))
    A("  local sk = root:FindFirstChild('SKYLINE'); g.Parent = sk or root end")
    # rede de seguranca
    vc = data["void_catch"]
    A("-- rede de seguranca: quem cai do lobby volta ao ponto seguro mais proximo (spawn, RESPAWN_*, pes de escada)")
    A("local SAFE = {")
    for s in data["safe_points"]:
        A("  {%s,{%s,%s,%s}}," % (lua_str(s["name"]), *s["pos"]))
    A("}")
    A("do local v = root:FindFirstChild('VOID_CATCH') or Instance.new('Part'); v.Name = 'VOID_CATCH'")
    A("  v.Anchored = true; v.CanCollide = false; v.CanTouch = true; v.CanQuery = false; v.Transparency = 1; v.CastShadow = false")
    A("  v.Size = Vector3.new(%s,%s,%s); v.Position = Vector3.new(%s,%s,%s) + ROOT_OFFSET" % (*vc["size"], *vc["pos"]))
    A("  v:ClearAllChildren()")
    A("  for _, s in ipairs(SAFE) do local at = Instance.new('Attachment'); at.Name = s[1]; at.Parent = v")
    A("    at.WorldPosition = Vector3.new(s[2][1], s[2][2], s[2][3]) + ROOT_OFFSET end")
    A("  v.Parent = root end")
    A(LUA_SERVER)
    A(lua_lighting(data["lighting_lobby"], data["sun_rbx"]))
    A("print(string.format('LOBBY_FORJA montado (EXPORT_ID %s): %d colisoes, %d marcadores, %d luzes (%d de dia), %d pontos seguros', EXPORT_ID, #COL, #MK, #LT, nDia, #SAFE))")
    src = "\n".join(L) + "\n"
    open(os.path.join(OUT, "montar_lobby_forja.lua"), "w", encoding="utf-8", newline="\n").write(src)


LUA_CHECK = r"""
-- CONFERENCIA DA IMPORTACAO: nomes normalizados, achadas/esperadas por FBX, faltando, eixo > 2048, duplicadas
local ACH, DUP = {}, 0
for _, d in ipairs(root:GetDescendants()) do
  if d:IsA('MeshPart') then
    local n = norm(d.Name)
    if MESH[n] then
      if ACH[n] and ACH[n] ~= d then DUP += 1
      else ACH[n] = d; if d.Name ~= n then d.Name = n end end
    end
  end
end
local POR, TOT, FALTA = {}, {}, {}
for n, e in pairs(MESH) do
  TOT[e[7]] = (TOT[e[7]] or 0) + 1
  if ACH[n] then POR[e[7]] = (POR[e[7]] or 0) + 1 else table.insert(FALTA, n) end
end
table.sort(FALTA)
local FBX_OK = true
for i, f in pairs(FBX) do
  local a, t = POR[i] or 0, TOT[i] or 0
  if t > 0 then
    local ok = a >= 0.9 * t
    if not ok then FBX_OK = false end
    print(string.format('IMPORT %-34s %4d / %4d %s', f, a, t, ok and 'ok' or '<-- FALTANDO (reimporte este FBX)'))
  end
end
if #FALTA > 0 then
  print(string.format('IMPORT: %d malhas faltando; as 20 primeiras:', #FALTA))
  for i = 1, math.min(20, #FALTA) do print('   ' .. FALTA[i]) end
end
if DUP > 0 then warn(string.format('IMPORT: %d MeshParts duplicadas (FBX importado 2 vezes?) - apague as sobras', DUP)) end
local GRANDE = 0
for _, d in ipairs(root:GetDescendants()) do
  if d:IsA('MeshPart') and math.max(d.Size.X, d.Size.Y, d.Size.Z) > 2048 then GRANDE += 1; warn('IMPORT: eixo > 2048: ' .. d:GetFullName()) end
end
print(string.format('IMPORT: %d MeshParts com eixo > 2048', GRANDE))
"""

LUA_ALIGN = r"""
-- ALINHAMENTO: compara as MeshParts importadas com MESH (Procrustes discreto no plano XZ) e corrige
local function alinhar()
  if not FBX_OK then warn('ALINHAR: abortado - algum FBX tem menos de 90% das malhas (veja IMPORT acima)'); return end
  local parts = {}
  for n, d in pairs(ACH) do table.insert(parts, d) end
  if #parts < 3 then warn('ALINHAR: poucas MeshParts com nome conhecido - confira se o importador manteve os nomes'); return end
  -- centroides POR FBX (grupo): tolera o importador recentralizar cada arquivo separadamente
  local G = {}
  for _, p in ipairs(parts) do local e = MESH[p.Name]
    local g = G[e[7]]; if not g then g = {ca = Vector3.zero, ce = Vector3.zero, n = 0}; G[e[7]] = g end
    g.ca += p.Position; g.ce += Vector3.new(e[1], e[2], e[3]); g.n += 1 end
  for _, g in pairs(G) do g.ca /= g.n; g.ce /= g.n end
  local function rel(p) local e = MESH[p.Name]; local g = G[e[7]]
    return p.Position - g.ca, Vector3.new(e[1], e[2], e[3]) - g.ce end
  local sa, se = 0, 0
  for _, p in ipairs(parts) do local a, b = rel(p); sa += a.Magnitude; se += b.Magnitude end
  local escala = (se > 0) and (sa / se) or 1
  local best, bestErr, bestMirror = 0, math.huge, false
  for _, mir in ipairs({false, true}) do
    for k = 0, 3 do
      local R = CFrame.Angles(0, k * math.pi / 2, 0); local err = 0
      for _, p in ipairs(parts) do
        local a, b = rel(p)
        if mir then b = Vector3.new(-b.X, b.Y, b.Z) end
        err += (a - R:VectorToWorldSpace(b) * escala).Magnitude
      end
      if err < bestErr then best, bestErr, bestMirror = k, err, mir end
    end
  end
  if bestMirror then warn('ALINHAR: o importador ESPELHOU o lobby. Nao da para corrigir aqui: troque a matriz T no export_roblox.py / eixos do FBX.') end
  if best ~= 0 then warn(string.format('ALINHAR: importador girou %d graus em Y - corrigindo', best * 90)) end
  if math.abs(escala - 1) > 0.05 then warn(string.format('ALINHAR: escala do importador %.3f (m->stud?) - corrigindo Size', escala)) end
  local Rinv = CFrame.Angles(0, -best * math.pi / 2, 0)
  for _, p in ipairs(parts) do local e = MESH[p.Name]
    if math.abs(escala - 1) > 0.05 then p.Size = p.Size / escala end
    local rot = p.CFrame - p.CFrame.Position
    p.CFrame = CFrame.new(Vector3.new(e[1], e[2], e[3]) + ROOT_OFFSET) * Rinv * rot
  end
  print(string.format('ALINHAR: ok (giro %d, escala %.3f, espelho %s)', best * 90, escala, tostring(bestMirror)))
end
if ALINHAR then alinhar() end
"""

LUA_APPLY = r"""
-- texturas: le os ids que o 3D Importer subiu (TextureID ou SurfaceAppearance) por familia
local function lerMapa(d)
  local ok, v = pcall(function() return d.TextureID end)
  if ok and v and v ~= '' then return v end
  local sa = d:FindFirstChildOfClass('SurfaceAppearance')
  if sa then
    local ok2, v2 = pcall(function() return sa.ColorMap end)
    if ok2 and v2 and v2 ~= '' then return v2 end
    local ok3, v3 = pcall(function() return sa.ColorMapContent.Uri end)
    if ok3 and v3 and v3 ~= '' then return v3 end
  end
  return nil
end
local function porMapa(sa, id)
  local ok = pcall(function() sa.ColorMap = id end)
  if not ok then ok = pcall(function() sa.ColorMapContent = Content.fromUri(id) end) end
  return ok
end
local function entrada(d)
  local e = MESH[d.Name]
  if e and MAT[e[9]] then return MAT[e[9]], e end
  return matOf(d.Name), e
end
local achados = {}
for _, d in ipairs(root:GetDescendants()) do
  if d:IsA('MeshPart') then
    local m = entrada(d)
    local key = m and (m.w or m.x)
    if key and (TEX[key] == nil or TEX[key] == '') then
      local id = lerMapa(d)
      if id then TEX[key] = id; achados[key] = id end
    end
  end
end
local nAch = 0
for k, v in pairs(achados) do nAch += 1; print('TEX encontrada', k, v) end
print(string.format('IMPORT: %d texturas encontradas nas MeshParts', nAch))
-- modelos de streaming: SKYLINE (persistente) e um Model Atomic por construcao/portal/forja
local MODELOS = {}
local function modelo(nome, modo)
  local m = MODELOS[nome]
  if m then return m end
  m = root:FindFirstChild(nome)
  if not (m and m:IsA('Model')) then m = Instance.new('Model'); m.Name = nome; m.Parent = root end
  pcall(function() m.ModelStreamingMode = modo end)
  MODELOS[nome] = m
  return m
end
-- aplica cor/material/sombra/textura por variante
local nOk, nSem, nTex, nSombra, nCasca = 0, 0, 0, 0, 0
for _, d in ipairs(root:GetDescendants()) do
  if d:IsA('MeshPart') then
    local m, e = entrada(d)
    d.Anchored = true; d.CanCollide = false; d.CanTouch = false; d.CanQuery = false
    pcall(function() d.CollisionFidelity = Enum.CollisionFidelity.Box end)
    pcall(function() d.RenderFidelity = Enum.RenderFidelity.Automatic end)
    if m then
      nOk += 1
      d.Color = m.c; d.Transparency = m.t
      d.Material = (LISO and not KEEP[m.m]) and Enum.Material.SmoothPlastic or m.m
      if e then d.CastShadow = e[8] else d.CastShadow = m.s and (d.Size.Magnitude > 4) end
      if d.CastShadow then nSombra += 1 end
      local sa = d:FindFirstChildOfClass('SurfaceAppearance')
      local sw = m.w and TEX[m.w] or ''
      local tx = m.x and TEX[m.x] or ''
      if m.w and sw ~= '' then
        -- espiral do portal: textura sempre (sem ela o disco vira um circulo chapado)
        if sa then sa:Destroy() end
        d.TextureID = sw; d.Material = Enum.Material.SmoothPlastic; nTex += 1
      elseif RICO and tx ~= '' then
        d.TextureID = ''
        if not sa then sa = Instance.new('SurfaceAppearance') end
        sa.AlphaMode = Enum.AlphaMode.Overlay
        if porMapa(sa, tx) then sa.Parent = d; nTex += 1
        else sa:Destroy(); d.TextureID = tx; nTex += 1 end
      else
        d.TextureID = ''
        if sa then sa:Destroy() end
      end
    else
      nSem += 1
    end
    if e then
      local fl = e[10] or ''
      if CAMERA_CASCAS and string.find(fl, 'o', 1, true) then
        -- casca que oclui a camera: o Popper so considera pecas CanCollide/CanQuery e opacas; o grupo SoVisual
        -- colide com Default (raio da camera) e NAO com Personagens (quem anda sao as COL invisiveis)
        d.CanCollide = true; d.CanQuery = true; d.CollisionGroup = 'SoVisual'
        pcall(function() d.CollisionFidelity = Enum.CollisionFidelity.PreciseConvexDecomposition end)
        nCasca += 1
      else
        d.CollisionGroup = 'Default'
      end
      if string.find(fl, 'k', 1, true) then
        pcall(function() d.RenderFidelity = Enum.RenderFidelity.Performance end)
        d.Parent = modelo('SKYLINE', Enum.ModelStreamingMode.Persistent)
      elseif e[11] and e[11] ~= '' then
        d.Parent = modelo(e[11], Enum.ModelStreamingMode.Atomic)
      end
    end
  end
end
print(string.format('MATERIAIS: %d MeshParts com variante reconhecida, %d sem (ficaram como vieram), %d texturizadas, %d com sombra, %d cascas de camera', nOk, nSem, nTex, nSombra, nCasca))
"""

LUA_SERVER = r"""
-- Script de servidor: personagens no grupo 'Personagens' (atravessam as cascas SoVisual) + rede de quedas
do
  local SSS = game:GetService('ServerScriptService')
  local s = SSS:FindFirstChild('LOBBY_FORJA_Servidor') or Instance.new('Script')
  s.Name = 'LOBBY_FORJA_Servidor'
  s.Source = [==[
-- gerado por montar_lobby_forja.lua (export_roblox.py) - nao editar a mao
local Players = game:GetService('Players')
local PhysicsService = game:GetService('PhysicsService')
local RunService = game:GetService('RunService')
pcall(function()
  for _, n in ipairs({'SoVisual', 'Personagens'}) do
    if not PhysicsService:IsCollisionGroupRegistered(n) then PhysicsService:RegisterCollisionGroup(n) end
  end
  PhysicsService:CollisionGroupSetCollidable('SoVisual', 'Personagens', false)
end)
local function grupo(inst) if inst:IsA('BasePart') then inst.CollisionGroup = 'Personagens' end end
local chao = setmetatable({}, {__mode = 'k'})   -- personagem -> Y do ultimo chao pisado
local function personagem(ch)
  for _, d in ipairs(ch:GetDescendants()) do grupo(d) end
  ch.DescendantAdded:Connect(grupo)
end
local function jogador(p)
  p.CharacterAdded:Connect(personagem)
  if p.Character then personagem(p.Character) end
end
Players.PlayerAdded:Connect(jogador)
for _, p in ipairs(Players:GetPlayers()) do jogador(p) end
-- rede de seguranca
local root = workspace:WaitForChild('LOBBY_FORJA', 60)
local catch = root and root:WaitForChild('VOID_CATCH', 60)
if not catch then return end
local seguros = {}
for _, a in ipairs(catch:GetChildren()) do if a:IsA('Attachment') then table.insert(seguros, a.WorldPosition) end end
local topo = catch.Position.Y + catch.Size.Y / 2
local ult = setmetatable({}, {__mode = 'k'})
local function dentro(p)
  local c, s = catch.Position, catch.Size
  return math.abs(p.X - c.X) <= s.X / 2 and math.abs(p.Z - c.Z) <= s.Z / 2
end
local function resgatar(ch)
  local hrp = ch:FindFirstChild('HumanoidRootPart'); if not hrp then return end
  local p = hrp.Position
  -- so quem caiu DO LOBBY (ultimo chao acima da rede): nao mexe em quem anda em areas mais baixas
  if not (chao[ch] and chao[ch] > topo + 8) or p.Y > topo or not dentro(p) then return end
  if ult[ch] and os.clock() - ult[ch] < 1 then return end
  ult[ch] = os.clock()
  local best, bd = nil, math.huge
  for _, s in ipairs(seguros) do
    local d = (Vector3.new(s.X, 0, s.Z) - Vector3.new(p.X, 0, p.Z)).Magnitude
    if d < bd then best, bd = s, d end
  end
  if not best then return end
  hrp.AssemblyLinearVelocity = Vector3.zero
  ch:PivotTo(CFrame.new(best + Vector3.new(0, 3.5, 0)) * (hrp.CFrame - hrp.CFrame.Position))
  chao[ch] = best.Y
end
catch.Touched:Connect(function(hit)
  local ch = hit.Parent
  if ch and ch:FindFirstChildOfClass('Humanoid') then resgatar(ch) end
end)
local acc = 0
RunService.Heartbeat:Connect(function(dt)
  acc += dt
  if acc < 0.2 then return end
  acc = 0
  for _, pl in ipairs(Players:GetPlayers()) do
    local ch = pl.Character
    local hum = ch and ch:FindFirstChildOfClass('Humanoid')
    local hrp = ch and ch:FindFirstChild('HumanoidRootPart')
    if hum and hrp then
      if hum.FloorMaterial ~= Enum.Material.Air then chao[ch] = hrp.Position.Y end
      if hrp.Position.Y < topo then resgatar(ch) end
    end
  end
end)
]==]
  s.Parent = SSS
end
"""


def lua_lighting(cfg, sun):
    L = ["if APLICAR_LIGHTING then", "  local Lg = game:GetService('Lighting')"]
    for k, v in cfg["Lighting"].items():
        if isinstance(v, list):
            L.append("  Lg.%s = Color3.fromRGB(%d,%d,%d)" % (k, *v))
        else:
            L.append("  Lg.%s = %s" % (k, v))
    for cls, props in cfg.items():
        if cls == "Lighting":
            continue
        L.append("  do local e = Lg:FindFirstChildOfClass('%s') or Instance.new('%s', Lg)" % (cls, cls))
        for k, v in props.items():
            if isinstance(v, list):
                L.append("    e.%s = Color3.fromRGB(%d,%d,%d)" % (k, *v))
            else:
                L.append("    e.%s = %s" % (k, v))
        L.append("  end")
    L.append("  local d = Lg:GetSunDirection()")
    L.append("  print(string.format('Lighting do lobby aplicado: sol (%%.2f, %%.2f, %%.2f), esperado (%.2f, %.2f, %.2f) = sol do Blender'," %
             tuple(sun) + " d.X, d.Y, d.Z))")
    L.append("  print('(lembre de devolver GeographicLatitude=22 nos perfis das ilhas)')")
    L.append("end")
    return "\n".join(L)


if __name__ == "__main__":
    main()
