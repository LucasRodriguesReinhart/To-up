# make_sheets_amostra.py - pranchas da primeira entrega da AMOSTRA (trecho de referencia):
# 1 referencia original | 2 clay da base da torre | 3 sobreposicao de silhueta (50% + diferenca) | 4 portal de perto
# 5 poste de perto | 6 arvores douradas de perto | 7 piso e margem de agua | 8 resultado no Roblox | 9 altura do jogador
import os
from PIL import Image, ImageDraw, ImageFont
R = os.path.dirname(os.path.abspath(__file__)); REFS = os.path.dirname(R)
def P(n): return os.path.join(R, n)
def Rf(n): return os.path.join(REFS, n)
def fit(im, w, h):
    im = im.convert('RGB'); r = min(w / im.width, h / im.height)
    im = im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)
    bg = Image.new('RGB', (w, h), (28, 28, 30)); bg.paste(im, ((w - im.width) // 2, (h - im.height) // 2)); return bg
try: font = ImageFont.truetype(r'C:\Windows\Fonts\segoeuib.ttf', 24)
except Exception: font = ImageFont.load_default()
def opt(p):
    return Image.open(p) if os.path.exists(p) else Image.new('RGB', (800, 450), (70, 30, 30))
def sheet(name, title, panels, W=1000, H=560):
    n = len(panels)
    out = Image.new('RGB', (W * n + 10 * (n + 1), H + 70), (28, 28, 30)); d = ImageDraw.Draw(out)
    d.text((14, 8), title, fill=(255, 255, 255), font=font)
    for i, (im, cap) in enumerate(panels):
        x = 10 + i * (W + 10)
        out.paste(fit(im, W, H), (x, 50)); d.text((x + 6, 52), cap, fill=(255, 220, 120) if i == 0 else (120, 220, 255), font=font)
    out.save(P(name)); print(name, out.size)
ref = Image.open(Rf('user_00_line6.png'))
sheet('A1_referencia.png', '1 - referencia original (Anime Expeditions, vista frontal da Tower)', [(ref, 'REFERENCIA')], W=1411, H=580)
sheet('A2_clay_base.png', '2 - clay da base da torre (Workbench, sem materiais) na camera correspondida', [(ref, 'REFERENCIA'), (opt(P('trecho_04_clay.png')), 'CLAY (camera match: FOV 102 h, avatar 5 studs, 12,5 atras)')])
sheet('A3_sobreposicao.png', '3 - sobreposicao 50% e diferenca de silhueta (vermelho = arestas da referencia, ciano = contorno do modelo)', [(opt(P('trecho_04_overlay50.png')), 'SOBREPOSICAO 50%'), (opt(P('trecho_04_diff.png')), 'DIFERENCA')])
sheet('A4_portal.png', '4 - portal de perto', [(Image.open(Rf('ref_tower_base.png')), 'REFERENCIA'), (opt(P('portal_03_tex.png')), 'BLENDER (texturizado, sem bloom)'), (opt(P('rb_portal.png')), 'ROBLOX')], W=760, H=560)
sheet('A5_poste.png', '5 - poste de perto (mesma inclinacao de camera)', [(Image.open(Rf('ref_lamp_left.png')), 'REFERENCIA'), (opt(P('poste_05_clay.png')), 'CLAY'), (opt(P('poste_05_tex.png')), 'BLENDER tex'), (opt(P('rb_poste.png')).crop((280, 0, 870, 645)) if os.path.exists(P('rb_poste.png')) else opt(P('rb_poste.png')), 'ROBLOX (recorte)')], W=480, H=900)
sheet('A6_arvores.png', '6 - arvores douradas de perto', [(ref.crop((180, 150, 560, 500)), 'REFERENCIA'), (opt(P('arvores_02_tex.png')), 'BLENDER tex'), (opt(P('rb_arvores.png')), 'ROBLOX')], W=700, H=700)
sheet('A7_piso_agua.png', '7 - piso e margem de agua', [(ref.crop((150, 380, 1250, 580)), 'REFERENCIA (piso)'), (opt(P('rb_piso_agua.png')), 'ROBLOX piso'), (Image.open(Rf('ref_floor_planter.png')), 'REFERENCIA (margem)'), (opt(P('rb_agua.png')), 'ROBLOX margem (lado)'), (opt(P('rb_agua_cima.png')), 'ROBLOX margem (cima)')], W=560, H=420)
sheet('A8_roblox.png', '8 - resultado importado no Roblox (mesma camera da referencia)', [(ref, 'REFERENCIA'), (opt(P('rb_geral.png')), 'ROBLOX (Studio, sem HUD)')])
sheet('A9_jogador.png', '9 - altura normal da camera do jogador (Play, HUD oculta)', [(ref, 'REFERENCIA'), (opt(P('rb_jogador.png')), 'ROBLOX (Play)')])
