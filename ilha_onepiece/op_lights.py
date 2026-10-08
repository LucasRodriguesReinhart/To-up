# op_lights - PASSE GLOBAL DE LUZ da Ilha 5 (ONE PIECE / WANO), M4 (PLANO_OP secao 10; PROMPT_USUARIO secao 17).
# Roda por ULTIMO na zona dressing (depois do op_veg, do op_props e do op_vfx): nao cria luz de cenario, AUDITA e
# HIERARQUIZA as luzes que os modulos de zona criaram, por NOME/REGRA (nunca por lista fixa: as lanternas
# L_OPProp_Lamp_* do op_props entram pela regra, quantas forem). Metodo do ds_lights da Ilha 4.
#
# WANO E DE DIA. Quem ilumina e o SOL (AreaAtmosphere perfil [5], ver roblox/AreaAtmosphere_area5.md) + Ambient; a
# PointLight so existe de dia onde se justifica:
#   posto 1  SUMMON: nucleo azul (L_OPSum_Core) > estrela (L_OPSum_Star) > 2 lanternas do podio (L_OPSum_Lamp_*);
#   posto 2  INTERIORES ACESSIVEIS (override de interior do export_op.INTERIOR_LIGHTS - o corte comum 0,35 x Range /
#            0,5 x Brightness deixa um comodo de 16-50 com Range 9): salao do castelo (L_OPCas_Hall_*, 3 chochin) e
#            casa de cha (L_OPCap_Int_*). Ficam dentro de casa: nao disputam a vista de fora com o summon;
#   posto 3  janelas acesas (L_OPCap_Win_*)                         -> NightOnly (export_op.NIGHT_ONLY)
#   posto 4  lanternas de caminho/andon/ponte (L_OPProp_Lamp_*)     -> NightOnly
#   posto 5  toro de pedra (L_OPProp_Toro_*, L_OPProp_Lamp_*Toro*)   -> NightOnly, as mais fracas
#   A area 5 tem ClockTime FIXO de dia (AreaAtmosphere): as NightOnly ficam APAGADAS em Wano; a hierarquia delas so
#   vale se um ciclo de noite chegar. A cidade de dia nao tem PointLight nenhuma (o Neon do papel das lanternas ja le).
# Energia do Blender -> Roblox (export_roblox.lights): R0 = min(60; 8 + 1,1 sqrt(E)), B0 = min(4; 0,6 + E/800);
#   Range = min(20; 0,35 R0), Brightness = min(1,5; 0,5 B0); override (INTERIOR_LIGHTS, lido do export_op.py por ast:
#   UMA fonte de verdade): Range = min(regra; R0), Brightness = min(regra; INTERIOR_BR_K x B0).
# Confere tambem: luz de dia FORA da lista justificada (AVISO), luz de janela fora da propria casa, luz do salao fora do
#   salao, luz da casa de cha fora da casa, luz fora da ilha; e o SOL de previa (SUN_Key) contra o sol do Roblox na
#   latitude do jogo (22): ClockTime que reproduz o rumo.
# Contagem: ER.BUDGET day_lights 36 (meta Wano <= 12 de dia). Tabela (LUZ ...) no log; JSON da folha com OP_LUX_JSON.
import os, sys, re, math, ast, json
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import op_lib as DL
import op_layout as L

WARM = (1.0, 0.64, 0.36)
BLUE = (0.36, 0.52, 1.0)
STARC = (1.0, 0.72, 0.36)
HALLC = (1.0, 0.68, 0.42)          # chochin branco do salao: um pouco menos laranja que a lanterna de rua

# (classe, posto, regex do nome, energia alvo OU (min, max) para normalizar sem apagar a intencao do autor, cor ou
#  None = mantem, raio da previa, sombra na previa, de dia?). A PRIMEIRA regra que casa vale.
RULES = [
    ("summon nucleo", 1, r"^L_OPSum_Core", 650.0, BLUE, 1.0, False, True),
    ("summon estrela", 1, r"^L_OPSum_Star", 420.0, STARC, 1.4, False, True),
    ("summon lanterna", 1, r"^L_OPSum_Lamp", 130.0, WARM, 0.3, False, True),
    ("summon (outra)", 1, r"^L_OPSum_", (100.0, 420.0), None, 0.4, False, True),
    ("salao do castelo (interior)", 2, r"^L_OPCas_Hall_", 260.0, HALLC, 0.5, False, True),
    ("casa de cha (interior)", 2, r"^L_OPCap_Int_", 260.0, WARM, 0.5, False, True),
    ("janela acesa", 3, r"^L_OPCap_Win_", 90.0, WARM, 0.4, False, False),
    ("toro", 5, r"^L_OPProp_(Toro|Lamp_\w*Toro)", (25.0, 45.0), WARM, 0.2, False, False),
    ("lanterna de caminho", 4, r"^L_OPProp_Lamp_", (40.0, 80.0), WARM, 0.3, False, False),
    ("noturna (outra)", 4, r"^L_OPProp_", (25.0, 80.0), None, 0.3, False, False),
]
DAY_MAX = 36
DAY_GOAL = 12
GAME_LAT = 22.0                    # GeographicLatitude das ilhas no jogo (montar M2: 'devolver 22 nos perfis')


def _export_consts():
    """INTERIOR_LIGHTS / INTERIOR_BR_K / NIGHT_ONLY / LIGHT_KEEP do export_op.py (sem importar: ele roda o export).
    Aceita 'ER.NIGHT_ONLY = ...' (atributo) e 'INTERIOR_LIGHTS = ...' (nome)."""
    out = {"INTERIOR_LIGHTS": (), "INTERIOR_BR_K": 0.75, "NIGHT_ONLY": ("L_OPProp_", "L_OPCap_Win_"), "LIGHT_KEEP": ()}
    try:
        tree = ast.parse(open(os.path.join(HERE, "export_op.py"), encoding="utf-8").read())
    except Exception as e:
        print("AVISO op_lights: export_op.py ilegivel (%s)" % e)
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
    """(Range, Brightness, override?) que o export vai gravar (mesma conta do export_roblox + export_op)"""
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
def _bbox(prefix):
    lo = hi = None
    for o in bpy.data.objects:
        if o.type != "MESH" or not o.name.startswith(prefix):
            continue
        mw = o.matrix_world
        for v in o.data.vertices:
            p = mw @ v.co
            lo = p.copy() if lo is None else Vector((min(lo.x, p.x), min(lo.y, p.y), min(lo.z, p.z)))
            hi = p.copy() if hi is None else Vector((max(hi.x, p.x), max(hi.y, p.y), max(hi.z, p.z)))
    return (lo, hi) if lo is not None else None


def _inside(p, bb, pad=0.6):
    lo, hi = bb
    return lo.x - pad <= p.x <= hi.x + pad and lo.y - pad <= p.y <= hi.y + pad and lo.z - pad <= p.z <= hi.z + pad


def check_positions():
    """luz de janela dentro da COL da propria casa; salao dentro do KEEP_HALL; casa de cha dentro da casa; summon perto
    da torre; o resto dentro da ilha. So AVISA (o conserto e no modulo dono)."""
    bad = 0
    hx0, hy0, hx1, hy1, hh = L.KEEP_HALL
    for o in scene_lights():
        p = o.matrix_world.translation
        nm = o.name
        msg = None
        m = re.match(r"^L_OPCap_(Win|Int)_(?:M\d)?(\w+?)(?:_\d+)?$", nm)
        if m:
            bb = _bbox("COL_OP_CapHouse" + m.group(2) + "_")
            if bb is None:
                msg = "sem COL_OP_CapHouse%s para conferir" % m.group(2)
            elif not _inside(p, bb, 3.0 if m.group(1) == "Win" else 0.6):     # janela: luz no plano do papel
                msg = "fora da casa %s (COL %.0f..%.0f, %.0f..%.0f, %.0f..%.0f)" % (
                    m.group(2), bb[0].x, bb[1].x, bb[0].y, bb[1].y, bb[0].z, bb[1].z)
        elif nm.startswith("L_OPCas_Hall_"):
            if not (hx0 <= p.x <= hx1 and hy0 <= p.y <= hy1 and L.CC < p.z < L.CC + hh + 1.0):
                msg = "fora do salao (KEEP_HALL)"
        elif nm.startswith("L_OPSum_"):
            if (p.xy - Vector((170.0, 214.0))).length > 30.0:
                msg = "longe da torre do summon"
        elif not (-300.0 < p.x < 400.0 and -140.0 < p.y < 640.0 and p.z > L.SEA):
            msg = "fora da ilha"
        if msg:
            bad += 1
            print("AVISO op_lights: %s em (%.1f, %.1f, %.1f) %s" % (nm, p.x, p.y, p.z, msg))
    print(("OK   " if bad == 0 else "AVISO ") + "LUZES posicao: %d fora do lugar" % bad)
    return bad


# ------------------------------------------------------------------ hierarquia
def apply():
    rows = []
    for o in scene_lights():
        r = rule_of(o.name)
        e0 = o.data.energy
        if r is None:
            print("AVISO op_lights: %s sem regra (fica como o autor deixou: E %.0f)" % (o.name, e0))
            cls, rank, e, dayok = "sem regra", 9, e0, False
        else:
            cls, rank, tgt, col, rad, sh, dayok = r[0], r[1], r[3], r[4], r[5], r[6], r[7]
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
                     "day_ok": dayok, "pos": [round(p.x, 2), round(p.y, 2), round(p.z, 2)],
                     "color": [round(c, 3) for c in o.data.color]})
    return rows


def check(rows):
    """dia: so as justificadas (summon + interiores), <= DAY_GOAL (teto 36); NightOnly batendo com a regra; hierarquia
    nos numeros do ROBLOX (o lider de cada posto nao passa o do posto acima; interiores com override ficam fora a
    partir do posto 2, como na DS); o nucleo do summon e a luz de fora mais forte"""
    day = [r for r in rows if not r["night"]]
    night = [r for r in rows if r["night"]]
    ok = len(day) <= DAY_MAX
    print(("OK   " if ok else "FAIL ") + "LUZES de dia %d / %d (meta Wano %d), NightOnly %d, total %d" % (
        len(day), DAY_MAX, DAY_GOAL, len(night), len(rows)))
    stray = [r["name"] for r in day if not r["day_ok"]]
    lost = [r["name"] for r in night if r["day_ok"]]
    good = not stray and not lost
    ok &= good
    print(("OK   " if good else "FAIL ") + "LUZES de dia so as justificadas (summon + salao + casa de cha)%s%s" % (
        ("; de dia SEM justificativa: " + ", ".join(stray)) if stray else "",
        ("; justificada caiu em NightOnly: " + ", ".join(lost)) if lost else ""))
    good = len(day) <= DAY_GOAL
    print(("OK   " if good else "AVISO ") + "LUZES de dia %d <= meta %d" % (len(day), DAY_GOAL))
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
    core = next((r for r in rows if r["name"] == "L_OPSum_Core"), None)
    if core:
        others = [r for r in rows if r is not core and not r["override"]]
        good = all(core["range"] >= r["range"] and core["brightness"] >= r["brightness"] for r in others)
        ok &= good
        print(("OK   " if good else "FAIL ") + "LUZES nucleo do summon Range %.1f Brightness %.2f = a mais forte de fora" % (
            core["range"], core["brightness"]))
    for r in rows:
        if r["override"]:
            print("OK   LUZES interior %s: Range %.1f Brightness %.2f (override %s)" % (
                r["name"], r["range"], r["brightness"],
                next(o for o in XC["INTERIOR_LIGHTS"] if r["name"].startswith(o[0]))[0]))
    return ok


def table(rows):
    for r in sorted(rows, key=lambda r: (r["rank"], r["name"])):
        print("LUZ %d %-30s %-28s E %6.0f (era %6.0f) -> Range %5.1f Brightness %4.2f %s%s" % (
            r["rank"], r["name"], r["class"], r["E"], r["E0"], r["range"], r["brightness"],
            "NightOnly" if r["night"] else "dia", " override" if r["override"] else ""))


# ------------------------------------------------------------------ sol de previa x sol do Roblox
def sun_roblox(clock, lat=GAME_LAT):
    """modelo do export_roblox.sun_setup (conferido no Studio): sol = (sin a cos t, -cos a cos t, -sin t),
    a = 2 pi ClockTime / 24, t = 23,5 - latitude"""
    a = 2 * math.pi * clock / 24.0
    t = math.radians(23.5 - lat)
    return Vector((math.sin(a) * math.cos(t), -math.cos(a) * math.cos(t), -math.sin(t)))


def local_of_rbx_dir(d):
    """direcao Roblox -> direcao LOCAL da ilha (inverso de x_mundo, z, -y_mundo e do giro de 145)"""
    wx, wy, wz = d.x, -d.z, d.y
    g = math.radians(-L.WORLD_YAW_DEG)
    return Vector((wx * math.cos(g) - wy * math.sin(g), wx * math.sin(g) + wy * math.cos(g), wz))


def sun_check():
    s = bpy.data.objects.get("SUN_Key")
    if s is None:
        print("AVISO op_lights: sem SUN_Key (sol de previa)")
        return None
    d = (s.matrix_world.to_3x3() @ Vector((0.0, 0.0, 1.0))).normalized()     # da cena PARA o sol (local)
    best = None
    for k in range(0, 24 * 20 + 1):
        c = k / 20.0
        v = local_of_rbx_dir(sun_roblox(c))
        if v.z <= 0.2:
            continue
        ang = math.degrees(d.angle(v))
        if best is None or ang < best[1]:
            best = (c, ang, v)
    c, ang, v = best
    elev = math.degrees(math.asin(max(-1.0, min(1.0, d.z))))
    print("LUZES sol de previa (local) (%.2f, %.2f, %.2f), elevacao %.0f: tras-esquerda de quem chega = %s" % (
        d.x, d.y, d.z, elev, "SIM" if d.x < 0 and d.y < 0 else "NAO"))
    print("LUZES sol do Roblox na latitude %.0f: ClockTime %.2f da o rumo local (%.2f, %.2f, %.2f), %.0f graus do sol "
          "de previa" % (GAME_LAT, c, v.x, v.y, v.z, ang))
    # solucao EXATA (perfil [5] tem 'lat' proprio no AreaAtmosphere [OP]): mesma conta do export_roblox.sun_setup
    g = math.radians(L.WORLD_YAW_DEG)
    wx, wy = d.x * math.cos(g) - d.y * math.sin(g), d.x * math.sin(g) + d.y * math.cos(g)
    r = Vector((wx, d.z, -wy))
    t = -math.asin(max(-1.0, min(1.0, r.z)))
    ct = max(1e-6, math.cos(t))
    clock = (math.atan2(r.x / ct, -r.y / ct) / (2 * math.pi) * 24.0) % 24.0
    lat = 23.5 - math.degrees(t)
    hz = Vector((r.x, r.z)).normalized()
    print("LUZES sol de previa = Roblox ClockTime %.2f + GeographicLatitude %.1f: GetSunDirection (%.3f, %.3f, %.3f), "
          "horizontal X/Z (%.2f, %.2f)" % (clock, lat, r.x, r.y, r.z, hz.x, hz.y))
    for ct_, la in ((9.05, 10.0), (13.5, 30.0), (15.3, GAME_LAT)):
        w = local_of_rbx_dir(sun_roblox(ct_, la))
        side = "tras-esquerda (fachada sul do castelo ao sol)" if w.y < 0 else "FRENTE (castelo em CONTRALUZ para quem chega)"
        print("LUZES   ClockTime %5.2f lat %4.1f -> sol local (%.2f, %.2f, %.2f) elevacao %.0f: %s" % (
            ct_, la, w.x, w.y, w.z, math.degrees(math.asin(max(-1.0, min(1.0, w.z)))), side))
    for ct in ():
        w = local_of_rbx_dir(sun_roblox(ct))
        side = "tras-esquerda (fachada sul do castelo ao sol)" if w.y < 0 else "FRENTE (castelo em CONTRALUZ para quem chega)"
        print("LUZES   ClockTime %5.2f -> sol local (%.2f, %.2f, %.2f) elevacao %.0f: %s" % (
            ct, w.x, w.y, w.z, math.degrees(math.asin(max(-1.0, min(1.0, w.z)))), side))
    return c


def neon_report():
    """area de Neon/emissivo que fica acesa DE DIA (o papel Glass_OP_Lantern e Neon no Roblox): so mede, para a folha e
    para o bloom do perfil [5]"""
    keys = ("Glass_OP_Lantern", "Window_OP_Warm", "Crystal_Sum", "Summon_Star", "Energy", "Glow")
    area = {}
    for o in bpy.data.objects:
        if o.type != "MESH" or o.hide_render or o.name.startswith(("COL_", "PREVIEW_", "SCALE_")):
            continue
        me = o.data
        idx = {}
        for i, m in enumerate(me.materials):
            if m and any(k in m.name for k in keys):
                idx[i] = m.name
        if not idx:
            continue
        sc = o.matrix_world.to_scale()
        k = abs(sc.x * sc.y * sc.z) ** (2.0 / 3.0)
        for p in me.polygons:
            if p.material_index in idx:
                nm = idx[p.material_index]
                area[nm] = area.get(nm, 0.0) + p.area * k
    for nm in sorted(area, key=lambda n: -area[n]):
        print("LUZES emissivo %-28s %7.0f studs2" % (nm, area[nm]))
    return area


# ------------------------------------------------------------------ cameras da folha (fora do export)
def cams():
    e = L.EYE
    zf = L.P + 1.2                      # piso interno da casa de cha (soco 0,5 + soleira 0,7)
    return {
        "CAM_OPLux_ChaFora": ((-104.0, 238.0, L.P + 6.5), (-136.0, 250.0, L.P + 5.0), 24),
        "CAM_OPLux_ChaDentro": ((-130.6, 246.0, zf + e), (-147.0, 251.0, zf + 3.0), 16),
        "CAM_OPLux_SalaoPorta": ((0.0, 368.0, L.CC + e), (0.0, 405.0, L.CC + 6.0), 22),
        "CAM_OPLux_SummonPraca": ((40.0, 196.0, L.P + e), (170.0, 214.0, L.T1 + 30.0), 24),
    }


def build():
    bpy.context.view_layer.update()
    for n, (loc, tgt, lens) in cams().items():
        DL.camera(n, loc, tgt, lens)
    # o op_lights e o ultimo do dressing: a conferencia da vegetacao contra os props (que nascem depois dela) roda
    # aqui, com os dois montados, SE o op_veg oferecer o gancho (como o ds_veg.after_props da Ilha 4)
    try:
        import op_veg
        if hasattr(op_veg, "after_props"):
            op_veg.after_props()
    except ImportError:
        pass
    except Exception as e:
        print("AVISO op_lights: op_veg.after_props falhou: %s" % e)
    bpy.context.view_layer.update()
    rows = apply()
    table(rows)
    check_positions()
    check(rows)
    sun_check()
    neon = neon_report()
    out = os.environ.get("OP_LUX_JSON")
    if out:
        json.dump({"lights": rows, "interior": [list(r) for r in XC["INTERIOR_LIGHTS"]], "neon": neon},
                  open(out, "w", encoding="utf-8"), indent=1)
        print("LUZES tabela gravada em", out)
    return rows


if __name__ == "__main__":
    # num .blend pronto: blender -b x.blend --python op_lights.py   (so a tabela/conferencia; nao salva)
    rows = []
    for o in scene_lights():
        r = rule_of(o.name)
        rng, br, ov = to_roblox(o.name, o.data.energy)
        p = o.matrix_world.translation
        rows.append({"name": o.name, "type": o.data.type, "class": r[0] if r else "sem regra", "rank": r[1] if r else 9,
                     "E0": round(o.data.energy, 1), "E": round(o.data.energy, 1), "range": rng, "brightness": br,
                     "override": ov, "night": is_night(o.name), "day_ok": bool(r and r[7]),
                     "pos": [round(p.x, 2), round(p.y, 2), round(p.z, 2)], "color": [round(c, 3) for c in o.data.color]})
    table(rows)
    check(rows)
    sun_check()
    neon = neon_report()
    out = os.environ.get("OP_LUX_JSON")
    if out:
        json.dump({"lights": rows, "interior": [list(r) for r in XC["INTERIOR_LIGHTS"]], "neon": neon},
                  open(out, "w", encoding="utf-8"), indent=1)
