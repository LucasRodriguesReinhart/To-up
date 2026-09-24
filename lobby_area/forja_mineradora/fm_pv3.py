# fm_pv3.py - portais v3 (modelados em separado no portal_studio e aprovados pelo usuario em 2026-09-24): um modulo
# por portal, fm_pv3_<key>.py, com build(rng). O One Piece continua em fm_portals.onepiece (era o padrao de qualidade).
# load() tem que rodar ANTES de fm_lib.make_materials() e tambem no export: cada modulo registra no topo os proprios
# materiais (fm_lib.MATS / RBX_CAL), a cor da luz (fm_portal_kit.LIGHT_COL) e a textura da espiral (fm_mat_textures).
import importlib

MODS = {"Naruto": "fm_pv3_naruto", "DragonBall": "fm_pv3_dragonball", "ShadowGarden": "fm_pv3_shadowgarden",
        "DemonSlayer": "fm_pv3_demonslayer", "OnePunchMan": "fm_pv3_onepunchman"}


# semente de cada portal (fixa por nome; era 707 + indice na ordem antiga): a troca Shadow Garden <-> Demon Slayer nao
# muda o visual aprovado
SEED = {"Naruto": 707, "DragonBall": 708, "ShadowGarden": 709, "DemonSlayer": 710, "OnePiece": 711, "OnePunchMan": 712}
STAIRS_SEED = {k: v + 101 for k, v in SEED.items()}     # (o estudio usava 808 + indice antigo)


def load():
    return {k: importlib.import_module(m) for k, m in MODS.items()}
