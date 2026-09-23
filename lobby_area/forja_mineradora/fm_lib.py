# fm_lib - nucleo do Lobby Vila-Forja (Anime Mining Simulator)
# 1 BU = 1 stud, Z para cima. Roblox = (x, z, -y) (mesmo mapeamento do export_roblox.py).
#
# POLITICA DE DETALHE (MB) - AVISO AOS DONOS DOS MODULOS
#   Medicao do export: ~29% dos tris (>= 202k) eram faixas de chanfro com menos de 0,2 stud e 52k eram fundos
#   escondidos (chanfro = 40% da FORGE, 36% de BUILDINGS, 41% de PROPS, 23% de TERRAIN). Por isso:
#     MB(name, coll, rng=None, detail="hero" | "near" | "far", floor=None)
#     "hero" (padrao) = como sempre: chanfra todas as arestas vivas pedidas por bevel=.
#     "near"          = chanfra SO as arestas do TOPO de cada primitiva (as duas pontas em z >= topo - 0,01);
#                       o resto sai vivo. Use para o que o jogador ve de perto mas nao e peca-heroi.
#     "far"           = bevel = 0 sempre e NAO cria a face de baixo de uma primitiva fechada que esta apoiada
#                       (z0 <= piso + 0,05). piso = floor: numero, funcao (x, y) -> z, ou None = niveis da planta
#                       (spawn 0, vale 4, piso da forja 5, ledge 14, terraco 30, ou enterrada abaixo de 0).
#     MB.gable_roof(..., shingle_bevel=None): chanfro das telhas; None = 0,12 em "hero" e 0 em "near"/"far".
#   Materiais: os donos so ESCOLHEM o nome; cor/brilho ficam aqui (MATS) e a traducao para o Roblox fica em
#   fm_mat_rbx.py (RBX_RULES / RBX_CAL). Novos desta rodada: Window_Warm (janela quente, NAO vira Neon; use em
#   window_glow), Forge_Glow_Soft, Stone_Heated, Grass_Dry, Water_Deep, Cliff_Rock_Top, P_OPM_DarkGlass,
#   P_<Naruto|DB|Shadow|DS|OP|OPM>_Glow (cor do braco da espiral). Lantern_Glow agora e ambar (emissao 1,2; no
#   Roblox Neon 255,146,56); Neon em janela so na forja e na loja. Espirais: textura propria por portal (v4).
#   Export: variantes pouco usadas voltam para a base, materiais < 60 studs2 por objeto vao para o vizinho
#   dominante (export_roblox.FOLD_TO) e o export FALHA se um dono passar do orcamento (FM_BUDGET=warn so avisa).
#   Apelidos (MAT_ALIAS): Flower_Yellow -> Flower_Pink, Flower_Blue -> Flower_White, Leaf_Pine_Light_B -> Leaf_Pine_Light.
#   FM_MAT_PREVIEW=roblox mostra a cor que o Roblox recebe (rbx_color, sem ruido nem textura); para aplicar num
#   .blend pronto: blender -b x.blend --python fm_mat_preview.py --python render.py -- <pasta> CAM_...
import bpy, bmesh, math, random, os, zlib
import numpy as np
from mathutils import Vector, Matrix, Euler, noise

D = math.radians
COLS = ["00_REFERENCE", "01_BLOCKOUT", "02_TERRAIN", "03_FORGE", "04_MINE",
        "05_WATER_SYSTEM", "06_PORTALS", "07_BUILDINGS", "08_PROPS", "09_VEGETATION",
        "10_RAILS", "11_LIGHTING", "12_VFX_HELPERS", "13_COLLISION", "14_EXPORT",
        "15_GAMEPLAY_MARKERS", "_SCALE_REFERENCE"]


# ------------------------------------------------------------------ cena
def reset_scene():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights,
                 bpy.data.curves, bpy.data.node_groups, bpy.data.images):
        for d in list(coll):
            try:
                coll.remove(d)
            except Exception:
                pass
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    for n in COLS:
        c = bpy.data.collections.new(n)
        bpy.context.scene.collection.children.link(c)


def coll(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c


def sub_coll(parent, name):
    p = coll(parent)
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        p.children.link(c)
    return c


# ------------------------------------------------------------------ materiais
# nome: (cor_linear, rough, metal, emissao, cor_emissao, variacao)
# Cores novas escritas em sRGB 0-255 via S() (mesmo formato linear de sempre). "variacao" so vale no
# shader legado (FM_MAT_PREVIEW=legado); a variacao que chega ao Roblox vem das VARIANTES (abaixo).
def S(r, g, b):
    """sRGB 0-255 -> linear (formato de MATS)"""
    def f(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (round(f(r), 4), round(f(g), 4), round(f(b), 4))


def to_srgb(c):
    out = []
    for x in c[:3]:
        x = max(0.0, min(1.0, x))
        out.append(int(round(255 * (x * 12.92 if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055))))
    return out


MATS = {
    # pedra: cinza QUENTE (concept), claro x escuro com contraste; rejunte escuro separa as pecas
    "Stone_Light":   (S(150, 141, 129), 0.85, 0.0, 0, None, 0.16),
    "Stone_Dark":    (S(100, 92, 86), 0.85, 0.0, 0, None, 0.16),
    # calcamento ~15% mais escuro e mais quente (a praca era o maior plano claro da tela)
    "Stone_Paving":  (S(136, 121, 104), 0.85, 0.0, 0, None, 0.20),
    "Stone_Grout":   (S(88, 82, 76), 0.95, 0.0, 0, None, 0.05),
    # pedra aquecida da forja: brasa escura (so brilho fraco no Blender; no Roblox e pedra, nao Neon)
    "Stone_Heated":  ((0.16, 0.045, 0.02), 0.8, 0.0, 1.2, (1.0, 0.26, 0.05), 0.08),
    "Cliff_Rock":    ((0.26, 0.26, 0.29), 0.9, 0.0, 0, None, 0.14),
    "Cliff_Rock_Dark": ((0.15, 0.15, 0.18), 0.9, 0.0, 0, None, 0.12),
    # perspectiva aerea: proximo < medio < longe em valor, cada plano mais frio; topo iluminado quente
    "Cliff_Rock_Mid":      ((0.36, 0.38, 0.48), 0.92, 0.0, 0, None, 0.10),
    "Cliff_Rock_Mid_Dark": ((0.24, 0.25, 0.33), 0.92, 0.0, 0, None, 0.08),
    "Cliff_Rock_Far":      ((0.55, 0.62, 0.78), 0.95, 0.0, 0, None, 0.05),
    "Cliff_Rock_Far_Dark": ((0.40, 0.45, 0.60), 0.95, 0.0, 0, None, 0.05),
    "Cliff_Rock_Top":      (S(150, 140, 135), 0.9, 0.0, 0, None, 0.10),
    # madeira: castanho mais rico (menos laranja-palido), escura com contraste
    "Wood_Light":    (S(160, 114, 74), 0.8, 0.0, 0, None, 0.18),
    "Wood_Dark":     (S(100, 66, 43), 0.8, 0.0, 0, None, 0.18),
    "Wood_Plank":    (S(136, 95, 61), 0.8, 0.0, 0, None, 0.22),
    # metais: ferro comum, ferro escuro, QUEIMADO (forja), OXIDADO (agua/mina/trilho), quente (emissivo)
    "Metal_Iron":    ((0.20, 0.20, 0.22), 0.45, 0.8, 0, None, 0.08),
    "Metal_Dark":    ((0.09, 0.09, 0.10), 0.5, 0.7, 0, None, 0.06),
    "Metal_Burnt":   (S(66, 56, 58), 0.6, 0.7, 0, None, 0.06),
    "Metal_Rust":    (S(130, 76, 48), 0.85, 0.25, 0, None, 0.10),
    "Metal_Brass":   ((0.60, 0.40, 0.14), 0.35, 0.9, 0, None, 0.06),
    "Metal_Heated":  ((0.40, 0.08, 0.02), 0.5, 0.3, 6, (1.0, 0.35, 0.06), 0.0),
    "Forge_Emissive": ((1.0, 0.45, 0.1), 0.5, 0.0, 14, (1.0, 0.42, 0.08), 0.0),
    # emissivos QUENTES (nao retangulos brancos): com emissao 9 o AgX queimava a lanterna para branco. Teste na
    # altura do jogador (AgX Punchy, dia e mina): (1, 0.52, 0.16) x 3 ainda le creme; (1, 0.36, 0.05) x 1.2 le ambar
    "Lantern_Glow":  ((1.0, 0.36, 0.05), 0.5, 0.0, 1.2, (1.0, 0.36, 0.05), 0.0),
    # janela iluminada comum: calor baixo; no Roblox vira SmoothPlastic (Neon em janela so na forja e na loja)
    "Window_Warm":   ((0.95, 0.42, 0.10), 0.5, 0.0, 0.8, (0.95, 0.42, 0.10), 0.0),
    "Forge_Glow_Soft": ((0.80, 0.24, 0.03), 0.5, 0.0, 1.5, (1.0, 0.30, 0.04), 0.0),
    # azul saturado sem vermelho: linear (0, 0.26, 1) = sRGB (0, 139, 255) ~ (0, 0.55, 1.0) normalizado
    "Crystal_Blue":  ((0.0, 0.26, 1.0), 0.15, 0.0, 0.9, (0.0, 0.26, 1.0), 0.0),
    "Crystal_Purple": ((0.4, 0.08, 1.0), 0.15, 0.0, 1.1, (0.42, 0.10, 1.0), 0.0),
    # nucleos dos cristais (so no export: as pontas pequenas do topo viram Neon, a casca fica SmoothPlastic)
    "Crystal_Blue_Core": ((0.25, 0.80, 1.0), 0.15, 0.0, 3.0, (0.25, 0.80, 1.0), 0.0),
    "Crystal_Purple_Core": ((0.62, 0.35, 1.0), 0.15, 0.0, 3.0, (0.62, 0.35, 1.0), 0.0),
    "Water":         ((0.02, 0.28, 0.42), 0.08, 0.0, 0.25, (0.03, 0.30, 0.45), 0.10),
    "Water_Deep":    ((0.01, 0.14, 0.24), 0.06, 0.0, 0.12, (0.02, 0.20, 0.32), 0.06),   # faixa central do rio
    "Water_Fall":    ((0.70, 0.88, 1.0), 0.2, 0.0, 0.55, (0.55, 0.8, 1.0), 0.0),
    "Foam":          ((0.90, 0.96, 1.0), 0.6, 0.0, 0.6, (0.85, 0.95, 1.0), 0.0),
    "Grass":         (S(96, 152, 58), 0.9, 0.0, 0, None, 0.20),   # menos limao, mais perto do concept
    "Grass_Dark":    ((0.05, 0.15, 0.05), 0.9, 0.0, 0, None, 0.16),
    "Grass_Dry":     (S(150, 138, 80), 0.9, 0.0, 0, None, 0.18),
    "Dirt":          ((0.24, 0.15, 0.08), 0.95, 0.0, 0, None, 0.16),
    "Roof":          (S(110, 108, 114), 0.75, 0.0, 0, None, 0.14),
    "Roof_Red":      (S(110, 58, 44), 0.7, 0.0, 0, None, 0.12),     # telha envelhecida marrom-avermelhada
    "Plaster":       ((0.58, 0.48, 0.36), 0.9, 0.0, 0, None, 0.08),
    "Cloth_Red":     ((0.55, 0.08, 0.07), 0.9, 0.0, 0, None, 0.06),
    "Cloth_Navy":    ((0.05, 0.07, 0.14), 0.9, 0.0, 0, None, 0.05),
    "Cloth_Canvas":  ((0.75, 0.66, 0.50), 0.9, 0.0, 0, None, 0.06),
    "Emblem_Cream":  ((0.85, 0.80, 0.68), 0.6, 0.0, 0, None, 0.0),
    "Rope":          ((0.62, 0.50, 0.32), 0.9, 0.0, 0, None, 0.08),
    "Leather":       ((0.30, 0.16, 0.08), 0.7, 0.0, 0, None, 0.08),
    "Smoke":         ((0.20, 0.19, 0.19), 1.0, 0.0, 0, None, 0.12),
    "Cloud":         ((0.95, 0.97, 1.0), 0.9, 0.0, 0.35, (0.9, 0.95, 1.0), 0.0),
    "Leaf_Pine":     ((0.03, 0.20, 0.08), 0.85, 0.0, 0, None, 0.20),
    "Leaf_Pine_Light": ((0.12, 0.36, 0.10), 0.85, 0.0, 0, None, 0.20),
    "Flower_Pink":   (S(232, 128, 168), 0.6, 0.0, 0, None, 0.0),
    "Flower_White":  (S(238, 234, 222), 0.6, 0.0, 0, None, 0.0),
    "Leaf_Sakura":   ((0.95, 0.55, 0.72), 0.8, 0.0, 0.2, (1.0, 0.6, 0.8), 0.12),
    "Leaf_Palm":     ((0.20, 0.50, 0.15), 0.8, 0.0, 0, None, 0.15),
    "Bark":          ((0.28, 0.18, 0.10), 0.9, 0.0, 0, None, 0.12),
    "Skin":          ((0.95, 0.75, 0.55), 0.7, 0.0, 0, None, 0.0),
    "Hair_Red":      ((0.75, 0.12, 0.05), 0.7, 0.0, 0, None, 0.0),
    "Dummy_Grey":    ((0.60, 0.62, 0.66), 0.7, 0.0, 0, None, 0.0),
    # portais (espirais: a cor aqui e a do BRACO; o desenho vem da textura de fm_mat_textures.SWIRL_SPEC)
    "P_Naruto_Red":  ((0.72, 0.10, 0.06), 0.7, 0.0, 0, None, 0.10),
    "P_Naruto_Swirl": (S(255, 115, 20), 0.3, 0.0, 1.5, S(255, 115, 20), 0.0),
    "P_DB_Gold":     ((0.95, 0.66, 0.15), 0.3, 0.85, 0, None, 0.05),
    "P_DB_White":    ((0.90, 0.90, 0.86), 0.5, 0.0, 0, None, 0.05),
    "P_DB_Orange":   ((1.0, 0.45, 0.05), 0.4, 0.0, 1.5, (1.0, 0.5, 0.1), 0.05),
    "P_DB_Swirl":    (S(255, 195, 30), 0.3, 0.0, 1.5, S(255, 195, 30), 0.0),
    "P_Shadow_Stone": ((0.02, 0.018, 0.035), 0.7, 0.0, 0, None, 0.10),
    "P_Shadow_Trim": ((0.04, 0.03, 0.06), 0.7, 0.0, 0, None, 0.08),
    "P_Shadow_Swirl": (S(150, 60, 255), 0.3, 0.0, 2.2, S(150, 60, 255), 0.0),
    "P_DS_Black":    ((0.07, 0.05, 0.05), 0.7, 0.0, 0, None, 0.08),
    "P_DS_Red":      ((0.62, 0.06, 0.05), 0.6, 0.0, 0.5, (0.8, 0.05, 0.02), 0.08),
    "P_DS_Swirl":    (S(185, 12, 22), 0.3, 0.0, 1.8, S(185, 12, 22), 0.0),
    "P_OP_Blue":     ((0.08, 0.20, 0.50), 0.6, 0.0, 0, None, 0.10),
    "P_OP_Swirl":    (S(25, 105, 255), 0.3, 0.0, 1.7, S(25, 105, 255), 0.0),
    "P_OPM_Concrete": ((0.20, 0.205, 0.215), 0.8, 0.0, 0, None, 0.10),
    "P_OPM_Glass":   ((0.10, 0.30, 0.60), 0.1, 0.2, 1.2, (0.2, 0.55, 1.0), 0.05),
    "P_OPM_DarkGlass": ((0.012, 0.025, 0.07), 0.12, 0.4, 0.2, (0.03, 0.14, 0.42), 0.04),   # marinho escuro
    "P_OPM_Neon":    (S(0, 225, 255), 0.3, 0.0, 3.5, S(0, 225, 255), 0.0),
    "P_OPM_Swirl":   (S(0, 225, 255), 0.3, 0.0, 1.5, S(0, 225, 255), 0.0),
    # brilhos dos portais na COR DO BRACO da espiral (P_<chave>_Glow); Gold/Red/Shadow sao os nomes antigos
    "P_Naruto_Glow": (S(255, 115, 20), 0.3, 0.0, 4.0, S(255, 115, 20), 0.0),
    "P_DB_Glow":     (S(255, 195, 30), 0.3, 0.0, 4.0, S(255, 195, 30), 0.0),
    "P_Shadow_Glow": (S(150, 60, 255), 0.3, 0.0, 4.0, S(150, 60, 255), 0.0),
    "P_DS_Glow":     (S(185, 12, 22), 0.3, 0.0, 5.0, S(185, 12, 22), 0.0),
    "P_OP_Glow":     (S(25, 105, 255), 0.3, 0.0, 4.0, S(25, 105, 255), 0.0),
    "P_OPM_Glow":    (S(0, 225, 255), 0.3, 0.0, 4.0, S(0, 225, 255), 0.0),
    "P_Gold_Glow":   (S(255, 195, 30), 0.3, 0.0, 4.0, S(255, 195, 30), 0.0),
    "P_Red_Glow":    (S(185, 12, 22), 0.3, 0.0, 5.0, S(185, 12, 22), 0.0),
    # blockout / colisao / marcadores
    "BLK_Grey":      ((0.5, 0.5, 0.5), 0.9, 0.0, 0, None, 0.0),
    "COL_Debug":     ((1.0, 0.1, 0.9), 0.9, 0.0, 0, None, 0.0),
}

SWIRL_R = 7.5
SWIRLS = {"P_Naruto_Swirl", "P_DB_Swirl", "P_Shadow_Swirl", "P_DS_Swirl", "P_OP_Swirl", "P_OPM_Swirl"}
# apelidos: o material pedido vira outro (menos materiais no Roblox; mesmo resultado no Blender)
MAT_ALIAS = {"Flower_Yellow": "Flower_Pink", "Flower_Blue": "Flower_White", "Leaf_Pine_Light_B": "Leaf_Pine_Light"}


def alias(name):
    return MAT_ALIAS.get(name, name)


# ------------------------------------------------------------------ variantes tonais (chegam ao Roblox)
# Cada primitiva (bloco, tabua, telha, coluna de rocha...) sorteia uma variante da familia com semente fixa
# por OBJETO (crc32 do nome) -> build deterministico. No export cada variante vira uma MeshPart com cor
# solida propria, entao o Roblox recebe pedras claras/escuras, tabuas com tom diferente etc.
# Orcamento de malhas: o numero de variantes usadas por (objeto, familia) cresce com o numero de
# primitivas daquela familia no objeto (VARIANT_T2 / VARIANT_T3) e e limitado pelo "cap" da familia.
# Objetos pequenos recebem UMA variante sorteada por objeto (variacao entre objetos sem custo de malha).
# Outros modulos podem registrar familias novas com add_variants() (antes de make_materials).
FAMILIES = {}        # base -> (cap, [(nome, peso), ...]); o 1o item e a propria base
VARIANT_OF = {}      # nome da variante -> base da familia
VARIANT_T2 = 24      # >= 24 primitivas da familia no objeto -> ate 2 variantes (orcamento de MeshParts)
VARIANT_T3 = 120     # >= 120 -> ate 3 variantes


def add_variants(base, variants, cap=3):
    """variants = [(nome, peso, cor_srgb_ou_None, rough_ou_None), ...]; o 1o costuma ser a propria base.
    Registra as variantes em MATS (setdefault) herdando rough/metal/emissao da base."""
    b = MATS[base]
    lst = []
    for v in variants:
        name, w = v[0], v[1]
        col = v[2] if len(v) > 2 else None
        rough = v[3] if len(v) > 3 and v[3] is not None else b[1]
        if name != base:
            MATS.setdefault(name, (S(*col) if col else b[0], rough, b[2], b[3], b[4], b[5]))
        VARIANT_OF[name] = base
        lst.append((name, float(w)))
    FAMILIES[base] = (cap, lst)


add_variants("Stone_Light", [("Stone_Light", 5), ("Stone_Light_B", 3, (172, 161, 145)),
                             ("Stone_Light_C", 2, (122, 115, 108))])
add_variants("Stone_Dark", [("Stone_Dark", 5), ("Stone_Dark_B", 3, (80, 70, 64)),
                            ("Stone_Dark_C", 2, (122, 113, 104))])
add_variants("Stone_Paving", [("Stone_Paving", 5), ("Stone_Paving_B", 3, (152, 136, 116)),
                              ("Stone_Paving_C", 2, (114, 101, 88))], cap=2)
add_variants("Wood_Dark", [("Wood_Dark", 5), ("Wood_Dark_B", 3, (118, 76, 45)), ("Wood_Dark_C", 2, (84, 62, 48))])
add_variants("Wood_Plank", [("Wood_Plank", 5), ("Wood_Plank_B", 3, (154, 108, 66)),
                            ("Wood_Plank_C", 2, (116, 89, 64))], cap=2)
add_variants("Wood_Light", [("Wood_Light", 5), ("Wood_Light_B", 3, (176, 128, 82)),
                            ("Wood_Light_C", 2, (142, 106, 78))], cap=2)
add_variants("Cliff_Rock", [("Cliff_Rock", 5), ("Cliff_Rock_B", 3, (160, 158, 164)),
                            ("Cliff_Rock_C", 2, (122, 121, 131))], cap=2)
add_variants("Cliff_Rock_Dark", [("Cliff_Rock_Dark", 5), ("Cliff_Rock_Dark_B", 3, (92, 92, 103)),
                                 ("Cliff_Rock_Dark_C", 2, (122, 120, 126))], cap=2)
add_variants("Roof", [("Roof", 5), ("Roof_B", 3, (95, 95, 103)), ("Roof_C", 2, (122, 114, 110))], cap=2)
# telha envelhecida: B = tom mais quente, C = musgo
add_variants("Roof_Red", [("Roof_Red", 5), ("Roof_Red_B", 3, (126, 68, 50)), ("Roof_Red_C", 2, (88, 86, 54))],
             cap=2)
add_variants("Plaster", [("Plaster", 5), ("Plaster_B", 3, (211, 197, 177)), ("Plaster_C", 2, (189, 171, 147))],
             cap=2)
add_variants("Grass", [("Grass", 6), ("Grass_B", 4, (84, 122, 48))], cap=2)     # B = oliva
add_variants("Dirt", [("Dirt", 6), ("Dirt_B", 4, (118, 95, 72))], cap=2)
add_variants("Leaf_Pine", [("Leaf_Pine", 6), ("Leaf_Pine_B", 4, (46, 104, 64))], cap=2)
# Leaf_Pine_Light sem a variante menta (Leaf_Pine_Light_B virou apelido de Leaf_Pine_Light)
add_variants("Bark", [("Bark", 6), ("Bark_B", 4, (122, 97, 73))], cap=2)

# metal por CONTEXTO do objeto: forja = ferro queimado; agua/mina/trilho = oxidado; resto = ferro comum
CONTEXT_FAMILIES = {
    "forge": {"Metal_Dark": (2, [("Metal_Dark", 5.0), ("Metal_Burnt", 5.0)]),
              "Metal_Iron": (2, [("Metal_Iron", 6.0), ("Metal_Burnt", 4.0)])},
    "wet": {"Metal_Iron": (2, [("Metal_Iron", 6.0), ("Metal_Rust", 4.0)]),
            "Metal_Dark": (2, [("Metal_Dark", 7.0), ("Metal_Rust", 3.0)])},
    "dry": {"Metal_Iron": (2, [("Metal_Iron", 8.0), ("Metal_Rust", 2.0)])},
}
VARIANT_OF.setdefault("Metal_Burnt", "Metal_Burnt")
VARIANT_OF.setdefault("Metal_Rust", "Metal_Rust")
# o fm_veg espalha arvores pelo NOME do material do terreno ("Grass"/"Grass_Dark") -> nao variar la
NO_VARIANT_PREFIX = {"Grass": ("TER_",), "Grass_Dark": ("TER_",)}


def object_context(name, coll_name):
    if coll_name == "03_FORGE" or name.startswith("FORGE_"):
        return "forge"
    if coll_name in ("04_MINE", "05_WATER_SYSTEM", "10_RAILS") or name.startswith(("MINE_", "WATER_", "RAIL_")):
        return "wet"
    return "dry"


def family_of(name):
    """nome de material (inclusive variante ou material de outro modulo) -> base da familia"""
    if name in VARIANT_OF:
        return VARIANT_OF[name]
    return name


# ------------------------------------------------------------------ texturas de detalhe (overlay)
# prefixo do material -> chave de textura (fm_mat_textures). Tolerante a materiais novos pelo prefixo.
TEX_RULES = (("Stone_", "stone"), ("P_OPM_Concrete", "stone"), ("Wood_", "wood"), ("Bark", "wood"),
             ("Roof", "roof"), ("Cliff_Rock", "rock"), ("Grass", "grass"), ("Plaster", "plaster"),
             ("Dirt", "dirt"))
# FM_MAT_PREVIEW: "rico" (padrao: variante + textura de detalhe = o que o Roblox recebe com RICO=true),
#                 "liso" (so a cor solida da variante = MeshPart SmoothPlastic), "legado" (shader antigo tint+ruido),
#                 "roblox" (a COR QUE O ROBLOX RECEBE: rbx_color calibrada, sem ruido nem textura; Neon brilha)
PREVIEW = os.environ.get("FM_MAT_PREVIEW", "rico").lower()


def tex_key(name):
    for p, k in TEX_RULES:
        if name.startswith(p):
            return k
    return None


def tex_tile(key):
    import fm_mat_textures
    return fm_mat_textures.TEXTURES[key][1]


_TEX_IMG = {}


def _tex_image(key):
    if key in _TEX_IMG and _TEX_IMG[key].name in bpy.data.images:
        return _TEX_IMG[key]
    import fm_mat_textures
    paths = fm_mat_textures.ensure()
    im = bpy.data.images.load(paths[key], check_existing=True)
    im.colorspace_settings.name = "sRGB"
    im.alpha_mode = "STRAIGHT"
    try:
        im.pack()
    except Exception:
        pass
    _TEX_IMG[key] = im
    return im


def _swirl_nodes(nt, bs, name, emit):
    """espiral do portal = a PNG do portal (fm_mat_textures.SWIRL_SPEC) em coordenadas GENERATED do disco
    (bbox do objeto: X = u, Z = v). E exatamente a imagem que vai para o Roblox (FBX e SurfaceGui)."""
    N = nt.nodes
    tc = N.new("ShaderNodeTexCoord")
    sp = N.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sp.inputs[0])
    cb = N.new("ShaderNodeCombineXYZ")
    nt.links.new(sp.outputs["X"], cb.inputs["X"])
    nt.links.new(sp.outputs["Z"], cb.inputs["Y"])
    im = N.new("ShaderNodeTexImage")
    im.image = _tex_image(name)
    im.interpolation = "Linear"
    im.extension = "EXTEND"
    nt.links.new(cb.outputs[0], im.inputs["Vector"])
    nt.links.new(im.outputs["Color"], bs.inputs["Base Color"])
    nt.links.new(im.outputs["Color"], bs.inputs["Emission Color"])
    bs.inputs["Emission Strength"].default_value = emit
    bs.inputs["Roughness"].default_value = 0.6


def _build_material(name, preview=None):
    preview = (preview or PREVIEW).lower()
    col, rough, metal, emit, ecol, var = MATS[name]
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bs = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bs.inputs["Roughness"].default_value = rough
    bs.inputs["Metallic"].default_value = metal
    nt.links.new(bs.outputs[0], out.inputs[0])
    base = (*col, 1.0)
    m.diffuse_color = base
    if name in SWIRLS:
        _swirl_nodes(nt, bs, name, emit)
        return m
    if preview == "roblox":
        # cor solida calibrada do Roblox (fm_mat_rbx.rbx_color); Neon = emissao da propria cor
        import fm_mat_rbx
        c = S(*fm_mat_rbx.rbx_color(name))
        bs.inputs["Base Color"].default_value = (*c, 1.0)
        m.diffuse_color = (*c, 1.0)
        rm = fm_mat_rbx.rbx_rule(name)[0]
        if rm == "Neon":
            bs.inputs["Emission Color"].default_value = (*c, 1.0)
            bs.inputs["Emission Strength"].default_value = 1.6
        elif rm == "Metal":
            bs.inputs["Metallic"].default_value = max(metal, 0.6)
        return m
    tk = tex_key(name) if preview == "rico" else None
    if preview == "legado" and var > 0:
        # tint por face (atributo 'tint') + ruido suave -> variacao pintada (NAO chega ao Roblox)
        at = nt.nodes.new("ShaderNodeAttribute")
        at.attribute_type = "GEOMETRY"
        at.attribute_name = "tint"
        ma = nt.nodes.new("ShaderNodeMath"); ma.operation = "MULTIPLY_ADD"
        ma.inputs[1].default_value = var
        ma.inputs[2].default_value = 1.0
        nt.links.new(at.outputs["Fac"], ma.inputs[0])
        tc = nt.nodes.new("ShaderNodeTexCoord")
        nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = 0.35
        nz.inputs["Detail"].default_value = 2.0
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.inputs["To Min"].default_value = 1.0 - var * 0.8
        mr.inputs["To Max"].default_value = 1.0 + var * 0.6
        nt.links.new(nz.outputs["Fac"], mr.inputs["Value"])
        mm = nt.nodes.new("ShaderNodeMath"); mm.operation = "MULTIPLY"
        nt.links.new(ma.outputs[0], mm.inputs[0])
        nt.links.new(mr.outputs[0], mm.inputs[1])
        hsv = nt.nodes.new("ShaderNodeHueSaturation")
        hsv.inputs["Color"].default_value = base
        nt.links.new(mm.outputs[0], hsv.inputs["Value"])
        nt.links.new(hsv.outputs[0], bs.inputs["Base Color"])
    elif tk:
        # cor solida da variante + textura de detalhe em overlay (UV "UVMap" gerada pelo MB, em studs/TILE)
        uvn = nt.nodes.new("ShaderNodeUVMap")
        uvn.uv_map = "UVMap"
        im = nt.nodes.new("ShaderNodeTexImage")
        im.image = _tex_image(tk)
        im.interpolation = "Linear"
        im.extension = "REPEAT"
        nt.links.new(uvn.outputs["UV"], im.inputs["Vector"])
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.blend_type = "MIX"
        mix.inputs["A"].default_value = base
        nt.links.new(im.outputs["Alpha"], mix.inputs["Factor"])
        nt.links.new(im.outputs["Color"], mix.inputs["B"])
        nt.links.new(mix.outputs["Result"], bs.inputs["Base Color"])
    else:
        bs.inputs["Base Color"].default_value = base
    if emit > 0:
        bs.inputs["Emission Color"].default_value = (*(ecol or col), 1)
        bs.inputs["Emission Strength"].default_value = emit
    if name in ("Water", "Water_Deep", "Water_Fall", "Foam"):
        bs.inputs["Coat Weight"].default_value = 0.3 if name in ("Water", "Water_Deep") else 0.0
    if name == "Smoke":
        bs.inputs["Alpha"].default_value = 0.9
    return m


def make_materials():
    import fm_mat_textures
    fm_mat_textures.ensure()      # detalhe (rico) + espirais (sempre: o disco do portal e a propria textura)
    for name in MATS:
        if name in MAT_ALIAS:
            continue
        _build_material(name)
    return


def apply_preview(mode=None):
    """refaz, num .blend ja montado, todos os materiais de MATS no modo pedido (rico/liso/legado/roblox)"""
    global PREVIEW
    PREVIEW = (mode or os.environ.get("FM_MAT_PREVIEW", "rico")).lower()
    n = 0
    for m in list(bpy.data.materials):
        if m.name in MATS:
            _build_material(m.name, PREVIEW)
            n += 1
        elif PREVIEW == "roblox" and m.users and not m.name.startswith(("RBX_", "Dots Stroke")):
            # material fora de MATS (sem registro): cor do Roblox a partir da cor de viewport
            import fm_mat_rbx
            c = S(*fm_mat_rbx.rbx_color(m.name, m))
            m.use_nodes = True
            nt = m.node_tree
            nt.nodes.clear()
            out = nt.nodes.new("ShaderNodeOutputMaterial")
            bs = nt.nodes.new("ShaderNodeBsdfPrincipled")
            bs.inputs["Base Color"].default_value = (*c, 1.0)
            if fm_mat_rbx.rbx_rule(m.name)[0] == "Neon":
                bs.inputs["Emission Color"].default_value = (*c, 1.0)
                bs.inputs["Emission Strength"].default_value = 1.6
            nt.links.new(bs.outputs[0], out.inputs[0])
            n += 1
    return n


def mat(name):
    name = alias(name)
    m = bpy.data.materials.get(name)
    if m is None and name in MATS:
        m = _build_material(name)   # material registrado depois do make_materials
    return m if m is not None else bpy.data.materials[name]


# ------------------------------------------------------------------ geometria util
def v3(x, y, z=0):
    return Vector((x, y, z))


def bezier(p0, p1, p2, p3, n):
    p0, p1, p2, p3 = map(Vector, (p0, p1, p2, p3))
    out = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        out.append(p0 * u ** 3 + p1 * 3 * u * u * t + p2 * 3 * u * t * t + p3 * t ** 3)
    return out


def arc(cx, cy, r, a0, a1, n, z=0.0):
    return [Vector((cx + r * math.cos(D(a0 + (a1 - a0) * i / n)),
                    cy + r * math.sin(D(a0 + (a1 - a0) * i / n)), z)) for i in range(n + 1)]


def resample(pts, step):
    pts = [Vector(p) for p in pts]
    out = [pts[0].copy()]
    acc = 0.0
    for a, b in zip(pts, pts[1:]):
        seg = (b - a).length
        d = step - acc
        while d <= seg:
            out.append(a + (b - a) * (d / seg))
            d += step
        acc = seg - (d - step)
    if (out[-1] - pts[-1]).length > step * 0.3:
        out.append(pts[-1].copy())
    return out


def path_len(pts):
    return sum((Vector(b) - Vector(a)).length for a, b in zip(pts, pts[1:]))


def point_in_poly(x, y, poly):
    ins = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i][0], poly[i][1]
        xj, yj = poly[j][0], poly[j][1]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi):
            ins = not ins
        j = i
    return ins


# ------------------------------------------------------------------ construtor de malha
DETAILS = ("hero", "near", "far")
_FLOOR_LEVELS = None


def floor_levels():
    """niveis de piso da planta (usados pelo detail='far' quando floor=None)"""
    global _FLOOR_LEVELS
    if _FLOOR_LEVELS is None:
        try:
            import fm_layout as _L
            _FLOOR_LEVELS = tuple(sorted({float(_L.SPAWN_Z), float(_L.FLOOR), float(_L.FL), float(_L.MID),
                                          float(_L.TERR)}))
        except Exception:
            _FLOOR_LEVELS = (0.0, 4.0, 5.0, 14.0, 30.0)
    return _FLOOR_LEVELS


class MB:
    """Acumula primitivas num unico bmesh com varios materiais; finish() cria o objeto.
    detail: "hero" (chanfro completo), "near" (chanfro so no topo), "far" (sem chanfro, sem fundo apoiado).
    floor: piso para o "far" (numero, funcao (x, y) -> z, ou None = niveis da planta)."""

    def __init__(self, name, collection, rng=None, detail="hero", floor=None):
        self.detail = detail if detail in DETAILS else "hero"
        self.floor = floor
        self.n_bottoms = 0      # fundos omitidos (detail="far")
        self.name = name
        self.coll = collection if not isinstance(collection, str) else coll(collection)
        self.bm = bmesh.new()
        self.tint = self.bm.faces.layers.float.new("tint")
        self.uvl = self.bm.loops.layers.uv.new("UVMap")
        self.mats = []          # nomes de material ou chaves de variante ("V", familia, slot)
        # semente padrao estavel entre execucoes (hash() do Python muda a cada processo -> build nao reprodutivel)
        self.rng = rng or random.Random(zlib.crc32(name.encode("utf-8")) & 0xffff)
        # sorteio de variantes: RNG proprio (nao consome self.rng -> geometria identica) e fixo por objeto
        self.vrng = random.Random(zlib.crc32(name.encode("utf-8")))
        self.vcount = {}
        self.ctx = object_context(name, getattr(self.coll, "name", ""))
        self._nprim = 0

    def _mi(self, m):
        if m not in self.mats:
            self.mats.append(m)
        return self.mats.index(m)

    def _family(self, m):
        ctx = CONTEXT_FAMILIES.get(self.ctx, {})
        if m in ctx:
            return ctx[m]
        fam = FAMILIES.get(m)
        if fam is None:
            return None
        for p in NO_VARIANT_PREFIX.get(m, ()):
            if self.name.startswith(p):
                return None
        return fam

    def _mi_for(self, m):
        """indice de material da primitiva: familias com variantes recebem um SLOT sorteado (resolvido no finish)"""
        fam = self._family(m)
        if fam is None or len(fam[1]) < 2:
            return self._mi(m)
        ws = [w for _, w in fam[1]]
        x = self.vrng.random() * sum(ws)
        slot = len(ws) - 1
        for i, w in enumerate(ws):
            x -= w
            if x <= 0:
                slot = i
                break
        self.vcount[m] = self.vcount.get(m, 0) + 1
        return self._mi(("V", m, slot))

    def _variant_names(self, m):
        """slot -> nome final, limitando o numero de variantes pelo volume de primitivas (orcamento de malhas)"""
        cap, vs = self._family(m)
        names = [n for n, _ in vs]
        ws = [w for _, w in vs]
        n = self.vcount.get(m, 0)
        k = 1 if n < VARIANT_T2 else (2 if n < VARIANT_T3 else 3)
        k = min(k, cap, len(vs))
        if k >= len(vs):
            return names
        r = random.Random(zlib.crc32(("%s|%s" % (self.name, m)).encode("utf-8")))
        pool = list(range(len(vs)))
        chosen = []
        while len(chosen) < k:
            x = r.random() * sum(ws[i] for i in pool)
            pick = pool[-1]
            for i in pool:
                x -= ws[i]
                if x <= 0:
                    pick = i
                    break
            chosen.append(pick)
            pool.remove(pick)
        main = max(chosen, key=lambda i: ws[i])
        return [names[i] if i in chosen else names[main] for i in range(len(vs))]

    def _uv(self, faces, m):
        """UV planar alinhada a primitiva (eixo maior = u, p.ex. veio da madeira ao longo da viga), em studs/TILE,
        com deslocamento proprio por primitiva. Vai no FBX e alimenta as texturas de detalhe (Blender e Roblox)."""
        tk = tex_key(m)
        if tk is None or not faces:
            return
        inv = 1.0 / tex_tile(tk)
        vs = {v for f in faces for v in f.verts}
        P = np.array([v.co[:] for v in vs])
        if len(P) >= 3:
            X = P - P.mean(0)
            w, V = np.linalg.eigh(X.T @ X)
            A = Vector(V[:, 2])
            B = Vector(V[:, 1])
        else:
            A, B = Vector((1, 0, 0)), Vector((0, 1, 0))
        k = self._nprim
        self._nprim += 1
        ou = (k * 0.6180339) % 1.0
        ov = (k * 0.4142135 + 0.37) % 1.0
        uvl = self.uvl
        for f in faces:
            nrm = f.normal
            u = A - nrm * A.dot(nrm)
            if u.length_squared < 0.09:
                u = B - nrm * B.dot(nrm)
                if u.length_squared < 1e-6:
                    u = nrm.orthogonal()
            u.normalize()
            v = nrm.cross(u)
            for lp in f.loops:
                co = lp.vert.co
                lp[uvl].uv = (co.dot(u) * inv + ou, co.dot(v) * inv + ov)

    def _resting(self, zmin, verts):
        """primitiva apoiada no piso? (z0 <= piso + 0,05)"""
        fl = self.floor
        if fl is None:
            lv = floor_levels()
            return zmin <= lv[0] + 0.05 or any(l - 1.0 <= zmin <= l + 0.05 for l in lv)
        if callable(fl):
            cx = sum(v.co.x for v in verts) / len(verts)
            cy = sum(v.co.y for v in verts) / len(verts)
            return zmin <= float(fl(cx, cy)) + 0.05
        return zmin <= float(fl) + 0.05

    def _drop_bottom(self, faces, verts):
        """detail='far': apaga a face de baixo (normal -Z no z minimo) de uma primitiva FECHADA e apoiada"""
        if not faces or not verts:
            return faces
        zmin = min(v.co.z for v in verts)
        if not self._resting(zmin, verts):
            return faces
        for f in faces:
            for e in f.edges:
                if len(e.link_faces) != 2:
                    return faces        # primitiva aberta (quad, fita...): nao mexe
        bottom = [f for f in faces if f.normal.z < -0.999 and all(abs(v.co.z - zmin) < 1e-3 for v in f.verts)]
        if not bottom:
            return faces
        bmesh.ops.delete(self.bm, geom=bottom, context="FACES_ONLY")
        self.n_bottoms += len(bottom)
        return {f for f in faces if f.is_valid}

    def _post(self, verts, m, tint, bevel, seg, angle=0.5):
        verts = [v for v in verts if v.is_valid]
        faces = {f for v in verts for f in v.link_faces}
        mi = self._mi_for(m)
        t = self.rng.uniform(-1, 1) if tint is None else tint
        for f in faces:
            f.material_index = mi
            f[self.tint] = t
            f.smooth = False
            f.normal_update()
        if self.detail == "far":
            bevel = 0
        if bevel and bevel > 0:
            # (as normais da primitiva ja estao atualizadas: nao recalcula o bmesh inteiro a cada peca)
            edges = {e for v in verts for e in v.link_edges}
            edges = [e for e in edges if len(e.link_faces) == 2 and e.calc_face_angle(0) > angle]
            if self.detail == "near" and edges:
                # so as arestas do topo da primitiva (as duas pontas em z >= topo - 0,01)
                top = max(v.co.z for v in verts)
                edges = [e for e in edges if e.verts[0].co.z >= top - 0.01 and e.verts[1].co.z >= top - 0.01]
            if edges:
                res = bmesh.ops.bevel(self.bm, geom=edges, offset=bevel, offset_type="OFFSET",
                                      segments=seg, profile=0.5, affect="EDGES", clamp_overlap=True)
                new = set(res.get("faces", ()))
                # faces do chanfro nascem com material 0: herdam o material/tint da primitiva
                for f in new:
                    f.material_index = mi
                    f[self.tint] = t
                    f.smooth = False
                faces = {f for f in faces if f.is_valid} | new
                for f in faces:
                    f.normal_update()
        if self.detail == "far":
            faces = self._drop_bottom(faces, verts)
        self._uv(faces, m)
        return faces

    def box(self, size, loc, rot=(0, 0, 0), m="Stone_Light", bevel=0.12, seg=1, tint=None):
        sx, sy, sz = size
        mb = min(sx, sy, sz)
        bev = min(bevel, mb * 0.3) if bevel else 0
        M = Matrix.LocRotScale(Vector(loc), Euler(rot), Vector((sx, sy, sz)))
        r = bmesh.ops.create_cube(self.bm, size=1.0, matrix=M)
        self._post(r["verts"], m, tint, bev, seg)

    def box2(self, p0, p1, m="Stone_Light", bevel=0.12, seg=1, tint=None):
        """caixa alinhada por cantos"""
        p0, p1 = Vector(p0), Vector(p1)
        c = (p0 + p1) / 2
        s = Vector((abs(p1.x - p0.x), abs(p1.y - p0.y), abs(p1.z - p0.z)))
        self.box(s, c, (0, 0, 0), m, bevel, seg, tint)

    def beam(self, a, b, w, h=None, m="Wood_Dark", bevel=0.08, roll=0.0, tint=None):
        """viga retangular de a ate b (secao w x h)"""
        a, b = Vector(a), Vector(b)
        h = h or w
        d = b - a
        L = d.length
        if L < 1e-4:
            return
        q = d.to_track_quat("X", "Z")
        R = q.to_matrix().to_4x4() @ Matrix.Rotation(roll, 4, "X")
        M = Matrix.Translation((a + b) / 2) @ R @ Matrix.Diagonal((L, w, h, 1))
        r = bmesh.ops.create_cube(self.bm, size=1.0, matrix=M)
        self._post(r["verts"], m, tint, min(bevel, min(w, h) * 0.3), 1)

    def cyl(self, r, h, loc, rot=(0, 0, 0), m="Metal_Iron", n=12, r2=None, bevel=0.08,
            seg=1, caps=True, tint=None, angle=0.5):
        M = Matrix.LocRotScale(Vector(loc), Euler(rot), Vector((1, 1, 1)))
        res = bmesh.ops.create_cone(self.bm, cap_ends=caps, cap_tris=False, segments=n,
                                    radius1=r, radius2=(r if r2 is None else r2), depth=h, matrix=M)
        self._post(res["verts"], m, tint, bevel, seg, angle=max(angle, (2 * math.pi / n) * 1.05))

    def rod(self, a, b, r, m="Metal_Iron", n=8, bevel=0.0, tint=None, caps=True):
        a, b = Vector(a), Vector(b)
        d = b - a
        L = d.length
        if L < 1e-4:
            return
        q = d.to_track_quat("Z", "Y")
        M = Matrix.Translation((a + b) / 2) @ q.to_matrix().to_4x4()
        res = bmesh.ops.create_cone(self.bm, cap_ends=caps, cap_tris=False, segments=n,
                                    radius1=r, radius2=r, depth=L, matrix=M)
        self._post(res["verts"], m, tint, bevel, 1, angle=2.0)

    def ico(self, r, loc, m="Leaf_Pine", sub=1, scale=(1, 1, 1), rot=(0, 0, 0), jitter=0.0,
            tint=None, seed=None):
        M = Matrix.LocRotScale(Vector(loc), Euler(rot), Vector(scale))
        res = bmesh.ops.create_icosphere(self.bm, subdivisions=sub, radius=r, matrix=M)
        vs = res["verts"]
        if jitter > 0:
            s = self.rng.random() * 100 if seed is None else seed
            for v in vs:
                n = noise.noise_vector(v.co * 0.35 + Vector((s, s * 0.7, s * 1.3)))
                v.co += n * jitter * r
        self._post(vs, m, tint, 0, 1)

    def rock(self, loc, size, m="Cliff_Rock", sub=1, rot=(0, 0, 0), jitter=0.28, tint=None, flat_bottom=True):
        sx, sy, sz = size
        M = Matrix.LocRotScale(Vector(loc), Euler(rot), Vector((sx, sy, sz)))
        res = bmesh.ops.create_icosphere(self.bm, subdivisions=sub, radius=0.5, matrix=Matrix.Identity(4))
        vs = res["verts"]
        s = self.rng.random() * 100
        for v in vs:
            n = noise.noise_vector(v.co * 1.7 + Vector((s, s * 0.3, s * 1.9)))
            v.co += n * jitter * 0.5
            if flat_bottom and v.co.z < -0.25:
                v.co.z = -0.25 + (v.co.z + 0.25) * 0.2
        for v in vs:
            v.co = M @ v.co
        self._post(vs, m, tint, 0, 1)

    def prism(self, pts, z0, z1, m="Stone_Light", bevel=0.0, seg=1, tint=None, top_only=False):
        """prisma vertical a partir de poligono 2D (sentido anti-horario)"""
        vb = [self.bm.verts.new((p[0], p[1], z0)) for p in pts]
        vt = [self.bm.verts.new((p[0], p[1], z1)) for p in pts]
        n = len(pts)
        fs = []
        fs.append(self.bm.faces.new(list(reversed(vb))))
        fs.append(self.bm.faces.new(vt))
        for i in range(n):
            j = (i + 1) % n
            fs.append(self.bm.faces.new((vb[i], vb[j], vt[j], vt[i])))
        allv = vb + vt
        if bevel and bevel > 0:
            self._post(allv, m, tint, bevel, seg, angle=0.6)
        else:
            self._post(allv, m, tint, 0, 1)

    def slab_poly(self, pts, z_top, thick, m, bevel=0.0, tint=None):
        self.prism(pts, z_top - thick, z_top, m, bevel, 1, tint)

    def sweep(self, pts, profile, m="Metal_Iron", closed_profile=True, tint=None, up=(0, 0, 1),
              caps=True):
        """varre um perfil 2D (u lateral, v vertical) ao longo de uma polilinha"""
        pts = [Vector(p) for p in pts]
        n = len(pts)
        if n < 2:
            return
        rings = []
        upv = Vector(up)
        for i, p in enumerate(pts):
            if i == 0:
                t = pts[1] - pts[0]
            elif i == n - 1:
                t = pts[-1] - pts[-2]
            else:
                t = (pts[i + 1] - pts[i]).normalized() + (pts[i] - pts[i - 1]).normalized()
            t.normalize()
            u = upv if abs(t.dot(upv)) < 0.95 else Vector((1, 0, 0))
            side = t.cross(u).normalized()
            vv = side.cross(t).normalized()
            ring = [self.bm.verts.new(p + side * a + vv * b) for a, b in profile]
            rings.append(ring)
        k = len(profile)
        rng = k if closed_profile else k - 1
        for r0, r1 in zip(rings, rings[1:]):
            for j in range(rng):
                j2 = (j + 1) % k
                try:
                    self.bm.faces.new((r0[j], r0[j2], r1[j2], r1[j]))
                except ValueError:
                    pass
        if caps and closed_profile:
            try:
                self.bm.faces.new(list(reversed(rings[0])))
                self.bm.faces.new(rings[-1])
            except ValueError:
                pass
        allv = [v for r in rings for v in r]
        self._post(allv, m, tint, 0, 1)

    def tube(self, pts, r, m="Metal_Iron", n=8, tint=None):
        prof = [(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n)) for i in range(n)]
        self.sweep(pts, prof, m, True, tint)

    def quad(self, a, b, c, d, m, tint=None):
        vs = [self.bm.verts.new(Vector(p)) for p in (a, b, c, d)]
        self.bm.faces.new(vs)
        self._post(vs, m, tint, 0, 1)

    def tri(self, a, b, c, m, tint=None):
        vs = [self.bm.verts.new(Vector(p)) for p in (a, b, c)]
        self.bm.faces.new(vs)
        self._post(vs, m, tint, 0, 1)

    def gable_roof(self, cx, cy, w, d, z_eave, rise, m="Roof", thick=0.8, over=1.5, axis="Y",
                   tint=None, shingles=True, ridge_m="Wood_Dark", shingle_bevel=None):
        """telhado de duas aguas; axis = direcao da cumeeira.
        shingle_bevel: chanfro de cada fiada de telhas (None = 0,12 em detail 'hero', 0 em 'near'/'far')"""
        sb = (0.12 if self.detail == "hero" else 0.0) if shingle_bevel is None else shingle_bevel
        # meia-agua como caixa inclinada
        if axis == "Y":
            half = w / 2 + over
            L = d + over * 2
            ang = math.atan2(rise, w / 2)
            slope = math.hypot(half, rise * half / (w / 2))
            for s in (-1, 1):
                cxx = cx + s * half / 2
                czz = z_eave + rise - (rise * (half / (w / 2))) / 2 + thick / 2
                if shingles:
                    rows = max(3, int(slope / 1.6))
                    for i in range(rows):
                        f0 = i / rows
                        f1 = (i + 1.25) / rows
                        xa = cx + s * half * (1 - f0)
                        xb = cx + s * half * (1 - min(f1, 1.0))
                        za = z_eave + rise - rise * (half / (w / 2)) * (1 - f0)
                        zb = z_eave + rise - rise * (half / (w / 2)) * (1 - min(f1, 1.0))
                        mid = Vector(((xa + xb) / 2, cy, (za + zb) / 2 + thick / 2))
                        ln = math.hypot(xa - xb, za - zb)
                        self.box((ln, L, thick * 0.7), mid, (0, s * ang, 0), m, sb, 1,
                                 tint=self.rng.uniform(-1, 1))
                else:
                    self.box((slope, L, thick), (cxx, cy, czz), (0, s * ang, 0), m, 0.15)
            self.box((1.1, L + 0.4, 1.1), (cx, cy, z_eave + rise + thick * 0.6), (0, 0, 0), ridge_m, 0.12)
        else:
            half = d / 2 + over
            L = w + over * 2
            ang = math.atan2(rise, d / 2)
            slope = math.hypot(half, rise * half / (d / 2))
            for s in (-1, 1):
                if shingles:
                    rows = max(3, int(slope / 1.6))
                    for i in range(rows):
                        f0 = i / rows
                        f1 = (i + 1.25) / rows
                        ya = cy + s * half * (1 - f0)
                        yb = cy + s * half * (1 - min(f1, 1.0))
                        za = z_eave + rise - rise * (half / (d / 2)) * (1 - f0)
                        zb = z_eave + rise - rise * (half / (d / 2)) * (1 - min(f1, 1.0))
                        mid = Vector((cx, (ya + yb) / 2, (za + zb) / 2 + thick / 2))
                        ln = math.hypot(ya - yb, za - zb)
                        self.box((L, ln, thick * 0.7), mid, (-s * ang, 0, 0), m, sb, 1,
                                 tint=self.rng.uniform(-1, 1))
                else:
                    cyy = cy + s * half / 2
                    czz = z_eave + rise - (rise * (half / (d / 2))) / 2 + thick / 2
                    self.box((L, slope, thick), (cx, cyy, czz), (-s * ang, 0, 0), m, 0.15)
            self.box((L + 0.4, 1.1, 1.1), (cx, cy, z_eave + rise + thick * 0.6), (0, 0, 0), ridge_m, 0.12)

    def gable_wall(self, cx, cy, w, z_base, rise, thick, axis_facing="Y", m="Plaster", tint=None):
        """triangulo de oitao (parede) - face normal ao eixo dado"""
        hw = w / 2
        if axis_facing == "Y":
            pts = [(-hw, 0), (hw, 0), (0, rise)]
            vs_f = [self.bm.verts.new((cx + a, cy - thick / 2, z_base + b)) for a, b in pts]
            vs_b = [self.bm.verts.new((cx + a, cy + thick / 2, z_base + b)) for a, b in pts]
        else:
            pts = [(-hw, 0), (hw, 0), (0, rise)]
            vs_f = [self.bm.verts.new((cx - thick / 2, cy + a, z_base + b)) for a, b in pts]
            vs_b = [self.bm.verts.new((cx + thick / 2, cy + a, z_base + b)) for a, b in pts]
        self.bm.faces.new(vs_f)
        self.bm.faces.new(list(reversed(vs_b)))
        for i in range(3):
            j = (i + 1) % 3
            self.bm.faces.new((vs_f[j], vs_f[i], vs_b[i], vs_b[j]))
        self._post(vs_f + vs_b, m, tint, 0, 1)

    def finish(self, parent=None, recalc=True):
        if len(self.bm.verts) == 0:
            self.bm.free()
            return None
        bmesh.ops.dissolve_degenerate(self.bm, dist=1e-4, edges=self.bm.edges[:])
        if recalc:
            bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces)
        # resolve os slots de variante -> nomes finais e junta indices que caem no mesmo material
        vmap = {}
        final = []
        for key in self.mats:
            if isinstance(key, tuple):
                fam = key[1]
                if fam not in vmap:
                    vmap[fam] = self._variant_names(fam)
                final.append(alias(vmap[fam][key[2]]))
            else:
                final.append(alias(key))
        uniq = []
        remap = []
        for n in final:
            if n not in uniq:
                uniq.append(n)
            remap.append(uniq.index(n))
        if remap != list(range(len(remap))):
            for f in self.bm.faces:
                if f.material_index < len(remap):
                    f.material_index = remap[f.material_index]
        self.mats = uniq
        me = bpy.data.meshes.new(self.name)
        self.bm.to_mesh(me)
        self.bm.free()
        for m in self.mats:
            me.materials.append(mat(m))
        ob = bpy.data.objects.new(self.name, me)
        self.coll.objects.link(ob)
        if parent is not None:
            ob.parent = parent
        return ob


# ------------------------------------------------------------------ colisao e marcadores
_COL_COUNT = {}


def col_box(area, size, loc, rot=(0, 0, 0), kind="Block"):
    """caixa de colisao simplificada (vira Part invisivel no Roblox)"""
    n = _COL_COUNT.get(area, 0) + 1
    _COL_COUNT[area] = n
    name = "COL_%s_%03d" % (area, n)
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = Vector(loc)
    ob.rotation_euler = Euler(rot)
    ob.scale = Vector(size)
    ob["col_kind"] = kind
    ob.display_type = "WIRE"
    ob.hide_render = True
    c = sub_coll("13_COLLISION", "COL_" + area)
    c.objects.link(ob)
    return ob


def col_box2(area, p0, p1, kind="Block"):
    p0, p1 = Vector(p0), Vector(p1)
    return col_box(area, (abs(p1.x - p0.x), abs(p1.y - p0.y), abs(p1.z - p0.z)), (p0 + p1) / 2, (0, 0, 0), kind)


def col_ramp(area, a, b, width, thick=1.0):
    """rampa de colisao de a (base) ate b (topo) - para escadas (Roblox: Part inclinada)"""
    a, b = Vector(a), Vector(b)
    d = b - a
    L = d.length
    yaw = math.atan2(d.y, d.x)
    pitch = math.atan2(d.z, math.hypot(d.x, d.y))
    c = (a + b) / 2
    # topo da rampa passa pelos bordos dos degraus: baixa o centro em thick/2 na normal
    nrm = Vector((-math.sin(pitch) * math.cos(yaw), -math.sin(pitch) * math.sin(yaw), math.cos(pitch)))
    c = c - nrm * thick / 2
    return col_box(area, (L, width, thick), c, (0, -pitch, yaw), kind="Ramp")


def col_beam(area, a, b, w, h):
    a, b = Vector(a), Vector(b)
    d = b - a
    yaw = math.atan2(d.y, d.x)
    return col_box(area, (d.length, w, h), (a + b) / 2, (0, 0, yaw))


def marker(name, loc, rot=(0, 0, 0), size=2.0, kind="PLAIN_AXES", c="15_GAMEPLAY_MARKERS", props=None):
    ob = bpy.data.objects.new(name, None)
    ob.empty_display_type = kind
    ob.empty_display_size = size
    ob.location = Vector(loc)
    ob.rotation_euler = Euler(rot)
    coll(c).objects.link(ob)
    for k, v in (props or {}).items():
        ob[k] = v
    return ob


def light(name, kind, loc, energy, color=(1, 0.7, 0.4), radius=0.5, rot=(0, 0, 0), c="11_LIGHTING"):
    ld = bpy.data.lights.new(name, kind)
    ld.energy = energy
    ld.color = color
    if hasattr(ld, "shadow_soft_size"):
        ld.shadow_soft_size = radius
    if kind == "POINT" and energy < 500:
        ld.use_shadow = False   # lanternas pequenas: sem sombra (custo; no Roblox tambem Shadows=false)
    ob = bpy.data.objects.new(name, ld)
    ob.location = Vector(loc)
    ob.rotation_euler = Euler(rot)
    coll(c).objects.link(ob)
    return ob


def camera(name, loc, target, lens=24, c="00_REFERENCE"):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.clip_end = 3000
    cd.clip_start = 0.5
    ob = bpy.data.objects.new(name, cd)
    ob.location = Vector(loc)
    d = Vector(target) - Vector(loc)
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    coll(c).objects.link(ob)
    return ob
