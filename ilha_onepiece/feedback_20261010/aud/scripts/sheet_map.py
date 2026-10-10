# sheet_map.py - folha U1..U16 -> captura -> dono (op_*.py) -> coordenadas locais
from PIL import Image, ImageDraw, ImageFont
PROJ = r"C:/Users/lucas/OneDrive/Desktop/To up/ilha_onepiece"
FB = PROJ + "/feedback_20261010/"
F = ImageFont.truetype("arial.ttf", 14); FBD = ImageFont.truetype("arialbd.ttf", 15); FT = ImageFont.truetype("arialbd.ttf", 24)
ITEMS = [
    ("01_casa_loja_C1.jpg", "U1 casas (loja C1)", "op_kit.house + op_m2_trecho (C1,C2,C5,C6)", "rua de chegada x -40..40, y 44..112, T1 88,2"),
    ("02_rua_capital_cima.jpg", "U1/U2 rua de chegada", "op_m2_trecho, op_capital (C4,C7,E*), op_layout.STREETS", "eixo x 0, y 44..112; viela leste y 104..118"),
    ("03_castelo_arvore_praca.jpg", "U3/U4 castelo + arvore", "op_castle (OP_Cas_*), op_tree (OP_Tree_*)", "torre (0,404) CC 136,2; arco ate 301"),
    ("04_borda_grama_arvores.jpg", "U4/U8 borda + arvores", "op_veg (OP_Veg_*), op_terrain (pele)", "faixas de borda sem piso (U8)"),
    ("05_ponte_canal_na_calcada.jpg", "U6 ponte do canal", "op_capital.canal_bridge, op_water, op_col", "(-174, 182) e (-174, 252), P 92,2"),
    ("06_poco.jpg", "U7 poco", "op_props (poco) + op_kit", "(-117,67) T1, (-205,164,5) W2b, terraco W3"),
    ("07_porto_cais_navio.jpg", "U9/U13 porto + H3 no muro", "op_harbor (H1-H5, pier, barcos), op_ship", "cais 42,2 x 120..246; H3 (176,120) 65,2"),
    ("08_summon_sem_tema_OP.jpg", "U10/U16 summon", "op_summon (alias il_summon + base)", "torre (170,214), terraco T1 88,2"),
    ("09_vilarejo_NE_santuario.jpg", "U11 vilarejo NE", "op_capital NE (N1-N10), op_terrain (NERocks)", "x 110..222, y 265..339; rocha 100-120"),
    ("10_pagode_no_pilar.jpg", "U13 pagode no pilar", "op_landmarks (OP_Lmk_Pagoda)", "pinaculo (-246,372), topo 158"),
    ("11_caminho_chao.jpg", "U2 caminho de laje", "op_capital (STREETS/yards), op_layout", "lajes retangulares sobre grama"),
    ("12_REF_ATMOSFERA_wano_anime.jpg", "U14 atmosfera alvo", "AreaAtmosphere [5], CeuWano, OnePieceIsland, op_vfx", "perfil GrandLine (hoje 9,05 h / azul)"),
    ("13_poste_luz.jpg", "U15 poste", "op_kit.lantern_post (+box_post), op_capital.lamp", "28 chamadas em capital/props/harbor/entry"),
    ("14_estandartes_cachoeira.jpg", "U16 bandeiras", "op_castle.banners, op_entry, op_plaza, op_m2_trecho, op_capital, op_summon", "~20 mastros/nobori na ilha"),
    ("15_canal_grama.jpg", "U8/U2 canal leste em grama", "op_water (canal), op_terrain, op_col (sem fundo)", "canal leste y 342..343 / bacia"),
    ("frames/video3_contato.jpg", "U8/U11/U12 video 3", "op_col + op_layout.ROCKS, op_capital NE", "telhados NE, montanha, bacia do adro"),
]
TW, TH = 400, 300
COLS = 4
rows = (len(ITEMS) + COLS - 1) // COLS
W, H = COLS * (TW + 20) + 20, 60 + rows * (TH + 92)
img = Image.new("RGB", (W, H), (18, 22, 30)); d = ImageDraw.Draw(img)
d.text((20, 16), "Wano V2 - mapeamento U1..U16 -> captura -> dono (op_*.py) -> coordenadas LOCAIS", fill=(255, 255, 255), font=FT)
for k, (fn, t, own, xy) in enumerate(ITEMS):
    r, c = divmod(k, COLS)
    x0, y0 = 20 + c * (TW + 20), 60 + r * (TH + 92)
    try:
        im = Image.open(FB + fn).convert("RGB")
        im.thumbnail((TW, TH))
        img.paste(im, (x0 + (TW - im.width) // 2, y0 + (TH - im.height) // 2))
    except Exception as e:
        d.text((x0, y0), str(e), fill=(255, 0, 0), font=F)
    d.rectangle([x0, y0, x0 + TW, y0 + TH], outline=(70, 80, 100))
    d.text((x0, y0 + TH + 6), t, fill=(255, 210, 120), font=FBD)
    d.text((x0, y0 + TH + 28), own[:58], fill=(220, 220, 220), font=F)
    d.text((x0, y0 + TH + 48), own[58:116], fill=(220, 220, 220), font=F)
    d.text((x0, y0 + TH + 66), xy, fill=(150, 200, 255), font=F)
img.save(PROJ + "/feedback_20261010/aud/U_mapeamento_donos.jpg", quality=88)
print("ok", img.size)
