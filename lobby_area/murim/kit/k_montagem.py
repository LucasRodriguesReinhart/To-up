# k_montagem.py - monta o LOBBY INTEIRO com o kit, seguindo a planta B2 aprovada.
# Coordenadas em BLENDER; a conversao para Roblox e (x,y,z) -> (-x, z, y), feita no montar_lobby.lua.
# Equivalencia com a planta B2 (que esta em Roblox): x_blender = -X_roblox, y_blender = Z_roblox, z_blender = Y_roblox.
#   patio central   x -70..70,  y -60..60,  z 0          Forja      x -36..36, y -146..-108, z 10
#   escadaria       y -92..-60, largura 46               terraco    x -62..62, y -152..-90
#   Via Imperial    y 60..140,  x -16..16                Portao     y 140..160, x -46..46
#   Lago de Jade    x -100..-70, y -70..130              Santuario  x -146..-104, y -45..45, z 6.4
#   Loja            x 104..130, y -24..16, z 8           Treino     x 72..100, y 20..56
import bpy, bmesh, math, json, os
from mathutils import Vector
from k_core import *
import k_pedra, k_madeira, k_dougong, k_telhado, k_props, k_veg, k_kit2, k_lobby, k_jardim, k_portal
import k_relva, k_materiais
# as tintas da relva entram em k_materiais.PD AGORA, no import: run_bg chama build_paints() depois
# de importar k_montagem e antes de build_lobby(), entao registrar aqui e o unico ponto que pega
# os dois lados. Registrar dentro de build_lobby() seria tarde - os shaders ja estariam prontos.
k_relva.registrar_relva(k_materiais)
from k_pavilhao import Kit, mirror_mesh

MOD = k_pedra.MOD; VAO = k_madeira.VAO; HCOL = k_madeira.H_COL
PLACE = []

class Montagem(Kit):
    """Kit + registro de posicoes em coordenadas do lobby."""
    def put(s, key, colname, loc, rot=0.0, scale=(1, 1, 1)):
        m = s.m[key]
        if not m['usado']:
            o = m; m['usado'] = True; o.location = loc; o.rotation_euler = (0, 0, math.radians(rot)); o.scale = scale
            if o.name not in col(colname).objects:
                for c in list(o.users_collection): c.objects.unlink(o)
                col(colname).objects.link(o)
        else:
            s.n[key] += 1; o = instance(m, '%s.%03d' % (m.name, s.n[key]), colname, loc, rot, scale)
        PLACE.append(dict(mesh=m.data.name, pos=[round(v, 3) for v in loc], rot=round(rot, 2), scale=[round(v, 4) for v in scale]))
        return o

# ---------------------------------------------------------------- helpers de composicao
# REGISTRO DE COTAS. A geometria anota aqui cada terraco e cada escada que constroi, e o
# gerar_lobby.py le este registro para emitir a colisao. Antes as mesmas alturas eram digitadas nos
# dois arquivos como literais independentes (9.98 / 6.38 / 7.98), e qualquer mudanca de cota na
# geometria deixava a colisao para tras - jogador flutuando ou afundado no terreno.
COTAS = {'terracos': [], 'escadas': []}

def _reg_terraco(nome, x0, x1, y0, y1, z_topo):
    COTAS['terracos'].append({'nome': nome, 'x0': x0, 'x1': x1, 'y0': y0, 'y1': y1, 'z': z_topo})

def _reg_escada(nome, eixo, a0, a1, b0, b1, z_topo, n, tread, sentido):
    COTAS['escadas'].append({'nome': nome, 'eixo': eixo, 'a0': a0, 'a1': a1, 'b0': b0, 'b1': b1,
                             'z': z_topo, 'n': n, 'tread': tread, 'sentido': sentido})

def terraco(K, C, x0, x1, y0, y1, z, escadas=()):
    """base sumeru + piso modular + balaustrada, com vaos onde houver escada. escadas = ((lado,'S'|'N'|'E'|'W', centro, largura),)"""
    nx = max(1, round((x1 - x0) / MOD)); ny = max(1, round((y1 - y0) / MOD))
    sx = (x1 - x0) / nx / MOD; sy = (y1 - y0) / ny / MOD
    def vao(lado, c):
        for (l, cen, lar) in escadas:
            if l == lado and abs(c - cen) < lar / 2: return True
        return False
    for i in range(nx):
        cx = x0 + (i + .5) * (x1 - x0) / nx
        if not vao('S', cx): K.put('sumeru', C, (x0 + i * (x1 - x0) / nx, y0, z), 0, (sx, 1, 1))
        if not vao('N', cx): K.put('sumeru', C, (x0 + (i + 1) * (x1 - x0) / nx, y1, z), 180, (sx, 1, 1))
    for j in range(ny):
        cy = y0 + (j + .5) * (y1 - y0) / ny
        if not vao('E', cy): K.put('sumeru', C, (x1, y0 + j * (y1 - y0) / ny, z), 90, (sy, 1, 1))
        if not vao('W', cy): K.put('sumeru', C, (x0, y0 + (j + 1) * (y1 - y0) / ny, z), 270, (sy, 1, 1))
    for ax in (x0 - .2, x1 + .2):
        for ay in (y0 - .2, y1 + .2): K.put('canto', C, (ax, ay, z), 0)
    # PODIO: o embasamento sumeru tem 3.98 de altura e era posto em z, entao abaixo de z ficava o VAZIO -
    # o terraco aparecia flutuando com o chao visivel por baixo (2.4 no Santuario, 4.0 na Loja, 6.0 na
    # Forja). Aqui vai a alvenaria que faltava, do chao ate o pe do sumeru, com uma faixa de cordao.
    if z > 0.05:
        pod = Builder('PODIO_%d_%d' % (round(x0), round(y0)), 61)
        pod.add(t_box(x0 - .1, x1 + .1, y0 - .1, y1 + .1, -.3, z - .45, bev=.22, seg=2), 'pedra', .38)
        pod.add(t_box(x0 - .45, x1 + .45, y0 - .45, y1 + .45, z - .45, z + .02, bev=.14, seg=2), 'piso', .55)
        for k in range(1, max(2, int(z / 1.9))):                       # cordoes horizontais na alvenaria
            zz = -.3 + k * (z - .15) / max(2, int(z / 1.9))
            pod.add(t_box(x0 - .28, x1 + .28, y0 - .28, y1 + .28, zz - .09, zz + .09, bev=.05), 'junta', .3 + .1 * k)
        pod.finish(C)
    H = z + 3.98
    for i in range(nx):
        for j in range(ny): K.put('piso', C, (x0 + i * (x1 - x0) / nx, y0 + j * (y1 - y0) / ny, H), 0, (sx, sy, 1))
    bx0, bx1, by0, by1 = x0 + .8, x1 - .8, y0 + .8, y1 - .8
    nbx = max(1, round((bx1 - bx0) / MOD)); nby = max(1, round((by1 - by0) / MOD))
    kx = (bx1 - bx0) / nbx / MOD; ky = (by1 - by0) / nby / MOD
    for i in range(nbx):
        cx = bx0 + (i + .5) * (bx1 - bx0) / nbx
        if not vao('S', cx): K.put('bal', C, (bx0 + i * (bx1 - bx0) / nbx, by0, H), 0, (kx, 1, 1))
        if not vao('N', cx): K.put('bal', C, (bx1 - i * (bx1 - bx0) / nbx, by1, H), 180, (kx, 1, 1))
    for j in range(nby):
        cy = by0 + (j + .5) * (by1 - by0) / nby
        if not vao('E', cy): K.put('bal', C, (bx1, by0 + j * (by1 - by0) / nby, H), 90, (ky, 1, 1))
        if not vao('W', cy): K.put('bal', C, (bx0, by1 - j * (by1 - by0) / nby, H), 270, (ky, 1, 1))
    nuc = Builder('NUC_%d_%d' % (int(x0), int(y0))); nuc.add(t_box(x0, x1, y0, y1, z, H - .45), 'junta', .3); nuc.finish(C)
    _reg_terraco('t_%s_%s' % (int(x0), int(y0)), x0, x1, y0, y1, H)
    return H

def escadaria(K, C, cx, y_topo, z_topo, n, largura, tread=1.9):
    """lance que desce do terraco (em y_topo) para o PATIO, em +Y. Descer em -Y punha a escada dentro do proprio
    terraco e deixava uma parede de 10 studs no eixo de entrada."""
    rise = z_topo / n
    _reg_escada('e_%d' % int(y_topo), 'Y', cx - largura / 2, cx + largura / 2, y_topo, y_topo, z_topo, n, tread, 1)
    d = Builder('ESCADA_%d' % int(y_topo), 46)
    for i in range(1, n + 1):
        z = z_topo - rise * i
        if z < .01: break
        y0 = y_topo + tread * (i - 1); y1 = y0 + tread
        d.add(t_box(cx - largura / 2, cx + largura / 2, y0, y1 + .16, 0, z, bev=.09, seg=2), 'pedra')
    L = tread * n
    for sx in (-1, 1):
        x0 = cx + sx * largura / 2; x1 = x0 + sx * 1.6
        poly = [(-.3, 0), (L + 1.9, 0), (L + 1.9, .75), (L + .9, .95), (0, z_topo + .42), (-.3, z_topo + .42)]
        d.add(t_prism([(y_topo + a2, c) for a2, c in poly], 'X', min(x0, x1), max(x0, x1), bev=.12, seg=3), 'pedra', .6)
    d.finish(C)

def escadaria_x(K, C, cy, x_topo, z_topo, n, largura, sentido, tread=1.7):
    """lance que desce do terraco no eixo X. A Loja e o Santuario tinham degraus de COLISAO gerados no
    gerar_lobby.py mas NENHUMA malha: o jogador subia no ar. Estas medidas copiam exatamente as caixas
    de colisao (degrau_loja e degrau_sant), senao a geometria e o que se pisa deixam de casar."""
    rise = z_topo / n
    _reg_escada('ex_%d' % int(x_topo), 'X', x_topo, x_topo, cy - largura / 2, cy + largura / 2, z_topo, n, tread, sentido)
    d = Builder('ESCADA_X_%d' % int(x_topo), 46)
    for i in range(1, n + 1):
        z = z_topo - rise * (i - 1)
        if z < .01: break
        x0 = x_topo + sentido * tread * (i - 1)
        x1 = x0 + sentido * tread
        d.add(t_box(min(x0, x1) - .08, max(x0, x1) + .08, cy - largura / 2, cy + largura / 2, 0, z, bev=.09, seg=2), 'pedra')
    L = tread * n
    for sy in (-1, 1):                                                   # parapeito inclinado dos dois lados
        y0 = cy + sy * largura / 2; y1 = y0 + sy * 1.6
        poly = [(0, 0), (sentido * (L + 1.9), 0), (sentido * (L + 1.9), .75),
                (sentido * (L + .9), .95), (0, z_topo + .42)]
        poly = [(x_topo + u, v) for u, v in poly]
        if sentido < 0: poly = poly[::-1]
        d.add(t_prism(poly, 'Y', min(y0, y1), max(y0, y1), bev=.12, seg=3), 'pedra', .6)
    d.finish(C)

def colunata(K, C, xs, y, z, alt=1.0, tipo='dg', parede=None, rot=0):
    """fila de colunas com base, arquitrave, prancha e dougong; `parede` opcional preenche os vaos."""
    for x in xs:
        K.put('colbase', C, (x, y, z), rot); K.put('coluna', C, (x, y, z), rot, (1, 1, alt))
        K.put(tipo, C, (x, y, z + HCOL * alt + .5), rot)
    for a, b in zip(xs, xs[1:]):
        m = (a + b) / 2; k = (b - a) / VAO
        K.put('arq', C, (m, y, z + HCOL * (alt - 1)), rot, (k, 1, 1)); K.put('prancha', C, (m, y, z + HCOL * (alt - 1)), rot, (k, 1, 1))
        K.put(tipo, C, (m, y, z + HCOL * alt + .5), rot)
        if parede: K.put(parede, C, (m, y, z + HCOL * (alt - 1)), rot, (k, 1, alt))

# ---------------------------------------------------------------- LOBBY
# ordem dos SEIS pads do Santuario, de y = -32.5 ate +32.5 (medido no Studio: Disco.AreaId de cada Portal<n>)
TEMAS_PORTAL = ('serio', 'mare', 'sombra', 'nichirin', 'ki', 'chakra')

# CANTEIROS do lobby: os bolsoes onde o verde pode existir. Fica em escopo de modulo porque DUAS
# secoes precisam dele e elas rodam em ordens diferentes - a vegetacao planta dentro deles, e a secao
# do chao constroi o meio-fio e decide onde nao calcar.
CANTEIRO = (
    (-166, -112, -186, -104), (112, 166, -186, -104),        # quinas da frente
    (-166, -112, 60, 140), (112, 166, 58, 140),              # quinas do fundo
    (-60, -24, -196, -160), (24, 60, -196, -160),            # ladeando a via do portao
    (-166, -114, -60, 30), (116, 166, -96, -58),             # faixas laterais
    (-58, -22, 74, 138), (22, 58, 74, 138),                  # entre o patio e o portao
    (-100, -68, 140, 186), (68, 100, 140, 186),              # fundo
)
def em_canteiro(x, y):
    for (x0, x1, y0, y1) in CANTEIRO:
        if x0 <= x <= x1 and y0 <= y <= y1: return True
    return False

def _frange(a, b, passo):
    v = a
    while v <= b + 1e-6:
        yield v
        v += passo

def build_lobby():
    for c in ('LOB_FORJA', 'LOB_PATIO', 'LOB_PORTAO', 'LOB_LESTE', 'LOB_OESTE', 'LOB_VEG', 'LOB_PROPS', 'LOB_CHAO'): clear_col(c)
    del PLACE[:]
    K = Montagem()
    # ---- masters: kit do Gate 1 + kit 2 + pecas do lobby
    for key, fn, C in (
        ('sumeru', k_pedra.sumeru_seg, 'LOB_PATIO'), ('canto', k_pedra.sumeru_canto, 'LOB_PATIO'), ('piso', k_pedra.piso_mod, 'LOB_PATIO'),
        ('bal', k_pedra.bal_seg, 'LOB_PATIO'), ('colbase', k_pedra.tambor_coluna, 'LOB_PATIO'), ('jard', k_pedra.jardineira, 'LOB_PATIO'),
        ('coluna', k_madeira.coluna, 'LOB_FORJA'), ('arq', k_madeira.arquitrave, 'LOB_FORJA'), ('prancha', k_madeira.prancha, 'LOB_FORJA'),
        ('janela', k_madeira.vao_janela, 'LOB_FORJA'), ('porta', k_madeira.vao_porta, 'LOB_FORJA'), ('parede', k_madeira.vao_parede, 'LOB_FORJA'),
        ('placa', k_madeira.placa, 'LOB_FORJA'), ('forro', k_props.forro_alpendre, 'LOB_FORJA'), ('tabua', k_props.tabua_dougong, 'LOB_FORJA'),
        ('terca', k_props.terca, 'LOB_FORJA'), ('dg', k_dougong.principal, 'LOB_FORJA'), ('dgc', k_dougong.canto, 'LOB_FORJA'),
        ('dg_int', k_dougong.intermediario, 'LOB_FORJA'), ('dg_sim', k_dougong.simples, 'LOB_FORJA'),
        ('lant', k_props.lanterna_palacio, 'LOB_PROPS'), ('lantV', k_props.lanterna_vermelha, 'LOB_PROPS'),
        ('pinA', lambda: k_veg.pinheiro(1, 'KIT_pinheiro_a', 1), 'LOB_VEG'), ('pinB', lambda: k_veg.pinheiro(2, 'KIT_pinheiro_b', -1), 'LOB_VEG'),
        ('arbA', lambda: k_veg.arbusto(1, 'KIT_arbusto_a'), 'LOB_VEG'), ('arbB', lambda: k_veg.arbusto(2, 'KIT_arbusto_b'), 'LOB_VEG'),
        ('tufo', k_veg.tufo, 'LOB_VEG'),
        ('estand', k_kit2.estandarte, 'LOB_PROPS'), ('sup_esp', k_kit2.suporte_espada, 'LOB_PROPS'), ('vaso', k_kit2.vaso, 'LOB_PROPS'),
        ('muro', k_kit2.muro_seg, 'LOB_PORTAO'), ('mpilar', k_kit2.muro_pilar, 'LOB_PORTAO'), ('tel_portao', k_kit2.telhado_portao, 'LOB_PORTAO'),
        ('muroA', lambda: k_kit2.muro_seg(9.0, 13.5), 'LOB_PORTAO'), ('mtorre', k_kit2.muro_torre, 'LOB_PORTAO'),
        ('penha1', lambda: k_lobby.penhasco(1), 'LOB_CHAO'), ('penha2', lambda: k_lobby.penhasco(2), 'LOB_CHAO'),
        ('penha3', lambda: k_lobby.penhasco(3), 'LOB_CHAO'), ('nuvem', k_lobby.banco_nuvem, 'LOB_CHAO'),
        ('queda', k_lobby.cascata, 'LOB_CHAO'),   # NAO usar 'torre': ja e a Torre do Fogo da Forja
        ('torre', k_lobby.torre_fogo, 'LOB_FORJA'), ('espada', lambda: k_lobby.minha_picareta(40.0), 'LOB_PATIO'), ('ped_esp', lambda: k_lobby.pedestal_espada(15.0, 8.4), 'LOB_PATIO'),
        ('fornalha', k_lobby.fornalha, 'LOB_FORJA'), ('bigorna', k_lobby.bigorna, 'LOB_FORJA'), ('fole', k_lobby.fole, 'LOB_FORJA'),
        ('calha', k_lobby.calha_tempera, 'LOB_FORJA'), ('laminas', k_lobby.altar_laminas, 'LOB_FORJA'), ('braseiro', k_lobby.braseiro, 'LOB_PROPS'),
        ('leaoA', lambda: k_lobby.leao(1), 'LOB_PROPS'), ('leaoB', lambda: k_lobby.leao(-1), 'LOB_PROPS'),
        ('ponte', k_lobby.ponte_lua, 'LOB_LESTE'), ('rocha1', lambda: k_lobby.rocha(1, 3.2), 'LOB_VEG'), ('rocha2', lambda: k_lobby.rocha(2, 2.2), 'LOB_VEG'),
        ('bambu', lambda: k_lobby.bambu(1), 'LOB_VEG'), ('bordo', lambda: k_lobby.bordo(1), 'LOB_VEG'),
        ('poste_t', k_lobby.poste_treino, 'LOB_OESTE'), ('boneco', k_lobby.boneco_treino, 'LOB_OESTE'), ('estante', k_lobby.estante_armas, 'LOB_OESTE'),
        ('peonia', lambda: k_jardim.peonia(1), 'LOB_VEG'), ('peonia2', lambda: k_jardim.peonia(2, 'JAR_peonia_b'), 'LOB_VEG'),
        ('crisa', lambda: k_jardim.crisantemo(1), 'LOB_VEG'), ('crisa2', lambda: k_jardim.crisantemo(2, 'JAR_crisantemo_b'), 'LOB_VEG'),
        ('lotus', lambda: k_jardim.lotus(1), 'LOB_VEG'), ('lotus2', lambda: k_jardim.lotus(2, 'JAR_lotus_b'), 'LOB_VEG'),
        ('ameixa', lambda: k_jardim.ameixeira(1), 'LOB_VEG'), ('ameixa2', lambda: k_jardim.ameixeira(2, 'JAR_ameixeira_b'), 'LOB_VEG'),
        ('canteiro', lambda: k_jardim.canteiro_flores(1), 'LOB_VEG'), ('canteiro2', lambda: k_jardim.canteiro_flores(2, 'JAR_canteiro_b', 5.0, 3.0), 'LOB_VEG'),
        ('grama', lambda: k_jardim.moita_grama(1), 'LOB_VEG'), ('grama2', lambda: k_jardim.moita_grama(2, 'JAR_grama_b'), 'LOB_VEG'),
        ('lant_pedra', k_jardim.lanterna_pedra, 'LOB_PROPS'), ('poco', k_jardim.poco, 'LOB_OESTE'),
        ('barril', k_jardim.barril, 'LOB_PROPS'), ('cesto', k_jardim.cesto, 'LOB_PROPS'), ('banco', k_jardim.banco, 'LOB_PROPS'),
        ('caixas', k_jardim.caixas, 'LOB_PROPS'), ('telhas_p', k_jardim.telhas_pilha, 'LOB_PROPS'),
        ('varal', k_jardim.varal, 'LOB_OESTE'), ('placa_loja', k_jardim.placa_loja, 'LOB_OESTE'), ('carroca', k_jardim.carroca, 'LOB_OESTE'),
    ) + tuple(                                     # um portal POR AREA, com a marca do anime e a cor do Config.Temas
        m for t in TEMAS_PORTAL for m in (
            ('por_mold_' + t, lambda t=t: k_portal.portal_moldura(t), 'LOB_LESTE'),
            ('por_vort_' + t, lambda t=t: k_portal.portal_vortice(t), 'LOB_LESTE'),
            ('por_base_' + t, lambda t=t: k_portal.portal_base(t), 'LOB_LESTE'),
            ('por_frag_' + t, lambda t=t: k_portal.portal_fragmento(1, t), 'LOB_LESTE'),
        )
    ):
        K.master(key, fn, C)
    # telhados proprios (cada um e uma malha; os hero assets merecem o seu)
    RF = k_telhado.Roof(EX=42.0, EY=25.0, RS=13.0, H=15.0, ZE=0.0, LIFT=3.6, SL=9.0, OUT=1.4, PER=2.15, LT=3.4)          # Forja, beiral inferior
    RF2 = k_telhado.Roof(EX=34.0, EY=19.0, RS=11.0, H=13.0, ZE=0.0, LIFT=3.2, SL=8.0, OUT=1.3, PER=1.8, LT=2.9)         # Forja, beiral superior
    RG = k_telhado.Roof(EX=26.0, EY=13.0, RS=8.0, H=10.0, ZE=0.0, LIFT=2.8, SL=7.0, OUT=1.2, PER=1.6, LT=2.6)           # Portao e Loja
    for nome, R in (('F1', RF), ('F2', RF2), ('G', RG)):
        for which, w in (('front', 'frente'), ('side', 'lado')):
            # O BRIEF pediu telhados VERDE-JADE com dourado, e o Salao da Forja era o unico em ouro
            # macico ('telhaImp'). Vai para 'jade' (3E7D6E), que e mais claro que a 'telha' (2E5A4C)
            # dos outros telhados: continua sendo o edificio que puxa o olho, mas por ser o verde
            # mais aceso da cena, e nao por ser de outra familia de cor. O dourado fica nas
            # cumeeiras, nos dragoes de beiral e nos remates, que e onde a referencia o poe.
            K.master('ag_%s_%s' % (nome, w), lambda R=R, which=which, nome=nome, w=w: k_telhado.agua(R, which, 'TEL_%s_agua_%s' % (nome, w), 'jade' if nome.startswith('F') else 'telha'), 'LOB_FORJA')
            K.master('be_%s_%s' % (nome, w), lambda R=R, which=which, nome=nome, w=w: k_telhado.beiral(R, which, 'TEL_%s_beiral_%s' % (nome, w)), 'LOB_FORJA')
        Be, anc = k_telhado.espigao(R, 'TEL_%s_espigao' % nome); K.master('esp_%s' % nome, Be, 'LOB_FORJA')
        Bv, tip, td = k_telhado.viga_canto(R, 'TEL_%s_viga_canto' % nome); K.master('vc_%s' % nome, Bv, 'LOB_FORJA')
        Bc, zc = k_telhado.cumeeira(R, 'TEL_%s_cumeeira' % nome); K.master('cume_%s' % nome, Bc, 'LOB_FORJA')
        K.m['_anc_' + nome] = anc; K.m['_zc_' + nome] = zc
        for key in ('esp_%s' % nome, 'vc_%s' % nome):
            # o espelho entra como master NAO usado: assim o primeiro K.put o posiciona. Marcando usado=True ele ficava
            # parado na origem da cena - que aqui e o centro do patio (tres telhados soltos no meio da praca).
            mm = mirror_mesh(K.m[key], K.m[key].name + '_esp', 'LOB_FORJA', axis=1)
            K.m[key + '_m'] = mm; K.n[key + '_m'] = 0; mm['usado'] = False
    K.master('chiwen', k_props.chiwen, 'LOB_FORJA')
    K.master('imortal', k_props.imortal, 'LOB_FORJA'); K.master('chuishou', k_props.chuishou, 'LOB_FORJA')
    for i in range(3): K.master('besta%d' % i, lambda i=i: k_props.besta(i), 'LOB_FORJA')

    def telhado(nome, cx, cy, z, C):
        """poe um telhado completo (4 aguas + beirais + espigoes + vigas de canto + cumeeira + bestas + chiwen)."""
        for w in ('frente', 'lado'):
            for k in ('ag_%s_%s' % (nome, w), 'be_%s_%s' % (nome, w)):
                K.put(k, C, (cx, cy, z), 0); K.put(k, C, (cx, cy, z), 180)
        for k in ('esp_%s' % nome, 'vc_%s' % nome):
            K.put(k, C, (cx, cy, z), 0); K.put(k, C, (cx, cy, z), 180)
            K.put(k + '_m', C, (cx, cy, z), 0); K.put(k + '_m', C, (cx, cy, z), 180)
        K.put('cume_%s' % nome, C, (cx, cy, z), 0)
        zc = K.m['_zc_' + nome]; R = {'F1': RF, 'F2': RF2, 'G': RG}[nome]
        Lr = R.EX - R.RS
        K.put('chiwen', C, (cx + Lr - .6, cy, z + zc), 0); K.put('chiwen', C, (cx - Lr + .6, cy, z + zc), 180)
        ordem = ['imortal', 'besta0', 'besta1', 'besta2', 'chuishou']
        for (sx, sy) in ((1, 1), (-1, -1), (1, -1), (-1, 1)):
            for key, (p, t) in zip(ordem, K.m['_anc_' + nome]):
                if (sx, sy) == (1, 1): q, tt = Vector(p), Vector((t.x, t.y, 0))
                elif (sx, sy) == (-1, -1): q, tt = Vector((-p.x, -p.y, p.z)), Vector((-t.x, -t.y, 0))
                elif (sx, sy) == (1, -1): q, tt = Vector((p.x, -p.y, p.z)), Vector((t.x, -t.y, 0))
                else: q, tt = Vector((-p.x, p.y, p.z)), Vector((-t.x, t.y, 0))
                ang = math.degrees(math.atan2(tt.y, tt.x)) + 90
                K.put(key, C, (cx + q.x, cy + q.y, z + q.z + 1.1), ang)

    # ================================================================ SALAO DA FORJA (-Y)
    C = 'LOB_FORJA'
    ZT = terraco(K, C, -62, 62, -152, -90, 6.0, escadas=(('N', 0, 46),))          # vao no lado do patio (y1 = -90)
    Z = ZT
    xs = [-36, -27, -18, -9, 0, 9, 18, 27, 36]
    colunata(K, C, xs, -108, Z, 1.25, 'dg', None)                                  # colunata do alpendre
    colunata(K, C, xs, -122, Z, 1.25, 'dg', None)                                  # linha da parede
    for y in (-134, -146):
        colunata(K, C, [-36, -18, 0, 18, 36], y, Z, 1.25, 'dg', None)
    for x in (-36, 36):
        for y in (-134, -146): K.put('coluna', C, (x, y, Z), 0, (1, 1, 1.25))
    ZC = Z + HCOL * 1.25 + .5                                                      # topo da prancha
    for x in (-27, -9, 9, 27): K.put('parede', C, (x, -122, Z), 180, (1, 1, 1.25))
    K.put('porta', C, (-18, -122, Z), 180, (1, 1, 1.25)); K.put('porta', C, (18, -122, Z), 180, (1, 1, 1.25))
    for x in (-36, 36):
        for y in (-116, -128, -140): K.put('parede', C, (x, y, Z), 90 if x > 0 else 270, (1, 1, 1.25))
    for x in (-27, -9, 9, 27): K.put('parede', C, (x, -152 + 6, Z), 0, (1, 1, 1.25))
    for x in xs: K.put('forro', C, (x, -115, ZC + k_dougong.Z_TOP), 0)
    telhado('F1', 0, -125, ZC + k_dougong.Z_TOP + 1.0, C)
    # ANDAR DE CLARABOIA. Entre os dois beirais nao havia NADA: olhando para cima dentro da Forja via-se
    # o ceu pelo vao inteiro. Num salao de beiral duplo esse andar e uma parede com janelas, e e ela que
    # sustenta o telhado de cima. A base fica em z=32.5, enterrada na agua do telhado inferior (que nesse
    # anel passa entre 34 e 44, calculado pela curva juzhe do k_telhado), para nao aparecer emenda.
    cl = Builder('FORJA_claraboia', 71)
    CX0, CX1, CY0, CY1 = -30.0, 30.0, -142.0, -112.0
    ZB, ZTopo = 32.5, 49.0
    for (a0, a1, b0, b1, eixo) in ((CX0, CX1, CY0 - .9, CY0 + .9, 'x'), (CX0, CX1, CY1 - .9, CY1 + .9, 'x'),
                                   (CX0 - .9, CX0 + .9, CY0, CY1, 'y'), (CX1 - .9, CX1 + .9, CY0, CY1, 'y')):
        cl.add(t_box(a0, a1, b0, b1, ZB, ZTopo - 3.0, bev=.16, seg=2), 'verm', .48)          # pano de parede
        cl.add(t_box(a0 - .3, a1 + .3, b0 - .3, b1 + .3, ZTopo - 3.0, ZTopo - 2.1, bev=.12), 'jadeE', .6)  # arquitrave
        cl.add(t_box(a0 - .45, a1 + .45, b0 - .45, b1 + .45, ZTopo - 2.1, ZTopo, bev=.14, seg=2), 'mad', .4)
        n = max(2, int(((a1 - a0) if eixo == 'x' else (b1 - b0)) / 6.0))                     # fiada de janelas
        for i in range(n):
            t = (i + .5) / n
            if eixo == 'x':
                cx = a0 + (a1 - a0) * t
                cl.add(t_box(cx - 1.9, cx + 1.9, b0 - .22, b1 + .22, ZTopo - 8.6, ZTopo - 3.4, bev=.10), 'madM', .5)
                cl.add(t_box(cx - 1.5, cx + 1.5, b0 - .34, b1 + .34, ZTopo - 8.2, ZTopo - 3.8), 'jade', .55)
            else:
                cy = b0 + (b1 - b0) * t
                cl.add(t_box(a0 - .22, a1 + .22, cy - 1.9, cy + 1.9, ZTopo - 8.6, ZTopo - 3.4, bev=.10), 'madM', .5)
                cl.add(t_box(a0 - .34, a1 + .34, cy - 1.5, cy + 1.5, ZTopo - 8.2, ZTopo - 3.8), 'jade', .55)
    for sx in (CX0, CX1):                                                                     # pilares de canto
        for sy in (CY0, CY1):
            cl.add(t_box(sx - 1.3, sx + 1.3, sy - 1.3, sy + 1.3, ZB, ZTopo - 1.9, bev=.14, seg=2), 'verm', .62)
    cl.finish(C)
    telhado('F2', 0, -127, ZC + k_dougong.Z_TOP + 1.0 + 17.0, C)
    K.put('placa', C, (0, -105.5, ZC + 2.4), 0)
    K.put('torre', C, (0, -143, Z))
    # A FORJA VEIO PARA A FRENTE. Ela estava no fundo do salao (y -146 a -128), atras da fachada que fica
    # em y=-122: o jogador entrava num interior escuro para achar o Ignis. Agora o conjunto ocupa o
    # alpendre (y -118 a -98), na frente da parede, de cara para a escadaria - e o ponto que o jogador
    # ve assim que sobe, e a forja passa a ser cenario vivo em vez de movel escondido.
    K.put('fornalha', C, (0, -116, Z), 180)
    K.put('bigorna', C, (-11, -104, Z)); K.put('fole', C, (15, -112, Z), 90)
    K.put('calha', C, (11, -102, Z), 90); K.put('laminas', C, (-26, -110, Z), 90)
    for sx in (-1, 1):
        K.put('braseiro', C, (sx * 16, -100, Z)); K.put('lant', C, (sx * 18, -108, Z + k_madeira.Z_ARQ * 1.25), 0, (.9, .9, .9))
        K.put('estand', C, (sx * 50, -96, Z), 0); K.put('leaoA' if sx > 0 else 'leaoB', C, (sx * 14, -88, 0), 0)
    # FILEIRAS FORMAIS DE ESTANDARTE ladeando o eixo. E o elemento que mais define o patio na
    # referencia: duas alas simetricas de mastros altos, nao enfeite solto na beirada.
    for j in range(6):
        yy = -52 + j * 21
        for sx in (-1, 1):
            K.put('estand', 'LOB_PROPS', (sx * 46, yy, 0), 0)
            if j % 2 == 0:
                K.put('lant_pedra', 'LOB_PROPS', (sx * 58, yy + 10, 0), 90 if sx > 0 else 270)
    # ================================================================ ESCADARIA + PATIO + ALTAR
    C = 'LOB_PATIO'
    escadaria(K, C, 0, -90, Z, 12, 46)
    # ---------------------------------------------------------------- PRACA HEXAGONAL
    # Era um retangulo de 140 x 120 lajeado em grade ortogonal: de cima lia como estacionamento, e as
    # seis direcoes de circulacao caiam nele sem nenhuma marcacao. RECORTAR o piso em hexagono nao
    # basta - piso hexagonal sem desenho le so como "praca de contorno irregular". Quem declara a
    # forma e o desenho: aneis hexagonais concentricos, seis raios do espelho aos vertices, e um marco
    # de pedra em cada vertice.
    #
    # Orientacao (coordenadas do BLENDER; o export espelha X):
    #   vertice +Y  -> de onde parte a via imperial ate o Grande Portao
    #   vertice -Y  -> de onde desce a escadaria do Salao da Forja do Ignis
    #   face   -X   -> fachada da galeria dos seis portais (fachada larga pede aresta reta na frente)
    #   face   +X   -> fachada da Loja, mesma razao
    #   4 vertices obliquos -> os jardins
    # Conferido contra as zonas DURO: t_sant em x -149..-101 e t_loja em +101..+133. Como o export
    # espelha X, no Roblox isso da PORTAIS A DIREITA e LOJA A ESQUERDA, que foi o pedido.
    HW, HL = 70.0, 74.0
    INC = (HL - 42.0) / HW                            # inclinacao das quatro faces obliquas
    def hexn(x, y):
        """norma hexagonal: 0 no centro, 1 exatamente na borda da praca. E dela que saem os aneis."""
        return max(abs(x) / HW, (abs(y) + INC * abs(x)) / HL)
    VERT = [(0, HL), (HW, 42.0), (HW, -42.0), (0, -HL), (-HW, -42.0), (-HW, 42.0)]
    ANG_V = [math.degrees(math.atan2(vy, vx)) % 360 for (vx, vy) in VERT]
    def no_raio(x, y):
        """o ladrilho cai num dos seis raios que ligam o espelho central aos vertices?"""
        r = math.hypot(x, y)
        if r < 25: return False
        a_ = math.degrees(math.atan2(y, x)) % 360
        larg = math.degrees(math.atan2(3.4, r))       # largura CONSTANTE de 3.4 studs, nao angular:
        for av in ANG_V:                              # raio de largura angular vira funil e nao le como caminho
            d_ = abs(a_ - av)
            if min(d_, 360 - d_) < larg: return True
        return False
    for f in range(6):                                # piso em 6 faixas (e nao ~900 lajes soltas)
        pp = Builder('PATIO_piso_%d' % f, 40 + f)
        for i in range(f * 5, min(30, (f + 1) * 5)):
            for j in range(32):
                x = -72 + i * 4.8; y = -78 + j * 4.9
                cx_, cy_ = x + 2.4, y + 2.45
                h_ = hexn(cx_, cy_)
                if h_ > 1.0 or h_ < .335: continue    # fora da praca, ou dentro do espelho central
                # a praca cresceu de 120 para 148 studs em Y, e o vertice norte, em (0, 74), passou a
                # entrar no corredor da via imperial, que comeca em y=60 e tem o topo 0.05 acima do
                # piso da praca. Duas superficies a 0.05 de distancia brigam pelo pixel de longe.
                # No trecho dela, a via manda.
                if abs(cx_) < 17.0 and cy_ > 58.0: continue
                anel = int(h_ * 7)                    # aneis hexagonais concentricos
                tinta = 'pedra' if no_raio(cx_, cy_) else ('junta' if anel % 3 == 2 else 'piso')
                pp.add(t_box(x + .10, x + 4.70, y + .10, y + 4.80, -.5, 0, bev=.05), tinta, .40 + .05 * (anel % 4))
        pp.finish(C)
    base_hex = Builder('PATIO_base', 47)              # manta de junta por baixo, no contorno do hexagono
    base_hex.add(t_prism([(vx * 1.012, vy * 1.012) for (vx, vy) in VERT], 'Z', -.66, -.42), 'junta', .25)
    base_hex.finish(C)
    # ESPELHO D'AGUA hexagonal GIRADO 30 graus em relacao a praca: assim as FACES do espelho ficam
    # voltadas para os VERTICES da praca, e cada uma das seis pontes cruza uma face de frente. Alinhado,
    # cada ponte cairia sobre um vertice do espelho, que e o encontro errado.
    HEX_E = [(23.0 * math.cos(math.radians(60 * k + 30)), 23.0 * math.sin(math.radians(60 * k + 30))) for k in range(6)]
    agua = Builder('PATIO_agua'); agua.add(t_prism(HEX_E, 'Z', -1.2, -.35), 'agua', .6); agua.finish(C)
    leito = Builder('PATIO_leito')
    leito.add(t_prism([(vx * 1.05, vy * 1.05) for (vx, vy) in HEX_E], 'Z', -1.6, -1.1), 'junta', .3); leito.finish(C)
    borda = Builder('PATIO_borda', 41)
    for k in range(6):                                                              # murete nas 6 faces do espelho
        a = math.radians(60 * k + 30)
        borda.add(xf(t_box(-13.6, 13.6, -.9, .9, -.7, .55, bev=.1), rot=(0, 0, 60 * k + 120),
                     loc=(24.2 * math.cos(a), 24.2 * math.sin(a), 0)), 'pedra', .45 + .06 * k)
    for k in range(6):                                                              # 6 pontes, uma por vertice
        a = math.radians(ANG_V[k])
        borda.add(xf(t_box(-4.6, 4.6, -5.2, 5.2, -1.4, .3, bev=.08), rot=(0, 0, ANG_V[k]),
                     loc=(19 * math.cos(a), 19 * math.sin(a), 0)), 'pedra', .5)
    # MEIO-FIO do hexagono, interrompido nos seis vertices - e por eles que se entra na praca.
    for k in range(6):
        (ax_, ay_) = VERT[k]; (bx_, by_) = VERT[(k + 1) % 6]
        comp = math.hypot(bx_ - ax_, by_ - ay_)
        ang = math.degrees(math.atan2(by_ - ay_, bx_ - ax_))
        mx, my = (ax_ + bx_) / 2, (ay_ + by_) / 2
        borda.add(xf(t_box(-comp / 2 + 8.0, comp / 2 - 8.0, -1.1, 1.1, -.62, .92, bev=.12),
                     rot=(0, 0, ang), loc=(mx, my, 0)), 'pedra', .52)
        borda.add(xf(t_box(-comp / 2 + 8.4, comp / 2 - 8.4, -.75, .75, -.62, 1.06, bev=.09),
                     rot=(0, 0, ang), loc=(mx, my, 0)), 'junta', .34)
    borda.finish(C)
    marcos = Builder('PATIO_marcos', 45)              # marco em cada vertice: e o que fixa a forma no olho
    for k, (vx, vy) in enumerate(VERT):
        f_ = 1 - 5.6 / math.hypot(vx, vy)
        ox, oy, rr = vx * f_, vy * f_, 2.1
        marcos.add(t_box(ox - rr, ox + rr, oy - rr, oy + rr, -.6, 4.4, bev=.16, seg=2), 'pedra', .58)
        marcos.add(t_box(ox - rr * .80, ox + rr * .80, oy - rr * .80, oy + rr * .80, 4.4, 5.3, bev=.14), 'junta', .4)
        marcos.add(xf(t_lathe([(0, 0), (rr * .66, .14), (rr * .52, 1.0), (0, 1.7)], 8), loc=(ox, oy, 5.3)), 'bronze', .62)
    marcos.finish(C)
    # o monumento cresceu de 17 para 40 studs: numa praca de 148 de vao, 17 lia como enfeite de
    # fonte. 40 poe a meia-lua acima da balaustrada e faz dele o centro que a referencia mostra.
    K.put('ped_esp', C, (0, 0, 0)); K.put('espada', C, (0, 0, 8.20))
    for k in range(4):
        a = math.radians(90 * k + 45)
        K.put('braseiro', 'LOB_PROPS', (12.5 * math.cos(a), 12.5 * math.sin(a), 6.0))
    # ================================================================ VIA IMPERIAL + GRANDE PORTAO (+Y)
    C = 'LOB_PORTAO'
    via = Builder('VIA_piso', 42)
    for j in range(16):
        y = 60 + j * 5
        via.add(t_box(-15.9, 15.9, y + .1, y + 4.9, -.45, .05, bev=.05), 'piso', .42 + .3 * (j % 3) / 3)
        via.add(t_box(-2.2, 2.2, y + .1, y + 4.9, -.4, .12, bev=.05), 'pedra', .6)     # caminho imperial no eixo
    via.finish(C)
    postes = Builder('VIA_postes', 43)
    for j, y in enumerate((72, 92, 112, 132)):
        for sx in (-1, 1):
            K.put('lantV', 'LOB_PROPS', (sx * 21, y, 8.2), 0, (1.15, 1.15, 1.15))
            postes.add(xf(t_lathe([(0, 0), (.6, 0), (.5, .5), (.34, 8.4), (0, 8.4)], 12), loc=(sx * 21, y, 0)), 'mad', .5)
            postes.add(t_box(min(sx * 21, sx * 20.5), max(sx * 21, sx * 20.5), y - .2, y + .2, 8.0, 8.4, bev=.05), 'mad', .55)
    postes.finish(C)
    for sx in (-1, 1):
        for y in (85, 120): K.put('estand', 'LOB_PROPS', (sx * 27, y, 0), 0)
        K.put('leaoA' if sx > 0 else 'leaoB', 'LOB_PROPS', (sx * 17, 134, 0), 180)
    # base da muralha do portao: 3 passagens
    mur = Builder('PORTAO_muralha', 44)
    for s in ((-46, -29), (-17, -11), (11, 17), (29, 46)):
        mur.add(t_box(s[0], s[1], 140, 160, 0, 16, bev=.2, seg=3), 'pedra', .45)
        mur.add(t_box(s[0] - .2, s[1] + .2, 139.8, 160.2, 0, 1.8, bev=.12), 'junta', .3)
    for a2, b2, z0 in ((-11, 11, 15), (-29, -17, 11), (17, 29, 11)):
        mur.add(t_box(a2, b2, 140, 160, z0, 16, bev=.14, seg=3), 'pedra', .5)
        mur.add(t_box(a2 + .3, b2 - .3, 139.7, 140.3, z0 - 1.1, z0 + .2, bev=.1), 'bronze', .55)
    mur.finish(C)
    pp = Builder('PORTAO_parapeito')
    for s in ((140, 141.6), (158.4, 160)): pp.add(t_box(-46, 46, s[0], s[1], 16, 18.4, bev=.12), 'pedra', .55)
    for x in range(-42, 43, 6): pp.add(t_box(x - 1.6, x + 1.6, 139.9, 141.7, 18.4, 20.2, bev=.1), 'pedra', .62)
    pp.finish(C)
    ZP = 18.4
    colunata(K, C, [-24, -12, 0, 12, 24], 144, ZP, .78, 'dg_int', None)
    colunata(K, C, [-24, -12, 0, 12, 24], 156, ZP, .78, 'dg_int', None)
    for x in (-24, -12, 0, 12, 24): K.put('parede', C, (x, 156, ZP), 180, (1, 1, .78))
    telhado('G', 0, 150, ZP + HCOL * .78 + .5 + k_dougong.Z1 + k_dougong.AH + 1.0, C)
    K.put('placa', C, (0, 142.6, ZP + 2.2), 0)
    for sx in (-1, 1):                                                              # muralha lateral
        for k in range(10):
            x = sx * (52 + k * 9)
            if abs(x) > 148: break
            K.put('muro', C, (x, 150, 0), 0)
        K.put('mpilar', C, (sx * 48, 150, 0), 0); K.put('mpilar', C, (sx * 148, 150, 0), 0)
    # ================================================================ LESTE: lago, ponte-lua, Santuario
    C = 'LOB_LESTE'
    # ---------------------------------------------------------------- LAGO DE CONTORNO TRABALHADO
    # O retangulo de 30 x 200 fazia duas coisas erradas: nao tinha nada da margem organica da
    # referencia, e invadia a escadaria do Santuario em 11.5 studs - quem descia dos portais descia
    # dentro da agua. O contorno abaixo recua justamente nesse ponto.
    # Borda OESTE (encosta no jardim) e borda LESTE (encosta no patio) sao listas de (y, x).
    # A escadaria do Santuario vem de x=-104 e desce PARA LESTE, morrendo em x=-88.5. Quem tem de
    # recuar e a borda OESTE do lago (a que encara a escada), nao a leste - na primeira tentativa eu
    # indentei a borda errada e a sobreposicao continuou igual. A oeste recua ate -84.5 na faixa da
    # escada, deixando 4 studs de terra firme na frente do ultimo degrau.
    OESTE = [(-72, -99), (-56, -101.5), (-40, -100), (-28, -95), (-19, -88),
             (-9, -84.5), (9, -84.5), (19, -88), (28, -95), (40, -100.5),
             (58, -99), (78, -101), (100, -99.5), (118, -97), (132, -98)]
    LESTE = [(-72, -71), (-54, -68.5), (-36, -72), (-18, -69), (0, -71.5),
             (18, -68.5), (34, -71.5), (56, -69), (78, -72), (102, -69.5), (120, -71), (132, -70)]
    pol = [(x, y) for (y, x) in OESTE] + [(x, y) for (y, x) in reversed(LESTE)]
    lago = Builder('LAGO_agua')
    lago.add(t_prism(pol, 'Z', -1.6, -.35), 'agua', .6); lago.finish(C)
    leito2 = Builder('LAGO_leito', 49)
    # leito em tres aneis: raso na margem, fundo no meio. Da profundidade visual sem custar nada.
    for k, (enc, z0, z1) in enumerate(((0.0, -3.2, -1.5), (3.2, -2.6, -1.5), (7.0, -2.0, -1.5))):
        pq = [((x + (1 if x > -85 else -1) * enc), y) for (x, y) in pol]
        leito2.add(t_prism(pq, 'Z', z0, z1), 'junta', .26 + .16 * k)
    import random as _rl
    rl = _rl.Random(5)
    for k in range(26):                                                             # pedras submersas junto as margens
        x = rl.choice([rl.uniform(-99, -94), rl.uniform(-76, -71)]); y = rl.uniform(-66, 126)
        leito2.add(t_blob(rl.uniform(.7, 1.6), (1.2, 1.0, .5), 1, lobes=4, lobe_amp=.3, seed=k, flat_bottom=-.3) and xf(t_blob(rl.uniform(.7, 1.6), (1.2, 1.0, .5), 1, lobes=4, lobe_amp=.3, seed=k, flat_bottom=-.3), loc=(x, y, -1.3)), 'pedra', rl.uniform(.35, .7))
    leito2.finish(C)
    mg = Builder('LAGO_margem', 48)
    # margem em BLOCOS irregulares meio submersos acompanhando o contorno, em vez de duas caixas
    # retas de 200 studs. E a pedra que quebra a linha da agua; sem ela a agua encosta na grama e
    # a transicao fica em corte seco.
    import random as _rmg; _mr = _rmg.Random(515)   # _r so e importado na secao de vegetacao, adiante
    for lado, borda in (('O', OESTE), ('L', LESTE)):
        for k in range(len(borda) - 1):
            (y0, x0), (y1, x1) = borda[k], borda[k + 1]
            passos = max(2, int(abs(y1 - y0) / 4.5))
            for i in range(passos):
                t = i / float(passos)
                yy = y0 + (y1 - y0) * t
                xx = x0 + (x1 - x0) * t
                fora = -1 if lado == 'O' else 1
                w = _mr.uniform(1.6, 3.4); h = _mr.uniform(2.0, 4.0)
                zz = _mr.uniform(-1.1, -.55)
                blo = t_prism([(-w, -h), (w * _mr.uniform(.7, 1.2), -h * .8), (w * .9, h),
                               (-w * _mr.uniform(.6, 1.1), h * .85)], 'Z', zz, zz + _mr.uniform(1.3, 2.3), bev=.16)
                xf(blo, rot=(0, 0, _mr.uniform(0, 360)), loc=(xx + fora * _mr.uniform(.2, 1.8), yy, 0))
                mg.add(blo, 'pedra', _mr.uniform(.34, .68))
                if _mr.random() > .72:                      # lotus flutuando junto da margem
                    mg.add(xf(t_lathe([(0, 0), (1.5, .02), (1.35, .16), (0, .2)], 9),
                              loc=(xx - fora * _mr.uniform(2.5, 6.0), yy + _mr.uniform(-2, 2), -.34)),
                           'folha_lotus', _mr.uniform(.3, .8))
    for s in ((131, 133), (-73, -71)): mg.add(t_box(-101.6, -68.4, s[0], s[1], -1.2, .6, bev=.12), 'pedra', .55)
    mg.finish(C)
    # A ponte-lua estava em y=0, atravessando exatamente onde a escadaria do Santuario desce
    # (Roblox X 88.5..104 na mesma faixa de Z). Quem descia dos portais batia no arco a ~4.8 de
    # altura. Achado pelo teste de caminhada no trecho, com raycast a cada stud. Vai para y=60.
    K.put('ponte', C, (-85, 60, .2), 0)
    ZG = terraco(K, C, -146, -104, -45, 45, 2.4, escadas=(('E', 0, 12),))
    # O TETO DO SANTUARIO SAIU. Ele passava rente ao topo dos portais (folga medida de 0.06 stud),
    # cortava o medalhao de cada um e, das capturas de Play, o usuario pediu para remover. Sem ele os
    # seis portais ficam num patio aberto, que e como a referencia mostra o portico dos mundos.
    # Ficam a escadaria (que antes nao tinha malha nenhuma) e a parede de fundo.
    escadaria_x(K, C, 0, -104, ZG, 8, 12, +1)
    # 6 PORTAIS: moon gate em volta dos discos de teleporte que o jogo ja tem (Roblox X=124.5, Z -32.5..32.5).
    # Em Blender: x = -124.5 e y = Z_roblox. O portal encara -X do Roblox, o que aqui e rotacao 90 em torno de Z.
    PX = -124.5
    for j, y in enumerate((-32.5, -19.5, -6.5, 6.5, 19.5, 32.5)):
        t = TEMAS_PORTAL[j]
        K.put('por_mold_' + t, C, (PX, y, ZG), 90)
        K.put('por_vort_' + t, C, (PX, y, ZG), 90)
        K.put('por_base_' + t, C, (PX + 6.5, y, ZG + .02), 0)
        for f in range(2):                                 # lascas flutuando NA FRENTE do portal: com +-7.4
            ang = 40 + 150 * f                             # elas invadiam o portal vizinho (os pads sao de 13 em 13)
            K.put('por_frag_' + t, C, (PX + 3.5, y + (4.2 if f == 0 else -4.2), ZG + 9.6 + 1.8 * f), ang)
    # parede do fundo atras dos portais
    nich = Builder('SANT_fundo', 45)
    nich.add(t_box(-146, -143.4, -45, 45, ZG, ZG + 15, bev=.12), 'verm', .45)
    for j, y in enumerate((-32.5, -19.5, -6.5, 6.5, 19.5, 32.5)):
        nich.add(t_box(-143.6, -143.0, y - 5.6, y + 5.6, ZG + .6, ZG + 13.4, bev=.08), 'vermS', .5 + .06 * j)
    nich.finish(C)
    # ---------------------------------------------------------------- GALERIA DOS PORTAIS (predio)
    # Colunata na frente dos portais criando VARANDA coberta de 14.5 studs (x -124.5 ate -110): o
    # jogador anda POR BAIXO da cobertura, que e a diferenca entre predio e muro decorado.
    gal = Builder('SANT_galeria', 413)
    XF, XB = -110.0, -146.0                      # face da colunata e parede de fundo
    HP = 17.0                                    # altura do pilar, do piso ate a face de baixo do beiral
    EIXOS = (-39.0, -26.0, -13.0, 0.0, 13.0, 26.0, 39.0)   # LIMITES de vao: nunca na frente de um portal
    for y in EIXOS:
        gal.add(xf(t_lathe([(0, 0), (2.6, 0), (2.6, .7), (2.35, .8)], 14), loc=(XF, y, ZG)), 'pedra', .5)
        gal.add(xf(t_lathe([(0, 0), (2.0, 0), (1.86, HP * .55), (1.72, HP)], 14), loc=(XF, y, ZG + .8)), 'verm', .45)
        gal.add(xf(t_lathe([(1.74, 0), (2.02, .1), (2.02, .5), (1.74, .6)], 14), loc=(XF, y, ZG + HP - 2.2)), 'ouro', .6)
    # viga e friso de dougong ligando os eixos (e a faixa que falta entre pilar e telhado)
    gal.add(t_box(XF - 1.9, XF + 1.9, -41.5, 41.5, ZG + HP, ZG + HP + 1.5, bev=.12, seg=2), 'mad', .42)
    gal.add(t_box(XF - 2.1, XF + 2.1, -41.5, 41.5, ZG + HP + 1.5, ZG + HP + 4.4, bev=.14, seg=2), 'verm', .5)
    for k in range(int(83 / 2.6)):
        yy = -41.0 + k * 2.6
        gal.add(t_box(XF - 2.8, XF + 2.8, yy - .62, yy + .62, ZG + HP + 1.9, ZG + HP + 3.5, bev=.1), 'jadeE', .4 + .5 * (k % 3) / 3)
    # nicho em arco por portal, rebaixado na parede do fundo
    for y in (-32.5, -19.5, -6.5, 6.5, 19.5, 32.5):
        gal.add(t_box(XB + .4, XB + 2.0, y - 5.8, y + 5.8, ZG + .3, ZG + 15.5, bev=.1), 'vermS', .42)
        arc = [Vector((XB + 1.2, y + math.cos(math.pi * i / 14) * 5.4, ZG + 15.2 + math.sin(math.pi * i / 14) * 3.1)) for i in range(15)]
        gal.add(t_tube(arc, [.55] * 15, 6), 'ouro', .58)
    # PLACA dourada na testeira, como o "世界之门" da referencia
    gal.add(t_box(XF - 2.6, XF - 2.0, -13.0, 13.0, ZG + HP + 4.8, ZG + HP + 9.0, bev=.14, seg=2), 'ouro', .72)
    gal.add(t_box(XF - 2.9, XF - 2.5, -12.0, 12.0, ZG + HP + 5.3, ZG + HP + 8.5, bev=.1), 'verm', .3)
    for k in range(4):
        yy = -8.4 + k * 5.6
        gal.add(t_box(XF - 3.1, XF - 2.85, yy - 1.5, yy + 1.5, ZG + HP + 5.9, ZG + HP + 7.9, bev=.08), 'ouro', .5 + .12 * k)
    # BALAUSTRADA na borda do terraco, dos dois lados da escadaria
    for sy in (-1, 1):
        for k in range(8):
            yy = sy * (13.0 + k * 4.2)
            if abs(yy) > 44: break
            gal.add(t_box(-105.6, -104.0, yy - .55, yy + .55, ZG, ZG + 2.3, bev=.09), 'pedra', .55)
        gal.add(t_box(-105.8, -103.8, sy * 12.4, sy * 44.6, ZG + 2.3, ZG + 2.9, bev=.1, seg=2), 'pedra', .6)
    gal.finish(C)
    # telhado do predio, reusando o kit: cobre da parede do fundo ate alem da colunata
    telhado('G', -128, 0, ZG + HP + 4.4, C)
    for sx in (-1, 1):
        K.put('lant', 'LOB_PROPS', (XF - 1.0, sx * 20, ZG + HP - 3.0), 0)
        K.put('lant', 'LOB_PROPS', (XF - 1.0, sx * 40, ZG + HP - 3.0), 0)
    # ================================================================ OESTE: jardim, loja, treino
    C = 'LOB_OESTE'
    ZL = terraco(K, C, 104, 130, -24, 16, 4.0, escadas=(('W', -4, 12),))
    escadaria_x(K, C, -4, 104, ZL, 10, 12, -1)   # havia degrau de colisao e nenhuma malha: escada invisivel
    colunata(K, C, [109, 118, 127], -19, ZL, .88, 'dg_int', None)
    colunata(K, C, [109, 118, 127], 11, ZL, .88, 'dg_int', None)
    for x in (109, 118, 127): K.put('parede', C, (x, 11, ZL), 180, (1, 1, .88))
    K.put('porta', C, (118, -19, ZL), 0, (1, 1, .88))
    K.put('janela', C, (109, -19, ZL), 0, (1, 1, .88)); K.put('janela', C, (127, -19, ZL), 0, (1, 1, .88))
    telhado('G', 117, -4, ZL + HCOL * .88 + .5 + k_dougong.Z1 + k_dougong.AH + 1.0, C)
    K.put('placa', C, (118, -21, ZL + 9.5), 0)
    # ---- INTERIOR DA LOJA. Antes era casca vazia: colunata, parede de fundo, telhado e mais nada.
    lj = Builder('LOJA_interior', 412)
    def tab(x0, x1, y0, y1, z0, z1, tinta, r=.5, bev=.06):
        lj.add(t_box(x0, x1, y0, y1, z0, z1, bev=bev, seg=2), tinta, r)
    # tapete
    tab(108, 128.5, -17, 9.5, ZL + .02, ZL + .12, 'tecido', .45, bev=.03)
    tab(109.2, 127.3, -15.8, 8.3, ZL + .12, ZL + .17, 'vermS', .55, bev=.03)
    # balcao em L, virado para quem entra pela porta (x=118, y=-19)
    for (x0, x1, y0, y1) in ((110.5, 125.5, -8.4, -6.0), (123.2, 125.5, -6.0, 2.5)):
        tab(x0, x1, y0, y1, ZL, ZL + 3.4, 'mad', .42)
        tab(x0 - .3, x1 + .3, y0 - .3, y1 + .3, ZL + 3.4, ZL + 3.8, 'madM', .55)
        tab(x0 + .4, x1 - .4, y0 - .34, y0 - .28, ZL + .8, ZL + 3.0, 'ouro', .6, bev=.03)
    # prateleiras na parede do fundo, com mercadoria
    import random as _rloja; rr = _rloja.Random(77)   # _r so e importado na secao de vegetacao, depois desta
    for k in range(3):
        zz = ZL + 2.0 + k * 2.3
        tab(108.6, 127.8, 9.0, 10.4, zz, zz + .32, 'mad', .48, bev=.04)
        for i in range(9):
            cx = 110 + i * 2.05
            alt = rr.uniform(.9, 1.7)
            t = rr.random()
            tinta = 'jade' if t > .68 else ('bronze' if t > .38 else 'creme')
            tab(cx - .62, cx + .62, 9.2, 10.2, zz + .32, zz + .32 + alt, tinta, rr.uniform(.2, .9), bev=.05)
    # prateleiras laterais
    for (px, lado) in ((108.4, 1), (128.0, -1)):
        for k in range(2):
            zz = ZL + 2.4 + k * 2.6
            tab(px, px + lado * 1.4, -15.5, 7.5, zz, zz + .32, 'mad', .48, bev=.04)
            for i in range(7):
                cy = -14 + i * 3.1
                alt = rr.uniform(.8, 1.5)
                tab(px + lado * .2, px + lado * 1.2, cy - .6, cy + .6, zz + .32, zz + .32 + alt,
                    'jade' if i % 3 else 'bronze', rr.uniform(.2, .9), bev=.05)
    # arcas e fardos no chao
    for (cx, cy, w, h) in ((112.0, 4.5, 1.9, 1.6), (115.5, 5.2, 1.5, 1.3), (121.5, 5.0, 2.1, 1.8),
                           (110.5, -12.5, 1.7, 1.4), (126.0, -12.0, 1.6, 1.5)):
        tab(cx - w, cx + w, cy - w * .72, cy + w * .72, ZL, ZL + h, 'mad', .4)
        tab(cx - w - .16, cx + w + .16, cy - w * .72 - .16, cy + w * .72 + .16, ZL + h, ZL + h + .3, 'madM', .55)
        tab(cx - .28, cx + .28, cy - w * .78, cy + w * .78, ZL + h * .35, ZL + h * .55, 'bronze', .6, bev=.03)
    # lampiao pendurado no meio do salao
    lj.add(xf(t_lathe([(0, 0), (.1, 0), (.1, 2.6), (0, 2.6)], 8), loc=(118, -4, ZL + 8.0)), 'ferro', .3)
    lj.add(xf(t_lathe([(0, 0), (1.05, .25), (1.15, 1.25), (.75, 1.9), (0, 2.0)], 12), loc=(118, -4, ZL + 6.0)), 'chama', .8)
    lj.add(xf(t_lathe([(0, 0), (1.2, .1), (1.2, .3), (0, .4)], 12), loc=(118, -4, ZL + 7.9)), 'ferro', .45)
    lj.finish(C)
    ar = Builder('TREINO_areia'); ar.add(t_box(72, 100, 20, 56, -.2, .1, bev=.04), 'palha', .35); ar.finish(C)
    for x in (80, 86, 92):
        for y in (30, 36, 42): K.put('poste_t', C, (x, y, 0), 0)
    for x, y in ((76, 50), (96, 50)): K.put('boneco', C, (x, y, 0), 0)
    K.put('estante', C, (86, 55, 0), 0)
    for sx, y in ((1, 22), (1, 54)): K.put('estand', 'LOB_PROPS', (100, y, 0), 0)
    cam = Builder('OESTE_caminho', 47)
    for (x, y) in ((84, -4), (96, -4)): cam.add(t_box(x - 6, x + 6, y - 4, y + 4, -.15, .05, bev=.04), 'piso', .5)
    cam.finish(C)
    # ================================================================ VEGETACAO E CHAO
    C = 'LOB_VEG'
    import random as _r
    rnd = _r.Random(99)
    # ---- ONDE NAO SE PLANTA. O espalhamento antigo sorteava x,y e plantava, sem olhar o que havia
    # embaixo: saiu flor em cima do calcamento, arbusto no meio do patio e cerejeira dentro do set de
    # treino. Cada caixa aqui e uma superficie dura ou de circulacao, com folga para o raio da planta.
    DURO = (
        ('patio',      -73,  73,  -79,   79), ('escadaria', -26,  26,  -94,  -58),
        ('via',        -19,  19,   56,  144), ('portao',    -49,  49,  136,  182),
        ('t_forja',    -65,  65, -156,  -86), ('t_sant',   -149, -101, -49,   49),
        ('t_loja',     101, 133,  -28,   20), ('treino',     69, 103,   16,   60),
        ('cam_oeste',  76, 104,  -10,    2),
    )
    barradas = {}
    def _borda_lago(lista, y):
        for k in range(len(lista) - 1):
            (ya, xa), (yb, xb) = lista[k], lista[k + 1]
            if ya <= y <= yb:
                t = (y - ya) / (yb - ya) if yb != ya else 0.0
                return xa + (xb - xa) * t
        return lista[-1][1]

    def no_lago(x, y, folga=2.8):
        """O lago deixou de ser o retangulo -103..-67 quando ganhou contorno trabalhado, mas a zona
        DURO continuou sendo o retangulo. Resultado medido: na faixa da escadaria do Santuario a agua
        recua ate x=-84.5 e o retangulo barrava ate -103, ou seja, 18 studs de terra nua sem calcamento
        bem no pe do ultimo degrau - era a queda de 3,40 studs que ficou em aberto. Aqui a barreira
        passa a ser o CONTORNO REAL, interpolado entre as duas margens."""
        if y < OESTE[0][0] or y > OESTE[-1][0]: return False
        return _borda_lago(OESTE, y) - folga <= x <= _borda_lago(LESTE, y) + folga

    def livre(x, y):
        if no_lago(x, y):
            barradas['lago'] = barradas.get('lago', 0) + 1
            return False
        for nome, x0, x1, y0, y1 in DURO:
            if x0 <= x <= x1 and y0 <= y <= y1:
                barradas[nome] = barradas.get(nome, 0) + 1
                return False
        return True
    def planta(key, x, y, z=0, s=1.0):
        if not livre(x, y): return False
        K.put(key, C, (x, y, z), rnd.uniform(0, 360), (s, s, s))
        return True
    # ESCALA DAS ARVORES. O pinheiro nasce com 9.6 de altura e o bordo com 10; ao lado de um salao de
    # 60 eles liam como arbusto ("arvore miuda"). Aqui vao a 1.8-2.4x, que e a proporcao que a referencia
    # de palacio mostra: copa na altura do primeiro beiral, emoldurando o edificio em vez de sumir.
    # O pinheiro novo ja nasce com H=18 e o bordo com H=17 (a versao de blob tinha 9.6 e 10, e por isso
    # precisava de multiplicador). Manter 2.1x aqui fazia a arvore passar de 37 studs e engolir a Loja.
    ESC_PIN, ESC_BOR = 1.0, 1.0
    # AS ARVORES PASSAM A NASCER DENTRO DOS CANTEIROS. As posicoes antigas eram escritas a mao sobre o
    # gramado de borda a borda; com o verde confinado a canteiro, quase todas caiam na calcada.
    # Aqui cada canteiro recebe um MACICO: grupo de 3 a 6 arvores com copas se tocando, em vez de
    # exemplar solitario - arvore isolada em area aberta le como poste de iluminacao.
    _arv = []
    def longe(x, y, d=13.0):
        for (ax, ay) in _arv:
            if math.hypot(x - ax, y - ay) < d: return False
        _arv.append((x, y)); return True
    for ci, (x0, x1, y0, y1) in enumerate(CANTEIRO):
        cx0, cx1 = x0 + 7, x1 - 7
        cy0, cy1 = y0 + 7, y1 - 7
        n = 3 + (ci % 3)                                        # quantidade IMPAR ou variada por canteiro
        for k in range(n + 2):
            ax = rnd.uniform(cx0, cx1); ay = rnd.uniform(cy0, cy1)
            if not longe(ax, ay, 11.0): continue
            if (ci + k) % 3 == 0:
                planta('bordo', ax, ay, 0, rnd.uniform(.80, 1.10) * ESC_BOR)
            else:
                planta('pinA' if (ci + k) % 2 else 'pinB', ax, ay, 0, rnd.uniform(.85, 1.20) * ESC_PIN)
        for k in range(4):                                      # arbusto ao pe, escondendo a juncao
            ax = rnd.uniform(cx0 - 4, cx1 + 4); ay = rnd.uniform(cy0 - 4, cy1 + 4)
            planta('arbA' if k % 2 else 'arbB', ax, ay, 0, rnd.uniform(.9, 1.5))
    # MARGEM ARBORIZADA do lago. No palacio chines a agua e sempre emoldurada por arvore; aqui ela
    # estava numa campina rasa. As duas fileiras ficam FORA da caixa do lago (x -103..-67), coladas nela.
    for k, yy in enumerate(range(-64, 132, 14)):
        lado = -106 if k % 2 == 0 else -64
        if longe(lado + (2 if k % 3 else -2), yy):
            planta('pinA' if k % 2 else 'pinB', lado + (2 if k % 3 else -2), yy, 0, rnd.uniform(.80, 1.15))
        if k % 2 == 0:
            if longe(-64 if lado < -100 else -106, yy + 7):
                planta('bordo', -64 if lado < -100 else -106, yy + 7, 0, rnd.uniform(.75, 1.05))
    for (x, y) in ((-66, -30), (-66, 30), (68, -40), (68, 44), (-104, -60), (108, 70)): planta('bambu', x, y, 0, 1.0)
    for (x, y, s) in ((-63, -62, 1.0), (58, -62, .9), (-60, 62, .95), (56, 64, 1.05), (-92, 24, 1.0), (88, -20, .9), (-30, -160, 1.1), (34, -158, 1.0)):
        planta('rocha1' if s > .95 else 'rocha2', x, y, 0, s)
    for k in range(26):
        planta('arbA' if k % 2 else 'arbB', rnd.uniform(-115, 115), rnd.uniform(-90, 130), 0, rnd.uniform(.7, 1.15))
    for k in range(40):
        planta('tufo', rnd.uniform(-118, 118), rnd.uniform(-95, 135), 0, rnd.uniform(.7, 1.2))
    # ---- FLORES E GRAMA (o gramado chapado era defeito declarado; agora tem flor, grama alta e canteiro)
    for (x, y, s_, key) in ((-58, -36, 1.0, 'peonia'), (-52, 22, .9, 'peonia2'), (52, -30, 1.05, 'peonia2'), (58, 26, .95, 'peonia'),
                            (-64, 4, 1.0, 'crisa'), (62, -6, .9, 'crisa2'), (-46, 52, 1.0, 'crisa2'), (48, 54, .95, 'crisa'),
                            (76, -52, 1.0, 'peonia'), (-124, -48, .9, 'crisa'), (112, 68, 1.0, 'peonia2'), (-128, 66, .95, 'crisa2')):
        planta(key, x, y, 0, s_)
    for (x, y, s_) in ((-60, -14, 1.0), (60, 12, .95), (-44, 40, 1.05), (46, -44, 1.0), (110, 44, .9), (-120, 30, 1.0)):
        planta('ameixa' if (x > 0) else 'ameixa2', x, y, 0, s_)   # (84,44) caia dentro do set de treino
    K.put('canteiro', C, (-56, -52, 0), 12); K.put('canteiro2', C, (56, -54, 0), -8)
    K.put('canteiro2', C, (-54, 58, 0), 96); K.put('canteiro', C, (58, 58, 0), 84)
    K.put('canteiro', C, (112, 26, 0), 90); K.put('canteiro2', C, (-124, -16, 0), 90)   # (86,20) e (-88,-16) caiam no treino e no lago
    for k in range(64):                                                            # grama alta na borda dos caminhos
        ang = rnd.uniform(0, 6.28); d = rnd.uniform(72, 112)
        gx = math.cos(ang) * d; gy = math.sin(ang) * d * 1.3
        if abs(gx) > 150 or abs(gy) > 150: continue
        planta('grama' if k % 2 else 'grama2', gx, gy, 0, rnd.uniform(.7, 1.3))
    for k in range(26):                                                            # grama junto ao patio
        gx = rnd.uniform(-70, 70); gy = rnd.choice([rnd.uniform(-68, -62), rnd.uniform(62, 68)])
        planta('grama2' if k % 2 else 'grama', gx, gy, 0, rnd.uniform(.7, 1.2))
    for (x, y, s_) in ((-88, -40, 1.0), (-82, 10, .9), (-94, 58, 1.05), (-86, 96, .95), (-80, -20, .85)):
        K.put('lotus' if s_ > .92 else 'lotus2', C, (x, y, -.3), rnd.uniform(0, 360), (s_, s_, s_))
    # ---- PROPS DE VILA na rua e no oeste
    P2 = 'LOB_PROPS'
    for (x, y, r) in ((-66, -56, 0), (66, -56, 0), (-66, 56, 180), (66, 56, 180), (-66, 0, 90), (66, 0, 270)):
        K.put('lant_pedra', P2, (x, y, 0), r)
    for (x, y, r) in ((20, 70, 0), (-20, 88, 0), (21, 110, 0), (-21, 128, 0)):
        K.put('lant_pedra', P2, (x, y, 0), r)
    K.put('poco', 'LOB_OESTE', (92, -34, 0), 0)
    K.put('varal', 'LOB_OESTE', (96, 8, 0), 90)
    K.put('placa_loja', 'LOB_OESTE', (101, -14, 0), 0)
    K.put('carroca', 'LOB_OESTE', (88, -22, 0), 28)
    for (x, y, r, key) in ((100, -30, 0, 'barril'), (98, -27, 0, 'barril'), (102, -24, 0, 'cesto'), (99, 18, 0, 'cesto'),
                           (103, 24, 0, 'caixas'), (96, 30, 0, 'telhas_p'), (94, -8, 0, 'banco'), (-64, 30, 90, 'banco'),
                           (64, -22, 270, 'banco'), (-100, 44, 0, 'barril'), (-98, 40, 0, 'cesto')):
        K.put(key, P2, (x, y, 0), r)
    # CALCAMENTO ORNAMENTAL em volta do monumento: aneis concentricos e raios, como o desenho de piso
    # que a referencia tem irradiando do centro. Antes era laje uniforme de ponta a ponta.
    orn = Builder('PATIO_ornamento', 407)
    for k, (r0, r1, tinta) in enumerate(((16.5, 18.5, 'junta'), (21.0, 22.2, 'bronze'),
                                         (27.0, 29.0, 'junta'), (33.5, 34.4, 'bronze'))):
        n = 48
        for i in range(n):
            a3 = math.tau * i / n; a4 = math.tau * (i + 1) / n
            orn.add(t_prism([(math.cos(a3) * r0, math.sin(a3) * r0), (math.cos(a4) * r0, math.sin(a4) * r0),
                             (math.cos(a4) * r1, math.sin(a4) * r1), (math.cos(a3) * r1, math.sin(a3) * r1)],
                            'Z', .01, .09), tinta, .35 + .12 * k)
    for i in range(16):                                                  # raios saindo do centro
        a3 = math.tau * i / 16
        raio = t_prism([(0, -.55), (14.0, -1.15), (14.0, 1.15), (0, .55)], 'Z', .01, .08)
        xf(raio, rot=(0, 0, math.degrees(a3)), loc=(math.cos(a3) * 19.5, math.sin(a3) * 19.5, 0))
        orn.add(raio, 'junta', .4 + .3 * (i % 3) / 3)
    orn.finish('LOB_PATIO')
    # PASSADEIRA VERMELHA subindo a escadaria da Forja, como o tapete da referencia
    tap = Builder('PATIO_passadeira', 408)
    for i in range(1, 13):
        z = Z - (Z / 12) * i
        if z < .01: break
        y0 = -90 + 1.9 * (i - 1)
        tap.add(t_box(-7.5, 7.5, y0, y0 + 2.06, z, z + .14, bev=.04), 'verm', .5 + .03 * (i % 3))
    tap.add(t_box(-7.5, 7.5, -66.8, -62.0, .0, .14, bev=.04), 'verm', .52)
    tap.finish('LOB_PATIO')
    # a base deixou de ser VERDE: o verde passou para dentro dos canteiros, e o que sobra por baixo
    # de tudo e terra escura. Era esta caixa unica de 360 x 415 em 'folha' que dominava toda captura.
    # ---------------------------------------------------------------- BORDA DO MUNDO
    # (a) cinturao de penhasco em tres patamares com RECUO: e o recuo que quebra a silhueta vertical
    #     e impede que volte a ler como parede de estudio.
    rb = _r.Random(808)
    BX, BY0, BY1 = 178.0, -213.0, 198.0
    def anel(nome, recuo, z, passo, esc):
        # PASSO MENOR QUE A LARGURA DO MODULO (18): os blocos se SOBREPOEM e formam parede. Antes o
        # passo era 26-34 contra modulo de 18, o que deixava folga entre eles - dai os "aneis de
        # volumes claros muito repetidos, com espacos azuis entre eles" que o usuario apontou.
        # A profundidade tambem varia por bloco, para a face nao ser um plano unico.
        n = 0
        def por(x, y):
            nonlocal n
            fora = 1 if (abs(x) > BX or y < BY0 or y > BY1) else -1
            dx = rb.uniform(-3.5, 3.5); dy = rb.uniform(-3.5, 3.5)
            K.put(nome % (1 + n % 3), 'LOB_CHAO',
                  (x + dx, y + dy, z + rb.uniform(-2.5, 2.5)),
                  rb.uniform(0, 360), (esc * rb.uniform(.78, 1.34),) * 3)
            n += 1
        for x in _frange(-BX - recuo, BX + recuo, passo):
            for y in (BY0 - recuo, BY1 + recuo): por(x, y)
        for y in _frange(BY0 - recuo, BY1 + recuo, passo):
            for x in (-BX - recuo, BX + recuo): por(x, y)
        return n
    # o primeiro anel sobe para -1.0: em -5.0 sobrava a faixa marrom da propria placa (topo -0.52)
    # aparecendo entre o muro e a rocha, que era justamente o corte que o cinturao veio esconder.
    n1 = anel('penha%d', 2.0, -1.0, 12.5, 1.00)     # passo 12.5 contra modulo de 18: sobrepoe
    n2 = anel('penha%d', 13.0, -17.0, 14.0, 1.20)
    n3 = anel('penha%d', 26.0, -33.0, 16.0, 1.45)
    # FUNDO DO MUNDO: os aneis de serra e nevoa sairam. Ampliados para centenas de studs eles
    # liam como fitas brancas no vazio (o usuario mandou a captura). Num simulator o ceu do
    # Roblox e o cinturao de penhasco ja fecham a borda; cenario distante custava caro e nao
    # estava ajudando.
    # quedas d'agua nascendo no labio do primeiro patamar e morrendo no banco de nuvem
    for (qx, qy, qr) in ((-BX - 4, -60, 90), (-BX - 4, 90, 90), (BX + 4, -30, 270),
                         (BX + 4, 110, 270), (-40, BY0 - 4, 180), (60, BY1 + 4, 0)):
        K.put('queda', 'LOB_CHAO', (qx, qy, -6.0), qr)
    ch = Builder('LOB_chao'); ch.add(t_box(-180, 180, -215, 200, -3, -.52), 'casca_escura', .3)
    # CALCADA: tudo o que nao e canteiro, nao e agua e nao e superficie ja construida vira pedra.
    # O topo fica em -0.50, rente ao topo da grama, para nao mexer nas caixas de colisao.
    # CALCAMENTO: nao e mais construido aqui. Eram 985 lajes de malha que, no jogo, liam como
    # tabuleiro e ainda chegavam escurecidas. O chao passou a ser Part chapada montada no
    # Roblox (export/chao_simples.lua): uma base, as juntas e o aro do hexagono. Mais claro,
    # mais barato e alteravel sem reassar nada.
    postas = 0

    # MEIO-FIO de cada canteiro, com a terra do miolo rebaixada: e a moldura construida que separa
    # jardim de calcada. Sem ela o verde le como textura de terreno.
    mf2 = Builder('LOB_canteiro', 409)
    for (x0, x1, y0, y1) in CANTEIRO:
        # bisel de 1 segmento e sem a faixa interna de junta: com seg=2 mais a faixa, os 12 canteiros
        # somavam 22.608 tris e estouravam o teto de 20 mil do importador do Roblox.
        for (a0, a1, b0, b1) in ((x0, x1, y0, y0 + 1.5), (x0, x1, y1 - 1.5, y1),
                                 (x0, x0 + 1.5, y0, y1), (x1 - 1.5, x1, y0, y1)):
            mf2.add(t_box(a0, a1, b0, b1, -.62, -.06, bev=.10, seg=1), 'piso', .58)
        # a terra tem de ficar ABAIXO da relva: com o topo em -0.30 contra -0.44 da relva, ela
        # tapava o verde e o canteiro saia marrom no render.
        mf2.add(t_box(x0 + 1.4, x1 - 1.4, y0 + 1.4, y1 - 1.4, -.62, -.56), 'casca_escura', .35)
        for k in range(int((x1 - x0) / 15)):                     # pilarete a cada ~15 studs
            xx = x0 + 7.5 + k * 15
            for yy in (y0 + .75, y1 - .75):
                mf2.add(t_box(xx - .85, xx + .85, yy - .95, yy + .95, -.62, .30, bev=.09, seg=1), 'piso', .64)
    mf2.finish('LOB_CHAO')

    # RELVA: saiu. A versao geometrica (manta + ladrilho de tufos + franja) custava ~890 mil
    # triangulos e, no jogo, virava um tapete de espinhos escuros - o usuario mandou a foto.
    # O verde agora e mancha de Part no chao, e o jardim em si fica por conta dele.
    ch.finish('LOB_CHAO')
    # MEIO-FIO: faixa de pedra na divisa do gramado com o patio e com a via. Sem ela a grama encosta
    # direto no calcamento e a transicao fica em corte seco, que era parte do ar de "jogado".
    mf = Builder('LOB_meiofio', 405)
    def fio(x0, x1, y0, y1):
        mf.add(t_box(x0, x1, y0, y1, -.62, -.30, bev=.06), 'piso', .55)
        mf.add(t_box(x0 + .18, x1 - .18, y0 + .18, y1 - .18, -.62, -.24, bev=.05), 'junta', .4)
    for (x0, x1, y0, y1) in ((-71.4, 71.4, -63.4, -62.0), (-71.4, 71.4, 62.0, 63.4),
                             (-71.4, -70.0, -63.4, 63.4), (70.0, 71.4, -63.4, 63.4),
                             (-17.4, -16.0, 62.0, 141.4), (16.0, 17.4, 62.0, 141.4)):
        fio(x0, x1, y0, y1)
    mf.finish('LOB_CHAO')
    # penhascos: massas facetadas de alturas variadas (a caixa lisa da 1a versao lia como parede de estudio)
    rr = _r.Random(7)
    def macico(nome, x0, x1, y0, y1, passo, hmin, hmax):
        pe = Builder(nome, 31)
        nx = max(1, int((x1 - x0) / passo)); ny = max(1, int((y1 - y0) / passo))
        for i in range(nx):
            for j in range(ny):
                ax = x0 + i * (x1 - x0) / nx; bx = x0 + (i + 1) * (x1 - x0) / nx
                ay = y0 + j * (y1 - y0) / ny; by = y0 + (j + 1) * (y1 - y0) / ny
                h = rr.uniform(hmin, hmax) * (1.0 + .45 * min(i, nx - 1 - i) / max(1, nx / 2))
                d = passo * .16
                pe.add(t_box(ax - d, bx + d, ay - d, by + d, -4, h, bev=1.1, seg=1), 'pedra', rr.uniform(.3, .62))
        pe.finish('LOB_CHAO')
    # MURALHA DO RECINTO no lugar dos macicos. As massas facetadas de pedra liam como parede de estudio
    # e eram o que o usuario chamou de "parede mal estruturada". Palacio chines se fecha com MURO, e o
    # muro do kit (rodape de pedra, pano vermelho com almofadas, friso e capa de telha) ja existia - so
    # estava sendo usado num trecho de 30 studs ao lado do portao. Aqui ele da a volta inteira, mais
    # alto (H 8.6 -> 13.5), com torre nos cantos e de espaco em espaco.
    MX, MY0, MY1 = 158.0, -192.0, 150.0
    PASSO = 13.0
    C = 'LOB_PORTAO'
    def linha_muro(x0, y0, x1, y1, pular=None):
        # enfileira segmentos de muro entre dois pontos, pulando um intervalo (o vao do Grande Portao)
        comp = math.hypot(x1 - x0, y1 - y0)
        n = max(1, int(round(comp / PASSO)))
        ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
        for i in range(n):
            t = (i + .5) / n
            cx = x0 + (x1 - x0) * t; cy = y0 + (y1 - y0) * t
            if pular and pular[0] <= cx <= pular[1] and pular[2] <= cy <= pular[3]: continue
            K.put('muroA', C, (cx, cy, 0), ang, (comp / n / 9.0, 1, 1))
    linha_muro(-MX, MY0, MX, MY0)
    linha_muro(-MX, MY0, -MX, MY1)
    linha_muro(MX, MY0, MX, MY1)
    linha_muro(-MX, MY1, MX, MY1, pular=(-50, 50, MY1 - 2, MY1 + 2))
    for (tx, ty) in ((-MX, MY0), (MX, MY0), (-MX, MY1), (MX, MY1)):
        K.put('mtorre', C, (tx, ty, 0), 0)
    for tx in (-MX + 79, MX - 79):
        K.put('mtorre', C, (tx, MY0, 0), 0)
    for ty in (MY0 + 86, MY0 + 172, MY0 + 258):
        for tx in (-MX, MX): K.put('mtorre', C, (tx, ty, 0), 0)
    for tx in (-54, 54):
        K.put('mtorre', C, (tx, MY1, 0), 0)
    C = 'LOB_VEG'
    # ---- registra as pecas UNICAS (piso, escadas, lago, via, penhascos...): elas sao criadas com Builder().finish()
    # direto, com a geometria ja em coordenadas do lobby, e por isso nao passam por K.put. Sem este passo elas ficam
    # fora de PLACE, fora do atlas e fora do FBX - foi o que fez o lobby aparecer flutuando na 1a montagem.
    # masters que nunca foram colocados ficam parados na origem da cena - que aqui e o CENTRO DO PATIO. Fora.
    nao_usados = []
    for key, o in list(K.m.items()):
        if not hasattr(o, 'data'): continue
        if not o.get('usado', False):
            nao_usados.append(o.name)
            for c in list(o.users_collection): c.objects.unlink(o)
            col('LOB_NAO_USADO').objects.link(o); o.location = (400, 400, 0)
    ja = {p['mesh'] for p in PLACE}
    soltas = 0
    for c in bpy.data.collections:
        if not c.name.startswith('LOB_') or c.name == 'LOB_NAO_USADO': continue
        for o in c.objects:
            if o.type != 'MESH' or o.data.name in ja: continue
            ja.add(o.data.name); soltas += 1
            PLACE.append(dict(mesh=o.data.name, pos=[0, 0, 0], rot=0, scale=[1, 1, 1]))
    if barradas:
        soltas_msg = 'vegetacao barrada por cair em superficie dura: ' + ', '.join('%s=%d' % kv for kv in sorted(barradas.items()))
    else:
        soltas_msg = 'vegetacao barrada por cair em superficie dura: nenhuma'
    rep = [soltas_msg,
           'pecas unicas registradas (geometria ja no lugar): %d' % soltas,
           'masters do kit nao usados neste lobby (tirados da origem): %s' % (', '.join(sorted(nao_usados)) or 'nenhum')]
    tot = 0
    for key, o in K.m.items():
        if not hasattr(o, 'data'): continue
        n_ = K.n.get(key, 0) + 1; tr = o.get('tris', 0); tot += tr * n_
        rep.append('%-26s %6d tris x %3d' % (o.name, tr, n_))
    unicas = [o for o in K.m.values() if hasattr(o, 'data')]
    rep.append('TOTAL ~%d tris em cena | malhas unicas %d (%d tris) | colocacoes %d' % (tot, len(unicas), sum(o.get('tris', 0) for o in unicas), len(PLACE)))
    import json as _json, os as _os
    _cam = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'lobby_cotas.json')
    _json.dump(COTAS, open(_cam, 'w'), indent=1)
    return K, rep
