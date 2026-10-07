# k_relva.py - RELVA GEOMETRICA do lobby.
# Substitui as placas t_box de k_montagem.py:809-818. O defeito nao era cor nem quantidade: era SILHUETA.
# A placa tinha 9-18 studs de aresta reta por 0.18 de altura (50:1 a 100:1) e a face dominante, vista de
# cima, era um quadrilatero. Aqui a unidade minima e a LAMINA: um prisma de 3 lados achatado, varrido por um
# arco, que FECHA EM BICO. Nada termina em reta e nada tem canto de 90 graus.
# Tres camadas: manta continua (cor) -> tufo (silhueta) -> franja de borda (o perfil contra a pedra).
# Sem alpha, sem billboard, sem shader: o gradiente raiz->ponta viaja no canal 'rnd' (cor de vertice) e
# entra no atlas no bake, exatamente como o resto do kit.
import math, random, bmesh
from mathutils import Vector
from k_core import Builder, t_blob, xf, smooth01, PAINTS

#                 base      sombra    realce    rough var  edge  ao   face spec emis
PD_RELVA = {   # acrescentar a k_materiais.PD (e a k_core.PAINTS). 'var' ALTO de proposito: e ele que da
               # amplitude a rampa raiz->ponta gravada em 'rnd'. Matiz numa faixa estreita, valor variando.
    'relva':  ('568A3A', '1B3319', 'CBE07C', .90, .42, .16, .90, .24, .0, 0),
    'relvaF': ('3E7038', '16301E', 'A6C86E', .90, .42, .16, .90, .20, .0, 0),   # frio: sombra, pe de pedra
    'relvaQ': ('72A047', '2A5226', 'E4F098', .90, .42, .16, .90, .28, .0, 0),   # quente: aberto, sol
    'manta':  ('3B6A2C', '142916', '8FB35C', .92, .34, .10, .92, .16, .0, 0),
    'musgo':  ('42763A', '16301C', '92BA64', .92, .26, .12, .90, .14, .0, 0),
}

def registrar_relva(k_materiais):
    for k, v in PD_RELVA.items():
        k_materiais.PD[k] = v; PAINTS[k] = v[0]

# ---------------------------------------------------------------- ruido de valor em coordenada de MUNDO
def _hsh(i, j, s):
    n = (i * 374761393 + j * 668265263 + s * 1274126177) & 0xffffffff
    n = ((n ^ (n >> 13)) * 1274126177) & 0xffffffff
    return ((n ^ (n >> 16)) & 0xffff) / 65535.0

def nz(x, y, freq, s=0):
    """a mancha de cor e de densidade nasce daqui: como e funcao de (x,y) do MUNDO, ela atravessa as pecas
    em vez de coincidir com elas. O sorteio por peca e o que pintava a fronteira que deveria sumir."""
    x *= freq; y *= freq
    i, j = math.floor(x), math.floor(y); fx, fy = x - i, y - j
    sx, sy = smooth01(fx), smooth01(fy)
    a, b = _hsh(i, j, s), _hsh(i + 1, j, s); c, d = _hsh(i, j + 1, s), _hsh(i + 1, j + 1, s)
    return (a * (1 - sx) + b * sx) * (1 - sy) + (c * (1 - sx) + d * sx) * sy

def nz2(x, y, f, s=0):
    return nz(x, y, f, s) * .68 + nz(x, y, f * 2.7, s + 91) * .32

GOLD = math.radians(137.507)

# ---------------------------------------------------------------- A LAMINA (10 tris)
def lamina(bm, lay, base, h, w, az, arco, v_raiz, v_ponta, esp=.40):
    """prisma de 3 lados achatado, varrido por um arco, com a largura caindo a ZERO na ponta.
    - o BICO e o que diz "planta" ao olho; aresta reta e canto de 90 graus nao existem em vegetacao.
    - a SECAO triangular (em vez de um plano) garante que a lamina nao suma de lado com o backface culling
      do Roblox e dispensa DoubleSided (que dobra o custo do asset); a quina da nervura pega luz e da volume.
    - v_raiz/v_ponta viram cor de vertice no canal 'rnd' = rampa de valor raiz->ponta assada no atlas.
      Sem esse escurecimento no pe, todo elemento vegetal parece flutuar por cima do chao."""
    dirh = Vector((math.cos(az), math.sin(az), 0.0))
    lado = Vector((-math.sin(az), math.cos(az), 0.0))
    L = h * arco
    def P(t):
        return base + dirh * (L * t ** 1.85) + Vector((0, 0, h * math.sin(t * math.pi * .47)))
    rings = []
    for t in (0.0, 0.50):
        p = P(t); ww = w * (1.0 - t) ** .60
        tan = (P(min(t + .07, 1.0)) - P(max(t - .07, 0.0))).normalized()
        nrm = tan.cross(lado).normalized()
        vs = []
        for kk in range(3):
            a = math.pi / 2 + kk * math.tau / 3
            vs.append(bm.verts.new(p + lado * (math.cos(a) * ww) + nrm * (math.sin(a) * ww * esp)))
        rings.append(vs)
        val = v_raiz + (v_ponta - v_raiz) * t
        for vv in vs: lay[vv] = val
    apex = bm.verts.new(P(1.0)); lay[apex] = v_ponta
    a, b = rings
    for i in range(3):
        j = (i + 1) % 3
        bm.faces.new((a[i], a[j], b[j], b[i]))          # 3 quads = 6 tris
        bm.faces.new((b[i], b[j], apex))                # 3 tris  -> o BICO
    bm.faces.new(a[::-1])                               # tampa da raiz = 1 tri (fica enterrada)
    return 10

# ---------------------------------------------------------------- O TUFO (~70 tris com 7 laminas)
def tufo(bm, lay, cx, cy, cz, rnd, n=7, h=.95, raio=.42, az0=0.0, w=.100, v_off=.0, hero=False):
    """a UNIDADE de plantio nunca e a lamina solta: e o tufo. As laminas saem de um mesmo ponto, abertas em
    leque, com ALTURAS DESIGUAIS (tufo de altura unica vira calota lisa - o retangulo de volta, agora redondo)
    e inclinadas PARA FORA do centro. Altura, azimute e tom sao HERDADOS do tufo: e a heranca, nao a
    densidade, que tira o ar de jardim aparado."""
    tris = 0
    for k in range(n):
        a = az0 + GOLD * k + rnd.uniform(-.55, .55)
        d = raio * (rnd.random() ** .55)
        base = Vector((cx + math.cos(a) * d, cy + math.sin(a) * d, cz))
        hh = h * (.62, .82, 1.0, 1.22, 1.42)[k % 5] * rnd.uniform(.88, 1.12)
        deitada = (k % 7 == 3)                          # 1 lamina quase deitada faz o tufo morder o chao
        # arco grande de proposito: de cima, lamina em pe cobre ~0.03 stud2 e deitada cobre ~0.15. E o unico
        # jeito de fechar o chao com 3-4 laminas por stud2 sem estourar o teto de 20 mil tris por malha.
        arco = rnd.uniform(1.15, 1.75) if deitada else rnd.uniform(.55, 1.05) + .25 * (d / max(raio, 1e-4))
        ww = w * rnd.uniform(.80, 1.18) * (1.15 if hero else 1.0)
        tris += lamina(bm, lay, base, hh, ww, a + rnd.uniform(-.35, .35), arco,
                       min(.97, max(.02, .04 + v_off + rnd.uniform(-.02, .03))),
                       min(.97, max(.02, .84 + v_off + rnd.uniform(-.09, .09))))
    return tris

def emitir(B, key, bm, lay):
    """rnd='keep' preserva a cor de vertice que a lamina ja pintou (a rampa raiz->ponta)."""
    if not bm.faces: bm.free(); return
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    cl = bm.loops.layers.color.new('rnd')
    for f in bm.faces:
        for l in f.loops:
            v = lay.get(l.vert, .5); l[cl] = (v, v, v, 1)
    B.add(bm, key, rnd='keep')

# ---------------------------------------------------------------- CAMADA 1: a manta
def altura_manta(x, y, z0=0.0):
    return z0 + .03 + .26 * nz2(x, y, .13, 3) + .10 * nz(x, y, .42, 11)

def manta_relva(B, x0, x1, y0, y1, z0=0.0, cel=1.4, seed=77):
    """UMA casca continua por canteiro, no lugar das N placas sorteadas. Ela carrega a COR; os tufos so
    quebram a silhueta. Topo ondulado (o valor segue o relevo: lombada clara, cava escura - sem isso a face
    quase horizontal recebe sempre a mesma luz e a manta le como tapete pintado) e BORDA recortada por uma
    onda LOBADA parametrizada pelo perimetro, que atravessa a quina. Recorte por vertice vira serra; quina
    viva de 90 graus le como placa, entao a quina tambem e erodida."""
    ni = max(6, int((x1 - x0) / cel)); nj = max(6, int((y1 - y0) / cel))
    cx = (x1 - x0) / ni; cy = (y1 - y0) / nj
    rnd = random.Random(seed)
    ordem = ([(i, 0) for i in range(ni + 1)] + [(ni, j) for j in range(1, nj + 1)] +
             [(i, nj) for i in range(ni - 1, -1, -1)] + [(0, j) for j in range(nj - 1, 0, -1)])
    per_u = {}; u = 0.0
    for k, ij in enumerate(ordem):
        per_u[ij] = u; u += cx if (ij[1] in (0, nj)) else cy
    Ptot = max(u, 1e-3)
    mordidas = [(rnd.uniform(0, Ptot), rnd.uniform(1.8, 4.5), rnd.uniform(.9, 2.1))
                for _ in range(max(4, int(Ptot / 15)))]
    def recorte(uu):
        d = (nz2(uu, 0, .085, 5) - .48) * 3.2 + (nz(uu, 0, .27, 19) - .5) * .9
        for (u0, larg, amp) in mordidas:                       # mordidas fundas que pegam varios vertices
            t = abs(((uu - u0 + Ptot * .5) % Ptot) - Ptot * .5)
            if t < larg: d -= amp * (1 - smooth01(t / larg))
        return d
    bm = bmesh.new(); lay = {}; vt = {}
    for i in range(ni + 1):
        for j in range(nj + 1):
            x = x0 + i * cx; y = y0 + j * cy
            if (i, j) in per_u:
                d = recorte(per_u[(i, j)])
                qd = min(math.hypot(i - a, j - b) for a, b in ((0, 0), (ni, 0), (0, nj), (ni, nj)))
                d -= 2.2 * max(0.0, 1 - qd / 4.5) ** 1.5       # quina erodida
                nx = (-1 if i == 0 else (1 if i == ni else 0))
                ny = (-1 if j == 0 else (1 if j == nj else 0))
                nl = math.hypot(nx, ny) or 1.0
                x += d * nx / nl; y += d * ny / nl; z = z0 + .02
            else:
                x += rnd.uniform(-.32, .32); y += rnd.uniform(-.32, .32)
                z = altura_manta(x, y, z0)
            v = bm.verts.new((x, y, z)); vt[(i, j)] = v
            borda = min(x - x0, x1 - x, y - y0, y1 - y)
            esc = max(0.0, (1.6 - borda) / 2.0)                # sombra de contato com a pedra
            lay[v] = min(.95, max(.04, .22 + .34 * ((z - z0 - .03) / .26) + .30 * nz2(x, y, .075, 17)
                                  + .16 * nz(x, y, .62, 29) - .28 * min(1.0, esc)))
    for i in range(ni):
        for j in range(nj):
            bm.faces.new((vt[(i, j)], vt[(i + 1, j)], vt[(i + 1, j + 1)], vt[(i, j + 1)]))
    emitir(B, 'manta', bm, lay)

# ---------------------------------------------------------------- CAMADA 2: o ladrilho de tufos (instanciado)
def tile_relva(nome, seed, lado=20.0, passo=1.95, hero_n=2, cap=14800):
    """LADRILHO de 20x20 para INSTANCIAR (4 rotacoes x 2 variantes = 8 leituras com 2 malhas; o motor baixa
    o MeshId uma vez). Distribuicao em dois niveis, tipo Voronoi: centros de chumaco numa grade jitterada e
    2-5 tufos em volta de cada um, herdando altura, azimute e tom. Alturas em PATAMARES por mancha de ruido
    (rasteira / media / alta), nunca um continuo, e falhas nuas pequenas e frequentes de proposito - grama
    perfeita de borda a borda le como tapete. A base fica 0.24 enterrada para nao aparecer o recorte com a
    manta ondulada."""
    B = Builder(nome, seed); rnd = random.Random(seed)
    alvos = {q: (bmesh.new(), {}) for q in 'MQF'}
    espec = []
    m = max(1, int(lado / passo))
    for i in range(m):
        for j in range(m):
            gx = -lado / 2 + (i + .5) * passo + rnd.uniform(-.85, .85)
            gy = -lado / 2 + (j + .5) * passo + rnd.uniform(-.85, .85)
            dens = nz2(gx + seed * 13, gy - seed * 7, .34, 31)
            if dens < .12: continue
            hn = nz2(gx - seed * 5, gy + seed * 11, .095, 61)
            if hn < .50: h0, nl, rr = rnd.uniform(.40, .60), 6, .30      # rasteira: cobre a maior parte
            elif hn < .88: h0, nl, rr = rnd.uniform(.80, 1.20), 7, .42   # media: o corpo do gramado
            else: h0, nl, rr = rnd.uniform(1.45, 2.10), 8, .58           # mancha alta
            tom = nz2(gx - 40, gy + 40, .055, 53)
            q, off = ('Q', .06) if tom > .64 else (('F', -.08) if tom < .33 else ('M', 0.0))
            az0 = rnd.uniform(0, 6.28)                                   # azimute herdado pelo chumaco
            for k in range(2 + int(dens * 3.2)):
                a = rnd.uniform(0, 6.28); d = rnd.uniform(0, 1.05)
                espec.append((gx + math.cos(a) * d, gy + math.sin(a) * d, -.24, nl,
                              h0 * rnd.uniform(.80, 1.20), rr * rnd.uniform(.8, 1.3),
                              az0 + rnd.uniform(-.45, .45), .100 * rnd.uniform(.88, 1.12), off, q, False))
    for g in range(hero_n):                                              # heroi SEMPRE em grupo de 3-4
        gx = rnd.uniform(-lado / 2 + 2, lado / 2 - 2); gy = rnd.uniform(-lado / 2 + 2, lado / 2 - 2)
        az0 = rnd.uniform(0, 6.28)
        for k in range(rnd.randint(3, 4)):
            a = rnd.uniform(0, 6.28); d = rnd.uniform(.4, 1.4)
            espec.append((gx + math.cos(a) * d, gy + math.sin(a) * d, -.28, 9,
                          rnd.uniform(1.9, 2.7), .55 + .35 * rnd.random(),
                          az0 + rnd.uniform(-.4, .4), .112, .02, 'M', True))
    rnd.shuffle(espec)                                                   # o orcamento RAREIA o conjunto
    espec = espec[:(cap - 300) // 70]                                    # inteiro; cortar um pedaco abriria buraco
    for (px, py, pz, nl, h, rr, az0, w, off, q, hero) in espec:
        bmq, layq = alvos[q]
        tufo(bmq, layq, px, py, pz, rnd, n=nl, h=h, raio=rr, az0=az0, w=w, v_off=off, hero=hero)
    for q, key in (('M', 'relva'), ('Q', 'relvaQ'), ('F', 'relvaF')):
        emitir(B, key, alvos[q][0], alvos[q][1])
    return B, len(espec)

# ---------------------------------------------------------------- CAMADA 3: a franja de borda
def franja_relva(B, x0, x1, y0, y1, z0=0.0, passo=1.90, cap=132, seed=3):
    """A densidade vai para a LINHA onde o verde encontra a pedra: de dentro do jogo o jogador ve o PERFIL
    do gramado contra o calcamento, na altura dos olhos, muito mais do que o miolo visto de cima. 3 fileiras
    deslocadas; a de fora TRANSBORDA por cima do meio-fio. Interrompida em ~22% dos pontos (borda continua
    volta a ser uma linha) e com tufos FUGIDOS plantados alem do meio-fio - sao eles, mais do que qualquer
    densidade a mais no miolo, que tiram o contorno do canteiro do quadrado perfeito."""
    rnd = random.Random(seed)
    bm, lay = bmesh.new(), {}; bmS, layS = bmesh.new(), {}
    per = []
    for (a0, a1, fixo, out, eh_x) in ((x0, x1, y0, Vector((0, -1, 0)), True), (x0, x1, y1, Vector((0, 1, 0)), True),
                                      (y0, y1, x0, Vector((-1, 0, 0)), False), (y0, y1, x1, Vector((1, 0, 0)), False)):
        for i in range(max(1, int((a1 - a0) / passo))):
            s = a0 + (i + .5) * passo + rnd.uniform(-.35, .35)
            per.append(((s, fixo) if eh_x else (fixo, s)) + (out,))
    espec = []
    for (x, y, out) in per:
        if rnd.random() < .22: continue
        for fila in range(3):
            off = out * (fila * -.85 + rnd.uniform(-.25, .25) + 1.05)
            px = x + off.x + rnd.uniform(-.35, .35); py = y + off.y + rnd.uniform(-.35, .35)
            t = rnd.random()
            h = (.60 + .42 * nz2(px, py, .10, 23)) * (2.8 if t > .88 else (1.6 if t > .58 else 1.0))
            az = math.atan2(out.y, out.x) + rnd.uniform(-.8, .8)         # 70% pendem para FORA
            if rnd.random() < .30: az += math.pi
            espec.append((px, py, h, az, fila == 0, 7))
    for (a0, a1, fixo, out, eh_x) in ((x0, x1, y0, Vector((0, -1, 0)), True), (x0, x1, y1, Vector((0, 1, 0)), True),
                                      (y0, y1, x0, Vector((-1, 0, 0)), False), (y0, y1, x1, Vector((1, 0, 0)), False)):
        for g in range(4):                                               # tufos FUGIDOS, na calcada
            s = rnd.uniform(a0 + 2, a1 - 2); d = rnd.uniform(1.3, 3.2)
            bx, by = ((s, fixo + out.y * d) if eh_x else (fixo + out.x * d, s))
            for k in range(rnd.randint(2, 4)):
                espec.append((bx + rnd.uniform(-.9, .9), by + rnd.uniform(-.9, .9),
                              rnd.uniform(.45, 1.1), rnd.uniform(0, 6.28), True, 6))
    rnd.shuffle(espec)
    for (px, py, h, az, frio, n) in espec[:cap]:
        bq, lq = (bmS, layS) if frio else (bm, lay)
        tufo(bq, lq, px, py, altura_manta(px, py, z0) - .22, rnd, n=n, h=h,
             raio=.34 + .16 * rnd.random(), az0=az, w=.096, v_off=(-.09 if frio else .04))
    emitir(B, 'relva', bm, lay); emitir(B, 'relvaF', bmS, layS)

def musgo_junta(B, pontos, seed=12):
    """calota lobada de musgo nas JUNTAS (pe do meio-fio, pe de rocha, pe de tronco): volume solido, sem
    alpha, que cobre o encontro verde/pedra. Na referencia o verde nunca encosta no calcamento com aresta
    limpa - sempre ha pedra, musgo ou copa cobrindo o encontro. ~50 tris cada (t_blob sub=1 com flat_bottom)."""
    rnd = random.Random(seed)
    for (x, y) in pontos:
        r = rnd.uniform(.55, 1.25)
        bm = t_blob(r, (1, rnd.uniform(.85, 1.15), rnd.uniform(.22, .32)), 1,
                    lobes=5, lobe_amp=.26, seed=rnd.randint(0, 999), flat_bottom=-r * .2)
        xf(bm, rot=(0, 0, rnd.uniform(0, 360)), loc=(x, y, .04))
        B.add(bm, 'musgo', rnd.uniform(.35, .78))

# ---------------------------------------------------------------- uso em k_montagem.py (canteiro de 40x40)
#   k_relva.registrar_relva(k_materiais)                       # uma vez, antes de build_paints()
#   mb = Builder('LOB_relva_a', 600)
#   k_relva.manta_relva(mb, x0, x1, y0, y1, z0=-.44)           # ~2.0k tris
#   k_relva.franja_relva(mb, x0, x1, y0, y1, z0=-.44)          # ~9.2k tris
#   k_relva.musgo_junta(mb, pontos_de_junta)                   # ~1.7k tris
#   mb.finish('LOB_CHAO')                                    # total ~12.6k  -> MALHA 1
#   for i, sd in enumerate((101, 202)):                      # ~14.0k e ~14.5k -> MALHAS 2 e 3
#       m, _ = k_veg.tile_relva('LOB_relva_tile_%s' % 'AB'[i], sd); m.finish('LOB_CHAO')
#   for k, (ox, oy) in enumerate(cantos_20x20):              # 4 instancias, 4 rotacoes
#       instance(masters[k % 2], 'LOB_relva_%d' % k, 'LOB_CHAO', loc=(ox, oy, 0), rot_z=(0, 90, 180, 270)[k])
