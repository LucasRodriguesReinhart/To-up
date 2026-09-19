# lv_layout.py - montagem do lobby completo em colecoes de export + plano de vegetacao.
# Colecoes: LV_PISO, LV_PRACA, LV_FORJA, LV_PORTAO, LV_LATERAIS, LV_KITVEG.
# A vegetacao NAO e cozida no mapa: masters no LV_KITVEG + placements.json
# (o Studio clona, padrao da rodada de vegetacao anterior).
import math, json, os, random
import importlib
import lvlib, lv_kit, lv_floor, lv_build
for m in (lvlib, lv_kit, lv_floor, lv_build):
    importlib.reload(m)
import bpy
from lvlib import B, coll, clear_collection

TAU = math.tau
FLOOR = lv_floor.FLOOR
TERR = lv_floor.TERR
EXPORT = lvlib.EXPORT

CHUNKS = ['LV_PISO', 'LV_PRACA', 'LV_FORJA', 'LV_PORTAO', 'LV_LATERAIS', 'LV_KITVEG']

def _clear_all():
    for name in CHUNKS:
        c = bpy.data.collections.get(name)
        if c:
            clear_collection(c)

def build_piso(mats):
    C = coll('LV_PISO')
    out = B('piso', C, mats)
    lv_floor.base_platform(out)
    lv_floor.water_ring(out)
    lv_floor.axis_walks(out)
    lv_floor.medallion(out)
    lv_floor.gazebo_islands(out)
    lv_floor.south_stairs_and_edge(out)
    lv_floor.north_terrace(out)
    lv_floor.side_terraces(out)
    lv_floor.garden_aprons(out)
    return out.finish()

def build_praca(mats):
    C = coll('LV_PRACA')
    out = B('praca', C, mats)
    R_ISLE = (lv_floor.R_CAN_IN + lv_floor.R_CAN_OUT) / 2
    # gazebos nas 4 diagonais
    for a in lv_floor.GAZ_ANGLES:
        cx, cy = math.cos(a) * R_ISLE, math.sin(a) * R_ISLE
        lv_kit.gazebo(out, (cx, cy, FLOOR), rot=a)
    # pontes leste/oeste sobre o canal
    for s in (-1, 1):
        lv_kit.bridge(out, (s * 59, 0, 4.72), rot=0, L=26, W=9)
    # postes: anel da praca central (8, nos cantos do octogono, fora dos eixos)
    for i in range(8):
        a = i / 8 * TAU + TAU / 16
        if abs(math.sin(a)) > .92 or abs(math.cos(a)) > .92:
            continue
        px, py = math.cos(a) * (lv_floor.R_PLAZA - 4), math.sin(a) * (lv_floor.R_PLAZA - 4)
        lv_kit.lamp_post(out, (px, py, FLOOR))
    # postes do boulevard sul (pares a cada 24)
    for yy in range(-64, -150, -28):
        for s in (-1, 1):
            lv_kit.lamp_post(out, (s * 18.5, yy, FLOOR))
    # postes do tramo norte + terraco
    for yy in (58, 84):
        for s in (-1, 1):
            lv_kit.lamp_post(out, (s * 18.5, yy, FLOOR if yy < 80 else TERR))
    # postes dos terracos laterais (cantos)
    for s in (-1, 1):
        for yy in (-38, 38):
            lv_kit.lamp_post(out, (s * 96, yy, TERR))
    # balaustrada do anel externo (borda da plataforma octogonal, com vaos nos eixos)
    RO = lv_floor.R_OUTER - 1.2
    pts = lvlib.reg_poly(RO, 8, lv_floor.ROT8)
    for i in range(8):
        p1 = pts[i]
        p2 = pts[(i + 1) % 8]
        mid = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
        # pula os lados atravessados pelos eixos N/S/L/O
        if abs(mid[0]) < 20 or abs(mid[1]) < 20:
            # lado do eixo: 2 trechos curtos com vao central
            for t0, t1 in ((.05, .32), (.68, .95)):
                q1 = (p1[0] + (p2[0]-p1[0])*t0, p1[1] + (p2[1]-p1[1])*t0)
                q2 = (p1[0] + (p2[0]-p1[0])*t1, p1[1] + (p2[1]-p1[1])*t1)
                lv_kit.balustrade(out, q1, q2, FLOOR)
        else:
            lv_kit.balustrade(out, (p1[0]*.98 + p2[0]*.02, p1[1]*.98 + p2[1]*.02),
                              (p1[0]*.02 + p2[0]*.98, p1[1]*.02 + p2[1]*.98), FLOOR)
        lv_kit.rail_post(out, p1, FLOOR)
    # balaustrada da borda interna do canal (protege a praca), com vaos p/ passarelas e eixos
    RI = lv_floor.R_CAN_IN - 2.2
    ptsi = lvlib.reg_poly(RI, 8, lv_floor.ROT8)
    for i in range(8):
        p1 = ptsi[i]
        p2 = ptsi[(i + 1) % 8]
        mid = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
        if abs(mid[0]) < 18 or abs(mid[1]) < 18:
            continue  # eixos
        # vao central para a passarela do gazebo
        for t0, t1 in ((.04, .30), (.70, .96)):
            q1 = (p1[0] + (p2[0]-p1[0])*t0, p1[1] + (p2[1]-p1[1])*t0)
            q2 = (p1[0] + (p2[0]-p1[0])*t1, p1[1] + (p2[1]-p1[1])*t1)
            lv_kit.balustrade(out, q1, q2, FLOOR)
    # canteiros com arvore nos 4 cantos da praca (entre eixos e passarelas)
    for i in range(4):
        a = i / 4 * TAU + TAU / 8
        px, py = math.cos(a) * 30, math.sin(a) * 30
        lv_kit.planter(out, (px, py, FLOOR), r=4.6)
    # fontes nos jardins
    for s in (-1, 1):
        lv_kit.fountain(out, (s * 56, -74, FLOOR - .1))
        lv_kit.fountain(out, (s * 84, 84, FLOOR - .1), r=5.2)
    # estandartes no boulevard
    for yy in (-78, -122):
        for s in (-1, 1):
            lv_kit.banner(out, (s * 13.5, yy, FLOOR), rot=math.pi/2 if s < 0 else math.pi/2, cloth='BLUE')
    # cristais decorativos perto do portao (identidade mineracao)
    for s in (-1, 1):
        lv_kit.crystal_cluster(out, (s * 34, -142, FLOOR), seed=7 + s)
    # nenufares e pedras no canal
    rng = random.Random(42)
    R_ISLE_IN, R_ISLE_OUT = lv_floor.R_CAN_IN + 3, lv_floor.R_CAN_OUT - 3
    for i in range(16):
        a = rng.uniform(0, TAU)
        # evita eixos e ilhas dos gazebos
        if abs(math.sin(a)) > .9 or abs(math.cos(a)) > .9:
            continue
        skip = False
        for ga in lv_floor.GAZ_ANGLES:
            if abs((a - ga + math.pi) % TAU - math.pi) < .35:
                skip = True
        if skip:
            continue
        rr = rng.uniform(R_ISLE_IN, R_ISLE_OUT)
        px, py = math.cos(a) * rr, math.sin(a) * rr
        if i % 2 == 0:
            lv_kit.lily_pad(out, (px, py, lv_floor.WATER_Z + .05), r=rng.uniform(.7, 1.3), seed=i)
        else:
            lv_kit.canal_rock(out, (px, py, lv_floor.BASIN_Z + .6), r=rng.uniform(1.0, 2.0), seed=i)
    return out.finish()

def build_forja(mats):
    C = coll('LV_FORJA')
    out = B('forja', C, mats)
    lv_build.forge(out)
    lv_build.wall_fountains(out)
    return out.finish()

def build_portao(mats):
    C = coll('LV_PORTAO')
    out = B('portao', C, mats)
    lv_build.south_gate(out)
    return out.finish()

def build_laterais(mats):
    C = coll('LV_LATERAIS')
    out = B('laterais', C, mats)
    lv_build.santuario(out, side=1)
    lv_build.loja(out, side=-1)
    lv_build.perimeter(out)
    return out.finish()

# ---------------------------------------------------------------- kit de vegetacao (masters)
VEG_MASTERS = {
    'VegArvoreAzul':   ('CommonTree_1', {0: 'TRUNK', 1: 'LEAFAZ'}),
    'VegArvoreAzul2':  ('CommonTree_1', {0: 'TRUNK', 1: 'LEAFAZ2'}),
    'VegArvoreOuro':   ('CommonTree_1', {0: 'TRUNK', 1: 'LEAFGD'}),
    'VegArvoreOuro2':  ('CommonTree_1', {0: 'TRUNK', 1: 'LEAFGD2'}),
    'VegArvoreLilas':  ('CommonTree_1', {0: 'TRUNK', 1: 'LEAFLV'}),
    'VegArvoreVerde':  ('CommonTree_1', {0: 'TRUNK', 1: 'LEAFVD'}),
    'VegPalmeira':     ('Environment_PalmTree_3', None),
    'VegArbustoFlor':  ('Bush_Common_Flowers', {0: 'LEAFVD', 1: 'FLORRS'}),
    'VegArbustoFlorBr': ('Bush_Common_Flowers', {0: 'LEAFVD2', 1: 'FLORBR'}),
    'VegArbusto':      ('Bush_Common', {0: 'LEAFVD'}),
    'VegArbustoAzul':  ('Bush_Common', {0: 'LEAFAZ2'}),
}

def build_kitveg(mats):
    C = coll('LV_KITVEG')
    made = []
    x = 0
    for name, (src, remap) in VEG_MASTERS.items():
        srco = bpy.data.objects.get(src)
        if not srco:
            print('FALTA master', src)
            continue
        cp = srco.copy()
        cp.data = srco.data.copy()
        cp.name = name
        C.objects.link(cp)
        cp.parent = None
        # NORMALIZA: aplica a matriz de mundo na malha e poe a origem na base central
        cp.data.transform(srco.matrix_world)
        cp.matrix_world = __import__('mathutils').Matrix.Identity(4)
        vs = cp.data.vertices
        if len(vs):
            xs = [v.co.x for v in vs]; ys = [v.co.y for v in vs]; zs = [v.co.z for v in vs]
            cx0, cy0, z0 = (min(xs)+max(xs))/2, (min(ys)+max(ys))/2, min(zs)
            cp.data.transform(__import__('mathutils').Matrix.Translation((-cx0, -cy0, -z0)))
        cp.location = (x, -70, 0)
        if remap:
            for slot_i, matname in remap.items():
                if slot_i < len(cp.material_slots):
                    cp.material_slots[slot_i].material = mats[matname]
        made.append(name)
        x += 18
    # pecas procedurais tambem viram masters clonaveis
    out = B('kitveg', C, mats)
    lv_kit.grass_tuft(out, (x, -70, 0), seed=3)
    lv_kit.crystal_cluster(out, (x + 12, -70, 0), r=1.6, h=3.6, seed=5)
    objs = out.finish()
    # renomeia para masters
    for o in objs:
        if 'GRAMA' in o.name:
            o.name = 'VegTufoGrama'
        elif 'NEON' in o.name:
            o.name = 'VegCristal'
    # flores da Poly Pizza (clump unico)
    fl = bpy.data.objects.get('Flower_3_Clump') or bpy.data.objects.get('Flower_1_Clump')
    if fl:
        cp = fl.copy(); cp.data = fl.data.copy(); cp.name = 'VegFlores'
        C.objects.link(cp); cp.parent = None
        cp.data.transform(fl.matrix_world)
        cp.matrix_world = __import__('mathutils').Matrix.Identity(4)
        vs = cp.data.vertices
        if len(vs):
            xs = [v.co.x for v in vs]; ys = [v.co.y for v in vs]; zs = [v.co.z for v in vs]
            cp.data.transform(__import__('mathutils').Matrix.Translation((-(min(xs)+max(xs))/2, -(min(ys)+max(ys))/2, -min(zs))))
        cp.location = (x + 24, -70, 0)
        made.append('VegFlores')
    return made

# ---------------------------------------------------------------- plano de plantio
def veg_plan():
    """Lista de {kit, x, y, z, rot, escala} em coords BLENDER (o build lua converte)."""
    rng = random.Random(7)
    P = []
    def put(kit, x, y, z, rot=None, s=None):
        P.append({'kit': kit, 'x': round(x, 2), 'y': round(y, 2), 'z': round(z, 2),
                  'rot': round(rng.uniform(0, 360) if rot is None else rot, 1),
                  's': round(rng.uniform(.9, 1.15) if s is None else s, 2)})
    # ---- palmeiras: boulevard sul, atras dos postes ----
    for yy in range(-58, -149, -26):
        for s in (-1, 1):
            put('VegPalmeira', s * 27, yy + rng.uniform(-3, 3), FLOOR)
    # ---- palmeiras nos cantos dos terracos laterais e do portao ----
    for s in (-1, 1):
        put('VegPalmeira', s * 118, 40, TERR)
        put('VegPalmeira', s * 118, -40, TERR)
        put('VegPalmeira', s * 44, -136, FLOOR)
    # ---- arvores azuis: anel externo da praca (diagonais) ----
    for i in range(4):
        a = i / 4 * TAU + TAU / 8
        for da, kit in ((-.28, 'VegArvoreAzul'), (.24, 'VegArvoreAzul2')):
            rr = lv_floor.R_OUTER - 7
            put(kit, math.cos(a + da) * rr, math.sin(a + da) * rr, FLOOR, s=rng.uniform(1.0, 1.3))
    # ---- arvores nos canteiros da praca (4 cantos): ouro ----
    for i in range(4):
        a = i / 4 * TAU + TAU / 8
        put('VegArvoreOuro2', math.cos(a) * 30, math.sin(a) * 30, FLOOR + 1.6, s=.85)
    # ---- flanco da forja: ouro ----
    for s in (-1, 1):
        put('VegArvoreOuro', s * 58, 118, FLOOR, s=1.3)
        put('VegArvoreOuro2', s * 72, 108, FLOOR, s=1.1)
        put('VegArvoreOuro', s * 34, 96, TERR, s=.95)
    # ---- portao: ouro ladeando ----
    for s in (-1, 1):
        put('VegArvoreOuro', s * 38, -128, FLOOR, s=1.25)
    # ---- jardins sul: mistura (lilas oeste, verde leste, azul) ----
    for s, kits in ((-1, ['VegArvoreLilas', 'VegArvoreAzul2', 'VegArvoreLilas']),
                    (1, ['VegArvoreVerde', 'VegArvoreAzul', 'VegArvoreVerde'])):
        ys = [-58, -92, -126]
        for k, yy in zip(kits, ys):
            put(k, s * rng.uniform(48, 74), yy + rng.uniform(-6, 6), FLOOR, s=rng.uniform(1.0, 1.25))
    # ---- jardins norte ----
    for s in (-1, 1):
        put('VegArvoreAzul', s * 84, 78, FLOOR, s=1.15)
        put('VegArvoreLilas' if s < 0 else 'VegArvoreVerde', s * 104, 66, FLOOR, s=.95)
    # ---- arbustos: pes de arvore + bordas ----
    bush_kits = ['VegArbustoFlor', 'VegArbusto', 'VegArbustoFlorBr', 'VegArbustoAzul']
    spots = []
    for p in list(P):
        if p['kit'].startswith('VegArvore'):
            a = rng.uniform(0, TAU)
            spots.append((p['x'] + math.cos(a) * 4.5, p['y'] + math.sin(a) * 4.5, p['z']))
    for s in (-1, 1):
        for yy in range(-50, -145, -16):
            spots.append((s * rng.uniform(36, 44), yy, FLOOR))
        for yy in range(-30, 40, 18):
            spots.append((s * (lv_floor.R_OUTER + rng.uniform(4, 8)) * .01 + s * 80, yy + 40, FLOOR))
    for i, (sx, sy, sz) in enumerate(spots):
        put(bush_kits[i % 4], sx, sy, sz, s=rng.uniform(.8, 1.3))
    # ---- tufos e flores nos jardins ----
    for s in (-1, 1):
        for i in range(16):
            put('VegTufoGrama', s * rng.uniform(30, 82), rng.uniform(-152, -48), FLOOR - .05, s=rng.uniform(.8, 1.6))
            if i % 2 == 0:
                put('VegFlores', s * rng.uniform(32, 80), rng.uniform(-150, -50), FLOOR - .05, s=rng.uniform(.9, 1.5))
        for i in range(8):
            put('VegTufoGrama', s * rng.uniform(62, 104), rng.uniform(62, 94), FLOOR - .05, s=rng.uniform(.8, 1.5))
            if i % 2 == 0:
                put('VegFlores', s * rng.uniform(64, 100), rng.uniform(64, 92), FLOOR - .05)
    # ---- cristais espalhados (identidade) ----
    for s in (-1, 1):
        put('VegCristal', s * 66, -118, FLOOR, s=1.2)
        put('VegCristal', s * 90, 84, FLOOR, s=.9)
    return P

def build_all():
    mats = lvlib.mat_all()
    if not bpy.data.images.get('lv_tiles'):
        lvlib.build_tile_texture()
    if not bpy.data.images.get('lv_stone'):
        lvlib.build_stone_texture()
    _clear_all()
    stats = {}
    stats['piso'] = len(build_piso(mats))
    stats['praca'] = len(build_praca(mats))
    stats['forja'] = len(build_forja(mats))
    stats['portao'] = len(build_portao(mats))
    stats['laterais'] = len(build_laterais(mats))
    stats['kitveg'] = build_kitveg(mats)
    plan = veg_plan()
    os.makedirs(EXPORT, exist_ok=True)
    with open(os.path.join(EXPORT, 'placements.json'), 'w') as f:
        json.dump(plan, f)
    stats['veg_total'] = len(plan)
    return stats
