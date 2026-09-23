# fm_mat_rbx - traducao dos materiais do lobby para o Roblox (Enum.Material, cor calibrada, transparencia, sombra)
# Sem efeitos colaterais na importacao: usado pelo export_roblox.py, pelo export_vfx.py (via export_roblox) e pelo
# preview FM_MAT_PREVIEW=roblox do fm_lib (o Blender mostra a cor que o Roblox recebe).
import fm_lib

# ------------------------------------------------------------------ Enum.Material por prefixo
# (prefixo, Enum.Material do modo padrao "hibrido" testado no Studio, transparencia, CastShadow)
# Hibrido (achado do Studio): material rico so onde a superficie e grande e lisa (Grass, Slate, Wood, Ground);
# SmoothPlastic onde a GEOMETRIA ja desenha o padrao (calcamento, alvenaria, telhas, folhas).
# Neon SO em lanternas, forja, cristais (nucleo), espirais e brilhos de portal: janela comum = Window_Warm (SmoothPlastic).
# Glass so em P_OPM_*. Agua/cachoeira/espuma opacas (a transparencia do Roblox mostra o fundo cinza).
RBX_RULES = [
    ("Stone_Grout", "SmoothPlastic", 0.0, False),
    ("Stone_Paving", "SmoothPlastic", 0.0, False),
    ("Stone_", "SmoothPlastic", 0.0, True),
    ("Cliff_Rock", "Slate", 0.0, True),
    ("Far_Haze", "SmoothPlastic", 0.0, False),
    ("Grass_Tuft", "Grass", 0.0, False),
    ("Grass", "Grass", 0.0, False),
    ("Dirt", "Ground", 0.0, False),
    ("Wood_", "Wood", 0.0, True),
    ("Bark", "Wood", 0.0, True),
    ("Rope", "Fabric", 0.0, False),                 # fina: sombra vira ruido
    ("Emblem_", "SmoothPlastic", 0.0, False),       # placa rente a parede
    ("Roof", "SmoothPlastic", 0.0, True),
    ("Plaster", "SmoothPlastic", 0.0, True),
    ("Leaf_", "SmoothPlastic", 0.0, False),
    ("Flower_", "SmoothPlastic", 0.0, False),
    ("Metal_Rust", "CorrodedMetal", 0.0, True),
    ("Metal_Heated", "Neon", 0.0, False),
    ("Metal_", "Metal", 0.0, True),
    ("P_DB_Gold", "Metal", 0.0, True),
    ("Water_Fall", "SmoothPlastic", 0.0, False),
    ("Water", "SmoothPlastic", 0.0, False),
    ("Foam", "SmoothPlastic", 0.0, False),
    ("P_OPM_Glass", "Glass", 0.2, True),
    ("P_OPM_DarkGlass", "Glass", 0.0, True),
    ("P_OPM_Neon", "Neon", 0.0, False),
    ("Cloth_", "Fabric", 0.0, True),
    ("Leather", "Fabric", 0.0, True),
    ("Crystal_Blue_Core", "Neon", 0.0, False),
    ("Crystal_Purple_Core", "Neon", 0.0, False),
    ("Crystal_", "SmoothPlastic", 0.0, False),      # casca; as pontas pequenas do topo saem como *_Core (Neon)
    ("Forge_Emissive", "Neon", 0.0, False),
    ("Forge_Glow_Soft", "Neon", 0.0, False),
    ("Lantern_Glow", "Neon", 0.0, False),
    ("Window_Warm", "SmoothPlastic", 0.0, False),
    ("Smoke", "SmoothPlastic", 0.3, False),
]
# materiais desconhecidos (registrados por outros modulos): palavra-chave -> (Material, transp, sombra)
RBX_KEYWORDS = [
    (("swirl", "glow", "emissive", "neon", "lantern", "crystal", "heated", "fire", "flame", "ember", "lava", "spark"),
     ("Neon", 0.0, False)),
    (("waterfall", "water", "foam", "spray"), ("SmoothPlastic", 0.0, False)),
    (("glass", "window"), ("Glass", 0.2, True)),
    (("rust", "corrod"), ("CorrodedMetal", 0.0, True)),
    (("metal", "iron", "steel", "gold", "brass", "bronze", "copper", "chain", "blade"), ("Metal", 0.0, True)),
    (("grass", "moss", "lawn"), ("Grass", 0.0, False)),
    (("leaf", "foliage", "petal", "bush", "ivy", "vine", "flower"), ("SmoothPlastic", 0.0, False)),
    (("cliff", "rock", "boulder", "slate"), ("Slate", 0.0, True)),
    (("wood", "plank", "bark", "beam", "timber", "log", "bamboo"), ("Wood", 0.0, True)),
    (("dirt", "mud", "soil", "ground", "gravel"), ("Ground", 0.0, False)),
    (("sand",), ("Sand", 0.0, False)),
    (("snow",), ("Snow", 0.0, False)),
    (("ice",), ("Ice", 0.0, True)),
    (("cloth", "banner", "fabric", "rope", "canvas", "leather", "flag", "sail"), ("Fabric", 0.0, True)),
]

# ------------------------------------------------------------------ cor calibrada
# (cor exportada antes, cor certa) testada no Studio (A/B em LOBBY_FORJA_PREVIEW.VARIANTE_CORRIGIDA). Aplica-se por
# RAZAO por canal a toda a familia registrada em fm_lib.VARIANT_OF (variantes B/C e mudancas de paleta seguem junto).
# None no 1o campo = cor ABSOLUTA. Nao ha mais fallback por prefixo: um material sem entrada (nem ele nem a base da
# familia registrada) sai com a propria cor do Blender. Perspectiva aerea explicita: proximo < medio < longe em
# valor, cada plano mais frio.
RBX_CAL = {
    "Cliff_Rock": ((139, 139, 147), (136, 130, 122)),
    "Cliff_Rock_Dark": ((108, 108, 118), (102, 96, 90)),
    "Cliff_Rock_Top": (None, (146, 136, 128)),
    "Cliff_Rock_Mid": (None, (132, 134, 146)),
    "Cliff_Rock_Mid_Dark": (None, (106, 108, 122)),
    "Cliff_Rock_Far": (None, (152, 160, 180)),
    "Cliff_Rock_Far_Dark": (None, (130, 136, 158)),
    "Far_Haze": (None, (150, 162, 170)),
    # familias cuja paleta do Blender mudou (pedra/madeira mais quentes, telhado mais escuro): (cor A no Blender
    # quando foi calibrada, alvo no Roblox); a paleta nova segue pela razao.
    "Stone_Light": ((150, 141, 129), (156, 148, 136)),
    "Stone_Dark": ((100, 92, 86), (102, 95, 88)),
    "Stone_Grout": ((88, 82, 76), (88, 82, 76)),
    "Stone_Paving": ((158, 145, 131), (158, 146, 132)),
    "Stone_Heated": (None, (120, 58, 36)),
    "Grass": ((96, 152, 58), (90, 134, 62)),
    "Grass_Dark": ((63, 108, 63), (60, 98, 60)),
    "Grass_Dry": (None, (140, 128, 76)),
    "Dirt": ((134, 108, 80), (124, 100, 76)),
    "Wood_Light": ((160, 114, 74), (148, 110, 80)),
    "Wood_Dark": ((100, 66, 43), (92, 64, 47)),
    "Wood_Plank": ((136, 95, 61), (126, 92, 66)),
    "Bark": ((144, 118, 89), (120, 98, 76)),
    "Rope": (None, (190, 172, 140)),
    "Roof": ((110, 108, 114), (106, 104, 106)),
    "Roof_Red": ((179, 89, 75), (168, 86, 74)),
    "Plaster": ((200, 184, 162), (196, 184, 166)),
    "Leaf_Pine": ((69, 134, 89), (64, 120, 70)),
    "Leaf_Pine_Light": ((129, 177, 111), (116, 158, 96)),
    "Leaf_Palm": ((124, 188, 108), (110, 166, 94)),
    "Leaf_Sakura": (None, (242, 188, 212)),
    "Flower_Pink": (None, (232, 128, 168)),
    "Flower_White": (None, (236, 232, 220)),
    "Metal_Dark": ((85, 85, 89), (78, 76, 76)),
    "Metal_Iron": ((124, 124, 129), (116, 114, 112)),
    "Metal_Brass": ((203, 170, 105), (186, 148, 90)),
    "Metal_Burnt": (None, (66, 56, 56)),
    "Metal_Rust": (None, (142, 88, 58)),
    "P_DB_Gold": ((249, 212, 108), (226, 178, 78)),
    # emissivos: laranja quente, nunca branco
    "Forge_Emissive": (None, (250, 150, 70)),
    "Forge_Glow_Soft": (None, (255, 110, 30)),
    "Lantern_Glow": (None, (255, 146, 56)),
    "Window_Warm": (None, (214, 140, 74)),
    "Metal_Heated": (None, (190, 86, 40)),
    "Crystal_Blue": (None, (30, 140, 230)),
    "Crystal_Blue_Core": (None, (70, 200, 255)),
    "Crystal_Purple": (None, (120, 72, 205)),
    "Crystal_Purple_Core": (None, (175, 120, 255)),
    # portais: espiral e brilhos na cor do BRACO
    "P_Naruto_Swirl": (None, (255, 115, 20)),
    "P_DB_Swirl": (None, (255, 195, 30)),
    "P_Shadow_Swirl": (None, (150, 60, 255)),
    "P_DS_Swirl": (None, (185, 12, 22)),
    "P_OP_Swirl": (None, (25, 105, 255)),
    "P_OPM_Swirl": (None, (0, 225, 255)),
    "P_Naruto_Glow": (None, (255, 115, 20)),
    "P_DB_Glow": (None, (255, 195, 30)),
    "P_Gold_Glow": (None, (255, 195, 30)),
    "P_Shadow_Glow": (None, (150, 60, 255)),
    "P_DS_Glow": (None, (185, 12, 22)),
    "P_Red_Glow": (None, (185, 12, 22)),
    "P_OP_Glow": (None, (25, 105, 255)),
    "P_OPM_Glow": (None, (0, 225, 255)),
    "P_OPM_Neon": (None, (0, 225, 255)),
    "P_Shadow_Stone": (None, (40, 34, 52)),
    "P_Shadow_Trim": (None, (58, 48, 72)),
    "P_OPM_Concrete": (None, (124, 126, 130)),
    "P_OPM_DarkGlass": (None, (22, 34, 62)),
    "Water": (None, (40, 128, 160)),
    "Water_Deep": (None, (24, 96, 128)),
    "Water_Fall": (None, (170, 212, 236)),
    "Foam": (None, (236, 244, 250)),
}


def srgb(c):
    return fm_lib.to_srgb(c)


def lin(c):
    """sRGB 0-255 -> linear"""
    return fm_lib.S(*c)


def family(name):
    return fm_lib.family_of(name)


def rbx_rule(name):
    """(Material, transparencia, CastShadow) pelo maior prefixo conhecido; senao por palavra-chave"""
    name = fm_lib.alias(name)
    fam = family(name)
    best = None
    for key in (name, fam):
        for p, m, t, s in RBX_RULES:
            if key.startswith(p) and (best is None or len(p) > len(best[0])):
                best = (p, m, t, s)
    if best:
        return best[1], best[2], best[3]
    if name in fm_lib.SWIRLS or "swirl" in name.lower():
        return "Neon", 0.0, False
    n = name.lower()
    for kws, res in RBX_KEYWORDS:
        if any(k in n for k in kws):
            if res[0] == "Glass" and not name.startswith("P_OPM_"):
                return "SmoothPlastic", 0.0, True     # Glass so em P_OPM_*
            return res
    return "SmoothPlastic", 0.0, True


def rbx_color(name, mat=None):
    """cor do Roblox: cor da variante (MATS) x correcao testada da familia registrada (razao por canal)"""
    name = fm_lib.alias(name)
    if name in fm_lib.MATS:
        c = srgb(fm_lib.MATS[name][0])
    elif mat is not None:
        c = srgb(tuple(mat.diffuse_color)[:3])
    else:
        c = [163, 162, 165]
    cal = RBX_CAL.get(name)
    fam = name
    if cal is None and name in fm_lib.VARIANT_OF:
        fam = fm_lib.VARIANT_OF[name]
        cal = RBX_CAL.get(fam)
    if not cal:
        return list(c)
    old, new = cal
    if old is None:
        if name in RBX_CAL:
            return list(new)
        old = srgb(fm_lib.MATS[fam][0]) if fam in fm_lib.MATS else c
    return [max(0, min(255, int(round(n * (x / max(o, 1)))))) for x, o, n in zip(c, old, new)]


def rbx_material(name):
    """compatibilidade (export_vfx): (Material estilizado, Material rico, transparencia) - o modo hibrido usa o
    mesmo Enum nos dois (o montar troca para SmoothPlastic com LISO=true)."""
    m, t, s = rbx_rule(name)
    return m, m, t


def base_color(mat):
    """compatibilidade (export_vfx): cor LINEAR cujo sRGB e a cor calibrada do Roblox"""
    name = mat.name if hasattr(mat, "name") else str(mat)
    return lin(rbx_color(name, mat if hasattr(mat, "diffuse_color") else None))
