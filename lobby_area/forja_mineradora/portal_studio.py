# portal_studio.py - ESTUDIO ISOLADO DOS PORTAIS: monta o terreno real do lobby (terraco, escadas, muro, montanhas,
# canal/cachoeiras) + UM portal (ou todos) e renderiza uma prancha fixa de avaliacao.
# uso:
#   blender -b --factory-startup --python portal_studio.py -- <Key|all> <pasta_saida_absoluta> [--atual] [--res 1600x900]
#                                                             [--fast] [--save] [--cams A_Hero,B_34L,...]
#   <Key>: Naruto DragonBall ShadowGarden DemonSlayer OnePiece OnePunchMan
#   modulo novo: fm_pv3_<key minusculo>.py com build(rng) (ex.: fm_pv3_naruto.py); --atual ou sem modulo novo ->
#   versao atual (fm_portals.<funcao>)
# saida: <pasta>/<Key>_<cam>.png (e <Key>.blend com --save); imprime METRICAS do portal (tris, materiais, COL)
import sys, os, time, importlib, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
KEY = argv[0] if argv else "all"
OUT = argv[1] if len(argv) > 1 else os.path.join(HERE, "_studio")
ATUAL = "--atual" in argv
FAST = "--fast" in argv
SAVE = "--save" in argv
RES = (1600, 900)
if "--res" in argv:
    w, h = argv[argv.index("--res") + 1].split("x")
    RES = (int(w), int(h))
CAMS = None
if "--cams" in argv:
    CAMS = argv[argv.index("--cams") + 1].split(",")
os.makedirs(OUT, exist_ok=True)

import fm_layout as L
FUNC = {"Naruto": "naruto", "DragonBall": "dragonball", "ShadowGarden": "shadow", "DemonSlayer": "demonslayer",
        "OnePiece": "onepiece", "OnePunchMan": "opm"}
MODN = {"Naruto": "fm_pv3_naruto", "DragonBall": "fm_pv3_dragonball", "ShadowGarden": "fm_pv3_shadowgarden",
        "DemonSlayer": "fm_pv3_demonslayer", "OnePiece": "fm_pv3_onepiece", "OnePunchMan": "fm_pv3_onepunchman"}
KEYS = L.PORTAL_KEYS if KEY == "all" else [KEY]

# modulos de portal novos precisam ser importados ANTES de make_materials (registram MATS.setdefault no topo)
new_mods = {}
for k in KEYS:
    if not ATUAL and os.path.exists(os.path.join(HERE, MODN[k] + ".py")):
        new_mods[k] = importlib.import_module(MODN[k])
import fm_lib, fm_parts, fm_terrain, fm_scene, fm_water, fm_portals
import fm_portal_terrace as PT
import fm_portal_kit as K

t0 = time.time()
fm_lib.reset_scene()
fm_lib.make_materials()
fm_scene.setup_render(res=RES)
fm_scene.setup_world()
fm_scene.setup_sun()
if hasattr(fm_scene, "compositor"):
    try:
        fm_scene.compositor()
    except Exception as e:
        print("compositor:", e)
fm_terrain.build_ground()
fm_terrain.build_cliffs()
fm_terrain.build_mountains()
try:
    fm_water.build()
except Exception as e:
    print("agua (contexto) falhou:", e)
print("contexto", round(time.time() - t0, 1))

rng = random.Random(707)
built = {}
for k in KEYS:
    t = time.time()
    if k in new_mods:
        import fm_pv3
        new_mods[k].build(random.Random(fm_pv3.SEED[k]))
        built[k] = MODN[k]
    else:
        getattr(fm_portals, FUNC[k])(random.Random(707))
        built[k] = "fm_portals." + FUNC[k] + " (atual)"
    # dressing da escada (lance 2, faixa y 86..99.4 no terraco): stairs(mb, px, rng) do modulo novo; sem ela, a versao
    # antiga do fm_portal_terrace (referencia). O onepiece atual ja monta o seu dentro do proprio portal.
    px = L.PORTAL_X[L.PORTAL_KEYS.index(k)]
    if k in new_mods or not ATUAL:
        smb = K.LeanMB("PORTAL_%s_Stairs" % k, "06_PORTALS", random.Random(707), vcap=1)
        if k in new_mods and hasattr(new_mods[k], "stairs"):
            new_mods[k].stairs(smb, px, random.Random(fm_pv3.STAIRS_SEED[k]))
            built[k] += " + stairs v3"
        elif k in fm_portals.STAIRS:
            fm_portals.STAIRS[k](smb, px, random.Random(707))
            built[k] += " + stairs antigo"
        smb.finish()
    print("PORTAL", k, built[k], round(time.time() - t, 1), "s")

# ------------------------------------------------------------------ metricas por portal
for k in KEYS:
    allo = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("PORTAL_" + k)]
    objs = [o for o in allo if not o.name.endswith("_Stairs")]
    stairs = [o for o in allo if o.name.endswith("_Stairs")]
    tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in objs)
    mats = sorted({m.name for o in objs for m in o.data.materials if m})
    px = L.PORTAL_X[L.PORTAL_KEYS.index(k)]
    cols = [o for o in bpy.data.objects if o.name.startswith("COL_Portal") and abs(o.location.x - px) < 16]
    cst = [o for o in cols if o.location.y < 99.5]
    print("METRICAS %s: objetos=%d tris=%d materiais=%d COL=%d [%s] mats=%s" % (
        k, len(objs), tris, len(mats), len(cols) - len(cst), built[k], ", ".join(mats)))
    if stairs:
        st = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in stairs)
        sm = sorted({m.name for o in stairs for m in o.data.materials if m})
        print("METRICAS_ESCADA %s: tris=%d materiais=%d (fora da paleta do portal: %s) COL=%d mats=%s" % (
            k, st, len(sm), ", ".join(m for m in sm if m not in mats) or "nenhum", len(cst), ", ".join(sm)))
    sw = bpy.data.objects.get("PORTAL_%s_Swirl" % k)
    mk = bpy.data.objects.get("PORTAL_" + k)
    print("CONTRATO %s: swirl=%s marcador=%s luz=%s" % (k, bool(sw), bool(mk), bool(bpy.data.objects.get("L_Portal_" + k))))


# ------------------------------------------------------------------ rota local (mesmo teste do fm_qa sobre COL_)
import fm_qa
bpy.context.view_layer.update()   # matrizes das COL recem-criadas
bvh, _nf = fm_qa.col_bvh()
for k in KEYS:
    px = L.PORTAL_X[L.PORTAL_KEYS.index(k)]
    rts = [("ESCADA->PAD", [(px, 80.0), (px, L.FLIGHT2_Y1 + 0.5), (px, L.FLIGHT2_Y1 + 6.0)], L.MID)]
    if k == "Naruto":
        kp = L.KONOHA_PATH
        rts.append(("PAD->KONOHA", [(px, L.FLIGHT2_Y1 + 6.0), (px, L.PORTAL_Y), kp[0]], L.TERR))
    for nm, pts, z0 in rts:
        f, _z = fm_qa.walk(bvh, pts, z0)
        print("ROTA %s %s: %s" % (k, nm, "OK" if not f else "FAIL " + str(f)))

# ------------------------------------------------------------------ cameras
def cam(name, loc, tgt, lens):
    return fm_lib.camera(name, loc, tgt, lens)


T, PY, Y0 = L.TERR, L.PORTAL_Y, L.FLIGHT2_Y1
SZ = T + 2.0 + 9.2
shots = []
if KEY == "all":
    shots.append(("ALL_Ledge", (0, 52, 44), (0, PY, SZ - 2), 15))
    shots.append(("ALL_Plaza", (0, -40, 22), (0, PY, SZ - 2), 26))
    for k in KEYS:
        px = L.PORTAL_X[L.PORTAL_KEYS.index(k)]
        shots.append(("%s_A_Hero" % k, (px, PY - 30, T + 7), (px, PY, SZ - 2), 28))
else:
    k = KEY
    px = L.PORTAL_X[L.PORTAL_KEYS.index(k)]
    shots += [
        ("%s_A_Hero" % k, (px, PY - 44, T + 9), (px, PY, SZ + 1), 30),
        ("%s_B_34L" % k, (px - 21, PY - 21, T + 8), (px, PY + 1, SZ - 3), 26),
        ("%s_C_34R" % k, (px + 21, PY - 21, T + 8), (px, PY + 1, SZ - 3), 26),
        ("%s_D_Side" % k, (px + 25, PY + 3, T + 9), (px, PY + 1, SZ - 3), 24),
        ("%s_E_Back" % k, (px + 12, PY + 16, T + 32), (px, PY - 1, SZ - 6), 22),
        ("%s_F_Player" % k, (px + 1.5, Y0 + 1.5, T + 5.5), (px, PY, SZ - 1.5), 20),
        ("%s_G_Far" % k, (px * 0.35, -30, 18), (px, PY, SZ - 3), 70),
        ("%s_H_Stairs" % k, (px, 60, 27), (px, 95, T + 3), 28),
        ("%s_I_Climb" % k, (px + 1.5, 84, 22), (px, 110, T + 6), 24),
    ]
sc = bpy.context.scene
if FAST:
    sc.eevee.taa_render_samples = 8
for name, loc, tgt, lens in shots:
    if CAMS and not any(name.endswith(c) for c in CAMS):
        continue
    ob = cam("STUDIO_" + name, loc, tgt, lens)
    sc.camera = ob
    sc.render.filepath = os.path.join(OUT, name + ".png")
    bpy.ops.render.render(write_still=True)
    print("RENDER", name)
if SAVE:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, KEY + ".blend"), compress=True)
print("STUDIO OK", KEY, round(time.time() - t0, 1), "s")
