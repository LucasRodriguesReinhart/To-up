# lv_build.py - construcoes do lobby: portao sul, Forja do Ignis (monumental),
# arcada do Santuario (viagem rapida), pavilhao da Loja, muros de perimetro.
# Linguagem: pedra clara + molduras de marmore + detalhes dourados + vitrais (ref. imagens 1,3,5,6,8).
import math
import importlib
import lvlib, lv_kit
importlib.reload(lvlib)
importlib.reload(lv_kit)
from lvlib import box, cyl, ball, lathe, torus, ngon_prism, ring_prism, reg_poly
import bpy, bmesh
from lvlib import _xform

TAU = math.tau
FLOOR = 5.0
TERR = 8.0

# ---------------------------------------------------------------- util: texto dourado
def gold_text(out, text, pos, rot=(0, 0, 0), size=6.0, depth=1.0, mat='GOLD'):
    cu = bpy.data.curves.new('txt_' + text, 'FONT')
    cu.body = text
    cu.size = size
    cu.extrude = depth / 2
    cu.align_x = 'CENTER'
    cu.align_y = 'CENTER'
    ob = bpy.data.objects.new('txt_' + text, cu)
    bpy.context.scene.collection.objects.link(ob)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bpy.data.objects.remove(ob, do_unlink=True)
    bm = bmesh.new()
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)
    # texto e criado no plano XY olhando +Z; levanta pro plano XZ olhando -Y
    _xform(bm, (0, 0, 0), (math.pi/2, 0, 0))
    _xform(bm, pos, rot)
    out.add(mat, bm)

# ---------------------------------------------------------------- arco apontado com moldura
def pointed_arch_frame(out, pos, w, spring_h, apex_h, depth, mat='MARB', rim='GOLD', rot_z=0.0):
    """Moldura de arco ogival: 2 arcos de circulo se cruzando no apice.
    pos = centro da abertura no nivel do chao. Plano XZ, profundidade Y."""
    x, y, z = pos
    r = w * .78
    cxs = [x - w/2 + w - r, x + w/2 - w + r]  # centros deslocados
    # jambas retas ate spring_h
    for sx in (-1, 1):
        out.add(mat, box((1.6, depth, spring_h), (x + sx * (w/2 + .3), y, z + spring_h/2), (0, 0, rot_z), bevel=.15))
        out.add(rim, box((.5, depth + .3, spring_h), (x + sx * (w/2 + 1.2), y, z + spring_h/2), (0, 0, rot_z)))
    # arcos (aproximados por segmentos de torus)
    for k, cx in enumerate([x - w/2 + r * 0 + (w/2 - r), x + (r - w/2)]):
        pass
    # implementacao simples: pontos ao longo do arco ogival
    steps = 10
    pts = []
    for i in range(steps + 1):
        t = i / steps
        # curva: do pe esquerdo ao apice (arco de raio r centrado no pe direito)
        a = math.pi - t * (math.pi - math.acos((w/2) / r) if r > w/2 else math.pi/2)
    # abordagem robusta: dois arcos de circulo
    r = w * .9
    c1 = (x + w/2 - r, z + spring_h)   # centro do arco que sobe da esquerda
    c2 = (x - w/2 + r, z + spring_h)
    apex_z = z + spring_h + math.sqrt(max(r*r - (w/2 - (r - w/2))**2, 0))
    for (cx, cz), a0, a1 in [ (c1, 0, None), (c2, None, math.pi) ]:
        # angulo do apice
        ax = x  # apice em x central
        cosv = max(-1, min(1, (ax - cx) / r))
        aapex = math.acos(cosv)
        if a0 is None:
            a0v, a1v = aapex, math.pi
        else:
            a0v, a1v = 0.0, aapex
        n = 7
        prev = None
        for i in range(n + 1):
            t = i / n
            a = a0v + (a1v - a0v) * t
            px = cx + math.cos(a) * r
            pz = cz + math.sin(a) * r
            if prev:
                mx, mz = (px + prev[0]) / 2, (pz + prev[1]) / 2
                L = math.hypot(px - prev[0], pz - prev[1])
                ang = math.atan2(pz - prev[1], px - prev[0])
                bmv = box((L + .22, depth, 1.6), (0, 0, 0))
                _xform(bmv, (mx, y, mz), (0, -ang, 0))
                out.add(mat, bmv)
                bmr = box((L + .22, depth + .3, .5), (0, 0, 0))
                _xform(bmr, (mx + (mz - z) * 0, y, mz + .95), (0, -ang, 0))
                out.add(rim, bmr)
            prev = (px, pz)

# ---------------------------------------------------------------- PORTAO SUL (saida p/ Area 1)
def south_gate(out):
    y = -150
    # torres gemeas
    for s in (-1, 1):
        x = s * 23
        out.add('TRIM', box((11, 11, 1.6), (x, y, FLOOR + .8), bevel=.2))
        out.add('STONE', box((9.6, 9.6, 25), (x, y, FLOOR + 1.6 + 12.5)))
        # pilastras de canto
        for sx in (-1, 1):
            for sy in (-1, 1):
                out.add('MARB', box((1.4, 1.4, 25), (x + sx * 4.6, y + sy * 4.6, FLOOR + 1.6 + 12.5), bevel=.12))
        # janela ogival estreita com vitral ciano (frente e tras)
        for sy in (-1, 1):
            out.add('MARB', box((3.4, .8, 8.5), (x, y + sy * 4.9, FLOOR + 14), bevel=.1))
            out.add('GLASS', box((2.4, .9, 7.2), (x, y + sy * 4.9, FLOOR + 14)))
            out.add('GOLD', box((.35, 1.0, 7.2), (x, y + sy * 4.95, FLOOR + 14)))
        # cornija + coroamento piramidal com ponta dourada
        out.add('MARB', box((11.4, 11.4, 1.1), (x, y, FLOOR + 27.2), bevel=.15))
        out.add('GOLD', box((11.8, 11.8, .4), (x, y, FLOOR + 28.0)))
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=7.4, radius2=.4, depth=7.5)
        _xform(bm, (x, y, FLOOR + 28.2 + 3.75), (0, 0, math.pi/4))
        out.add('GLASS', bm)
        out.add('GOLD', lathe([(.5, 0), (.6, .2), (.15, .6), (.02, 2.6)], (x, y, FLOOR + 35.6), seg=8))
        # lanternas nas faces internas
        out.add('NEON', ball(.55, (x - s * 5.4, y - 3.4, FLOOR + 9), seg=8))
        out.add('GOLD', lathe([(.62, 0), (.5, .2), (.2, .5)], (x - s * 5.4, y - 3.4, FLOOR + 9.4), seg=8))
    # arco central entre torres
    pointed_arch_frame(out, (0, y, FLOOR), 15, 11, 21, 6.5)
    # preenchimento lateral entre o arco e as torres (fecha o vao)
    for s in (-1, 1):
        out.add('STONE', box((9.6, 5.6, 15.9), (s * 13.6, y, FLOOR + 13.05)))
        out.add('MARB', box((1.0, 6.0, 15.9), (s * 9.1, y, FLOOR + 13.05), bevel=.1))
    # verga superior + parapeito
    out.add('STONE', box((34, 6.5, 7.5), (0, y, FLOOR + 24.5)))
    out.add('MARB', box((35, 7.2, 1.0), (0, y, FLOOR + 28.6), bevel=.15))
    lv_kit.balustrade(out, (-17, y - 3.3), (17, y - 3.3), FLOOR + 29.2, h=2.6)
    lv_kit.balustrade(out, (-17, y + 3.3), (17, y + 3.3), FLOOR + 29.2, h=2.6)
    # emblema dourado acima do arco: anel + gema facetada (identidade de mineracao)
    out.add('GOLD', torus(4.0, .6, (0, y - 3.4, FLOOR + 33.0), (math.pi/2, 0, 0), seg=18, sides=7))
    out.add('BLUE', cyl(3.3, .5, (0, y - 3.3, FLOOR + 33.0), rot=(math.pi/2, 0, 0), seg=16))
    gem = bmesh.new()
    bmesh.ops.create_cone(gem, cap_ends=True, segments=6, radius1=2.2, radius2=.9, depth=1.6)
    _xform(gem, (0, y - 3.6, FLOOR + 33.7), (math.pi/2, 0, 0))
    out.add('NEON', gem)
    gem2 = bmesh.new()
    bmesh.ops.create_cone(gem2, cap_ends=True, segments=6, radius1=2.2, radius2=.1, depth=1.8)
    _xform(gem2, (0, y - 3.6, FLOOR + 32.0), (-math.pi/2, 0, 0))
    out.add('NEON', gem2)
    # portoes dourados abertos (2 folhas)
    for s in (-1, 1):
        bm = bmesh.new()
        # folha: grade de barras verticais + travessas
        leafw = 7.2
        for i in range(5):
            b2 = box((.5, .5, 16.5), (i * (leafw/4) - leafw/2, 0, 8.25))
            tmp = bpy.data.meshes.new('t'); b2.to_mesh(tmp); b2.free(); bm.from_mesh(tmp); bpy.data.meshes.remove(tmp)
        for zz in (2, 8, 14.5):
            b2 = box((leafw, .45, .9), (0, 0, zz))
            tmp = bpy.data.meshes.new('t'); b2.to_mesh(tmp); b2.free(); bm.from_mesh(tmp); bpy.data.meshes.remove(tmp)
        # pontas de lanca
        for i in range(5):
            b2 = lathe([(.4, 0), (.02, 1.4)], (i * (leafw/4) - leafw/2, 0, 16.6), seg=6)
            tmp = bpy.data.meshes.new('t'); b2.to_mesh(tmp); b2.free(); bm.from_mesh(tmp); bpy.data.meshes.remove(tmp)
        # abre a folha ~105 graus pra dentro
        ang = s * math.radians(105)
        M = None
        _xform(bm, (0, 0, 0), (0, 0, ang))
        px = s * 7.5
        _xform(bm, (px, y + 2.2, FLOOR))
        out.add('GOLD', bm)

# ---------------------------------------------------------------- FORJA DO IGNIS (norte)
def forge(out):
    yF = 118            # plano da fachada (mais perto da praca = mais monumental)
    zb = TERR           # piso do terraco
    CH = 54             # altura do corpo central
    WH = 34             # altura das alas
    # ---- corpo central ----
    out.add('STONE', box((56, 30, CH), (0, yF + 15, zb + CH/2)))
    for sx in (-1, 1):
        out.add('MARB', box((3.6, 2.6, CH), (sx * 26, yF - .9, zb + CH/2), bevel=.2))
        out.add('MARB', box((3.6, 2.6, CH), (sx * 16, yF - .9, zb + CH/2), bevel=.2))
        out.add('GOLD', box((3.9, .5, 1.3), (sx * 26, yF - 2.1, zb + CH - 2)))
        out.add('GOLD', box((3.9, .5, 1.3), (sx * 16, yF - 2.1, zb + CH - 2)))
    for zz, hh in [(zb + 30, 1.5), (zb + CH - .9, 2.0)]:
        out.add('MARB', box((58, 32, hh), (0, yF + 15, zz), bevel=.2))
    out.add('GOLD', box((58.5, 32.5, .55), (0, yF + 15, zb + CH + .4)))
    lv_kit.balustrade(out, (-28, yF - .8), (28, yF - .8), zb + CH + .7, h=2.8)
    # ---- portal ogival com alcova de forja ----
    pointed_arch_frame(out, (0, yF - 1.2, zb), 13, 13, 22, 5.0)
    out.add('DARK', box((19, 1.2, 27), (0, yF + 12, zb + 13.5)))
    out.add('DARK', box((18, 14, .8), (0, yF + 5, zb + 26.6)))
    for sx in (-1, 1):
        out.add('STONE', box((2.6, 14, 27), (sx * 9.0, yF + 5, zb + 13.5)))
    out.add('STONE', box((21, 14, 3.5), (0, yF + 5, zb + 24.6)))
    out.add('TILE2', box((17, 15, .5), (0, yF + 4.2, zb + .25)))
    # boca da forja incandescente
    out.add('TRIM', torus(5.2, 1.1, (0, yF + 11, zb + 5.4), (math.pi/2, 0, 0), seg=16, sides=7, arc=math.pi))
    out.add('EMBER', torus(4.5, .55, (0, yF + 10.8, zb + 5.4), (math.pi/2, 0, 0), seg=16, sides=6, arc=math.pi))
    out.add('EMBER', box((8.4, .6, 6.0), (0, yF + 11.2, zb + 3.0)))
    out.add('DARK', box((10.0, .4, 7.4), (0, yF + 11.6, zb + 3.7)))
    for xx in (-5.0, 0, 5.0):
        out.add('EMBER', box((1.7, 9, .12), (xx, yF + 6.0, zb + .56)))
    # ---- rosacea ----
    zc = zb + 39
    out.add('MARB', torus(6.4, 1.1, (0, yF - 1.2, zc), (math.pi/2, 0, 0), seg=22, sides=7))
    out.add('GOLD', torus(5.4, .45, (0, yF - 1.3, zc), (math.pi/2, 0, 0), seg=22, sides=6))
    out.add('EMBER', cyl(5.0, .6, (0, yF - .9, zc), rot=(math.pi/2, 0, 0), seg=20))
    for i in range(8):
        a = i / 8 * TAU
        out.add('GOLD', box((.65, .5, 9.8), (0, yF - 1.4, zc), (0, a, 0)))
    # ---- texto FORJA ----
    gold_text(out, 'FORJA', (0, yF - 2.8, zb + CH - 5.2), size=7.2, depth=1.8)
    # ---- alas laterais ----
    for s in (-1, 1):
        xw = s * 45
        out.add('STONE', box((34, 26, WH), (xw, yF + 16, zb + WH/2)))
        out.add('MARB', box((35, 27, 1.4), (xw, yF + 16, zb + WH + .7), bevel=.2))
        out.add('GOLD', box((35.4, 27.4, .5), (xw, yF + 16, zb + WH + 1.6)))
        lv_kit.balustrade(out, (xw - 17, yF + 2.8), (xw + 17, yF + 2.8), zb + WH + 1.9, h=2.6)
        for k in (-1, 1):
            wx = xw + k * 8.5
            out.add('MARB', box((6.0, 1.2, 15), (wx, yF + 3.0, zb + 15.5), bevel=.15))
            out.add('GLASS', box((4.6, 1.0, 13.4), (wx, yF + 2.9, zb + 15.5)))
            out.add('GOLD', box((.55, 1.25, 13.4), (wx, yF + 2.85, zb + 15.5)))
            out.add('GOLD', box((4.6, 1.25, .55), (wx, yF + 2.85, zb + 15.5)))
            out.add('MARB', lathe([(2.9, 0), (2.4, .9), (.45, 1.6)], (wx, yF + 3.5, zb + 23.2), seg=10))
        out.add('TRIM', box((35, 27.5, 2.4), (xw, yF + 16, zb + 1.2)))
    out.add('TRIM', box((57, 31, 2.4), (0, yF + 15, zb + 1.2)))
    # ---- torre central ----
    tz = zb + CH + 1
    pts8 = reg_poly(14, 8, TAU/16)
    out.add('STONE', ngon_prism(pts8, 19, (0, yF + 15, tz)))
    for i in range(8):
        a = i / 8 * TAU + TAU/16
        px, py = math.cos(a) * 13.2, math.sin(a) * 13.2
        out.add('MARB', box((2.4, 2.4, 19), (px, yF + 15 + py, tz + 9.5), (0, 0, a), bevel=.15))
    for i in range(8):
        a = i / 8 * TAU
        px, py = math.cos(a) * 13.7, math.sin(a) * 13.7
        out.add('EMBER', box((2.8, 1.2, 9), (px, yF + 15 + py, tz + 9.5), (0, 0, a + math.pi/2)))
        out.add('MARB', box((3.7, .8, 10), (px * .99, yF + 15 + py * .99, tz + 9.5), (0, 0, a + math.pi/2)))
    out.add('MARB', ngon_prism(reg_poly(15, 8, TAU/16), 1.5, (0, yF + 15, tz + 19)))
    out.add('GOLD', ngon_prism(reg_poly(15.3, 8, TAU/16), .55, (0, yF + 15, tz + 20.5)))
    dome_z = tz + 21.2
    prof = [(math.cos(t/6 * math.pi/2) * 13.6, math.sin(t/6 * math.pi/2) * 10.4) for t in range(7)]
    out.add('GLASS', lathe(prof, (0, yF + 15, dome_z), seg=20))
    for i in range(8):
        a = i / 8 * TAU + TAU/16
        bmrib = bmesh.new()
        prev = None
        for k in range(7):
            t = k / 6
            rr = math.cos(t * math.pi/2) * 13.9
            zz = math.sin(t * math.pi/2) * 10.4
            px, py = math.cos(a) * rr, math.sin(a) * rr
            v1 = bmrib.verts.new((px - math.sin(a)*.42, py + math.cos(a)*.42, zz))
            v2 = bmrib.verts.new((px + math.sin(a)*.42, py - math.cos(a)*.42, zz))
            v3 = bmrib.verts.new((px * 1.03, py * 1.03, zz + .32))
            if prev:
                bmrib.faces.new([prev[0], v1, v3, prev[2]])
                bmrib.faces.new([prev[2], v3, v2, prev[1]])
            prev = (v1, v2, v3)
        bmesh.ops.recalc_face_normals(bmrib, faces=bmrib.faces)
        _xform(bmrib, (0, yF + 15, dome_z))
        out.add('GOLD', bmrib)
    out.add('GOLD', lathe([(1.5, 0), (1.7, .45), (.55, 1.0), (.65, 1.5), (.02, 5.6)], (0, yF + 15, dome_z + 10.3), seg=10))
    # pinaculos nos cantos do corpo central
    for sx in (-1, 1):
        for sy2 in (0, 1):
            px = sx * 26
            py = yF + (0 if sy2 == 0 else 30)
            out.add('MARB', box((3.2, 3.2, 3.8), (px, py, zb + CH + .8), bevel=.2))
            out.add('GLASS', lathe([(1.7, 0), (.05, 4.8)], (px, py, zb + CH + 4.6), seg=8))
            out.add('GOLD', lathe([(.45, 0), (.02, 1.8)], (px, py, zb + CH + 9.2), seg=6))
    # ---- props de forja no terraco ----
    out.add('TRIM', box((5.4, 4.2, 1.6), (14, 102, zb + .8), bevel=.2))
    out.add('TRIM', box((3.2, 2.6, 1.6), (14, 102, zb + 2.2)))
    out.add('GOLD', box((4.6, 2.2, 1.5), (14, 102, zb + 3.6)))
    out.add('GOLD', cyl(.75, 1.8, (16.6, 102, zb + 3.0), rot=(0, math.pi/2, 0), seg=8, r2=.35))
    for sx in (-1, 1):
        bx = sx * 27
        out.add('TRIM', box((2.2, 2.2, .5), (bx, 106, zb + .25)))
        out.add('TRIM', cyl(.5, 5.4, (bx, 106, zb + .5), seg=8))
        out.add('GOLD', lathe([(.6, 0), (1.6, .8), (1.8, 1.4), (1.2, 1.6)], (bx, 106, zb + 5.9), seg=10))
        out.add('EMBER', ball(1.15, (bx, 106, zb + 7.6), seg=8))
    for i, (dx, dy, dz, rr) in enumerate([(0, 0, 0, 0), (1.6, .4, 0, .3), (.8, .2, 1, .15)]):
        out.add('GOLD', box((2.4, 1.1, .9), (19 + dx, 99 + dy, zb + .45 + dz * .95), (0, 0, rr)))

# ---------------------------------------------------------------- SANTUARIO (viagem rapida, leste)
def santuario(out, side=1):
    """Arcada de 6 baias no terraco leste. side=+1 -> +X do Blender."""
    x0 = side * 132          # parede de fundo
    cores = ['LEAFAZ', 'LEAFGD', 'LEAFCY', 'LEAFLV', 'WATER', 'EMBER']  # tema 1..6
    # plataforma ja vem de lv_floor.side_terraces
    # parede de fundo continua
    out.add('STONE', box((3, 82, 17), (x0 + side * 4, 0, TERR + 8.5)))
    out.add('MARB', box((3.6, 84, 1.2), (x0 + side * 4, 0, TERR + 17.2), bevel=.15))
    out.add('GOLD', box((3.8, 84.5, .4), (x0 + side * 4, 0, TERR + 18.0)))
    for i in range(6):
        yb = -32.5 + i * 13
        # colunas da baia
        for sy in (-1, 1):
            py = yb + sy * 5.2
            out.add('TRIM', box((2.0, 2.0, .5), (x0, py, TERR + .25)))
            out.add('MARB', lathe([(.8, 0), (.65, .4), (.62, 8.6), (.75, 9.1), (.85, 9.5), (.78, 9.9)],
                                  (x0, py, TERR + .5), seg=10))
            out.add('GOLD', box((1.8, 1.8, .35), (x0, py, TERR + 10.6), (0, 0, 0)))
        # arco romano
        out.add('MARB', torus(5.2, .75, (x0, yb, TERR + 10.8), (0, math.pi/2, 0), seg=12, sides=6, arc=math.pi))
        out.add('GOLD', torus(5.2, .3, (x0 - side * .5, yb, TERR + 10.8), (0, math.pi/2, 0), seg=12, sides=5, arc=math.pi))
        # entablamento
        out.add('MARB', box((3.4, 13.2, 1.6), (x0, yb, TERR + 17.0), bevel=.15))
        # nicho de fundo com vitral da cor do tema + emblema
        out.add('MARB', box((1.4, 7.6, 10.5), (x0 + side * 2.4, yb, TERR + 7.2), bevel=.1))
        out.add(cores[i], box((1.5, 6.2, 9.2), (x0 + side * 2.5, yb, TERR + 7.2)))
        out.add('GOLD', torus(2.1, .3, (x0 + side * 1.6, yb, TERR + 11.5), (0, math.pi/2, 0), seg=14, sides=5))
        # pedestal do disco de viagem
        px = x0 - side * 7.5
        out.add('TRIM', cyl(4.4, .5, (px, yb, TERR), seg=18, bevel=.08))
        out.add('MARB', cyl(3.9, .5, (px, yb, TERR + .5), seg=18, bevel=.08))
        out.add(cores[i], cyl(3.1, .3, (px, yb, TERR + 1.0), seg=16))
        out.add('GOLD', torus(3.35, .18, (px, yb, TERR + 1.2), seg=18, sides=5))
        out.add('NEON', torus(2.5, .1, (px, yb, TERR + 1.32), seg=16, sides=5))
    # coroamento central: fronton com emblema
    out.add('MARB', box((3.8, 15, 3.2), (x0, 0, TERR + 19.4), bevel=.2))
    out.add('GOLD', torus(2.6, .4, (x0 - side * 2.2, 0, TERR + 21.0), (0, math.pi/2, 0), seg=16, sides=6))
    out.add('NEON', cyl(2.0, .5, (x0 - side * 1.9, 0, TERR + 21.0), rot=(0, math.pi/2, 0), seg=14))

# ---------------------------------------------------------------- LOJA DE MOCHILAS (oeste)
def loja(out, side=-1):
    x0 = side * 124          # frente do pavilhao
    # corpo
    out.add('STONE', box((22, 44, 15), (x0 + side * 11, 0, TERR + 7.5)))
    out.add('MARB', box((23, 45, 1.2), (x0 + side * 11, 0, TERR + 15.6), bevel=.2))
    out.add('GOLD', box((23.4, 45.4, .4), (x0 + side * 11, 0, TERR + 16.4)))
    lv_kit.balustrade(out, (x0 + side * 1.5, -22.5), (x0 + side * 1.5, 22.5), TERR + 16.6, h=2.6)
    # telhado piramidal raso central
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=15, radius2=1.2, depth=6.5)
    _xform(bm, (x0 + side * 11, 0, TERR + 16.6 + 3.25), (0, 0, math.pi/4))
    out.add('GLASS', bm)
    out.add('GOLD', lathe([(.9, 0), (.3, .5), (.02, 2.8)], (x0 + side * 11, 0, TERR + 23.2), seg=8))
    # 3 arcos frontais
    for i, yb in enumerate((-13, 0, 13)):
        for sy in (-1, 1):
            py = yb + sy * 5.4
            out.add('MARB', lathe([(.75, 0), (.6, .4), (.58, 7.6), (.7, 8.1), (.8, 8.5)], (x0, py, TERR), seg=10))
            out.add('GOLD', box((1.7, 1.7, .3), (x0, py, TERR + 8.9)))
        out.add('MARB', torus(5.4, .7, (x0, yb, TERR + 9.2), (0, math.pi/2, 0), seg=12, sides=6, arc=math.pi))
        out.add('GOLD', torus(5.4, .28, (x0 - side * .5, yb, TERR + 9.2), (0, math.pi/2, 0), seg=12, sides=5, arc=math.pi))
        # vitrine/alcova
        if i == 1:
            out.add('DARK', box((1.2, 9.4, 11), (x0 + side * 2.2, yb, TERR + 5.5)))
            # balcao
            out.add('WOOD', box((3.2, 8.6, 2.6), (x0 + side * 4.2, yb, TERR + 1.3)))
            out.add('MARB', box((3.6, 9.0, .5), (x0 + side * 4.2, yb, TERR + 2.85)))
            # mochilas expostas (volumes simples coloridos)
            for k, (dy, cor) in enumerate([(-2.6, 'LEAFAZ'), (0, 'EMBER'), (2.6, 'LEAFGD')]):
                out.add(cor, box((1.6, 1.8, 2.2), (x0 + side * 4.2, yb + dy, TERR + 4.2), bevel=.3))
                out.add('WOOD', box((.4, 1.2, .5), (x0 + side * 3.4, yb + dy, TERR + 5.0)))
        else:
            out.add('DARK', box((1.2, 9.4, 11), (x0 + side * 2.2, yb, TERR + 5.5)))
            out.add('GLASS', box((.8, 8.4, 9.6), (x0 + side * 1.8, yb, TERR + 5.2)))
    # faixa de letreiro
    out.add('BLUE', box((1.2, 20, 3.0), (x0 - side * .4, 0, TERR + 13.0)))
    gold_text(out, 'LOJA', (x0 - side * 1.4, 0, TERR + 13.0), rot=(0, 0, side < 0 and math.pi/2 or -math.pi/2), size=2.6, depth=.8)
    # OBS: rotacao do texto ajustada no layout conforme o eixo real do Studio

# ---------------------------------------------------------------- MUROS DE PERIMETRO
def perimeter(out):
    """Muro alto com arcadas cegas + tampa dourada. Norte fechado pela Forja."""
    H = 21
    # oeste e leste: fecham do canto sul (-150) ao canto norte (150)
    for s in (-1, 1):
        x = s * 152
        out.add('STONE', box((5, 302, H), (x, 0, FLOOR - 2 + H/2)))
        out.add('MARB', box((6, 304, 1.4), (x, 0, FLOOR - 2 + H + .7), bevel=.2))
        out.add('GOLD', box((6.4, 304.5, .4), (x, 0, FLOOR - 2 + H + 1.6)))
        # arcadas cegas
        for yy in range(-132, 133, 24):
            out.add('TRIM', box((1.2, 7.5, 12), (x - s * 2.4, yy, FLOOR + 5)))
            out.add('MARB', torus(3.75, .6, (x - s * 2.4, yy, FLOOR + 11),
                                  (0, math.pi/2, 0), seg=10, sides=5, arc=math.pi))
    # norte: trechos laterais (a Forja fecha o centro)
    for s in (-1, 1):
        out.add('STONE', box((96, 5, H + 6), (s * 104, 152, FLOOR - 2 + (H + 6)/2)))
        out.add('MARB', box((97, 6, 1.4), (s * 104, 152, FLOOR - 2 + H + 6 + .7), bevel=.2))
        out.add('GOLD', box((97.4, 6.4, .4), (s * 104, 152, FLOOR - 2 + H + 6 + 1.6)))
    # sul: muros baixos do portao ate os cantos
    for s in (-1, 1):
        out.add('STONE', box((122, 4.5, 10), (s * 91, -150, FLOOR + 5 - 1)))
        out.add('MARB', box((61, 5.2, 1.0), (s * 60, -150, FLOOR + 9.4), bevel=.15))
        lv_kit.balustrade(out, (s * 32, -152.6), (s * 89, -152.6), FLOOR + 9.8, h=2.6)
        lv_kit.balustrade(out, (s * 32, -147.4), (s * 89, -147.4), FLOOR + 9.8, h=2.6)
        # arcadas cegas no muro sul
        for xx in range(18, 55, 18):
            out.add('TRIM', box((7, 1.2, 7), (s * (32 + xx), -147.6, FLOOR + 3.4)))
            out.add('MARB', torus(3.4, .55, (s * (32 + xx), -147.6, FLOOR + 6.8), (math.pi/2, 0, 0), seg=10, sides=5, arc=math.pi))
    # torres de canto (4)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = sx * 149, sy * 149
            out.add('STONE', cyl(9, H + 10, (cx, cy, FLOOR - 2), seg=14))
            out.add('MARB', cyl(9.8, 1.4, (cx, cy, FLOOR - 2 + H + 10), seg=14, bevel=.2))
            out.add('GOLD', cyl(10.0, .5, (cx, cy, FLOOR - 1 + H + 10.6), seg=14))
            prof = [(math.cos(t/5 * math.pi/2) * 9.2, math.sin(t/5 * math.pi/2) * 6.4) for t in range(6)]
            out.add('GLASS', lathe(prof, (cx, cy, FLOOR - 2 + H + 11.2), seg=14))
            out.add('GOLD', lathe([(.5, 0), (.02, 3.2)], (cx, cy, FLOOR + H + 15.6), seg=8))

# ---------------------------------------------------------------- FONTES DE PAREDE (terraco norte)
def wall_fountains(out):
    for s in (-1, 1):
        x = s * 38
        y = 126.5
        out.add('MARB', box((7.5, 2.2, 11), (x, y, TERR + 5.5), bevel=.2))
        out.add('TRIM', box((6.2, 1.6, 9.6), (x, y - .4, TERR + 5.2)))
        out.add('MARB', torus(2.6, .5, (x, y - .9, TERR + 8.4), (math.pi/2, 0, 0), seg=12, sides=5, arc=math.pi))
        out.add('NEON', ball(.7, (x, y - .9, TERR + 7.2), seg=8))
        # bica + bacia
        out.add('FOAM', box((.8, .5, 4.4), (x, y - 1.7, TERR + 3.4)))
        out.add('MARB', lathe([(3.4, 0), (3.6, .8), (3.1, 1.1), (2.9, 1.5)], (x, y - 3.4, TERR), seg=14))
        out.add('WATER', cyl(2.9, .3, (x, y - 3.4, TERR + .95), seg=14))
