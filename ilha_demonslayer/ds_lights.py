# ds_lights - PASSE GLOBAL DE LUZ da Ilha 4 (DEMON SLAYER), agente 3c da Onda 3 (PLANO_DS secao 10, prompt secao 17,
# fase 14). Roda no FIM da zona dressing (depois do ds_veg, do ds_props e do ds_vfx): nao cria luz nova de cenario,
# AUDITA e HIERARQUIZA todas as luzes que os modulos de zona criaram, por NOME/REGRA (nunca por lista fixa - as
# lanternas L_DSProp_Lamp_* do ds_props entram pela regra, quantas forem).
#
# NOITE LEGIVEL = lua fria (ds_scene: sol de previa no SUDOESTE local) + janelas quentes + lanternas quentes. A forma
# le so com o ambiente (validado com as luzes apagadas e emissao zerada); a luz so HIERARQUIZA. Postos (PLANO sec. 10):
#   1. boca da fornalha (L_DSFrg_FurnaceMouth) e fornalha (L_DSFrg_Furnace, interior): laranja, Range 28 no Roblox
#      pelo override de interior (export_ds.INTERIOR_LIGHTS); sao as unicas com Brightness > 1,5;
#   2. janelas da forja e da torre (L_DSFrg_*): torre > oficina/ala leste > forno de carvao;
#   3. summon (L_DSSum_*): nucleo azul + 2 lanternas do podio + estrela CONTIDA (abaixo da forja: equilibrio de
#      destaque pedido pela onda 2b - o dourado nao pode ler mais que a boca);
#   4. casas (L_DSVil_*): 1 luz quente por casa; os interiores de V1 e V6 ganham override de interior (o corte do
#      export_roblox 0,35 x Range / 0,5 x Brightness deixa um comodo de 18-24 com Range 8 e Brightness 0,45);
#   5. lanternas de caminho (L_DSProp_Lamp_*, NightOnly pelo export_ds.NIGHT_ONLY);
#   6. toro de pedra (L_DSProp_Toro_*, L_DSProp_Lamp_*Toro*/Patamar/SumTop: NightOnly, as mais fracas).
# Energia do Blender -> Roblox (export_roblox.lights): R0 = min(60; 8 + 1,1 sqrt(E)), B0 = min(4; 0,6 + E/800);
#   Range = min(20; 0,35 R0), Brightness = min(1,5; 0,5 B0); override (INTERIOR_LIGHTS, lido do export_ds.py por ast:
#   uma fonte de verdade so): Range = min(regra; R0), Brightness = min(regra; INTERIOR_BR_K * B0).
# Tambem confere luz fora do lugar: luz de janela de casa fora da propria casa vira AVISO (ONDA 4: o caso que existia -
#   o kura V4, que usava o retorno LOCAL de kura_window - foi corrigido na fonte, no ds_kit; o remendo que movia a luz
#   saiu). A boca da fornalha continua reposta (RELOCATE: decisao de luz, nao conserto).
# Contagem: ER.BUDGET day_lights 36 (meta ~16 de dia + ~24 NightOnly). Imprime a tabela (LUZ ...) e grava o JSON da
# folha com DS_LUX_JSON=<arquivo>.
import os, re, math, ast, json
import bpy
from mathutils import Vector
import ds_lib as DL
import ds_layout as L

HERE = os.path.dirname(os.path.abspath(__file__))

FIRE = (1.0, 0.45, 0.14)
MOUTH = (1.0, 0.50, 0.20)
WARM = (1.0, 0.64, 0.34)
HEARTH = (1.0, 0.56, 0.28)
BLUE = (0.36, 0.52, 1.0)
STARC = (1.0, 0.70, 0.36)

# (classe, posto, regex do nome, energia alvo OU (min, max) para normalizar sem apagar a intencao do autor, cor ou
#  None = mantem, raio da previa, sombra na previa). A PRIMEIRA regra que casa vale.
RULES = [
    ("boca da fornalha", 1, r"^L_DSFrg_FurnaceMouth$", 2000.0, MOUTH, 0.9, True),
    ("fornalha (interior)", 1, r"^L_DSFrg_Furnace$", 2600.0, FIRE, 1.0, True),
    ("torre da forja", 2, r"^L_DSFrg_TowerWin", 600.0, WARM, 0.6, False),
    ("janela da forja", 2, r"^L_DSFrg_(Workshop|East)", 320.0, WARM, 0.4, False),
    ("forno de carvao", 2, r"^L_DSFrg_Kiln", 220.0, FIRE, 0.4, False),
    ("forja (outra)", 2, r"^L_DSFrg_", (150.0, 600.0), None, 0.4, False),
    ("summon nucleo", 3, r"^L_DSSum_Core", 450.0, BLUE, 1.0, False),
    ("summon lanterna", 3, r"^L_DSSum_Lamp", 160.0, WARM, 0.3, False),
    ("summon estrela", 3, r"^L_DSSum_Star", 160.0, STARC, 1.2, False),
    ("summon (outra)", 3, r"^L_DSSum_", (100.0, 450.0), None, 0.4, False),
    ("casa interior V6 (irori)", 4, r"^L_DSVil_V6_Irori", 240.0, HEARTH, 0.4, False),
    ("casa interior", 4, r"^L_DSVil_(V1|V6)_", (120.0, 200.0), WARM, 0.3, False),
    ("janela de casa", 4, r"^L_DSVil_Win_", 260.0, WARM, 0.4, False),
    ("casa (outra)", 4, r"^L_DSVil_", (90.0, 260.0), None, 0.3, False),
    ("toro", 6, r"^L_DSProp_(Toro|Lamp_\w*(Toro|Patamar|SumTop))", (50.0, 90.0), WARM, 0.3, False),
    ("lanterna de caminho", 5, r"^L_DSProp_Lamp_", (90.0, 160.0), WARM, 0.3, False),
    ("noturna (outra)", 5, r"^L_DSProp_", (50.0, 160.0), None, 0.3, False),
]
DAY_MAX = 36


def _export_consts():
    """INTERIOR_LIGHTS / INTERIOR_BR_K / NIGHT_ONLY / LIGHT_KEEP lidos do export_ds.py (sem importar: ele roda o export)"""
    out = {"INTERIOR_LIGHTS": (), "INTERIOR_BR_K": 0.75, "NIGHT_ONLY": ("L_DSProp_",), "LIGHT_KEEP": ()}
    try:
        tree = ast.parse(open(os.path.join(HERE, "export_ds.py"), encoding="utf-8").read())
    except Exception as e:
        print("AVISO ds_lights: export_ds.py ilegivel (%s)" % e)
        return out
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for t in node.targets:
            nm = t.id if isinstance(t, ast.Name) else (t.attr if isinstance(t, ast.Attribute) else None)
            if nm in out:
                try:
                    out[nm] = ast.literal_eval(node.value)
                except Exception:
                    pass
    return out


XC = _export_consts()


def rule_of(name):
    for r in RULES:
        if re.match(r[2], name):
            return r
    return None


def to_roblox(name, e):
    """(Range, Brightness, override?) que o export vai gravar para esta luz (mesma conta do export_roblox + export_ds)"""
    r0 = min(60.0, 8.0 + math.sqrt(max(e, 0.0)) * 1.1)
    b0 = min(4.0, 0.6 + e / 800.0)
    rng, br = min(20.0, r0 * 0.35), min(1.5, b0 * 0.5)
    ov = next((r for r in XC["INTERIOR_LIGHTS"] if name.startswith(r[0])), None)
    if ov:
        rng, br = min(ov[1], r0), min(ov[2], XC["INTERIOR_BR_K"] * b0)
    return round(rng, 1), round(br, 2), bool(ov)


def is_night(name):
    return name.startswith(tuple(XC["NIGHT_ONLY"]))


def scene_lights():
    return sorted((o for o in bpy.data.objects if o.type == "LIGHT" and o.data.type in ("POINT", "SPOT")),
                  key=lambda o: o.name)


# ------------------------------------------------------------------ luz fora do lugar
def _house_box(nm):
    ob = bpy.data.objects.get("DS_Vil_House" + nm)
    if ob is None or ob.type != "MESH":
        return None
    mw = ob.matrix_world
    vs = [mw @ v.co for v in ob.data.vertices]
    if not vs:
        return None
    lo = Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs)))
    hi = Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))
    win = []
    for p in ob.data.polygons:
        mt = ob.data.materials[p.material_index] if p.material_index < len(ob.data.materials) else None
        if mt and mt.name.startswith("Window_DS_Warm"):
            win.append((mw @ p.center).z)
    return lo, hi, (sum(win) / len(win) if win else lo.z + 4.0)


def _mouth_pos():
    """boca: a luz sai do fundo do tunel (y 471,5, acima da nascenca do arco: a sombra do arco escondia o patio) para
    1 stud dentro da FACE do bloco de alvenaria, na altura do peito - lava o intradorso, a soleira e o sando do patio"""
    import ds_forge as FG
    return (FG.MX, FG.BFY + 1.0, FG.DOMA + 4.2)


RELOCATE = {"L_DSFrg_FurnaceMouth": _mouth_pos}


def fix_positions():
    """RELOCATE (boca da fornalha). Luz de janela de casa (L_DSVil_Win_<casa>) fora da propria casa: AVISO (o conserto e
    na fonte, no ds_kit). Outras luzes: so avisa se cairem fora da ilha."""
    fixed = []
    for o in scene_lights():
        if o.name in RELOCATE:
            p0 = tuple(o.matrix_world.translation)
            o.parent = None
            o.location = RELOCATE[o.name]()
            print("LUZ reposta   %-24s (%.1f, %.1f, %.1f) -> (%.1f, %.1f, %.1f)" % ((o.name,) + p0 + tuple(o.location)))
            fixed.append(o.name)
            continue
        m = re.match(r"^L_DSVil_Win_(V\d)", o.name)
        if m:
            hb = _house_box(m.group(1))
            if hb:
                lo, hi, zw = hb
                p = o.matrix_world.translation
                if not (lo.x - 1.0 <= p.x <= hi.x + 1.0 and lo.y - 1.0 <= p.y <= hi.y + 1.0 and lo.z - 1.0 <= p.z <= hi.z):
                    print("AVISO ds_lights: %s em (%.1f, %.1f, %.1f) fora da casa %s (corrigir no ds_kit/ds_village)" % (
                        o.name, p.x, p.y, p.z, m.group(1)))
            continue
        p = o.matrix_world.translation
        if not (-260.0 < p.x < 300.0 and -140.0 < p.y < 720.0 and p.z > 30.0):
            print("AVISO ds_lights: %s fora da ilha (%.1f, %.1f, %.1f)" % (o.name, p.x, p.y, p.z))
    return fixed


# ------------------------------------------------------------------ hierarquia
def apply():
    rows = []
    for o in scene_lights():
        r = rule_of(o.name)
        e0 = o.data.energy
        if r is None:
            print("AVISO ds_lights: %s sem regra (fica como o autor deixou: E %.0f)" % (o.name, e0))
            cls, rank, e = "sem regra", 9, e0
        else:
            cls, rank, tgt, col, rad, sh = r[0], r[1], r[3], r[4], r[5], r[6]
            e = min(max(e0, tgt[0]), tgt[1]) if isinstance(tgt, tuple) else tgt
            o.data.energy = e
            if col:
                o.data.color = col
            o.data.shadow_soft_size = rad
            o.data.use_shadow = sh
        rng, br, ov = to_roblox(o.name, e)
        p = o.matrix_world.translation
        rows.append({"name": o.name, "type": o.data.type, "class": cls, "rank": rank, "E0": round(e0, 1),
                     "E": round(e, 1), "range": rng, "brightness": br, "override": ov, "night": is_night(o.name),
                     "pos": [round(p.x, 2), round(p.y, 2), round(p.z, 2)],
                     "color": [round(c, 3) for c in o.data.color]})
    return rows


def check(rows):
    """hierarquia medida nos numeros do ROBLOX: a luz mais forte de cada posto (Range x Brightness) nao passa a mais
    forte do posto acima; os interiores com override (dentro de casa, nao disputam a vista de fora) ficam fora da
    conta a partir do posto 2; a boca e a mais forte de fora"""
    day = [r for r in rows if not r["night"]]
    night = [r for r in rows if r["night"]]
    ok = len(day) <= DAY_MAX
    print(("OK   " if ok else "FAIL ") + "LUZES de dia %d / %d, NightOnly %d, total %d" % (len(day), DAY_MAX, len(night),
                                                                                       len(rows)))
    by = {}
    for r in rows:
        if r["rank"] >= 9 or (r["override"] and r["rank"] > 1):
            continue
        by.setdefault(r["rank"], []).append(r)
    ranks = sorted(by)
    lead = {k: max(by[k], key=lambda x: (x["brightness"], x["range"])) for k in ranks}
    for a, b in zip(ranks, ranks[1:]):
        la, lb = lead[a], lead[b]
        good = lb["brightness"] <= la["brightness"] + 1e-6 and lb["range"] <= la["range"] + 1e-6
        ok &= good
        print(("OK   " if good else "FAIL ") + "LUZES posto %d (%s R %.1f B %.2f) acima do posto %d (%s R %.1f B %.2f)" % (
            a, la["name"], la["range"], la["brightness"], b, lb["name"], lb["range"], lb["brightness"]))
    mouth = next((r for r in rows if r["name"] == "L_DSFrg_FurnaceMouth"), None)
    if mouth:
        others = [r for r in rows if r["rank"] > 1]
        good = all(mouth["range"] >= r["range"] and mouth["brightness"] > r["brightness"] for r in others)
        ok &= good
        print(("OK   " if good else "FAIL ") + "LUZES boca da fornalha Range %.1f Brightness %.2f acima de todas fora "
              "da forja" % (mouth["range"], mouth["brightness"]))
    return ok


def table(rows):
    for r in sorted(rows, key=lambda r: (r["rank"], r["name"])):
        print("LUZ %d %-30s %-24s E %6.0f (era %6.0f) -> Range %5.1f Brightness %4.2f %s%s" % (
            r["rank"], r["name"], r["class"], r["E"], r["E0"], r["range"], r["brightness"],
            "NightOnly" if r["night"] else "dia", " override" if r["override"] else ""))


def moon_check():
    """previa: a lua (SUN_Key) tem de vir do SUDOESTE local, fria (PLANO secao 10)"""
    s = bpy.data.objects.get("SUN_Key")
    if s is None:
        print("AVISO ds_lights: sem SUN_Key (lua de previa)")
        return
    d = (s.matrix_world.to_3x3() @ Vector((0.0, 0.0, 1.0))).normalized()     # da cena PARA a lua
    az = math.degrees(math.atan2(d.y, d.x))
    c = s.data.color
    good = d.x < 0 and d.y < 0 and c[2] >= c[0]
    print(("OK   " if good else "AVISO ") + "LUZES lua de previa: rumo local (%.2f, %.2f, %.2f) azimute %.0f graus "
          "(sudoeste = entre -180 e -90), cor (%.2f, %.2f, %.2f)" % (d.x, d.y, d.z, az, c[0], c[1], c[2]))


# ------------------------------------------------------------------ cameras da folha 3c (studio_ds pega CAMS)
T1, T2, T3, T4 = L.T1, L.T2, L.T3, L.T4
CAMS = {
    # a boca vista de longe (antecampo e pe da subida, tele) e de perto (soleira do patio)
    "CAM_DSLux_MouthFar": ((10.0, 300.0, T1 + L.EYE), (0.0, 468.0, T4 + 6.0), 40),
    "CAM_DSLux_MouthYard": ((14.0, 432.0, T4 + L.EYE), (0.0, 470.0, T4 + 6.5), 24),
    # summon x forja da clareira (a mesma visada do PlayerHeight_Clearing, mais fechada nos dois)
    "CAM_DSLux_Balance": ((-20.0, 140.0, T1 + L.EYE), (121.0, 405.0, T1 + 24.0), 30),
    # vila de noite (rua baixa) e interior V6
    "CAM_DSLux_VillageNight": ((-30.0, 120.0, T1 + 12.0), (-100.0, 250.0, T2 + 4.0), 24),
}


def neon_report():
    """ONDA 6b (item 55): o campo de papel Neon (Glass_DS_Lantern: lanternas do kit e de caminho) contra o Neon da
    boca (Fire_DS_Glow). No Play os ~110 papeis somados ao bloom competiam com a boca: a cor do papel baixou de
    saturacao no ds_lib (232,146,66 -> 214,144,88) e a hierarquia continua nas PointLights (a boca e a unica com
    Brightness > 1,5). Aqui so MEDE (area e cor), para a folha."""
    area = {"Glass_DS_Lantern": 0.0, "Fire_DS_Glow": 0.0}
    nobj = 0
    for o in bpy.data.objects:
        if o.type != "MESH" or o.hide_render or o.name.startswith(("COL_", "PREVIEW_", "SCALE_")):
            continue
        me = o.data
        idx = {i: m.name for i, m in enumerate(me.materials) if m and m.name in area}
        if not idx:
            continue
        nobj += 1
        sc = o.matrix_world.to_scale()
        k = abs(sc.x * sc.y * sc.z) ** (2.0 / 3.0)
        for p in me.polygons:
            if p.material_index in idx:
                area[idx[p.material_index]] += p.area * k
    c = DL.DSMATS.get("Glass_DS_Lantern", (None,))[0]
    rgb = [int(round(v)) for v in DL.fm_lib.to_srgb(c)] if c else None
    print("LUZES neon: papel %.0f studs2 (cor %s), boca/fogo %.0f studs2, %d objetos" % (
        area["Glass_DS_Lantern"], rgb, area["Fire_DS_Glow"], nobj))
    return area


def build():
    bpy.context.view_layer.update()
    # ONDA 6b (item 44): o ds_lights e o ultimo do dressing - a conferencia da vegetacao contra os props (que nascem
    # DEPOIS dela) roda aqui, com os dois ja montados (ds_veg.after_props: raiz/capim que atravessa prop sai)
    try:
        import ds_veg
        ds_veg.after_props()
    except Exception as e:
        print("AVISO ds_lights: ds_veg.after_props falhou: %s" % e)
    bpy.context.view_layer.update()
    fixed = fix_positions()
    bpy.context.view_layer.update()
    rows = apply()
    table(rows)
    check(rows)
    moon_check()
    neon_report()
    out = os.environ.get("DS_LUX_JSON")
    if out:
        json.dump({"lights": rows, "interior": [list(r) for r in XC["INTERIOR_LIGHTS"]], "fixed": fixed},
                  open(out, "w", encoding="utf-8"), indent=1)
        print("LUZES tabela gravada em", out)
    return rows


if __name__ == "__main__":
    # num .blend pronto: blender -b x.blend --python ds_lights.py   (so a tabela/conferencia, nao muda nada salvo)
    rows = []
    for o in scene_lights():
        r = rule_of(o.name)
        rng, br, ov = to_roblox(o.name, o.data.energy)
        p = o.matrix_world.translation
        rows.append({"name": o.name, "type": o.data.type, "class": r[0] if r else "sem regra", "rank": r[1] if r else 9,
                     "E0": round(o.data.energy, 1), "E": round(o.data.energy, 1), "range": rng, "brightness": br,
                     "override": ov, "night": is_night(o.name), "pos": [round(p.x, 2), round(p.y, 2), round(p.z, 2)],
                     "color": [round(c, 3) for c in o.data.color]})
    table(rows)
    check(rows)
    moon_check()
    out = os.environ.get("DS_LUX_JSON")
    if out:
        json.dump({"lights": rows, "interior": [list(r) for r in XC["INTERIOR_LIGHTS"]], "fixed": []},
                  open(out, "w", encoding="utf-8"), indent=1)
