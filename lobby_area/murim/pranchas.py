# pranchas.py - pranchas da etapa 1-3 do lobby "Seita da Forja Celeste":
#   B1_paleta_materiais.png : paleta + amostras de material estilizado (pintadas por codigo, sem foto)
#   B2_planta.png           : planta do lobby (coordenadas Roblox) com zonas, niveis, marcos e fluxo do jogador
import os, math
from PIL import Image, ImageDraw, ImageFont
R = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(R, 'pranchas'); os.makedirs(OUT, exist_ok=True)
def font(sz, bold=False):
    try: return ImageFont.truetype(r'C:\Windows\Fonts\segoeui%s.ttf' % ('b' if bold else ''), sz)
    except Exception: return ImageFont.load_default()
F14, F16, F18, F22, F28 = font(14), font(16), font(18, True), font(22, True), font(28, True)
BG = (30, 30, 33)

PAL = [
    ('Vermelho imperial', '#B8321E', 'colunas, paredes, portas'), ('Vermelho sombra', '#7E2014', 'faces em sombra, vigas'),
    ('Ouro', '#E0A83A', 'cumeeiras, aneis, emblemas'), ('Bronze', '#8C6A2E', 'braseiros, sinos, ferragens'),
    ('Madeira escura', '#4A2E1E', 'vigas, dougong, portas'), ('Madeira media', '#7A4B2A', 'postes de treino, pontes'),
    ('Pedra clara quente', '#DCCDB0', 'terracos, balaustradas'), ('Pedra do piso', '#B9AD95', 'lajes do patio'),
    ('Junta / pedra escura', '#8F846E', 'juntas, bases, rochas em sombra'), ('Telha jade escuro', '#2E5A4C', 'telhados gerais'),
    ('Telha imperial', '#D4A034', 'SO o Salao da Forja'), ('Ferro da forja', '#2B2624', 'lareira, bigorna, chamine'),
    ('Brasa', '#FF7A1A', 'lareira, braseiros'), ('Chama', '#FFC84A', 'chamas, lanternas'),
    ('Pinheiro', '#3E6B3A', 'copas em camadas'), ('Folha clara', '#6E9A45', 'arbustos, grama'),
    ('Bordo vermelho', '#C4432B', 'arvores de acento'), ('Bambu', '#7FA85A', 'moitas junto aos muros'),
    ('Agua turquesa', '#3FA0A0', 'superficie do lago'), ('Fundo do lago', '#2A6C6A', 'leito, canal'),
]
def hexc(h): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
def shade(c, k): return tuple(max(0, min(255, int(v * k))) for v in c)

def swatch_tile(d, x, y, w, h, base):
    """telha estilizada: fiadas largas com realce na crista e sombra na calha (pintado)."""
    d.rectangle([x, y, x + w, y + h], fill=shade(base, .85))
    n = 6; rw = w / n
    for i in range(n):
        cx = x + i * rw
        d.rounded_rectangle([cx + 1, y, cx + rw - 1, y + h], radius=int(rw / 2), fill=base)
        d.rounded_rectangle([cx + 3, y, cx + rw * .45, y + h], radius=int(rw / 3), fill=shade(base, 1.18))
        d.rectangle([cx + rw * .8, y, cx + rw - 1, y + h], fill=shade(base, .7))
    for j in range(4):
        yy = y + j * h / 4
        d.ellipse([x - 2, yy - 3, x + w + 2, yy + 3], outline=shade(base, .6), width=1)
def swatch_stone(d, x, y, w, h, base):
    d.rectangle([x, y, x + w, y + h], fill=shade(base, .8))
    bw, bh = w / 3, h / 3
    for j in range(3):
        off = (bw / 2) if j % 2 else 0
        for i in range(-1, 4):
            bx = x + i * bw + off
            box = [max(x, bx + 2), y + j * bh + 2, min(x + w, bx + bw - 2), y + (j + 1) * bh - 2]
            if box[2] - box[0] > 4:
                d.rounded_rectangle(box, radius=6, fill=shade(base, 1 + .06 * ((i + j) % 3 - 1)))
                d.line([box[0] + 3, box[1] + 3, box[2] - 3, box[1] + 3], fill=shade(base, 1.2), width=2)
def swatch_wood(d, x, y, w, h, base):
    d.rectangle([x, y, x + w, y + h], fill=base)
    for j in range(5):
        yy = y + (j + .5) * h / 5
        d.line([x, yy, x + w, yy + 4], fill=shade(base, .8), width=3)
        d.line([x, yy - 5, x + w, yy - 2], fill=shade(base, 1.15), width=1)
def swatch_flat(d, x, y, w, h, base):
    d.rectangle([x, y, x + w, y + h], fill=base)
    d.rectangle([x, y, x + w, y + h * .3], fill=shade(base, 1.15))
    d.rectangle([x, y + h * .75, x + w, y + h], fill=shade(base, .8))
def swatch_water(d, x, y, w, h, base):
    d.rectangle([x, y, x + w, y + h], fill=base)
    for j in range(6):
        yy = y + (j + .5) * h / 6
        pts = [(x + i, yy + 3 * math.sin(i / 9 + j)) for i in range(0, w + 1, 3)]
        d.line(pts, fill=shade(base, 1.35), width=2)
    d.ellipse([x + w * .2, y + h * .4, x + w * .35, y + h * .55], fill=shade(base, .6))
    d.ellipse([x + w * .6, y + h * .6, x + w * .72, y + h * .72], fill=shade(base, .6))
def swatch_metal(d, x, y, w, h, base):
    d.rectangle([x, y, x + w, y + h], fill=base)
    d.polygon([(x, y), (x + w * .5, y), (x + w * .2, y + h)], fill=shade(base, 1.25))
    d.rectangle([x, y + h * .8, x + w, y + h], fill=shade(base, .6))

def prancha_paleta():
    W, H = 1500, 980
    im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im)
    d.text((20, 14), 'B1 - Direcao de arte: paleta e materiais estilizados (pintados por codigo, sem foto)', fill='white', font=F22)
    d.text((20, 46), 'Cartoon premium: cores chapadas + variacao suave + realce de aresta; detalhe so em beirais, cumeeiras, portas e pedestais.', fill=(200, 200, 200), font=F14)
    x0, y0, sw, sh, gap = 20, 80, 270, 78, 14
    for i, (nm, hx, uso) in enumerate(PAL):
        col, row = i % 5, i // 5
        x = x0 + col * (sw + gap); y = y0 + row * (sh + 44)
        d.rounded_rectangle([x, y, x + sw, y + sh], radius=10, fill=hexc(hx))
        d.rounded_rectangle([x, y + sh - 22, x + sw, y + sh], radius=10, fill=shade(hexc(hx), .75))
        d.text((x + 8, y + 6), nm, fill='white' if sum(hexc(hx)) < 480 else (20, 20, 20), font=F16)
        d.text((x + 8, y + sh + 4), hx + '  ' + uso, fill=(215, 215, 215), font=F14)
    # materiais
    yb = y0 + 4 * (sh + 44) + 20
    d.text((20, yb), 'Amostras de material (leitura a 40 studs): telha jade | telha imperial | pedra clara | piso | madeira | vermelho laqueado | bronze | agua', fill='white', font=F18)
    mats = [('telha jade', swatch_tile, '#2E5A4C'), ('telha imperial', swatch_tile, '#D4A034'), ('pedra clara', swatch_stone, '#DCCDB0'),
            ('piso', swatch_stone, '#B9AD95'), ('madeira', swatch_wood, '#4A2E1E'), ('vermelho laqueado', swatch_flat, '#B8321E'),
            ('bronze', swatch_metal, '#8C6A2E'), ('agua', swatch_water, '#3FA0A0')]
    mw, mh = 168, 168
    for i, (nm, fn, hx) in enumerate(mats):
        x = 20 + i * (mw + 15); y = yb + 34
        fn(d, x, y, mw, mh, hexc(hx))
        d.rectangle([x, y, x + mw, y + mh], outline=(60, 60, 60), width=2)
        d.text((x, y + mh + 6), nm, fill=(230, 230, 230), font=F16)
    # regras curtas
    ry = yb + 34 + mh + 40
    rules = ['Colunas d=2.2-2.6 com entasis, base de pedra em tambor, anel de ouro no topo.',
             'Telhado: 2 beirais so na Forja; balanco 5-6; cantos levantados; fiadas de 1.2; cumeeira grossa em ouro com terminais.',
             'Dougong em 2-3 degraus arredondados, pintado em faixas, so nos edificios principais.',
             'Rochas facetadas em cunha; pinheiros em 3-4 camadas; bordos em massas redondas; bambu junto aos muros.',
             'Ouro fosco (Reflectance <= .1); Neon so em brasas/chamas pequenas; sem textura fotografica; normal map so em telha e pedra grande.',
             'Luz: fim de tarde (ClockTime ~15.5), ambiente levemente frio; Forja com luzes laranja; lanternas ambar.']
    for i, r in enumerate(rules): d.text((20, ry + i * 22), '- ' + r, fill=(220, 220, 220), font=F14)
    im.save(os.path.join(OUT, 'B1_paleta_materiais.png')); print('B1', im.size)

def prancha_planta():
    # planta: x Roblox horizontal (esquerda = -x oeste), z Roblox vertical (cima = -z Forja, baixo = +z saida)
    W, H = 1500, 1150; S = 3.0   # px por stud
    im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im)
    cx, cz = 720, 560   # origem (0,0)
    def X(x): return cx + x * S
    def Z(z): return cz + z * S
    def rect(x0, x1, z0, z1, fill, outline=None, w=1): d.rectangle([X(x0), Z(z0), X(x1), Z(z1)], fill=fill, outline=outline, width=w)
    def label(x, z, t, f=F14, fill='white', anchor='mm'): d.text((X(x), Z(z)), t, fill=fill, font=f, anchor=anchor)
    # terreno
    rect(-165, 165, -205, 180, hexc('#3E5A34'))
    # penhascos norte
    rect(-165, 165, -205, -152, hexc('#6E6658')); label(0, -178, 'PENHASCOS + pinheiros (limite norte, y ate 70)', F16)
    rect(-165, -152, -152, 150, hexc('#6E6658')); rect(152, 165, -152, 150, hexc('#6E6658'))
    # muros
    rect(-152, -148, -70, 146, hexc('#B8321E')); rect(148, 152, -70, 146, hexc('#B8321E'))
    rect(-152, -46, 146, 154, hexc('#B8321E')); rect(46, 152, 146, 154, hexc('#B8321E'))
    # lago leste + riacho + cascata
    rect(70, 100, -70, 130, hexc('#3FA0A0')); rect(84, 94, -150, -70, hexc('#3FA0A0')); label(85, -100, 'riacho', F14)
    label(85, 100, 'LAGO DE JADE\n(agua y -1.5)', F16, anchor='mm')
    rect(80, 98, -156, -150, hexc('#DDF3F3')); label(89, -160, 'cascata', F14)
    # terraco da forja
    rect(-62, 62, -150, -92, hexc('#DCCDB0'), hexc('#8F846E'), 2)
    rect(-36, 36, -146, -108, hexc('#D4A034'), hexc('#7A4B2A'), 2)
    rect(-36, 36, -118, -108, hexc('#B8321E'))
    label(0, -127, 'SALAO DA FORJA  72 x 38\ntelhado duplo dourado, cumeeira y 46', F16, fill=(40, 30, 10))
    d.ellipse([X(-6), Z(-146), X(6), Z(-134)], fill=hexc('#2B2624')); label(0, -140, 'Torre\ndo Fogo', F14)
    d.ellipse([X(-6), Z(-122), X(6), Z(-110)], fill=hexc('#FF7A1A')); label(0, -116, 'IGNIS', F14, fill='black')
    label(0, -100, 'terraco y 10 + balaustrada', F14, fill=(40, 30, 10))
    label(-49, -125, 'altar de\nlaminas', F14, fill=(40, 30, 10)); label(49, -125, 'fole +\ncalha', F14, fill=(40, 30, 10))
    # escadaria
    rect(-23, 23, -92, -60, hexc('#C9BB9E'), hexc('#8F846E'), 1)
    for i in range(12): d.line([X(-23), Z(-60 - i * 2.5), X(23), Z(-60 - i * 2.5)], fill=hexc('#8F846E'))
    rect(-5, 5, -90, -60, hexc('#E0A83A')); label(0, -76, 'danbi', F14, fill='black')
    label(-40, -76, 'ESCADARIA\n12 degraus\ny 0 -> 10', F14)
    # patio
    rect(-70, 70, -60, 60, hexc('#B9AD95'), hexc('#8F846E'), 2)
    d.ellipse([X(-23), Z(-23), X(23), Z(23)], fill=hexc('#3FA0A0'))
    d.ellipse([X(-13), Z(-13), X(13), Z(13)], fill=hexc('#DCCDB0'))
    for (a, b) in [(-24, -12), (12, 24)]:
        rect(a, b, -4, 4, hexc('#DCCDB0')); rect(-4, 4, a, b, hexc('#DCCDB0'))
    d.line([X(0), Z(-11), X(0), Z(11)], fill=hexc('#E0A83A'), width=5); label(0, 0, 'ESPADA\nANCESTRAL', F14, fill='black')
    label(38, 44, 'PATIO CENTRAL 140 x 120 (y 0)', F16, fill=(40, 30, 10))
    # spawn
    rect(-5, 5, -67, -57, hexc('#FFC84A')); label(38, -52, 'SPAWN (0,5,-66)\nhoje nasce olhando +Z', F14, fill='black')
    # via imperial + portao
    rect(-16, 16, 60, 140, hexc('#C9BB9E')); label(0, 100, 'VIA IMPERIAL\nlanternas + estandartes', F14, fill='black')
    for z in (72, 92, 112, 132):
        for x in (-20, 20): d.ellipse([X(x) - 3, Z(z) - 3, X(x) + 3, Z(z) + 3], fill=hexc('#E0A83A'))
    rect(-46, 46, 140, 160, hexc('#8F846E'), hexc('#4A2E1E'), 2)
    rect(-11, 11, 140, 160, hexc('#2B2624')); rect(-29, -17, 140, 160, hexc('#2B2624')); rect(17, 29, 140, 160, hexc('#2B2624'))
    rect(-46, 46, 160, 180, hexc('#8F846E'))
    label(-100, 134, 'GRANDE PORTAO 92 x 20\nbase y 16, torre de 2 beirais\n(cumeeira ~y 42)', F14)
    label(100, 138, 'saida -> corredor Lobby_Area1\n(piso y 0 em z 178)', F14)
    # leste: ponte-lua + santuario
    rect(70, 100, -4, 4, hexc('#7A4B2A')); label(85, -10, 'PONTE-LUA', F14)
    rect(104, 146, -45, 45, hexc('#DCCDB0'), hexc('#8F846E'), 2); rect(104, 120, -6, 6, hexc('#C9BB9E'))
    rect(142, 146, -45, 45, hexc('#B8321E'))
    for z in (-32, -20, -6, 7, 19, 32): d.ellipse([X(124) - 6, Z(z) - 6, X(124) + 6, Z(z) + 6], fill=hexc('#2A6C6A'), outline=hexc('#E0A83A'))
    label(125, 56, 'SANTUARIO DOS PORTAIS\ngaleria aberta, piso y 6.4\n(6 portais mantidos)', F14)
    # oeste: jardim, loja, treino
    rect(-104, -70, -4, 4, hexc('#C9BB9E')); rect(-104, -84, -3, 3, hexc('#A89B84'))
    rect(-130, -104, -24, 16, hexc('#DCCDB0'), hexc('#8F846E'), 2); rect(-130, -120, -16, 16, hexc('#B8321E'))
    d.ellipse([X(-120), Z(-4), X(-112), Z(4)], fill=hexc('#FFC84A')); label(-117, -30, 'CASA DO INTENDENTE\n(Loja de Mochilas, piso y 8)\nMailBox', F14)
    rect(-100, -72, 20, 56, hexc('#C9B27A')); label(-86, 38, 'PATIO DE TREINO\npostes, bonecos,\nestantes de armas', F14, fill='black')
    for (x, z) in [(-80, -40), (-96, -54), (-84, 12), (-100, 70), (-80, 90), (-96, 120), (108, 62), (108, 92), (110, 122), (112, -60), (60, -160), (-60, -160), (130, -70)]:
        d.ellipse([X(x) - 9, Z(z) - 9, X(x) + 9, Z(z) + 9], fill=hexc('#3E6B3A'))
    for (x, z) in [(-76, 66), (-110, 100), (104, 40), (-48, -156)]:
        d.ellipse([X(x) - 8, Z(z) - 8, X(x) + 8, Z(z) + 8], fill=hexc('#C4432B'))
    label(-118, 60, 'JARDIM OESTE\npinheiros, bordos, rochas', F14)
    # fluxo
    def arrow(p0, p1, col=(255, 255, 255)):
        d.line([X(p0[0]), Z(p0[1]), X(p1[0]), Z(p1[1])], fill=col, width=4)
        ang = math.atan2(Z(p1[1]) - Z(p0[1]), X(p1[0]) - X(p0[0]))
        for s in (-1, 1):
            d.line([X(p1[0]), Z(p1[1]), X(p1[0]) - 10 * math.cos(ang - s * .5) / S, Z(p1[1]) - 10 * math.sin(ang - s * .5) / S], fill=col, width=4)
    arrow((0, -56), (0, -100)); arrow((0, -50), (0, -26)); arrow((0, 26), (0, 138)); arrow((0, 160), (0, 176))
    arrow((26, 0), (68, 0)); arrow((-26, 0), (-68, 0))
    # legenda
    lx, ly = 20, 60
    leg = ['FLUXO: spawn -> (subir) Forja/Ignis 54 studs | spawn -> Espada 62 | Espada -> Portao 150 | Espada -> Portais 110 (ponte) | Espada -> Loja 116',
           'NIVEIS: patio 0 | terraco da Forja 10 | galeria dos portais 6.4 | loja 8 | portao base 16, cumeeira ~42 | Forja cumeeira 46, Torre do Fogo 66 | espada 33 | penhascos 48-84',
           'MARCOS (visiveis de qualquer ponto): telhado dourado + Torre do Fogo (-Z) | Espada Ancestral (centro) | torre do Grande Portao (+Z)']
    d.rectangle([0, H - 76, W, H], fill=BG)
    for i, t in enumerate(leg): d.text((lx, H - 70 + i * 22), t, fill=(225, 225, 225), font=F14)
    d.rectangle([0, 0, W, 44], fill=BG)
    d.text((20, 10), 'B2 - Planta do lobby "Seita da Forja Celeste" (coordenadas Roblox; -Z em cima = Forja, +Z embaixo = saida para as areas)', fill='white', font=F22)
    im.save(os.path.join(OUT, 'B2_planta.png')); print('B2', im.size)

if __name__ == '__main__':
    prancha_paleta(); prancha_planta()
