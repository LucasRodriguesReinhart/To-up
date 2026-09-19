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
import k_pedra, k_madeira, k_dougong, k_telhado, k_props, k_veg, k_kit2, k_lobby
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
    return H

def escadaria(K, C, cx, y_topo, z_topo, n, largura, tread=1.9):
    """lance que desce do terraco (em y_topo) para o PATIO, em +Y. Descer em -Y punha a escada dentro do proprio
    terraco e deixava uma parede de 10 studs no eixo de entrada."""
    rise = z_topo / n
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
        ('torre', k_lobby.torre_fogo, 'LOB_FORJA'), ('espada', lambda: k_lobby.espada_ancestral(38.0), 'LOB_PATIO'), ('ped_esp', lambda: k_lobby.pedestal_espada(11.0, 6.0), 'LOB_PATIO'),
        ('fornalha', k_lobby.fornalha, 'LOB_FORJA'), ('bigorna', k_lobby.bigorna, 'LOB_FORJA'), ('fole', k_lobby.fole, 'LOB_FORJA'),
        ('calha', k_lobby.calha_tempera, 'LOB_FORJA'), ('laminas', k_lobby.altar_laminas, 'LOB_FORJA'), ('braseiro', k_lobby.braseiro, 'LOB_PROPS'),
        ('leaoA', lambda: k_lobby.leao(1), 'LOB_PROPS'), ('leaoB', lambda: k_lobby.leao(-1), 'LOB_PROPS'),
        ('ponte', k_lobby.ponte_lua, 'LOB_LESTE'), ('rocha1', lambda: k_lobby.rocha(1, 3.2), 'LOB_VEG'), ('rocha2', lambda: k_lobby.rocha(2, 2.2), 'LOB_VEG'),
        ('bambu', lambda: k_lobby.bambu(1), 'LOB_VEG'), ('bordo', lambda: k_lobby.bordo(1), 'LOB_VEG'),
        ('poste_t', k_lobby.poste_treino, 'LOB_OESTE'), ('boneco', k_lobby.boneco_treino, 'LOB_OESTE'), ('estante', k_lobby.estante_armas, 'LOB_OESTE'),
    ):
        K.master(key, fn, C)
    # telhados proprios (cada um e uma malha; os hero assets merecem o seu)
    RF = k_telhado.Roof(EX=42.0, EY=25.0, RS=13.0, H=15.0, ZE=0.0, LIFT=3.6, SL=9.0, OUT=1.4, PER=2.15, LT=3.4)          # Forja, beiral inferior
    RF2 = k_telhado.Roof(EX=34.0, EY=19.0, RS=11.0, H=13.0, ZE=0.0, LIFT=3.2, SL=8.0, OUT=1.3, PER=1.8, LT=2.9)         # Forja, beiral superior
    RG = k_telhado.Roof(EX=26.0, EY=13.0, RS=8.0, H=10.0, ZE=0.0, LIFT=2.8, SL=7.0, OUT=1.2, PER=1.6, LT=2.6)           # Portao e Loja
    for nome, R in (('F1', RF), ('F2', RF2), ('G', RG)):
        for which, w in (('front', 'frente'), ('side', 'lado')):
            K.master('ag_%s_%s' % (nome, w), lambda R=R, which=which, nome=nome, w=w: k_telhado.agua(R, which, 'TEL_%s_agua_%s' % (nome, w), 'telhaImp' if nome.startswith('F') else 'telha'), 'LOB_FORJA')
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
    telhado('F2', 0, -127, ZC + k_dougong.Z_TOP + 1.0 + 17.0, C)
    K.put('placa', C, (0, -105.5, ZC + 2.4), 0)
    K.put('torre', C, (0, -143, Z))
    K.put('fornalha', C, (0, -146, Z), 180)
    K.put('bigorna', C, (-8, -130, Z)); K.put('fole', C, (16, -140, Z), 90)
    K.put('calha', C, (9, -128, Z), 90); K.put('laminas', C, (-30, -136, Z), 90)
    for sx in (-1, 1):
        K.put('braseiro', C, (sx * 16, -100, Z)); K.put('lant', C, (sx * 18, -108, Z + k_madeira.Z_ARQ * 1.25), 0, (.9, .9, .9))
        K.put('estand', C, (sx * 50, -96, Z), 0); K.put('leaoA' if sx > 0 else 'leaoB', C, (sx * 14, -88, 0), 0)
    # ================================================================ ESCADARIA + PATIO + ALTAR
    C = 'LOB_PATIO'
    escadaria(K, C, 0, -90, Z, 12, 46)
    for f in range(6):                                                              # piso em 6 faixas (e nao 672 lajes soltas)
        pp = Builder('PATIO_piso_%d' % f, 40 + f)
        for i in range(f * 5, min(28, (f + 1) * 5)):
            for j in range(24):
                x = -70 + i * 5; y = -60 + j * 5
                if abs(x + 2.5) < 24 and abs(y + 2.5) < 24: continue                # buraco do altar/espelho
                pp.add(t_box(x + .08, x + 4.92, y + .08, y + 4.92, -.5, 0, bev=.05), 'piso')
        pp.add(t_box(-70, 70, -60, 60, -.62, -.42), 'junta', .25)
        pp.finish(C)
    agua = Builder('PATIO_agua'); agua.add(t_lathe([(0, -1.2), (23, -1.2), (23, -.35), (0, -.35)], 32), 'agua', .6); agua.finish(C)
    leito = Builder('PATIO_leito'); leito.add(t_lathe([(0, -1.6), (23.4, -1.6), (23.4, -1.1), (0, -1.1)], 32), 'junta', .3); leito.finish(C)
    borda = Builder('PATIO_borda', 41)
    for k in range(8):
        a = math.radians(45 * k)
        borda.add(xf(t_box(-9.6, 9.6, -.8, .8, -.7, .5, bev=.1), rot=(0, 0, 45 * k + 90), loc=(23.6 * math.cos(a), 23.6 * math.sin(a), 0)), 'pedra', .45 + .06 * k)
    for k in range(4):                                                              # 4 pontes de pedra sobre o espelho
        a = math.radians(90 * k)
        borda.add(xf(t_box(-4.5, 4.5, -4.2, 4.2, -1.4, .3, bev=.08), rot=(0, 0, 90 * k), loc=(17 * math.cos(a), 17 * math.sin(a), 0)), 'pedra', .5)
    borda.finish(C)
    K.put('ped_esp', C, (0, 0, 0)); K.put('espada', C, (0, 0, 6.35))
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
    lago = Builder('LAGO_agua'); lago.add(t_box(-100, -70, -70, 130, -1.6, -.35), 'agua', .6); lago.finish(C)
    leito2 = Builder('LAGO_leito', 49)
    leito2.add(t_box(-100.5, -69.5, -70.5, 130.5, -3.2, -1.5), 'junta', .3)
    import random as _rl
    rl = _rl.Random(5)
    for k in range(26):                                                             # pedras submersas junto as margens
        x = rl.choice([rl.uniform(-99, -94), rl.uniform(-76, -71)]); y = rl.uniform(-66, 126)
        leito2.add(t_blob(rl.uniform(.7, 1.6), (1.2, 1.0, .5), 1, lobes=4, lobe_amp=.3, seed=k, flat_bottom=-.3) and xf(t_blob(rl.uniform(.7, 1.6), (1.2, 1.0, .5), 1, lobes=4, lobe_amp=.3, seed=k, flat_bottom=-.3), loc=(x, y, -1.3)), 'pedra', rl.uniform(.35, .7))
    leito2.finish(C)
    mg = Builder('LAGO_margem', 48)
    for s in ((-101.6, -99.6), (-70.4, -68.4)): mg.add(t_box(s[0], s[1], -71, 131, -1.2, .6, bev=.12, seg=3), 'pedra', .5)
    for s in ((131, 133), (-73, -71)): mg.add(t_box(-101.6, -68.4, s[0], s[1], -1.2, .6, bev=.12), 'pedra', .55)
    mg.finish(C)
    K.put('ponte', C, (-85, 0, .2), 0)
    ZG = terraco(K, C, -146, -104, -45, 45, 2.4, escadas=(('E', 0, 12),))
    colunata(K, C, [-141, -132, -123, -114], -39, ZG, .82, 'dg_sim', None)
    colunata(K, C, [-141, -132, -123, -114], 39, ZG, .82, 'dg_sim', None)
    for y in (-39, 39):
        for x in (-141, -132, -123, -114): K.put('parede', C, (x, y, ZG), 0 if y < 0 else 180, (1, 1, .82))
    telhado('G', -125, 0, ZG + HCOL * .82 + .5 + k_dougong.Z1 + k_dougong.AH + 1.0, C)
    nich = Builder('SANT_nichos', 45)
    for j, y in enumerate((-32, -20, -6, 7, 19, 32)):                              # moldura dos 6 portais
        nich.add(t_box(-144, -142, y - 4, y + 4, ZG, ZG + 13, bev=.12), 'verm', .45 + .07 * j)
        nich.add(t_box(-142.4, -141.6, y - 3.4, y + 3.4, ZG + 1.2, ZG + 10.4, bev=.08), 'ouro', .6)
        nich.add(t_box(-142.0, -141.4, y - 2.6, y + 2.6, ZG + 1.8, ZG + 9.6), 'jadeE', .5)
    nich.finish(C)
    for sx in (-1, 1):
        K.put('lant', 'LOB_PROPS', (-110, sx * 20, ZG + 11), 0)
    # ================================================================ OESTE: jardim, loja, treino
    C = 'LOB_OESTE'
    ZL = terraco(K, C, 104, 130, -24, 16, 4.0, escadas=(('W', -4, 12),))
    colunata(K, C, [109, 118, 127], -19, ZL, .88, 'dg_int', None)
    colunata(K, C, [109, 118, 127], 11, ZL, .88, 'dg_int', None)
    for x in (109, 118, 127): K.put('parede', C, (x, 11, ZL), 180, (1, 1, .88))
    K.put('porta', C, (118, -19, ZL), 0, (1, 1, .88))
    K.put('janela', C, (109, -19, ZL), 0, (1, 1, .88)); K.put('janela', C, (127, -19, ZL), 0, (1, 1, .88))
    telhado('G', 117, -4, ZL + HCOL * .88 + .5 + k_dougong.Z1 + k_dougong.AH + 1.0, C)
    K.put('placa', C, (118, -21, ZL + 9.5), 0)
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
    def planta(key, x, y, z=0, s=1.0):
        K.put(key, C, (x, y, z), rnd.uniform(0, 360), (s, s, s))
    for (x, y, s) in ((-64, -78, 1.1), (-58, 40, 1.0), (-52, 96, .9), (46, -78, 1.05), (54, 38, 1.0), (62, 92, .95),
                      (104, 40, 1.0), (112, -46, .9), (-108, 62, 1.0), (-96, -60, .95), (30, -170, 1.2), (-30, -168, 1.15)):
        planta('pinA' if (x + y) % 2 else 'pinB', x, y, 0, s)
    for (x, y, s) in ((-44, -66, 1.0), (40, -66, 1.0), (-40, 66, .9), (44, 70, .95), (-76, 20, 1.0), (76, -30, .9)):
        planta('bordo', x, y, 0, s)
    for (x, y) in ((-66, -30), (-66, 30), (68, -40), (68, 44), (-104, -60), (108, 70)): planta('bambu', x, y, 0, 1.0)
    for (x, y, s) in ((-63, -62, 1.0), (58, -62, .9), (-60, 62, .95), (56, 64, 1.05), (-92, 24, 1.0), (88, -20, .9), (-30, -160, 1.1), (34, -158, 1.0)):
        planta('rocha1' if s > .95 else 'rocha2', x, y, 0, s)
    for k in range(26):
        planta('arbA' if k % 2 else 'arbB', rnd.uniform(-115, 115), rnd.uniform(-90, 130), 0, rnd.uniform(.7, 1.15))
    for k in range(40):
        planta('tufo', rnd.uniform(-118, 118), rnd.uniform(-95, 135), 0, rnd.uniform(.7, 1.2))
    ch = Builder('LOB_chao'); ch.add(t_box(-180, 180, -215, 200, -3, -.5), 'folha', .35); ch.finish('LOB_CHAO')
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
    macico('PENHASCO_N', -180, 180, -212, -162, 26, 34, 62)
    macico('PENHASCO_W', -182, -152, -162, 168, 26, 28, 48)
    macico('PENHASCO_E', 152, 182, -162, 168, 26, 28, 48)
    macico('PENHASCO_S1', -182, -60, 168, 200, 28, 22, 38)
    macico('PENHASCO_S2', 60, 182, 168, 200, 28, 22, 38)
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
    rep = ['pecas unicas registradas (geometria ja no lugar): %d' % soltas,
           'masters do kit nao usados neste lobby (tirados da origem): %s' % (', '.join(sorted(nao_usados)) or 'nenhum')]
    tot = 0
    for key, o in K.m.items():
        if not hasattr(o, 'data'): continue
        n_ = K.n.get(key, 0) + 1; tr = o.get('tris', 0); tot += tr * n_
        rep.append('%-26s %6d tris x %3d' % (o.name, tr, n_))
    unicas = [o for o in K.m.values() if hasattr(o, 'data')]
    rep.append('TOTAL ~%d tris em cena | malhas unicas %d (%d tris) | colocacoes %d' % (tot, len(unicas), sum(o.get('tris', 0) for o in unicas), len(PLACE)))
    return K, rep
