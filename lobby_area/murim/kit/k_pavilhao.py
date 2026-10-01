# k_pavilhao.py - GATE 1: "Pavilhao-Modelo" montado SO com pecas do kit (3 vaos x 2, alpendre frontal, telhado wudian).
# Cada peca e modelada uma vez (master) e repetida por copia ligada; e assim que ira para o Roblox (importa 1x, duplica).
import bpy, bmesh, math, json, os
from mathutils import Vector
from k_core import *
import k_pedra, k_madeira, k_dougong, k_telhado, k_props, k_veg, k_kit2

TZ = k_pedra.TZ; MOD = k_pedra.MOD; VAO = k_madeira.VAO
ZP = TZ + k_madeira.H_COL + .5          # topo da prancha = base dos dougong (17.5)
ZD = ZP + k_dougong.Z_TOP               # topo dos dougong (22.02)
ROOF = dict(EX=18.9, EY=14.4, RS=9.5, H=13.0, ZE=ZD + 1.0, LIFT=3.0, SL=7.5, OUT=1.25)
PLACE = []                               # (master, nome, pos, rot_z, escala) -> placements.json para o Studio

def mirror_mesh(src, name, colname, axis=1):
    bm = bmesh.new(); bm.from_mesh(src.data)
    s = [1, 1, 1]; s[axis] = -1
    bmesh.ops.scale(bm, vec=s, verts=bm.verts); bmesh.ops.reverse_faces(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in src.data.materials: me.materials.append(m)
    o = bpy.data.objects.new(name, me); col(colname).objects.link(o); o['espelho_de'] = src.name; o['tris'] = src.get('tris', 0); return o

class Kit:
    def __init__(s): s.m = {}; s.n = {}
    def master(s, key, builder, colname):
        B = builder() if callable(builder) else builder
        tr = B.tris(); o = B.finish(colname); s.m[key] = o; s.n[key] = 0; o['tris'] = tr; o['usado'] = False; return o
    def put(s, key, colname, loc, rot=0.0, scale=(1, 1, 1)):
        m = s.m[key]
        if not m['usado']:
            o = m; m['usado'] = True; o.location = loc; o.rotation_euler = (0, 0, math.radians(rot)); o.scale = scale
            if o.name not in col(colname).objects:
                for c in list(o.users_collection): c.objects.unlink(o)
                col(colname).objects.link(o)
        else:
            s.n[key] += 1; o = instance(m, '%s.%03d' % (m.name, s.n[key]), colname, loc, rot, scale)
        PLACE.append(dict(mesh=m.data.name, pos=[round(v, 4) for v in loc], rot=rot, scale=list(scale))); return o

def build():
    for c in ('BANCADA', 'BANCADA2', 'TELHADO', 'PAV_BANCADA', 'PAV_KIT2', 'PAV_PEDRA', 'PAV_MADEIRA', 'PAV_DOUGONG', 'PAV_TELHADO', 'PAV_PROPS', 'PAV_VEG', 'PAV_CHAO'): clear_col(c)
    del PLACE[:]
    K = Kit(); R = k_telhado.Roof(**ROOF)
    # ------------------------------------------------ PEDRA
    for key, fn in (('sumeru', k_pedra.sumeru_seg), ('canto', k_pedra.sumeru_canto), ('piso', k_pedra.piso_mod), ('bal', k_pedra.bal_seg),
                    ('poste', k_pedra.bal_poste), ('escada', k_pedra.escada), ('colbase', k_pedra.tambor_coluna), ('jard', k_pedra.jardineira), ('tambor', k_pedra.bal_tambor)):
        K.master(key, fn, 'PAV_PEDRA')
    HX, HY = 4 * MOD, 3 * MOD
    for i in range(8):
        x = -HX + i * MOD
        if i not in (3, 4): K.put('sumeru', 'PAV_PEDRA', (x, -HY, 0), 0)
        K.put('sumeru', 'PAV_PEDRA', (x + MOD, HY, 0), 180)
    for j in range(6):
        y = -HY + j * MOD
        K.put('sumeru', 'PAV_PEDRA', (HX, y, 0), 90); K.put('sumeru', 'PAV_PEDRA', (-HX, y + MOD, 0), 270)
    for sx in (-1, 1):
        for sy in (-1, 1): K.put('canto', 'PAV_PEDRA', (sx * (HX + .2), sy * (HY + .2), 0), 0)
    for i in range(8):
        for j in range(6): K.put('piso', 'PAV_PEDRA', (-HX + i * MOD, -HY + j * MOD, TZ), 0)
    K.put('escada', 'PAV_PEDRA', (0, -HY, 0), 0)
    bx, by = HX - .8, HY - .8; sxl = (2 * bx) / 8 / MOD; syl = (2 * by) / 6 / MOD; stepx = 2 * bx / 8; stepy = 2 * by / 6
    for i in range(8):
        if i in (3, 4): continue
        K.put('bal', 'PAV_PEDRA', (-bx + i * stepx, -by, TZ), 0, (sxl, 1, 1))
    K.put('poste', 'PAV_PEDRA', (-bx + 3 * stepx, -by, TZ), 0)
    for i in range(6): K.put('bal', 'PAV_PEDRA', (bx, -by + i * stepy, TZ), 90, (syl, 1, 1))
    for i in range(8): K.put('bal', 'PAV_PEDRA', (bx - i * stepx, by, TZ), 180, (sxl, 1, 1))
    for i in range(6): K.put('bal', 'PAV_PEDRA', (-bx, by - i * stepy, TZ), 270, (syl, 1, 1))
    nuc = Builder('PAV_terraco_nucleo'); nuc.add(t_box(-HX, HX, -HY, HY, 0, TZ - .45), 'junta', .3); nuc.finish('PAV_PEDRA')
    # ------------------------------------------------ MADEIRA
    for key, fn in (('coluna', k_madeira.coluna), ('arq', k_madeira.arquitrave), ('prancha', k_madeira.prancha), ('viga', lambda: k_madeira.viga_alpendre(VAO)),
                    ('janela', k_madeira.vao_janela), ('porta', k_madeira.vao_porta), ('parede', k_madeira.vao_parede), ('placa', k_madeira.placa),
                    ('forro', k_props.forro_alpendre), ('tabua', k_props.tabua_dougong), ('terca', k_props.terca)):
        K.master(key, fn, 'PAV_MADEIRA')
    cols = [(x, y) for x in (-13.5, -4.5, 4.5, 13.5) for y in (-9, 0, 9)]
    for (x, y) in cols:
        K.put('colbase', 'PAV_PEDRA', (x, y, TZ), 0); K.put('coluna', 'PAV_MADEIRA', (x, y, TZ), 0)
    for y, rows in ((-9, 'ext'), (0, 'par'), (9, 'ext')):
        for x in (-9, 0, 9):
            K.put('arq', 'PAV_MADEIRA', (x, y, TZ), 0); K.put('prancha', 'PAV_MADEIRA', (x, y, TZ), 0)
    for x in (-13.5, 13.5):
        for y in (-4.5, 4.5):
            K.put('arq', 'PAV_MADEIRA', (x, y, TZ), 90); K.put('prancha', 'PAV_MADEIRA', (x, y, TZ), 90)
    for x in (-13.5, -4.5, 4.5, 13.5): K.put('viga', 'PAV_MADEIRA', (x, 0, TZ), 0)
    K.put('janela', 'PAV_MADEIRA', (-9, 0, TZ), 0); K.put('porta', 'PAV_MADEIRA', (0, 0, TZ), 0); K.put('janela', 'PAV_MADEIRA', (9, 0, TZ), 0)
    for x in (-9, 0, 9): K.put('parede', 'PAV_MADEIRA', (x, 9, TZ), 180)
    K.put('parede', 'PAV_MADEIRA', (13.5, 4.5, TZ), 90); K.put('parede', 'PAV_MADEIRA', (-13.5, 4.5, TZ), 270)
    for x in (-9, 0, 9):
        K.put('forro', 'PAV_MADEIRA', (x, -4.5, ZD), 0)
        K.put('tabua', 'PAV_MADEIRA', (x, -9, ZP), 0); K.put('tabua', 'PAV_MADEIRA', (x, 9, ZP), 0); K.put('tabua', 'PAV_MADEIRA', (x, 0, ZP), 0, (1, 1, .58))
    for x in (-13.5, 13.5):
        for y in (-4.5, 4.5): K.put('tabua', 'PAV_MADEIRA', (x, y, ZP), 90, (1, 1, 1.32))
    k = (2 * (13.5 + 2.1 + .6)) / 3 / VAO
    for i in (-1, 0, 1):
        K.put('terca', 'PAV_MADEIRA', (i * VAO * k, -9 - 2.1, ZD), 0, (k, 1, 1)); K.put('terca', 'PAV_MADEIRA', (i * VAO * k, 9 + 2.1, ZD), 0, (k, 1, 1))
    k2 = (2 * (9 + 2.1 + .6)) / 2 / VAO
    for sx in (-1, 1):
        for i in (-.5, .5): K.put('terca', 'PAV_MADEIRA', (sx * (13.5 + 2.1), i * VAO * k2, ZD), 90, (k2, 1, 1))
    K.put('placa', 'PAV_MADEIRA', (0, -9 - 3.05, ZP + 2.6), 0)
    K.m['placa'].rotation_euler = (math.radians(-13), 0, 0)
    # ------------------------------------------------ DOUGONG
    K.master('dg', k_dougong.principal, 'PAV_DOUGONG'); K.master('dgc', k_dougong.canto, 'PAV_DOUGONG'); K.master('dg_sim', k_dougong.simples, 'PAV_DOUGONG')
    for x in (-10.5, -7.5, -4.5, -1.5, 1.5, 4.5, 7.5, 10.5):
        K.put('dg', 'PAV_DOUGONG', (x, -9, ZP), 0); K.put('dg', 'PAV_DOUGONG', (x, 9, ZP), 180)
    for y in (-6, -3, 0, 3, 6):
        K.put('dg', 'PAV_DOUGONG', (13.5, y, ZP), 90); K.put('dg', 'PAV_DOUGONG', (-13.5, y, ZP), 270)
    for (x, y, r) in ((13.5, -9, 0), (13.5, 9, 90), (-13.5, 9, 180), (-13.5, -9, 270)): K.put('dgc', 'PAV_DOUGONG', (x, y, ZP), r)
    # ------------------------------------------------ TELHADO
    for which, nm in (('front', 'frente'), ('side', 'lado')):
        a = K.master('agua_' + nm, lambda w=which, n=nm: k_telhado.agua(R, w, 'KIT_agua_' + n), 'PAV_TELHADO')
        b = K.master('beiral_' + nm, lambda w=which, n=nm: k_telhado.beiral(R, w, 'KIT_beiral_' + n), 'PAV_TELHADO')
        for key in ('agua_' + nm, 'beiral_' + nm):
            K.put(key, 'PAV_TELHADO', (0, 0, 0), 0); K.put(key, 'PAV_TELHADO', (0, 0, 0), 180)
    Be, anchors = k_telhado.espigao(R); K.master('esp', Be, 'PAV_TELHADO')
    Bv, tip, tdir = k_telhado.viga_canto(R); K.master('vcanto', Bv, 'PAV_TELHADO')
    for key in ('esp', 'vcanto'):
        K.put(key, 'PAV_TELHADO', (0, 0, 0), 0); K.put(key, 'PAV_TELHADO', (0, 0, 0), 180)
        mm = mirror_mesh(K.m[key], K.m[key].name + '_esp', 'PAV_TELHADO', axis=1); K.m[key + '_m'] = mm; K.n[key + '_m'] = 0; mm['usado'] = True
        PLACE.append(dict(mesh=mm.data.name, pos=[0, 0, 0], rot=0, scale=[1, 1, 1]))
        K.put(key + '_m', 'PAV_TELHADO', (0, 0, 0), 180)
    Bc, zc = k_telhado.cumeeira(R); K.master('cume', Bc, 'PAV_TELHADO'); K.put('cume', 'PAV_TELHADO', (0, 0, 0), 0)
    K.master('chiwen', k_props.chiwen, 'PAV_PROPS'); Lr = R.EX - R.RS
    K.put('chiwen', 'PAV_PROPS', (Lr - .6, 0, zc), 0); K.put('chiwen', 'PAV_PROPS', (-Lr + .6, 0, zc), 180)
    K.master('imortal', k_props.imortal, 'PAV_PROPS'); K.master('chuishou', k_props.chuishou, 'PAV_PROPS')
    for i in range(3): K.master('besta%d' % i, lambda i=i: k_props.besta(i), 'PAV_PROPS')
    order = ['imortal', 'besta0', 'besta1', 'besta2', 'chuishou']
    for (sx, sy) in ((1, 1), (-1, -1), (1, -1), (-1, 1)):          # (1,1)=frente-direita original; espelhos por sinal
        for key, (p, t) in zip(order, anchors):
            q = Vector((p.x * sx, p.y * (1 if sx * sy > 0 else -1) * (1 if sx > 0 else -1), p.z))
            tt = Vector((t.x * sx, t.y * (1 if sx * sy > 0 else -1) * (1 if sx > 0 else -1), 0))
            # quadrantes: FR (x+,y-), BL = rot180 (x-,y+), BR = espelho Y (x+,y+), FL = rot180 do espelho (x-,y-)
            if (sx, sy) == (1, 1): q, tt = Vector(p), Vector((t.x, t.y, 0))
            elif (sx, sy) == (-1, -1): q, tt = Vector((-p.x, -p.y, p.z)), Vector((-t.x, -t.y, 0))
            elif (sx, sy) == (1, -1): q, tt = Vector((p.x, -p.y, p.z)), Vector((t.x, -t.y, 0))
            else: q, tt = Vector((-p.x, p.y, p.z)), Vector((-t.x, t.y, 0))
            ang = math.degrees(math.atan2(tt.y, tt.x)) + 90
            K.put(key, 'PAV_PROPS', (q.x, q.y, q.z + (1.15 if key == 'chuishou' else 1.06)), ang)
    # ------------------------------------------------ PROPS + VEGETACAO + CHAO
    K.master('lant', k_props.lanterna_palacio, 'PAV_PROPS')
    for x in (-9, 9): K.put('lant', 'PAV_PROPS', (x, -9, TZ + k_madeira.Z_ARQ), 0, (.85, .85, .85))
    K.master('pinA', lambda: k_veg.pinheiro(1, 'KIT_pinheiro_a', 1), 'PAV_VEG'); K.master('pinB', lambda: k_veg.pinheiro(2, 'KIT_pinheiro_b', -1), 'PAV_VEG')
    K.master('arbA', lambda: k_veg.arbusto(1, 'KIT_arbusto_a'), 'PAV_VEG'); K.master('arbB', lambda: k_veg.arbusto(2, 'KIT_arbusto_b'), 'PAV_VEG')
    K.master('tufo', k_veg.tufo, 'PAV_VEG')
    K.put('jard', 'PAV_PEDRA', (-11.5, -21.5, 0), 0); K.put('jard', 'PAV_PEDRA', (11.5, -21.5, 0), 22.5)
    K.put('pinA', 'PAV_VEG', (-11.5, -21.5, 1.7), 20); K.put('pinB', 'PAV_VEG', (11.5, -21.5, 1.7), -35, (.92, .92, .92))
    for (x, y, r, key, s) in ((-17.5, -18.6, 0, 'arbA', 1.0), (-20.2, -17.6, 80, 'arbB', .8), (17.8, -18.4, 200, 'arbB', 1.05), (20.6, -17.8, 40, 'arbA', .75), (23.3, -9, 120, 'arbA', .9), (-23.4, -6, 300, 'arbB', .95)):
        K.put(key, 'PAV_VEG', (x, y, 0), r, (s, s, s))
    for (x, y, r, s) in ((-15.2, -17.4, 0, 1), (-8.2, -17.3, 50, .9), (8.3, -17.2, 100, 1.1), (15.4, -17.5, 170, .95), (22.6, -13.4, 30, 1), (-22.7, -12.2, 220, 1.05), (-13.6, -22.8, 10, .8), (13.2, -23.4, 140, .85)):
        K.put('tufo', 'PAV_VEG', (x, y, 0), r, (s, s, s))
    # ------------------------------------------------ KIT 2: muro com portao pequeno, estandartes, suportes de espada, vasos
    for key, fn in (('estand', k_kit2.estandarte), ('sup_esp', k_kit2.suporte_espada), ('vaso', k_kit2.vaso), ('muro', k_kit2.muro_seg),
                    ('mpilar', k_kit2.muro_pilar), ('tel_portao', k_kit2.telhado_portao)):
        K.master(key, fn, 'PAV_KIT2')
    XM = 36.0                                                       # linha do muro, a direita do pavilhao, ao longo de Y
    for y in (-18, -9, 9, 18): K.put('muro', 'PAV_KIT2', (XM, y, 0), 90)
    for y in (-22.5, 22.5): K.put('mpilar', 'PAV_KIT2', (XM, y, 0), 0)
    # portao pequeno = pecas que JA existem + o telhado de duas aguas. Proporcao corrigida na autorrevisao: com a coluna inteira
    # (13) o portao lia "poste com chapeu"; aqui a coluna entra a 72% da altura e o conjunto desce junto (o kit aceita escala).
    KZ = .72; topo = k_madeira.H_COL * KZ                          # 9.36
    dz = topo - k_madeira.H_COL                                     # a arquitrave/prancha tem a cota embutida: desce por offset
    for y in (-4.5, 4.5):
        K.put('colbase', 'PAV_KIT2', (XM, y, 0), 0); K.put('coluna', 'PAV_KIT2', (XM, y, 0), 0, (1, 1, KZ))
        K.put('dg_sim', 'PAV_KIT2', (XM, y, topo + .5), 90)
    K.put('arq', 'PAV_KIT2', (XM, 0, dz), 90); K.put('prancha', 'PAV_KIT2', (XM, 0, dz), 90)
    zt = topo + .5 + k_dougong.Z1 + k_dougong.AH + .74               # topo dos sheng do dougong simples
    K.put('terca', 'PAV_KIT2', (XM, 0, zt), 90, (1.3, 1, 1))
    K.put('tel_portao', 'PAV_KIT2', (XM, 0, zt + 1.0 - (k_kit2.PORTAO_RISE - .42)), 90)
    for sx in (-1, 1):
        K.put('estand', 'PAV_KIT2', (sx * 16.5, -27.5, 0), 0)
        K.put('sup_esp', 'PAV_KIT2', (sx * 7.2, -31.5, 0), 0)
        K.put('vaso', 'PAV_PROPS', (sx * 2.9, -1.75, TZ), 0)
    g = Builder('PAV_chao'); g.add(t_box(-60, 60, -60, 50, -.6, 0), 'piso', .5); g.finish('PAV_CHAO')
    # pecas do kit que nao entram no pavilhao ficam na bancada (para o bake nao pega-las enterradas na origem)
    K.master('dg_int', k_dougong.intermediario, 'PAV_BANCADA'); K.master('lantV', k_props.lanterna_vermelha, 'PAV_BANCADA')
    bench = [k for k, o in K.m.items() if not o.get('usado', False) and not k.endswith('_m')]
    for i, key in enumerate(bench): K.put(key, 'PAV_BANCADA', (70 + 9 * (i % 4), -20 + 9 * (i // 4), 6 if key == 'lantV' else 0), 0)
    tot = 0; rep = []
    for key, o in K.m.items():
        n = K.n.get(key, 0) + 1; tr = o.get('tris', 0); tot += tr * n; rep.append('%-16s %6d tris x %3d' % (o.name, tr, n))
    rep.append('TOTAL em cena ~%d tris; malhas unicas %d (%d tris)' % (tot, len(K.m), sum(o.get('tris', 0) for o in K.m.values())))
    return K, R, rep


ATLAS = {
    'A_PEDRA': ['KIT_sumeru_seg', 'KIT_sumeru_canto', 'KIT_piso_mod', 'KIT_bal_seg', 'KIT_bal_poste', 'KIT_escada', 'KIT_col_base', 'KIT_jardineira', 'KIT_bal_tambor'],
    'A_MAD1': ['KIT_coluna', 'KIT_arquitrave', 'KIT_prancha', 'KIT_viga_alpendre', 'KIT_placa'],
    'A_VAOS': ['KIT_vao_janela', 'KIT_vao_porta', 'KIT_vao_parede'],
    'A_MAD2': ['KIT_forro_alpendre', 'KIT_tabua_dougong', 'KIT_terca', 'KIT_viga_canto', 'KIT_beiral_frente', 'KIT_beiral_lado'],
    'A_DOUG': ['KIT_dougong_principal', 'KIT_dougong_canto', 'KIT_dougong_intermediario', 'KIT_dougong_simples'],
    'A_TELHA': ['KIT_agua_frente', 'KIT_agua_lado', 'KIT_espigao', 'KIT_cumeeira'],
    'A_PROPS': ['KIT_chiwen', 'KIT_imortal', 'KIT_chuishou', 'KIT_besta_0', 'KIT_besta_1', 'KIT_besta_2', 'KIT_lanterna_palacio', 'KIT_lanterna_vermelha'],
    'A_VEG': ['KIT_pinheiro_a', 'KIT_pinheiro_b', 'KIT_arbusto_a', 'KIT_arbusto_b', 'KIT_tufo_a'],
    'A_KIT2': ['KIT_estandarte', 'KIT_suporte_espada', 'KIT_vaso', 'KIT_muro_seg', 'KIT_muro_pilar', 'KIT_telhado_portao'],
}
ISOLAR = {'KIT_piso_mod': (95, 20, 4.0)}      # pecas genericas: assar longe dos vizinhos para o AO nao marcar um contexto especifico

def remirror():
    """recria as malhas espelhadas a partir das originais (depois do UV, para herdarem as mesmas UVs)."""
    out = []
    for o in bpy.data.objects:
        srcn = o.get('espelho_de')
        if not srcn: continue
        src = bpy.data.objects[srcn]; bm = bmesh.new(); bm.from_mesh(src.data)
        bmesh.ops.scale(bm, vec=(1, -1, 1), verts=bm.verts); bmesh.ops.reverse_faces(bm, faces=bm.faces)
        bm.to_mesh(o.data); bm.free(); o.data.materials.clear()
        for m in src.data.materials: o.data.materials.append(m)
        out.append(o.name)
    return out

def bake_set(atlases, which, size=2048, samples=24):
    import k_materiais
    out = []
    # o bake precisa selecionar os objetos: garante que TODAS as colecoes PAV_* estao na view layer (um render anterior
    # com k_render.only() pode ter excluido a PAV_BANCADA, onde moram as pecas do kit que nao entram no pavilhao)
    for lc in bpy.context.view_layer.layer_collection.children:
        if lc.name.startswith('PAV_'): lc.exclude = False; lc.collection.hide_render = False
    bpy.context.view_layer.update()
    for atlas in atlases:
        objs = [bpy.data.objects[n] for n in ATLAS[atlas]]; moved = {}
        for o in objs:
            if o.name in ISOLAR: moved[o] = o.location.copy(); o.location = ISOLAR[o.name]
        bpy.context.view_layer.update()
        try: out.append(k_materiais.bake(atlas, objs, which, size=size, samples=samples))
        finally:
            for o, l in moved.items(): o.location = l
    return out
