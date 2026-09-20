# k_jardim.py - ambientacao do jardim e da vila: flores (peonia, crisantemo, lotus, ameixeira), canteiros, grama alta,
# e props de rua de vila chinesa (lanterna de pedra, poco, barril, cesto, banco, varal, caixas, telhas empilhadas,
# placa de loja, carroca de mao). Mesma linguagem do kit: perfis desenhados, chanfro por escala, tintas de k_core.
import math, random
import bmesh
from mathutils import Vector, Matrix
from k_core import *
from k_props import crom, lerp_list, bmesh_tri_prism

# ---------------------------------------------------------------- petalas e flores
def petala(L=1.0, W=.55, curva=.28, espessura=.05, ponta=.55):
    """petala como superficie curva com espessura: base estreita, meio largo, ponta arredondada."""
    bm = bmesh.new(); NU, NV = 6, 4; grid = []
    for i in range(NU + 1):
        u = i / NU
        meia = W * (.30 + .70 * math.sin(math.pi * min(1.0, u * 1.05)) ** .8)
        if u > .82: meia *= ponta + (1 - ponta) * (1 - (u - .82) / .18)
        row = []
        for j in range(NV + 1):
            v = j / NV - .5
            z = curva * (u ** 1.4) + (1 - (2 * v) ** 2) * curva * .30
            row.append(Vector((v * 2 * meia, u * L, z)))
        grid.append(row)
    vs = [[bm.verts.new(p) for p in row] for row in grid]
    for i in range(NU):
        for j in range(NV): bm.faces.new((vs[i][j], vs[i][j + 1], vs[i + 1][j + 1], vs[i + 1][j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.normal_update()
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=-espessura)
    for f in bm.faces: f.smooth = True
    return bm

def _flor(B, key_petala, key_miolo, x, y, z, R=1.0, n=8, camadas=2, tomb=42, rot=0.0, curva=.28):
    """flor generica: coroas de petalas em camadas com inclinacao decrescente + miolo."""
    for c in range(camadas):
        k = 1.0 - .30 * c
        for i in range(n):
            a = 360 * i / n + (180 / n) * c + rot
            bm = petala(R * k, R * .55 * k, curva * k)
            xf(bm, rot=(tomb - 16 * c, 0, 0)); xf(bm, rot=(0, 0, a)); xf(bm, loc=(x, y, z + .06 * c))
            B.add(bm, key_petala, .35 + .5 * ((i + c) % 4) / 4)
    B.add(xf(t_lathe([(0, 0), (R * .26, 0), (R * .30, R * .10), (R * .18, R * .20), (0, R * .22)], 10), loc=(x, y, z + .06 * camadas)), key_miolo, .7)

def peonia(seed=1, name='JAR_peonia'):
    """peonia: a flor imperial. Moita com 3 flores grandes rosadas em alturas diferentes e folhagem larga."""
    B = Builder(name, 801 + seed); rnd = random.Random(seed)
    for i, (x, y, h, R) in enumerate(((0, 0, 2.5, 1.15), (1.5, .7, 1.9, .95), (-1.2, -.8, 2.2, 1.05))):
        caule = crom([(x * .25, y * .25, 0), (x * .6, y * .6, h * .55), (x, y, h)], 3)
        B.add(t_tube(caule, lerp_list([.13, .10, .08], len(caule)), 6), 'folha', .35)
        _flor(B, 'flor_rosa', 'flor_ouro', x, y, h, R, n=9, camadas=3, tomb=46 + rnd.uniform(-8, 8), rot=rnd.uniform(0, 40))
    for k in range(7):
        a = rnd.uniform(0, math.tau); d = rnd.uniform(.7, 2.1)
        fx, fy = math.cos(a) * d, math.sin(a) * d
        bm = petala(1.5, 1.0, .18, .07, .75)
        xf(bm, rot=(rnd.uniform(58, 78), 0, math.degrees(a) - 90)); xf(bm, loc=(fx * .35, fy * .35, rnd.uniform(.3, .9)))
        B.add(bm, 'folha', rnd.uniform(.3, .8))
    return B

def crisantemo(seed=1, name='JAR_crisantemo'):
    """crisantemo: muitas petalas finas e longas; flores amarelas menores."""
    B = Builder(name, 811 + seed); rnd = random.Random(seed)
    for (x, y, h) in ((0, 0, 2.0), (1.1, -.6, 1.6), (-.9, .8, 1.75)):
        caule = crom([(x * .3, y * .3, 0), (x * .7, y * .7, h * .6), (x, y, h)], 3)
        B.add(t_tube(caule, lerp_list([.10, .08, .06], len(caule)), 5), 'folha', .35)
        for c in range(2):
            k = 1.0 - .26 * c
            for i in range(10):
                a = 360 * i / 10 + 18 * c
                bm = petala(.85 * k, .16 * k, .34 * k, .035, .35)
                xf(bm, rot=(52 - 18 * c, 0, 0)); xf(bm, rot=(0, 0, a)); xf(bm, loc=(x, y, h + .05 * c))
                B.add(bm, 'flor_amarela', .3 + .55 * ((i + c) % 3) / 3)
        B.add(xf(t_lathe([(0, 0), (.16, 0), (.14, .12), (0, .16)], 8), loc=(x, y, h + .16)), 'flor_ouro', .75)
    for k in range(6):
        a = rnd.uniform(0, math.tau); d = rnd.uniform(.5, 1.5)
        bm = petala(1.0, .7, .16, .06, .6)
        xf(bm, rot=(rnd.uniform(60, 80), 0, math.degrees(a) - 90)); xf(bm, loc=(math.cos(a) * d * .4, math.sin(a) * d * .4, rnd.uniform(.2, .6)))
        B.add(bm, 'folha', rnd.uniform(.3, .75))
    return B

def lotus(seed=1, name='JAR_lotus'):
    """lotus para a agua: 2 folhas circulares flutuando, 1 flor aberta e 1 botao."""
    B = Builder(name, 821 + seed); rnd = random.Random(seed)
    for (x, y, r) in ((0, 0, 1.9), (2.2, 1.1, 1.5), (-1.6, 1.8, 1.2)):
        bm = t_lathe([(0, .12), (r * .35, .06), (r * .75, .0), (r, .10), (r * .98, .16), (r * .70, .07), (0, .2)], 16)
        xf(bm, loc=(x, y, 0)); B.add(bm, 'folha_lotus', .35 + .3 * (r % 1))
    _flor(B, 'flor_rosa', 'flor_ouro', -.4, -1.7, .18, .85, n=8, camadas=2, tomb=40)
    bx, by = 1.9, -1.2
    cl = crom([(bx, by, 0), (bx, by, .5), (bx, by, .85)], 2)
    B.add(t_tube(cl, lerp_list([.09, .08, .07], len(cl)), 5), 'folha', .4)
    bm = t_lathe([(0, 0), (.30, .28), (.34, .62), (.20, .95), (.05, 1.15), (0, 1.2)], 8)
    xf(bm, loc=(bx, by, .8)); B.add(bm, 'flor_rosa', .6)
    return B

def ameixeira(seed=1, name='JAR_ameixeira'):
    """meihua: tronco escuro retorcido e nuvens de flor branca-rosada. Simbolo da seita de espada."""
    B = Builder(name, 831 + seed); rnd = random.Random(seed)
    tr = crom([(0, 0, 0), (.5, .3, 1.8), (-.4, .1, 3.4), (.3, -.2, 4.6)], 4)
    B.add(t_tube(tr, lerp_list([.75, .55, .40, .30], len(tr)), 7), 'casca_escura', .35)
    galhos = []
    for i in range(5):
        a = math.radians(72 * i + rnd.uniform(-22, 22)); d = rnd.uniform(2.6, 4.2)
        base = Vector((.15, 0, 2.6 + rnd.uniform(-.6, 1.2)))
        pta = Vector((math.cos(a) * d, math.sin(a) * d, base.z + rnd.uniform(1.2, 2.6)))
        g = crom([tuple(base), tuple((base + pta) / 2 + Vector((0, 0, .5))), tuple(pta)], 4)
        B.add(t_tube(g, lerp_list([.26, .16, .09], len(g)), 6), 'casca_escura', .45)
        galhos.append(pta)
    for p in galhos:
        for k in range(4):
            o = Vector((rnd.uniform(-1.1, 1.1), rnd.uniform(-1.1, 1.1), rnd.uniform(-.6, .9)))
            _flor(B, 'flor_branca', 'flor_ouro', p.x + o.x, p.y + o.y, p.z + o.z, rnd.uniform(.26, .40), n=5, camadas=1, tomb=30, rot=rnd.uniform(0, 72), curva=.16)
    return B

def canteiro_flores(seed=1, name='JAR_canteiro', L=7.0, W=3.4):
    """canteiro de pedra com terra e flores baixas misturadas (as 3 cores da paleta)."""
    B = Builder(name, 841 + seed); rnd = random.Random(seed)
    B.add(t_box(-L / 2, L / 2, -W / 2, W / 2, 0, .85, bev=.12, seg=2), 'pedra', .5)
    B.add(t_box(-L / 2 + .45, L / 2 - .45, -W / 2 + .45, W / 2 - .45, .5, 1.0), 'casca', .3)
    for k in range(16):
        x = rnd.uniform(-L / 2 + .8, L / 2 - .8); y = rnd.uniform(-W / 2 + .8, W / 2 - .8)
        h = rnd.uniform(.35, .9)
        cl = crom([(x, y, .9), (x, y, .9 + h * .6), (x, y, .9 + h)], 2)
        B.add(t_tube(cl, lerp_list([.07, .06, .05], len(cl)), 5), 'folha', .4)
        cor = ('flor_rosa', 'flor_amarela', 'flor_branca')[k % 3]
        _flor(B, cor, 'flor_ouro', x, y, .9 + h, rnd.uniform(.26, .40), n=6, camadas=1, tomb=38, rot=rnd.uniform(0, 60), curva=.18)
    for k in range(10):
        x = rnd.uniform(-L / 2 + .5, L / 2 - .5); y = rnd.uniform(-W / 2 + .5, W / 2 - .5)
        bm = petala(rnd.uniform(.5, .8), .5, .14, .05, .7)
        xf(bm, rot=(rnd.uniform(62, 82), 0, rnd.uniform(0, 360))); xf(bm, loc=(x, y, .95))
        B.add(bm, 'folha', rnd.uniform(.3, .8))
    return B

def moita_grama(seed=1, name='JAR_grama'):
    """tufo de grama ALTA para quebrar a borda do gramado (o gramado chapado era um defeito declarado)."""
    B = Builder(name, 851 + seed); rnd = random.Random(seed)
    for k in range(14):
        a = rnd.uniform(0, math.tau); d = rnd.uniform(0, 1.1); h = rnd.uniform(1.2, 2.6)
        base = Vector((math.cos(a) * d, math.sin(a) * d, 0))
        arco = rnd.uniform(.5, 1.3); ta = rnd.uniform(0, math.tau)
        pts = crom([tuple(base), tuple(base + Vector((math.cos(ta) * arco * .3, math.sin(ta) * arco * .3, h * .65))), tuple(base + Vector((math.cos(ta) * arco, math.sin(ta) * arco, h)))], 3)
        w = rnd.uniform(.10, .16)
        bm = bmesh.new(); prev = None
        for i, p in enumerate(pts):
            t = i / (len(pts) - 1); ww = w * (1 - t * .92)
            par = [bm.verts.new(p + Vector((ww, 0, 0))), bm.verts.new(p + Vector((-ww, 0, 0)))]
            if prev: bm.faces.new((prev[0], par[0], par[1], prev[1]))
            prev = par
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        B.add(bm, 'folha' if k % 3 else 'bambu', rnd.uniform(.3, .85))
    return B

# ---------------------------------------------------------------- props de vila
def lanterna_pedra(name='VIL_lanterna_pedra'):
    """toro/dengloung de pedra: base, fuste, camara de luz e capa. Altura ~5."""
    B = Builder(name, 861)
    def octo(r): return [(r * math.cos(math.radians(22.5 + 45 * i)), r * math.sin(math.radians(22.5 + 45 * i))) for i in range(8)]
    B.add(t_prism(octo(1.25), 'Z', 0, .55, bev=.1), 'pedra', .45)
    B.add(t_lathe([(0, .55), (.62, .55), (.55, .95), (.42, 2.3), (.52, 2.7), (0, 2.7)], 12), 'pedra', .55)
    B.add(t_prism(octo(1.05), 'Z', 2.7, 3.0, bev=.08), 'pedra', .6)
    B.add(t_prism(octo(.85), 'Z', 3.0, 4.0, bev=.06), 'chama', .8)
    for i in range(8):
        a = math.radians(45 * i)
        B.add(xf(t_box(-.1, .1, -.1, .1, 3.0, 4.0, bev=.03), rot=(0, 0, 45 * i), loc=(.85 * math.cos(a), .85 * math.sin(a), 0)), 'pedra', .5)
    B.add(t_prism(octo(1.35), 'Z', 4.0, 4.3, bev=.1), 'pedra', .5)
    B.add(t_lathe([(0, 4.3), (1.3, 4.3), (.9, 4.75), (.3, 5.0), (0, 5.05)], 8, smooth=False), 'pedra', .62)
    B.add(t_lathe([(0, 0), (.24, 0), (.3, .2), (.16, .42), (0, .5)], 10), 'pedra', .7)
    return B

def poco(name='VIL_poco'):
    """poco de pedra com telhadinho, roldana, corda e balde."""
    B = Builder(name, 862)
    def octo(r): return [(r * math.cos(math.radians(22.5 + 45 * i)), r * math.sin(math.radians(22.5 + 45 * i))) for i in range(8)]
    B.add(t_prism(octo(2.7), 'Z', 0, .4, bev=.1), 'pedra', .42)
    for k in range(3):
        B.add(t_prism(octo(2.45 - .05 * k), 'Z', .4 + k * .75, 1.1 + k * .75, bev=.12, seg=2), 'pedra', .45 + .12 * k)
    B.add(t_prism(octo(2.6), 'Z', 2.6, 3.0, bev=.12, seg=2), 'pedra', .6)
    B.add(t_prism(octo(2.1), 'Z', 2.5, 2.65), 'agua', .7)
    for sx in (-1, 1):
        B.add(t_box(sx * 2.2 - .22, sx * 2.2 + .22, -.22, .22, 3.0, 7.0, bev=.06), 'madM', .5)
    B.add(xf(t_lathe([(0, -2.3), (.18, -2.3), (.18, 2.3), (0, 2.3)], 8), rot=(0, 90, 0), loc=(0, 0, 6.6)), 'mad', .55)
    B.add(xf(t_lathe([(0, -.35), (.5, -.35), (.55, 0), (.5, .35), (0, .35)], 12), rot=(0, 90, 0), loc=(0, 0, 6.6)), 'mad', .45)
    B.add(t_tube([Vector((.8, 0, 6.5)), Vector((.8, 0, 4.2))], [.05, .05], 5), 'palha', .5)
    bal = t_lathe([(0, 0), (.5, 0), (.56, .75), (.5, .8), (0, .8)], 10); xf(bal, loc=(.8, 0, 3.4)); B.add(bal, 'madM', .5)
    for z in (3.5, 4.05): B.add(xf(t_lathe([(.52, z), (.62, z + .04), (.62, z + .14), (.52, z + .18)], 10), loc=(.8, 0, 0)), 'ferro', .35)
    # telhadinho de duas aguas sobre o poco
    for s in (-1, 1):
        B.add(t_prism([(0, 7.1), (s * 3.2, 6.0), (s * 3.2, 5.7), (0, 6.8)], 'X', -3.4, 3.4, bev=.08), 'telha', .5)
    B.add(t_box(-3.5, 3.5, -.35, .35, 7.0, 7.45, bev=.1), 'telha', .6)
    return B

def barril(name='VIL_barril'):
    B = Builder(name, 863)
    B.add(t_lathe([(0, 0), (1.0, 0), (1.05, .18), (1.22, 1.1), (1.22, 1.9), (1.05, 2.8), (1.0, 3.0), (0, 3.0)], 14), 'madM', .5)
    for z in (.35, 1.45, 2.55): B.add(t_lathe([(1.06, z), (1.3, z + .05), (1.3, z + .32), (1.06, z + .38)], 14), 'ferro', .35)
    B.add(t_lathe([(0, 2.95), (.95, 2.95), (.95, 3.1), (0, 3.1)], 14), 'mad', .45)
    return B

def cesto(name='VIL_cesto'):
    B = Builder(name, 864)
    B.add(t_lathe([(0, 0), (.85, 0), (1.15, .5), (1.3, 1.5), (1.35, 2.0), (1.2, 2.1), (1.15, 1.5), (1.0, .5), (.75, .12), (0, .12)], 14), 'palha', .5)
    for z in (.45, 1.05, 1.65): B.add(t_lathe([(1.02 + z * .12, z), (1.12 + z * .12, z + .03), (1.12 + z * .12, z + .16), (1.02 + z * .12, z + .19)], 14), 'palha', .72)
    return B

def banco(name='VIL_banco'):
    B = Builder(name, 865)
    B.add(t_box(-2.6, 2.6, -.75, .75, 1.35, 1.7, bev=.09), 'madM', .5)
    for sx in (-1, 1):
        B.add(t_box(sx * 2.1 - .3, sx * 2.1 + .3, -.62, .62, 0, 1.35, bev=.08), 'mad', .45)
        B.add(t_box(sx * 2.25 - .18, sx * 2.25 + .18, -.7, .7, .55, .8, bev=.05), 'mad', .55)
    return B

def caixas(name='VIL_caixas'):
    """pilha de caixas de madeira com cintas - carga de loja."""
    B = Builder(name, 866); rnd = random.Random(866)
    for (x, y, z, s, r) in ((0, 0, 0, 1.6, 0), (0.15, -.2, 1.6, 1.4, 12), (-.1, .25, 3.0, 1.15, -18)):
        bm = t_box(-s, s, -s, s, 0, s * 1.25, bev=.1, seg=2)
        xf(bm, rot=(0, 0, r), loc=(x, y, z)); B.add(bm, 'madM', rnd.uniform(.35, .7))
        for k in (-1, 1):
            b2 = t_box(-s - .04, s + .04, k * s * .55 - .1, k * s * .55 + .1, 0, s * 1.25, bev=.03)
            xf(b2, rot=(0, 0, r), loc=(x, y, z)); B.add(b2, 'mad', .4)
    return B

def telhas_pilha(name='VIL_telhas'):
    """telhas empilhadas encostadas no muro - obra em andamento, marca de lugar vivo."""
    B = Builder(name, 867); rnd = random.Random(867)
    for k in range(9):
        z = k * .28; off = rnd.uniform(-.12, .12)
        bm = t_lathe([(0, -1.1), (.42, -1.1), (.42, 1.1), (0, 1.1)], 8, smooth=False)
        xf(bm, rot=(0, 90, rnd.uniform(-5, 5))); xf(bm, loc=(off, 0, z + .42))
        B.add(bm, 'telha', rnd.uniform(.3, .8))
    return B

def varal(name='VIL_varal', L=9.0):
    """varal entre dois postes com panos - o detalhe que faz a rua parecer habitada."""
    B = Builder(name, 868); rnd = random.Random(868)
    B2 = B
    for sx in (-1, 1):                                                       # postes nas pontas
        bm = t_lathe([(0, 0), (.3, 0), (.26, 5.4), (0, 5.5)], 8); xf(bm, loc=(sx * L / 2, 0, 0)); B2.add(bm, 'madM', .5)
    n = 18
    pts = [Vector((-L / 2 + L * i / n, 0, 5.2 - .55 * math.sin(math.pi * i / n))) for i in range(n + 1)]
    B2.add(t_tube(pts, [.05] * len(pts), 4), 'palha', .5)
    for k, (t, w, h, cor) in enumerate(((.18, 1.5, 2.4, 'tecido'), (.42, 1.2, 1.9, 'flor_branca'), (.62, 1.6, 2.6, 'jade'), (.82, 1.1, 1.7, 'tecido'))):
        i = int(t * n); p = pts[i]
        bm = bmesh.new(); NX, NZ = 5, 6; grid = []
        for a in range(NX + 1):
            row = []
            for b in range(NZ + 1):
                x = -w / 2 + w * a / NX; z = -h * b / NZ
                y = .10 * math.sin(3.1 * b / NZ + a * .8) * (b / NZ)
                row.append(bm.verts.new(p + Vector((x, y, z))))
            grid.append(row)
        for a in range(NX):
            for b in range(NZ): bm.faces.new((grid[a][b], grid[a][b + 1], grid[a + 1][b + 1], grid[a + 1][b]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=-.05)
        for f in bm.faces: f.smooth = True
        B2.add(bm, cor, .35 + .15 * k)
    return B2

def placa_loja(name='VIL_placa_loja'):
    """placa vertical de loja pendurada num braco de ferro, com borla."""
    B = Builder(name, 869)
    B.add(t_lathe([(0, 0), (.22, 0), (.18, 6.2), (0, 6.3)], 8), 'ferro', .4)
    B.add(t_box(-.12, .12, 0, 2.4, 5.7, 5.95, bev=.05), 'ferro', .45)
    B.add(xf(t_lathe([(0, 0), (.14, 0), (.1, .3), (0, .34)], 6), loc=(0, 2.2, 5.6)), 'bronze', .55)
    B.add(t_box(-.16, .16, 1.55, 2.85, 2.6, 5.5, bev=.08), 'verm', .5)
    for s in (-1, 1):
        ya, yb = sorted((s * .16, s * .2))
        B.add(t_box(min(ya, yb), max(ya, yb), 1.7, 2.7, 2.75, 5.35, bev=.04), 'ouro', .6)
        B.add(t_box(min(ya, yb), max(ya, yb) + s * .02, 1.95, 2.45, 3.1, 5.0, bev=.03), 'creme', .7)
    bl = t_lathe([(0, 0), (.1, 0), (.26, -.9), (0, -.96)][::-1], 8); xf(bl, loc=(0, 2.2, 2.6)); B.add(bl, 'tecido', .5)
    return B

def carroca(name='VIL_carroca'):
    """carroca de mao com carga - da a sensacao de que alguem trabalha ali."""
    B = Builder(name, 870)
    B.add(t_box(-2.4, 2.4, -1.4, 1.4, 1.5, 1.85, bev=.08), 'madM', .5)
    for s in (-1, 1):
        B.add(t_box(-2.4, 2.4, s * 1.4 - .16, s * 1.4 + .16, 1.85, 2.7, bev=.06), 'madM', .55)
    B.add(t_box(-2.5, -2.2, -1.4, 1.4, 1.85, 2.9, bev=.06), 'madM', .6)
    for s in (-1, 1):
        w = t_lathe([(0, -.22), (1.5, -.22), (1.5, .22), (0, .22)], 14)
        xf(w, rot=(0, 90, 0)); xf(w, loc=(0, s * 1.65, 1.5)); B.add(w, 'mad', .4)
        h = t_lathe([(0, -.26), (.42, -.26), (.42, .26), (0, .26)], 10)
        xf(h, rot=(0, 90, 0)); xf(h, loc=(0, s * 1.65, 1.5)); B.add(h, 'ferro', .35)
        for k in range(6):
            a = math.radians(60 * k)
            B.add(xf(t_box(-1.35, 1.35, -.09, .09, -.09, .09), rot=(math.degrees(a), 0, 0), loc=(0, s * 1.65, 1.5)), 'mad', .5)
        B.add(t_box(2.3, 4.4, s * .5 - .14, s * .5 + .14, 1.5, 1.8, bev=.05), 'madM', .5)
    for (x, y, z, r) in ((-.8, 0, 2.7, 1.0), (.9, .3, 2.7, .85), (.2, -.5, 3.4, .7)):
        B.add(xf(t_lathe([(0, 0), (r, 0), (r * 1.05, r * .55), (r * .8, r * 1.1), (0, r * 1.2)], 10), loc=(x, y, z)), 'palha', .55)
    return B
