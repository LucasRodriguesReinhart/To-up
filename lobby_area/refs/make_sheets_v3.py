# make_sheets_v3.py - pranchas de comparacao referencia x jogo (revisao 3 da Etapa C)
import os
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
def opt(n):
    return Image.open(P(n)) if os.path.exists(P(n)) else Image.new('RGB', (800, 450), (60, 30, 30))
ref0 = Image.open(P('user_00_line6.png'))
sheet('v3_comp_01_geral.png', '1 - visao geral limpa (camera ~9 studs de altura, ~66 da fachada, FOV 70)', ref0.crop((250, 0, 1160, 580)), 'REFERENCIA', opt('v3_final_01_geral.png'), 'JOGO - revisao 3 (Studio, luz v4, sem HUD)')
sheet('v3_comp_02_entrada.png', '2 - entrada e Ignis (pe da escada)', Image.open(P('ref_tower_base.png')), 'REFERENCIA (porta da Tower)', opt('v3_final_02_entrada.png'), 'JOGO - alcova do Ignis')
sheet('v3_comp_03_fachada.png', '3 - fachada de perto (relevo: molduras duplas, pilastras, cornija)', ref0.crop((380, 60, 820, 470)), 'REFERENCIA', opt('v3_final_03_fachada.png'), 'JOGO')
sheet('v3_comp_04_poste.png', '4 - poste em escala comparavel (avatar ao lado)', Image.open(P('user_06_line6.png')), 'REFERENCIA', opt('v3_final_04_poste.png'), 'JOGO - poste 0,8 (Play)', W=760, H=680)
sheet('v3_comp_05_piso.png', '5 - piso (inlays embutidos, medalhao em plataforma, folhas)', Image.open(P('ref_floor_planter.png')), 'REFERENCIA', opt('v3_final_05_piso.png'), 'JOGO')
sheet('v3_comp_06_vegetacao.png', '6 - vegetacao (alamos v3, arvores redondas, capim, cobertura)', ref0.crop((700, 60, 1300, 560)), 'REFERENCIA', opt('v3_final_06_vegetacao.png'), 'JOGO')
sheet('v3_comp_07_agua_cima.png', '7a - agua vista de cima', Image.open(P('user_03_line6.png')).crop((600, 0, 1802, 700)), 'REFERENCIA (canal)', opt('v3_final_07_agua_cima.png'), 'JOGO')
sheet('v3_comp_07_agua_lado.png', '7b - agua vista de lado (ponte, margem curva, pedras)', Image.open(P('ref_canal_bridge.png')), 'REFERENCIA', opt('v3_final_07_agua_lado.png'), 'JOGO')
sheet('v3_comp_08_agua_limite.png', '8 - limite inferior da agua (de baixo/lateral: sem bloco ciano exposto)', opt('v3_final_08_agua_limite_a.png'), 'JOGO - por baixo do passeio externo', opt('v3_final_08_agua_limite_b.png'), 'JOGO - do patamar olhando para baixo')
sheet('v3_comp_09_clay.png', '9 - geometria clay', Image.open(P('sec3b_tower_clay.png')), 'TORRE (clay)', Image.open(P('sec3c_agua_baixo_clay.png')), 'AGUA/PONTE (clay)')
sheet('v3_comp_10_ignis.png', '10 - interacao com Ignis (Play): prompt visivel e UI da Forja aberta', opt('v3_final_10_ignis_prompt.png'), 'PROMPT "Falar" no belly', opt('v3_final_10_ignis_ui.png'), 'UI aberta apos acionar')
sheet('v3_comp_11_jogador.png', '11 - altura normal da camera do jogador (Play, HUD oculta)', ref0.crop((250, 0, 1160, 580)), 'REFERENCIA', opt('v3_final_11_jogador.png'), 'JOGO')
