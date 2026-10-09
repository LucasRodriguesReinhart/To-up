# sn_paint.py - PINTURA ASSADA por peca (metodo aprovado no kit Murim): sombra de AO colorida, luz pintada de cima,
# gradiente de altura, variacao por pedra, mancha larga de pincel, realce de aresta convexa, musgo nas faces de cima,
# sujeira no pe das paredes e brilho pintado dos metais. Tudo vai para o ColorMap (o Roblox ignora cor de vertice).
# Fluxo por grupo (um Build do wb_lib, ex. "WB_Frg_Anvil"): juntar as malhas nao-Neon -> semente por pedra -> trocar
# os materiais SN_/WB_ pelas tintas P_* -> dividir por area (densidade alvo em px/stud) -> smart project -> assar EMIT
# no Cycles (CPU) -> material final SNB_<atlas> (1 textura 1024, o teto do Roblox). Neon/agua/fogo ficam como estao.
import bpy
import bmesh
import math
import os
import random
import time
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "textures", "baked")
os.makedirs(TEX, exist_ok=True)
SIZE = 1024                     # teto do Roblox para SurfaceAppearance
PACK = 0.62                     # fracao util do atlas depois do smart project + margem
GROUND_Z = 7.0                  # chao da praca (Blender z = Roblox y)


def hex_lin(h):
    c = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


#              base      sombra    realce   var  aresta  ao  cima  brilho musgo sujeira raio_aresta
PD = {
    "pedra":     ("B9AB8C", "5F5544", "EADFC6", .10, .50, .85, .16, .00, .00, .40, .22),
    "pedra_mus": ("B3A688", "5B5243", "E4D9BF", .10, .50, .85, .16, .00, .60, .40, .22),
    "pedra_esc": ("8A8170", "3D372E", "BCB29E", .10, .45, .85, .14, .00, .35, .40, .22),
    "entalhe":   ("C3B597", "5F5440", "EFE4CB", .05, .55, .90, .16, .00, .00, .30, .16),
    "piso":      ("ADA087", "5A5242", "D8CEB6", .16, .32, .85, .05, .00, .18, .00, .16),
    "basalto":   ("5C5654", "201D1C", "A39A93", .10, .50, .85, .12, .00, .25, .20, .25),
    "ferro_tita": ("514F51", "171617", "CDCBC6", .06, .62, .85, .12, .22, .00, .20, .35),
    "ferro":     ("38342F", "0E0C0B", "86807A", .08, .50, .85, .10, .16, .00, .10, .12),
    "aco":       ("8C949E", "3A4048", "E6ECF2", .05, .50, .70, .08, .35, .00, .00, .10),
    "bronze":    ("8C6830", "3A250E", "DDB872", .08, .50, .80, .08, .30, .00, .10, .14),
    "ouro":      ("C28A2C", "6E3A0C", "F4CC6A", .05, .45, .70, .06, .32, .00, .00, .12),
    "madeira":   ("7E6852", "36291C", "B8A286", .14, .38, .85, .10, .00, .00, .25, .12),
    "madeira_esc": ("5A4434", "1E140C", "8E7058", .12, .35, .85, .10, .00, .00, .20, .12),
    "couro":     ("6E4632", "2A160C", "A87A5C", .10, .30, .85, .10, .05, .00, .00, .10),
    "tecido_verm": ("A8261A", "4E0B06", "E9603F", .05, .25, .80, .12, .00, .00, .00, .10),
    "tecido_ouro": ("C8962E", "6A4410", "F4D27E", .05, .25, .80, .12, .00, .00, .00, .10),
    "tecido_azul": ("3E5FA6", "17244A", "8EB0F0", .05, .25, .80, .12, .00, .00, .00, .10),
    "tecido_verde": ("4A7E4A", "1A3A1E", "9AD08A", .05, .25, .80, .12, .00, .00, .00, .10),
    "tecido_ocre": ("CC963C", "6A4614", "F6D088", .05, .25, .80, .12, .00, .00, .00, .10),
    "tecido_creme": ("E2D4B4", "8A7A5E", "FFF6E2", .05, .25, .80, .12, .00, .00, .00, .10),
    "tecido_violeta": ("7A46AA", "2E1446", "C8A0F0", .05, .25, .80, .12, .00, .00, .00, .10),
    "tecido_tan": ("D09A55", "6A4420", "F6D3A0", .04, .28, .85, .14, .00, .00, .00, .12),
    "corda":     ("C4A068", "6A5030", "EED8A8", .06, .25, .80, .12, .00, .00, .00, .08),
    "couro_claro": ("8A5634", "36200E", "C69468", .08, .30, .85, .10, .05, .00, .00, .08),
    "papel": ("EEE4C8", "9C8E6E", "FFFFFF", .04, .15, .60, .10, .00, .00, .00, .05),
    "telha": ("C4643C", "5E2412", "F2A27A", .12, .40, .90, .12, .00, .10, .00, .14),
    "telha_esc": ("96462E", "3E160A", "D27E5E", .10, .40, .90, .12, .00, .05, .00, .14),
    "terracota": ("BA6440", "5A2614", "EAA07A", .08, .40, .85, .10, .00, .00, .00, .10),
    "musgo":     ("6E9C40", "2A4A1A", "BCDC7C", .16, .22, .80, .30, .00, .00, .00, .12),
    "hera":      ("528636", "1C3A16", "A2D06A", .16, .22, .80, .30, .00, .00, .00, .10),
    "flor_azul": ("7896EC", "34449A", "D2DEFF", .10, .20, .60, .25, .00, .00, .00, .08),
    "flor_rosa": ("F0B0C4", "9A5A70", "FFE4EC", .10, .20, .60, .25, .00, .00, .00, .08),
    "flor_branca": ("F2EEE6", "A8A096", "FFFFFF", .08, .20, .60, .25, .00, .00, .00, .08),
    "crosta":    ("3E2A24", "120A08", "84503A", .08, .40, .85, .08, .00, .00, .00, .20),
    "carvao":    ("2C2826", "0A0908", "5E5650", .10, .30, .85, .08, .00, .00, .00, .10),
    "palha":     ("C9A86A", "7A5A2E", "EFD9A4", .12, .30, .85, .10, .00, .00, .00, .10),
    "casca":     ("7A5A3E", "35220F", "AC8862", .12, .35, .80, .10, .00, .10, .00, .14),
    "folha":     ("6CA044", "1F4A2A", "D4EC8C", .10, .10, .90, .10, .00, .00, .00, .25),
    "folha_clara": ("8AB84C", "2E5A2A", "E6F29A", .10, .10, .90, .10, .00, .00, .00, .25),
    "folha_ouro": ("D6A23A", "7A3E1C", "FFE08A", .10, .10, .90, .10, .00, .00, .00, .25),
    "pinho":     ("3F7A4E", "12302A", "A8D27A", .10, .12, .90, .10, .00, .00, .00, .20),
    "grama":     ("78AC48", "2C5622", "C4DE7A", .00, .04, .92, .10, .00, .00, .00, .20),
    "terra":     ("A88A64", "5A4630", "D6BC92", .00, .10, .90, .08, .00, .00, .00, .20),
    "barranco":  ("8C7458", "3E3022", "BEA688", .00, .20, .90, .14, .00, .25, .00, .25),
    "junco":     ("86A452", "34501E", "C8DC86", .10, .10, .80, .20, .00, .00, .00, .08),
    "flor_amarela": ("F2D25A", "9A7414", "FFF4C0", .10, .20, .60, .25, .00, .00, .00, .08),
}
# efeitos extras por tinta: mancha de forja (mottle), escorrido de ferrugem (rust), patina verde do bronze (verdigris)
EXTRA = {
    "ferro_tita": {"mottle": .10, "rust": .30},
    "ferro": {"mottle": .08, "rust": .25},
    "bronze": {"verdigris": .55},
    "ouro": {"verdigris": .15},
    "basalto": {"mottle": .06},
    "folha": {"toon": 1.0}, "folha_clara": {"toon": 1.0}, "folha_ouro": {"toon": 1.0}, "pinho": {"toon": 1.0},
    "casca": {"toon": .5},
    "grama": {"patch": 1.0}, "terra": {"patch": .5}, "junco": {"toon": .8},
}
# material do pipeline -> tinta
MAT2PAINT = {
    "SN_Ashlar": "pedra", "SN_Ashlar_Moss": "pedra_mus", "SN_Ashlar_Dark": "pedra_esc", "SN_Carved": "entalhe",
    "SN_Plaza": "piso", "SN_Rubble": "pedra", "SN_Basalt": "basalto", "SN_Iron": "ferro_tita", "SN_Bronze": "bronze",
    "SN_Gold": "ouro", "SN_Chain": "ferro", "SN_Moss": "musgo", "SN_Ivy": "hera", "SN_WoodAged": "madeira",
    "SN_FlowerBlue": "flor_azul", "SN_Petal": "flor_rosa", "SN_LavaCrust": "crosta",
    "WB_Iron": "ferro", "WB_Dark": "ferro", "WB_Steel": "aco", "WB_Bark": "casca", "WB_Leaf": "folha",
    "WB_Pine": "pinho", "WB_Plank": "madeira", "WB_Timber": "madeira_esc", "WB_LeatherDark": "couro",
    "WB_Cloth_Red": "tecido_verm", "WB_Cloth_Gold": "tecido_ouro", "WB_Coal": "carvao", "WB_FlowerWhite": "flor_branca",
    "SN_Leaf": "folha", "SN_LeafLight": "folha_clara", "SN_LeafGold": "folha_ouro", "SN_PineLeaf": "pinho",
    "SN_Bark": "casca",
    "SN_Grass": "grama", "SN_Path": "terra", "SN_Bank": "barranco", "SN_ShoreRock": "pedra_esc", "SN_Reed": "junco",
    "SN_Tuft": "folha", "SN_TuftLight": "folha_clara", "SN_FlowerYellow": "flor_amarela",
    "SN_CanvasRed": "tecido_verm", "SN_CanvasBlue": "tecido_azul", "SN_CanvasGreen": "tecido_verde",
    "SN_CanvasOchre": "tecido_ocre", "SN_CanvasCream": "tecido_creme", "SN_CanvasViolet": "tecido_violeta",
    "SN_Leather": "couro_claro", "SN_Paper": "papel", "SN_RoofTile": "telha", "SN_RoofTileDark": "telha_esc",
    "SN_Terracotta": "terracota", "SN_CanvasTan": "tecido_tan", "SN_LeatherDark": "couro", "SN_Rope": "corda", "SN_Slate": "ferro",
    "WB_Rock": "basalto", "WB_Stone": "pedra", "WB_Hay": "palha", "WB_Wood": "madeira", "WB_Rope": "palha",
}


def _paint_of(mname):
    if mname in MAT2PAINT:
        return MAT2PAINT[mname]
    base = mname.split(".")[0]
    return MAT2PAINT.get(base)


def keep_separate(mname):
    """materiais que NAO entram no atlas: Neon (lava, runas, cristais, fogo), agua, vidro, espirais, cenario distante"""
    import fm_lib
    base = mname.split(".")[0]
    v = fm_lib.MATS.get(base)
    if v is not None and v[3] and v[3] > 0:
        return True
    return _paint_of(base) is None


# ------------------------------------------------------------------ tintas (materiais de bake)
def _n(nt, typ, **kw):
    n = nt.nodes.new(typ)
    for k, v in kw.items():
        setattr(n, k, v)
    return n


def build_paint(key):
    base, shad, high, var, edge, ao, face, spec, moss, grime, erad = PD[key]
    m = bpy.data.materials.get("P_" + key) or bpy.data.materials.new("P_" + key)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    L = nt.links.new
    out = _n(nt, "ShaderNodeOutputMaterial")
    em = _n(nt, "ShaderNodeEmission")
    geo = _n(nt, "ShaderNodeNewGeometry")

    def math_(op, a, b=None, clamp=False):
        n = _n(nt, "ShaderNodeMath", operation=op, use_clamp=clamp)
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                L(v, n.inputs[i])
        return n.outputs[0]

    def mixc(mode, fac, c1, c2):
        n = _n(nt, "ShaderNodeMixRGB", blend_type=mode)
        if isinstance(fac, (int, float)):
            n.inputs[0].default_value = fac
        else:
            L(fac, n.inputs[0])
        for i, c in ((1, c1), (2, c2)):
            if isinstance(c, tuple):
                n.inputs[i].default_value = c
            else:
                L(c, n.inputs[i])
        return n.outputs[0]

    def ramp(v, p0, p1):
        n = _n(nt, "ShaderNodeMapRange", clamp=True)
        n.inputs[1].default_value = p0
        n.inputs[2].default_value = p1
        L(v, n.inputs[0])
        return n.outputs[0]

    def noise(scale, detail, rough=0.5):
        n = _n(nt, "ShaderNodeTexNoise")
        n.inputs["Scale"].default_value = scale
        n.inputs["Detail"].default_value = detail
        n.inputs["Roughness"].default_value = rough
        L(geo.outputs["Position"], n.inputs["Vector"])
        return n.outputs[0]

    pos = _n(nt, "ShaderNodeSeparateXYZ")
    L(geo.outputs["Position"], pos.inputs[0])
    nrm = _n(nt, "ShaderNodeSeparateXYZ")
    L(geo.outputs["Normal"], nrm.inputs[0])
    att = _n(nt, "ShaderNodeAttribute", attribute_name="rnd")
    # fatores multiplicativos do valor
    vr = math_("ADD", math_("MULTIPLY", math_("SUBTRACT", att.outputs["Factor"], .5), var * 2.0), 1.0)
    nA = math_("ADD", math_("MULTIPLY", math_("SUBTRACT", noise(.045, 2.0), .5), .26), 1.0)     # manchas de ~20 studs
    nB = math_("ADD", math_("MULTIPLY", math_("SUBTRACT", noise(.42, 3.0), .5), .10 if var > .04 else .04), 1.0)
    hgt = ramp(pos.outputs["Z"], GROUND_Z - 2.0, GROUND_Z + 48.0)
    grad = math_("ADD", math_("MULTIPLY", hgt, .16), .86)                                       # mais claro no alto
    fc = math_("ADD", math_("MULTIPLY", nrm.outputs["Z"], face), 1.0)                          # luz pintada de cima
    mval = math_("MULTIPLY", math_("MULTIPLY", vr, math_("MULTIPLY", nA, nB)), math_("MULTIPLY", grad, fc))
    col = mixc("MULTIPLY", 1.0, (*hex_lin(base), 1), mval)
    # sombra de AO colorida (a sombra pintada puxa para a cor de sombra, nao para o preto)
    aon = _n(nt, "ShaderNodeAmbientOcclusion", samples=16)
    aon.inputs["Distance"].default_value = 3.2
    aof = ramp(aon.outputs["AO"], .18, .92)
    sh = mixc("MULTIPLY", 1.0, (*hex_lin(shad), 1), mval)
    col = mixc("MIX", math_("ADD", math_("MULTIPLY", aof, ao * .85), 1 - ao * .85), sh, col)
    ex = EXTRA.get(key, {})
    if ex.get("toon"):
        dl = _n(nt, "ShaderNodeVectorMath", operation="DOT_PRODUCT")
        L(geo.outputs["Normal"], dl.inputs[0])
        dl.inputs[1].default_value = (-0.40, -0.45, 0.80)
        tl = ramp(dl.outputs["Value"], -0.35, 0.85)
        dark = mixc("MULTIPLY", 1.0, col, (0.50, 0.62, 0.78, 1))
        lite = mixc("MULTIPLY", 1.0, col, (1.22, 1.16, 0.90, 1))
        tc_ = mixc("MIX", tl, dark, lite)
        col = mixc("MIX", ex["toon"], col, tc_)
    if ex.get("patch"):
        # gramado: manchas largas amareladas e touceiras escuras (quebra o verde chapado)
        pa = math_("MULTIPLY", ramp(noise(.018, 2.0), .5, .72), .55 * ex["patch"])
        col = mixc("MIX", pa, col, mixc("MULTIPLY", 1.0, (*hex_lin("B4C860"), 1), mval))
        pd = math_("MULTIPLY", ramp(noise(.075, 3.0, .6), .56, .7), .45 * ex["patch"])
        col = mixc("MIX", pd, col, mixc("MULTIPLY", 1.0, (*hex_lin("4E8434"), 1), mval))
        pf = math_("MULTIPLY", ramp(noise(.9, 2.0), .62, .7), .35 * ex["patch"])
        col = mixc("MIX", pf, col, mixc("MULTIPLY", 1.0, (*hex_lin("9CCC5C"), 1), mval))
    if ex.get("mottle"):
        mt = math_("ADD", math_("MULTIPLY", math_("SUBTRACT", noise(1.15, 2.0, .6), .5), ex["mottle"] * 2.0), 1.0)
        col = mixc("MULTIPLY", 1.0, col, _gray(nt, L, mt))
    if ex.get("rust"):
        vm = _n(nt, "ShaderNodeVectorMath", operation="MULTIPLY")
        L(geo.outputs["Position"], vm.inputs[0])
        vm.inputs[1].default_value = (0.22, 0.22, 0.035)
        nzr = _n(nt, "ShaderNodeTexNoise")
        nzr.inputs["Scale"].default_value = 1.0
        nzr.inputs["Detail"].default_value = 3.0
        L(vm.outputs[0], nzr.inputs["Vector"])
        side = math_("SUBTRACT", 1.0, math_("ABSOLUTE", nrm.outputs["Z"]))
        rm_ = math_("MULTIPLY", math_("MULTIPLY", ramp(nzr.outputs[0], .56, .7), side), ex["rust"] * .8, clamp=True)
        col = mixc("MIX", rm_, col, mixc("MULTIPLY", 1.0, (*hex_lin("8E5230"), 1), mval))
    if ex.get("verdigris"):
        vg = math_("MAXIMUM", math_("SUBTRACT", 1.0, aof), math_("MULTIPLY", ramp(nrm.outputs["Z"], .5, .9), .45))
        vg = math_("MULTIPLY", math_("MULTIPLY", vg, ramp(noise(.5, 3.0), .35, .6)), ex["verdigris"], clamp=True)
        col = mixc("MIX", vg, col, mixc("MULTIPLY", 1.0, (*hex_lin("5FA48C"), 1), mval))
    # CALOR: mapas de calor (frente/tras) projetados em XZ a partir das faces de lava do grupo -> fuligem + brasa
    hv = {}
    for nm_ in ("HX0", "HW", "HZ0", "HH", "HYC", "HMODE", "HZL"):
        vn = _n(nt, "ShaderNodeValue")
        vn.name = nm_
        vn.outputs[0].default_value = 1.0
        hv[nm_] = vn.outputs[0]
    hu = math_("DIVIDE", math_("SUBTRACT", pos.outputs["X"], hv["HX0"]), hv["HW"])
    pv = math_("ADD", math_("MULTIPLY", pos.outputs["Z"], math_("SUBTRACT", 1.0, hv["HMODE"])),
               math_("MULTIPLY", pos.outputs["Y"], hv["HMODE"]))
    hw_ = math_("DIVIDE", math_("SUBTRACT", pv, hv["HZ0"]), hv["HH"])
    cxyz = _n(nt, "ShaderNodeCombineXYZ")
    L(hu, cxyz.inputs[0])
    L(hw_, cxyz.inputs[1])
    heats = []
    for nm_ in ("HEAT_F", "HEAT_B"):
        im = _n(nt, "ShaderNodeTexImage")
        im.name = nm_
        im.extension = "CLIP"
        L(cxyz.outputs[0], im.inputs["Vector"])
        heats.append(im.outputs["Color"])
    front = _n(nt, "ShaderNodeMath", operation="GREATER_THAN")
    L(pos.outputs["Y"], front.inputs[0])
    L(hv["HYC"], front.inputs[1])
    hm = mixc("MIX", front.outputs[0], heats[1], heats[0])
    hsep = _n(nt, "ShaderNodeSeparateColor")
    L(hm, hsep.inputs[0])
    fall = math_("SUBTRACT", 1.0, math_("MULTIPLY", hv["HMODE"],
                                         ramp(math_("SUBTRACT", pos.outputs["Z"], hv["HZL"]), 0.6, 4.5)))
    scorch = math_("MULTIPLY", math_("MULTIPLY", hsep.outputs[1], .75), fall, clamp=True)   # G = fuligem larga
    glow = math_("MULTIPLY", hsep.outputs[0], fall)                                      # R = brasa estreita
    col = mixc("MIX", scorch, col, mixc("MULTIPLY", 1.0, (*hex_lin("2A1C18"), 1), mval))
    hot = mixc("MIX", ramp(glow, .45, .95), (*hex_lin("C2341A"), 1), (*hex_lin("FF9A3C"), 1))
    col = mixc("MIX", math_("MULTIPLY", ramp(glow, .08, .7), .92, clamp=True), col, hot)
    # sujeira no pe (respingo de terra ate ~3 studs do chao)
    if grime > 0:
        gm = math_("MULTIPLY", math_("SUBTRACT", 1.0, ramp(pos.outputs["Z"], GROUND_Z - .2, GROUND_Z + 3.5)), grime * .55)
        gm = math_("MULTIPLY", gm, math_("ADD", math_("MULTIPLY", noise(.6, 2.0), .8), .4), clamp=True)
        col = mixc("MIX", gm, col, (*hex_lin(shad), 1))
    # musgo nas faces voltadas para cima + nas frestas baixas
    if moss > 0:
        up = ramp(nrm.outputs["Z"], .45, .8)
        blot = ramp(noise(.16, 3.0, .6), .52 - moss * .12, .58 - moss * .12)
        crev = math_("MULTIPLY", math_("SUBTRACT", 1.0, aof), ramp(noise(.3, 2.0), .45, .6))
        mm = math_("MAXIMUM", math_("MULTIPLY", up, blot), math_("MULTIPLY", crev, .8))
        mm = math_("MULTIPLY", mm, moss, clamp=True)
        mcol = mixc("MULTIPLY", 1.0, (*hex_lin("6E9C40"), 1),
                    math_("MULTIPLY", math_("ADD", math_("MULTIPLY", aof, .45), .55), math_("MULTIPLY", nA, fc)))
        col = mixc("MIX", mm, col, mcol)
    # realce de aresta convexa: desvio entre a normal chanfrada (Bevel) e a normal real, apagado nos cantos concavos
    bvn = _n(nt, "ShaderNodeBevel", samples=8)
    bvn.inputs["Radius"].default_value = erad
    dte = _n(nt, "ShaderNodeVectorMath", operation="DOT_PRODUCT")
    L(bvn.outputs["Normal"], dte.inputs[0])
    L(geo.outputs["Normal"], dte.inputs[1])
    edg = math_("MULTIPLY", ramp(math_("SUBTRACT", 1.0, dte.outputs["Value"]), .012, .14), aof)
    col = mixc("MIX", math_("MULTIPLY", edg, edge), col, (*hex_lin(high), 1))
    # brilho pintado fixo (metais): mancha de luz que nao depende da camera
    if spec > 0:
        dot = _n(nt, "ShaderNodeVectorMath", operation="DOT_PRODUCT")
        L(geo.outputs["Normal"], dot.inputs[0])
        dot.inputs[1].default_value = (-.35, -.55, .76)
        sp = math_("MULTIPLY", math_("POWER", math_("MAXIMUM", dot.outputs["Value"], 0.0), 7.0), spec, clamp=True)
        col = mixc("SCREEN", sp, col, (*hex_lin(high), 1))
    L(col, em.inputs["Color"])
    L(em.outputs[0], out.inputs["Surface"])
    img = _n(nt, "ShaderNodeTexImage")
    img.name = "BAKE"
    m.diffuse_color = (*hex_lin(base), 1)
    return m


def _gray(nt, L, v):
    c = nt.nodes.new("ShaderNodeCombineColor")
    for i in range(3):
        L(v, c.inputs[i])
    return c.outputs[0]


def build_paints():
    for k in PD:
        build_paint(k)


# ------------------------------------------------------------------ preparo das malhas
def _parts(me):
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.faces.ensure_lookup_table()
    part = {}
    k = 0
    for f in bm.faces:
        if f.index in part:
            continue
        stack = [f]
        part[f.index] = k
        while stack:
            g = stack.pop()
            for e in g.edges:
                for h in e.link_faces:
                    if h.index not in part:
                        part[h.index] = k
                        stack.append(h)
        k += 1
    bm.free()
    return part, k


def _seed_parts(me, seed):
    """atributo 'rnd' (0..1) constante por pedaco solto: cada pedra/tabua com um tom proprio"""
    part, k = _parts(me)
    rr = random.Random(seed)
    vals = [rr.random() for _ in range(k)]
    at = me.attributes.get("rnd") or me.attributes.new("rnd", "FLOAT", "FACE")
    at.data.foreach_set("value", [vals[part[i]] for i in range(len(me.polygons))])
    return part, k


WATER_Z = -13.0


def _on_plateau(x, z, margin=1.0):
    import sn_layout as L_
    import sn_vegplan as VP
    return VP._in_poly(x, z, L_.PLATEAU) and VP._edge_dist(x, z, L_.PLATEAU) > margin


def cull_hidden(ob, dmax=2.5, eps=0.004, frac=0.94, ground=GROUND_Z - 0.2):
    """apaga faces que ninguem ve (adaptado do op_kit.cull_hidden da Ilha 5): (a) face encostada numa face voltada para
    ela, (b) face dentro de outro volume do mesmo objeto, (c) fundo apoiado no chao e faces inteiras abaixo do chao.
    So apaga se TODOS os raios (centro, vertices, meios de aresta) confirmam. Devolve (faces, area) cortadas."""
    from mathutils.bvhtree import BVHTree
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.transform(ob.matrix_world)
    bm.normal_update()
    bm.faces.ensure_lookup_table()

    def _gkey(f):
        c = f.calc_center_median()
        return (round(c.x, 4), round(c.y, 4), round(c.z, 4), round(f.normal.x, 3), round(f.normal.y, 3),
                round(f.normal.z, 3), len(f.verts))
    order = sorted(bm.faces, key=_gkey)
    tv, tp, t2f = [], [], []
    for f in order:
        cs = [v.co.copy() for v in f.verts]
        k0 = min(range(len(cs)), key=lambda i: (round(cs[i].x, 4), round(cs[i].y, 4), round(cs[i].z, 4)))
        cs = cs[k0:] + cs[:k0]
        tp.append(list(range(len(tv), len(tv) + len(cs))))
        tv += cs
        t2f.append(f.index)
    tree = BVHTree.FromPolygons(tv, tp)
    kill = []
    for f in bm.faces:
        n = f.normal
        if n.length < 0.5:
            continue
        zs = [v.co.z for v in f.verts]
        cc = f.calc_center_median()
        if max(zs) < WATER_Z - 0.3:
            kill.append(f)                                 # inteira debaixo d'agua
            continue
        if _on_plateau(cc.x, -cc.y) and (max(zs) < ground - 0.3 or (n.z < -0.9 and max(zs) < ground + 0.45)):
            kill.append(f)                                 # enterrada / apoiada no chao do plato
            continue
        c = f.calc_center_median()
        vs_ = [v.co for v in f.verts]
        pts = [c] + [c + (v - c) * frac for v in vs_]
        pts += [c + ((vs_[i] + vs_[(i + 1) % len(vs_)]) / 2 - c) * frac for i in range(len(vs_))]
        pts += [c + (v - c) * 0.5 for v in vs_]
        t1 = (vs_[1] - vs_[0])
        if t1.length > 1e-6:
            t1 = t1.normalized()
            t2 = n.cross(t1)
            dj = t1 * 0.00131 + t2 * 0.00217
            pts = [p + dj for p in pts]
        ok = True
        for p in pts:
            hit = tree.ray_cast(p + n * eps, n, dmax)
            if hit[0] is None or t2f[hit[2]] == f.index:
                ok = False
                break
            if hit[1].dot(n) < 0.0 and hit[3] > 2 * eps:
                ok = False
                break
        if ok:
            kill.append(f)
    area = sum(f.calc_area() for f in kill)
    nk = len(kill)
    if kill:
        bmesh.ops.delete(bm, geom=kill, context="FACES")
    bm.transform(ob.matrix_world.inverted())
    bm.to_mesh(me)
    bm.free()
    me.update()
    return nk, area


def _apply_paints(ob):
    me = ob.data
    for i, m in enumerate(me.materials):
        key = _paint_of(m.name) if m else None
        me.materials[i] = bpy.data.materials["P_" + (key or "pedra")]


def _split_by_area(ob, area_max):
    """divide o objeto em pedacos <= area_max (pedacos soltos inteiros; bissecao no eixo maior pela mediana de area)"""
    me = ob.data
    part, k = _parts(me)
    cen = [Vector((0, 0, 0)) for _ in range(k)]
    area = [0.0] * k
    mw = ob.matrix_world
    for p in me.polygons:
        a = p.area
        cen[part[p.index]] += (mw @ p.center) * a
        area[part[p.index]] += a
    for i in range(k):
        if area[i] > 0:
            cen[i] /= area[i]
    tot = sum(area)
    if tot <= area_max:
        return [ob], tot

    def cut(ids):
        if sum(area[i] for i in ids) <= area_max or len(ids) < 2:
            return [ids]
        ax = max(range(3), key=lambda a: max(cen[i][a] for i in ids) - min(cen[i][a] for i in ids))
        ids = sorted(ids, key=lambda i: cen[i][ax])
        half = sum(area[i] for i in ids) / 2
        acc = 0.0
        j = 0
        for j, i in enumerate(ids):
            acc += area[i]
            if acc >= half:
                break
        j = max(1, min(len(ids) - 1, j + 1))
        return cut(ids[:j]) + cut(ids[j:])
    groups = cut(list(range(k)))
    res = []
    for gi, ids in enumerate(groups):
        sel = set(ids)
        bm = bmesh.new()
        bm.from_mesh(me)
        bm.faces.ensure_lookup_table()
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if part[f.index] not in sel], context="FACES")
        nm = me.copy()
        bm.to_mesh(nm)
        bm.free()
        no = ob.copy()
        no.data = nm
        no.name = "%s_%d" % (ob.name, gi + 1)
        for c in ob.users_collection:
            c.objects.link(no)
        res.append(no)
    old = ob.data
    bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.meshes.remove(old)
    return res, tot


def _unwrap(ob, margin=0.004):
    bpy.context.view_layer.update()
    for o in list(bpy.context.view_layer.objects):
        if o is not None:
            o.select_set(False)
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    me = ob.data
    while me.uv_layers:
        me.uv_layers.remove(me.uv_layers[0])
    me.uv_layers.new(name="UVMap")
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(62), island_margin=margin, area_weight=0.0,
                             correct_aspect=True, scale_to_bounds=False)
    bpy.ops.object.mode_set(mode="OBJECT")


def _bake(ob, atlas, samples=16, size=SIZE):
    sc = bpy.context.scene
    eng0 = sc.render.engine
    img = bpy.data.images.get(atlas)
    if img:
        bpy.data.images.remove(img)
    img = bpy.data.images.new(atlas, size, size, alpha=False)
    img.colorspace_settings.name = "sRGB"
    for m in ob.data.materials:
        n = m.node_tree.nodes["BAKE"]
        n.image = img
        m.node_tree.nodes.active = n
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = False
    bpy.context.view_layer.update()
    for o in list(bpy.context.view_layer.objects):
        if o is not None:
            o.select_set(False)
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    try:
        bpy.ops.object.bake(type="EMIT", margin=6, use_clear=True)
    finally:
        sc.render.engine = eng0
    n = size * size
    px = [0.0] * (n * 4)
    img.pixels.foreach_get(px)
    cheio = sum(1 for i in range(0, n * 4, 4 * 97) if px[i] + px[i + 1] + px[i + 2] > .02) / (n / 97)
    if cheio < .01:
        raise RuntimeError("BAKE VAZIO em %s (%.0f%%)" % (atlas, cheio * 100))
    path = os.path.join(TEX, atlas + ".png")
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    return path, cheio


def _black():
    im = bpy.data.images.get("_HEAT_NONE")
    if im is None:
        im = bpy.data.images.new("_HEAT_NONE", 4, 4, alpha=False)
        im.pixels.foreach_set([0.0, 0.0, 0.0, 1.0] * 16)
        im.colorspace_settings.name = "Non-Color"
    return im


def _blur(a, sig):
    import numpy as np
    r = max(1, int(sig * 3))
    x = np.arange(-r, r + 1)
    k = np.exp(-x * x / (2.0 * sig * sig))
    k /= k.sum()
    a = np.apply_along_axis(lambda m: np.convolve(m, k, mode="same"), 0, a)
    return np.apply_along_axis(lambda m: np.convolve(m, k, mode="same"), 1, a)


def _set_heat(img_f, img_b, x0=0.0, w=1.0, z0=0.0, h=1.0, yc=0.0, mode=0.0, zl=0.0):
    for m in bpy.data.materials:
        if m.name.startswith("P_") and m.node_tree and "HEAT_F" in m.node_tree.nodes:
            nt = m.node_tree
            nt.nodes["HEAT_F"].image = img_f
            nt.nodes["HEAT_B"].image = img_b
            nt.nodes["HX0"].outputs[0].default_value = x0
            nt.nodes["HW"].outputs[0].default_value = w
            nt.nodes["HZ0"].outputs[0].default_value = z0
            nt.nodes["HH"].outputs[0].default_value = h
            nt.nodes["HYC"].outputs[0].default_value = yc
            nt.nodes["HMODE"].outputs[0].default_value = mode
            nt.nodes["HZL"].outputs[0].default_value = zl


def heat_maps(prefix, ob, ppst=4.0, glow=1.1, scorch=4.5, pad=16.0):
    """rasteriza as faces de lava do grupo no plano XZ (frente e tras separadas pelo centro em Y do grupo) e borra:
    R = brasa (sigma curto), G = fuligem (sigma largo). Liga as imagens e o mapeamento em todas as tintas."""
    import numpy as np
    lava = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(prefix + "__") and o.data.materials
            and o.data.materials[0] and o.data.materials[0].name.split(".")[0] in ("SN_Lava", "SN_LavaHot")]
    bb = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    yc = sum(v.y for v in bb) / 8
    tris = []
    up_a = side_a = 0.0
    for o in lava:
        for p in o.data.polygons:
            n = (o.matrix_world.to_3x3() @ p.normal)
            if abs(n.z) > 0.7:
                up_a += p.area
            else:
                side_a += p.area
    mode = 1.0 if up_a > side_a else 0.0
    for o in lava:
        mw = o.matrix_world
        me = o.data
        me.calc_loop_triangles()
        for lt in me.loop_triangles:
            vs = [mw @ me.vertices[i].co for i in lt.vertices]
            cy = (mw @ me.polygons[lt.polygon_index].center).y
            tris.append((True if mode else (cy > yc), (vs[0], vs[1], vs[2])))
    if not tris:
        _set_heat(_black(), _black())
        return None
    x0 = min(v.x for v in bb) - pad
    x1 = max(v.x for v in bb) + pad
    if mode:
        z0 = min(v.y for v in bb) - pad
        z1 = max(v.y for v in bb) + pad
    else:
        z0 = min(v.z for v in bb) - pad
        z1 = max(v.z for v in bb) + pad
    Wn = int((x1 - x0) * ppst)
    Hn = int((z1 - z0) * ppst)
    ims = {}
    for side in ((True,) if mode else (True, False)):
        mask = np.zeros((Hn, Wn))
        for s_, (a, b, c) in tris:
            if s_ != side:
                continue
            P = np.array([[(v.x - x0) * ppst, ((v.y if mode else v.z) - z0) * ppst] for v in (a, b, c)])
            lo = np.clip(np.floor(P.min(0)).astype(int), 0, [Wn - 1, Hn - 1])
            hi = np.clip(np.ceil(P.max(0)).astype(int) + 1, 0, [Wn, Hn])
            if hi[0] <= lo[0] or hi[1] <= lo[1]:
                continue
            ys, xs = np.mgrid[lo[1]:hi[1], lo[0]:hi[0]]
            px, py = xs + 0.5, ys + 0.5
            (ax, ay), (bx, by), (cx, cy) = P
            d = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
            if abs(d) < 1e-6:
                mask[np.clip(P[:, 1].astype(int), 0, Hn - 1), np.clip(P[:, 0].astype(int), 0, Wn - 1)] = 1.0
                continue
            l1 = ((by - cy) * (px - cx) + (cx - bx) * (py - cy)) / d
            l2 = ((cy - ay) * (px - cx) + (ax - cx) * (py - cy)) / d
            l3 = 1 - l1 - l2
            ins = (l1 >= -0.05) & (l2 >= -0.05) & (l3 >= -0.05)
            mask[ys[ins], xs[ins]] = 1.0
        g1 = _blur(mask, glow * ppst)
        g2 = _blur(mask, scorch * ppst)
        if g1.max() > 0:
            g1 = np.clip(g1 / g1.max() * 1.6, 0, 1)
        if g2.max() > 0:
            g2 = np.clip(g2 / g2.max() * 1.8, 0, 1)
        rgba = np.zeros((Hn, Wn, 4), dtype=np.float32)
        rgba[:, :, 0] = g1
        rgba[:, :, 1] = g2
        rgba[:, :, 3] = 1.0
        nm = "_HEAT_%s_%s" % (prefix, "F" if side else "B")
        im = bpy.data.images.get(nm)
        if im:
            bpy.data.images.remove(im)
        im = bpy.data.images.new(nm, Wn, Hn, alpha=False, float_buffer=True)
        im.colorspace_settings.name = "Non-Color"
        im.pixels.foreach_set(rgba.ravel())
        ims[side] = im
    zl = 0.0
    if tris:
        zs = sorted(sum(v.z for v in tri) / 3 for _, tri in tris)
        zl = zs[len(zs) // 2]
    _set_heat(ims[True], ims.get(False, ims[True]), x0, x1 - x0, z0, z1 - z0, yc, mode, zl)
    return ims


def _geo_hash(me):
    """impressao digital da malha (posicoes arredondadas + topologia dos loops) para saber se a UV guardada serve"""
    import hashlib
    import numpy as np
    co = np.zeros(len(me.vertices) * 3, dtype=np.float64)
    me.vertices.foreach_get("co", co)
    lv = np.zeros(len(me.loops), dtype=np.int64)
    me.loops.foreach_get("vertex_index", lv)
    h = hashlib.sha1()
    h.update(np.round(co, 3).astype(np.float32).tobytes())
    h.update(lv.tobytes())
    return h.hexdigest()


def _uv_save(me, path, gh):
    import numpy as np
    uv = np.zeros(len(me.loops) * 2, dtype=np.float32)
    me.uv_layers["UVMap"].data.foreach_get("uv", uv)
    np.savez_compressed(path, uv=uv, gh=np.array([gh]))


def _uv_load(me, path, gh):
    """devolve True se a UV guardada e desta mesma malha (e a aplica)"""
    import numpy as np
    import os
    if not os.path.exists(path):
        return False
    d = np.load(path)
    if str(d["gh"][0]) != gh or len(d["uv"]) != len(me.loops) * 2:
        return False
    while me.uv_layers:
        me.uv_layers.remove(me.uv_layers[0])
    me.uv_layers.new(name="UVMap")
    me.uv_layers["UVMap"].data.foreach_set("uv", d["uv"])
    return True


def final_material(atlas, path):
    m = bpy.data.materials.get(atlas) or bpy.data.materials.new(atlas)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bs = nt.nodes.new("ShaderNodeBsdfPrincipled")
    im = nt.nodes.new("ShaderNodeTexImage")
    im.image = bpy.data.images.load(path, check_existing=True)
    im.image.reload()
    bs.inputs["Roughness"].default_value = 0.85
    nt.links.new(im.outputs["Color"], bs.inputs["Base Color"])
    nt.links.new(bs.outputs[0], out.inputs[0])
    m.diffuse_color = (0.6, 0.6, 0.6, 1)
    return m


def bake_group(prefix, atlas_base, pps=8.0, samples=16, reuse=False, size=SIZE):
    """junta as malhas pintaveis do Build <prefix> e assa em 1+ atlas SNB_<atlas_base>[_k]. pps = px por stud alvo."""
    t0 = time.time()
    if "P_pedra" not in bpy.data.materials:
        build_paints()
    objs = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(prefix + "__")
            and o.data.materials and o.data.materials[0] and not keep_separate(o.data.materials[0].name)]
    if not objs:
        return []
    bpy.context.view_layer.update()
    for o in list(bpy.context.view_layer.objects):
        if o is not None:
            o.select_set(False)
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    if len(objs) > 1:
        bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    ob.name = "%s__SNB_%s" % (prefix, atlas_base)
    nk, ak = cull_hidden(ob)
    print("CULL %s: %d faces / %.0f studs2 escondidas" % (prefix, nk, ak))
    _apply_paints(ob)
    heat_maps(prefix, ob)
    area_max = size * size * PACK / (pps * pps)
    parts, tot = _split_by_area(ob, area_max)
    out = []
    for k, o in enumerate(parts):
        atlas = "SNB_%s" % atlas_base + ("_%d" % (k + 1) if len(parts) > 1 else "")
        o.name = "%s__%s" % (prefix, atlas)
        _seed_parts(o.data, atlas)
        path = os.path.join(TEX, atlas + ".png")
        uvp = os.path.join(TEX, atlas + ".uv.npz")
        gh = _geo_hash(o.data)
        ok = reuse and os.path.exists(path) and _uv_load(o.data, uvp, gh)
        if not ok:
            if reuse:
                print("  %s: malha mudou (ou sem UV guardada) -> reassando" % atlas)
            _unwrap(o)
            path, cheio = _bake(o, atlas, samples, size)
            _uv_save(o.data, uvp, gh)
        m = final_material(atlas, path)
        o.data.materials.clear()
        o.data.materials.append(m)
        o.data.polygons.foreach_set("material_index", [0] * len(o.data.polygons))
        o.data.update()
        out.append(atlas)
    print("BAKE %s: %.0f studs2 -> %d atlas %s em %.0fs" % (prefix, tot, len(parts), out, time.time() - t0))
    return out
