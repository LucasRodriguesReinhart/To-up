# make_sheets_v2.py - pranchas de comparacao referencia x jogo (revisao 2 da Etapa C)
import os, sys
from PIL import Image, ImageDraw, ImageFont
R = os.path.dirname(os.path.abspath(__file__))
def P(n): return os.path.join(R, n)
def fit(im, w, h):
    im = im.convert('RGB'); r = min(w / im.width, h / im.height)
    im = im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)
    bg = Image.new('RGB', (w, h), (28, 28, 30)); bg.paste(im, ((w - im.width) // 2, (h - im.height) // 2)); return bg
try: font = ImageFont.truetype(r'C:\Windows\Fonts\segoeuib.ttf', 24)
except Exception: font = ImageFont.load_default()
def sheet(name, title, left, lcap, right, rcap, W=1000, H=560):
    out = Image.new('RGB', (W * 2 + 30, H + 70), (28, 28, 30)); d = ImageDraw.Draw(out)
    d.text((14, 8), title, fill=(255, 255, 255), font=font)
    out.paste(fit(left, W, H), (10, 50)); out.paste(fit(right, W, H), (W + 20, 50))
    d.text((14, 52), lcap, fill=(255, 220, 120), font=font); d.text((W + 24, 52), rcap, fill=(120, 220, 255), font=font)
    out.save(P(name)); print(name, out.size)
ref0 = Image.open(P('user_00_line6.png'))
sheet('v2_comp_1_torre.png', 'V1 - visao geral da torre (camera a ~9 studs de altura, ~66 da fachada, FOV 70)', ref0.crop((250, 0, 1160, 580)), 'REFERENCIA', Image.open(P('v2_final_1_torre.png')), 'JOGO - revisao 2 (Studio, luz v3)')
sheet('v2_comp_2_entrada.png', 'V2 - entrada e Ignis (pe da escada)', Image.open(P('ref_tower_base.png')), 'REFERENCIA (porta da Tower)', Image.open(P('v2_final_2_entrada.png')), 'JOGO - alcova do Ignis (escala 0,62)')
sheet('v2_comp_3_poste.png', 'V3 - poste e piso de perto', Image.open(P('user_06_line6.png')), 'REFERENCIA', Image.open(P('v2_final_3_poste.png')), 'JOGO - poste v2', W=760, H=680)
sheet('v2_comp_4_agua.png', 'V4 - agua e margem', Image.open(P('user_03_line6.png')).crop((600, 0, 1802, 700)), 'REFERENCIA (canal)', Image.open(P('v2_final_4_agua.png')), 'JOGO - espelho d\'agua com prateleira rasa e margem curva')
sheet('v2_comp_5_vegetacao.png', 'V5 - vegetacao (alamos dourados, capim, arbustos)', ref0.crop((700, 60, 1300, 560)), 'REFERENCIA', Image.open(P('v2_final_5_vegetacao.png')), 'JOGO - canteiro do terraco')
sheet('v2_comp_6_clay.png', 'V6 - geometria sem materiais (clay): torre e entrada', Image.open(P('sec2_tower_clay.png')), 'TRECHO v2 - vista geral (clay)', Image.open(P('sec2_entrada_clay.png')), 'TRECHO v2 - entrada (clay)')
sheet('v2_comp_7_jogador.png', 'V7 - altura normal do jogador (Play, camera padrao)', ref0.crop((250, 0, 1160, 580)), 'REFERENCIA', Image.open(P('v2_final_7_jogador.png')), 'JOGO - em Play, atras do personagem')
if os.path.exists(P('kit2_poste_clay.png')):
    sheet('v2_comp_8_poste_clay.png', 'Poste: recorte da referencia x geometria clay (mesma inclinacao de camera)', Image.open(P('ref_lamp_left.png')), 'REFERENCIA (recorte)', Image.open(P('kit2_poste_clay.png')), 'POSTE v2 (clay)', W=600, H=900)
