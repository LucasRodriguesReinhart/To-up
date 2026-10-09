# sn_lib.py - base do lobby SANTUARIO DO DEUS-FERREIRO sobre o pipeline do Wolfberg (wb_lib: Build com UV por peca,
# materiais WB_*, texturas V2) e o compartilhado do lobby (forja_mineradora: fm_lib/export_roblox SO LEITURA).
# Acrescenta os materiais SN_* (pedra de templo, frisos de runas, basalto, bronze, musgo, lava/runa/cristal Neon) e
# as texturas do sn_tex. Coordenadas: Roblox (X leste, Z sul, Y cima) nas plantas; Blender = (X, -Z, Y).
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WB = os.path.normpath(os.path.join(HERE, "..", "wolfberg"))
for p in (WB, HERE):
    if p in sys.path:
        sys.path.remove(p)
    sys.path.insert(0, p)            # ordem final: HERE, WB, (VILA, FORJA via wb_lib)

import wb_lib as W                   # noqa: E402  (registra o caminho do pipeline compartilhado)
import fm_lib                        # noqa: E402
import fm_mat_textures as TX         # noqa: E402
import wb_tex                        # noqa: E402
import sn_tex                        # noqa: E402
from fm_lib import MATS, S           # noqa: E402

SNMATS = {
    "SN_Ashlar":        ((192, 182, 160), 0.9, 0.0, 0, None, 0.0),
    "SN_Ashlar_Dark":   ((126, 118, 110), 0.9, 0.0, 0, None, 0.0),
    "SN_Ashlar_Moss":   ((176, 170, 146), 0.9, 0.0, 0, None, 0.0),
    "SN_Carved":        ((192, 182, 162), 0.9, 0.0, 0, None, 0.0),
    "SN_Basalt":        ((88, 82, 80), 0.9, 0.0, 0, None, 0.0),
    "SN_Iron":          ((67, 73, 87), 0.6, 0.4, 0, None, 0.0),
    "SN_Bronze":        ((120, 96, 62), 0.45, 0.7, 0, None, 0.0),
    "SN_Moss":          ((80, 118, 48), 0.9, 0.0, 0, None, 0.0),
    "SN_WoodAged":      ((112, 96, 80), 0.85, 0.0, 0, None, 0.0),
    "SN_Plaza":         ((200, 190, 170), 0.9, 0.0, 0, None, 0.0),
    "SN_Rubble":        ((160, 150, 134), 0.9, 0.0, 0, None, 0.0),
    # cor solida / brilho (Neon no Roblox)
    "SN_Lava":          ((255, 110, 30), 0.5, 0.0, 3.0, (255, 100, 25), 0.0),
    "SN_LavaHot":       ((255, 214, 110), 0.5, 0.0, 4.0, (255, 210, 100), 0.0),
    "SN_LavaCrust":     ((52, 30, 26), 0.9, 0.0, 0, None, 0.0),
    "SN_Rune":          ((255, 214, 128), 0.5, 0.0, 2.2, (255, 206, 110), 0.0),
    "SN_CrystalBlue":   ((120, 210, 255), 0.3, 0.0, 1.8, (110, 200, 255), 0.0),
    "SN_CrystalAmber":  ((255, 176, 70), 0.3, 0.0, 1.8, (255, 170, 60), 0.0),
    "SN_Gold":          ((214, 172, 82), 0.35, 0.9, 0, None, 0.0),
    "SN_Chain":         ((70, 64, 62), 0.6, 0.6, 0, None, 0.0),
    "SN_FlowerBlue":    ((118, 150, 236), 0.8, 0.0, 0, None, 0.0),
    "SN_Petal":         ((240, 176, 196), 0.8, 0.0, 0, None, 0.0),
    "SN_Ivy":           ((70, 120, 52), 0.85, 0.0, 0, None, 0.0),
    "SN_RockFar":       ((126, 120, 112), 0.9, 0.0, 0, None, 0.0),
    "SN_SnowFar":       ((226, 232, 242), 0.9, 0.0, 0, None, 0.0),
    "SN_Mountain":      ((140, 150, 168), 0.9, 0.0, 0, None, 0.0),
    "SN_Hills":         ((112, 164, 72), 0.9, 0.0, 0, None, 0.0),
    "SN_Leaf":          ((108, 160, 68), 0.85, 0.0, 0, None, 0.0),
    "SN_LeafLight":     ((138, 184, 76), 0.85, 0.0, 0, None, 0.0),
    "SN_LeafGold":      ((214, 162, 58), 0.85, 0.0, 0, None, 0.0),
    "SN_PineLeaf":      ((63, 122, 78), 0.85, 0.0, 0, None, 0.0),
    "SN_Bark":          ((122, 90, 62), 0.9, 0.0, 0, None, 0.0),
    "SN_CanvasRed":     ((178, 52, 40), 0.85, 0.0, 0, None, 0.0),
    "SN_CanvasBlue":    ((58, 92, 160), 0.85, 0.0, 0, None, 0.0),
    "SN_CanvasGreen":   ((70, 120, 70), 0.85, 0.0, 0, None, 0.0),
    "SN_CanvasOchre":   ((204, 150, 60), 0.85, 0.0, 0, None, 0.0),
    "SN_CanvasCream":   ((226, 212, 180), 0.85, 0.0, 0, None, 0.0),
    "SN_CanvasViolet":  ((120, 70, 170), 0.85, 0.0, 0, None, 0.0),
    "SN_CanvasTan":     ((208, 154, 85), 0.85, 0.0, 0, None, 0.0),
    "SN_LeatherDark":   ((84, 52, 32), 0.85, 0.0, 0, None, 0.0),
    "SN_Rope":          ((196, 160, 104), 0.85, 0.0, 0, None, 0.0),
    "SN_Leather":       ((120, 76, 46), 0.85, 0.0, 0, None, 0.0),
    "SN_Paper":         ((238, 228, 200), 0.85, 0.0, 0, None, 0.0),
    "SN_RoofTile":      ((196, 98, 60), 0.85, 0.0, 0, None, 0.0),
    "SN_RoofTileDark":  ((150, 70, 46), 0.85, 0.0, 0, None, 0.0),
    "SN_Terracotta":    ((186, 100, 64), 0.85, 0.0, 0, None, 0.0),
    "SN_Slate":         ((40, 46, 56), 0.85, 0.0, 0, None, 0.0),
    "SN_CrystalViolet": ((186, 120, 255), 0.3, 0.0, 1.8, (186, 120, 255), 0.0),
    "SN_CrystalRed":    ((255, 80, 70), 0.3, 0.0, 1.8, (255, 80, 70), 0.0),
    "SN_HillA":         ((108, 162, 72), 0.9, 0.0, 0, None, 0.0),
    "SN_HillB":         ((124, 174, 80), 0.9, 0.0, 0, None, 0.0),
    "SN_HillC":         ((146, 178, 88), 0.9, 0.0, 0, None, 0.0),
    "SN_HillForest":    ((66, 112, 62), 0.9, 0.0, 0, None, 0.0),
    "SN_PineFarDark":   ((44, 86, 58), 0.9, 0.0, 0, None, 0.0),
    "SN_PineFar":       ((58, 108, 66), 0.9, 0.0, 0, None, 0.0),
    "SN_PineFarLight":  ((86, 136, 78), 0.9, 0.0, 0, None, 0.0),
}
SN_TEX_RULES = [("SN_Ashlar_Dark", "sn_ashlar_dark"), ("SN_Ashlar_Moss", "sn_ashlar_moss"), ("SN_Ashlar", "sn_ashlar"),
                ("SN_Carved", "sn_carved"), ("SN_Basalt", "sn_basalt"), ("SN_Bronze", "sn_bronze"), ("SN_Moss", "sn_moss"),
                ("SN_WoodAged", "sn_wood_aged"), ("SN_Plaza", "sn_plaza"), ("SN_Rubble", "sn_rubble"),
                ("SN_Ivy", "wb_leaf"), ("SN_RockFar", "sn_rock_far"), ("SN_SnowFar", "sn_snow_far"),
                ("SN_Mountain", "sn_mountain"), ("SN_Hills", "sn_hills")]
SN_GRAIN = ("SN_WoodAged",)
SN_RBX_RULES = [("SN_LavaHot", "Neon", 0.0, False), ("SN_Lava", "Neon", 0.0, False), ("SN_Rune", "Neon", 0.0, False),
                ("SN_Crystal", "Neon", 0.0, False), ("SN_Gold", "Metal", 0.0, True), ("SN_Bronze", "Metal", 0.0, True),
                ("SN_Chain", "Metal", 0.0, True), ("SN_Moss", "Grass", 0.0, True), ("SN_Ivy", "Grass", 0.0, True),
                ("SN_Flower", "SmoothPlastic", 0.0, False), ("SN_Petal", "SmoothPlastic", 0.0, False),
                ("SN_", "SmoothPlastic", 0.0, True)]
_done = [False]


def register():
    W.register()
    if _done[0]:
        return
    _done[0] = True
    for k, (c, rough, metal, emit, ecol, var) in SNMATS.items():
        MATS.setdefault(k, (S(*c), rough, metal, emit, S(*ecol) if ecol else None, var))
    for r in reversed(SN_RBX_RULES):
        if r not in fm_lib.RBX_RULES:
            fm_lib.RBX_RULES.insert(0, r)
    for p, k in reversed(SN_TEX_RULES):
        if (p, k) not in fm_lib.TEX_RULES:
            fm_lib.TEX_RULES = ((p, k),) + tuple(fm_lib.TEX_RULES)
    W.GRAIN = tuple(W.GRAIN) + SN_GRAIN
    TX.TEXTURES.update(sn_tex.TEXTURES)
    _ens, _path = TX.ensure, TX.path

    def ensure(force=False, out_dir=None):
        sn = {k: TX.TEXTURES.pop(k) for k in list(TX.TEXTURES) if k in sn_tex.TEXTURES}
        try:
            paths = _ens(force, out_dir)
        finally:
            TX.TEXTURES.update(sn)
        paths.update(sn_tex.ensure())
        return paths

    def path(key):
        return sn_tex.path(key) if key in sn_tex.TEXTURES else _path(key)
    TX.ensure, TX.path = ensure, path
    sn_tex.ensure()


# atalhos reexportados
Build = W.Build
RB = W.RB
V = W.V
camera = W.camera
render = W.render
reset_scene = W.reset_scene
collection = W.collection


def setup_render(res=(1600, 900), samples=64):
    """manha quente: sol baixo a leste-sudeste raspando as ruinas; ceu claro"""
    W.setup_render(res=res, samples=samples, sun_rot=(58, 0, 128), sun_energy=3.1, sky=(0.56, 0.74, 0.95), world=0.75,
                   exposure=-0.15)
    bloom()


def bloom(threshold=1.0, strength=0.45, size=0.55, fog=0.5, fog_start=90.0, fog_depth=1500.0,
          haze=(0.74, 0.83, 0.95)):
    """compositor das previas: NEVOA de distancia (passe Mist, imita a Atmosphere do Roblox) + bloom (Neon/BloomEffect)"""
    import bpy
    sc = bpy.context.scene
    try:
        vl = sc.view_layers[0]
        vl.use_pass_mist = True
        ms = sc.world.mist_settings
        ms.start = fog_start
        ms.depth = fog_depth
        ms.falloff = "LINEAR"
        ng = bpy.data.node_groups.get("SN_Comp") or bpy.data.node_groups.new("SN_Comp", "CompositorNodeTree")
        ng.nodes.clear()
        for it in list(ng.interface.items_tree):
            ng.interface.remove(it)
        ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        rl = ng.nodes.new("CompositorNodeRLayers")
        mul = ng.nodes.new("ShaderNodeMath")
        mul.operation = "MULTIPLY"
        mul.use_clamp = True
        mul.inputs[1].default_value = fog
        mix = ng.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.blend_type = "MIX"
        mix.inputs[7].default_value = (*haze, 1.0)
        gl = ng.nodes.new("CompositorNodeGlare")
        out = ng.nodes.new("NodeGroupOutput")
        for k, v in (("Type", "Bloom"), ("Quality", "High")):
            try:
                gl.inputs[k].default_value = v
            except Exception as e:
                print("bloom", k, e)
        gl.inputs["Threshold"].default_value = threshold
        gl.inputs["Strength"].default_value = strength
        gl.inputs["Size"].default_value = size
        if "Mist" in rl.outputs and fog > 0:
            ng.links.new(rl.outputs["Mist"], mul.inputs[0])
            ng.links.new(mul.outputs[0], mix.inputs[0])
            ng.links.new(rl.outputs["Image"], mix.inputs[6])
            ng.links.new(mix.outputs[2], gl.inputs["Image"])
        else:
            print("NEVOA indisponivel (sem passe Mist)")
            ng.links.new(rl.outputs["Image"], gl.inputs["Image"])
        ng.links.new(gl.outputs["Image"], out.inputs[0])
        sc.compositing_node_group = ng
        sc.render.use_compositing = True
    except Exception as e:
        print("BLOOM indisponivel:", e)
