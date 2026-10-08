# vm_forge.py - FORJA DO IGNIS (onda V2a): o MARCO do lobby Vila Medieval, no fim do eixo norte. Substitui o volume de
# blockout da forja do V0 (vm_blockout.forge(): objetos VM_Frg_* e caixas COL_Forge_*), sem editar o vm_blockout: o
# build() apaga essas pecas e constroi as finais no lugar. Fala a lingua do kit aprovado no V1 (vm_kit, SO LEITURA):
# pedra arredondada em fiadas com junta recuada, enxaimel (frechais, montantes, X, diagonais), telha em fiadas.
#
# PECAS (coordenadas ROBLOX: X leste, Z sul, Y cima; Blender = (X, -Z, Y)):
#   SALAO (x -17..15, z -50..-78,4): base de pedra arredondada GRANDE ate 15, enxaimel ate o frechal (34,6); por
#     dentro pedra cinza + forro de tabuas entre as vigas (oficina escura: o Ignis em silhueta contra a fornalha),
#     FRENTE ABERTA com 2 pilares de madeira grossos (2,8) sobre soco de pedra, verga dupla (32..34,6) com cintas de
#     ferro e maos-francesas, oitao enxaimel com a PLACA DA BIGORNA (bronze), telhado de 48 graus em fiadas, tesouras
#     (linha + pendural + escoras) a vista por dentro. Piso de lajes no topo 6,99.
#   FORNALHA (fundo, x -8,9..7,1): bloco de pedra com BOCA EM ARCO de aduelas (vao 8, nascenca 13, fecho 17), recesso
#     de 4 forrado de fuligem; o fogo fica DENTRO da moldura (fundo e leito Neon, carvao por cima, linguas de fogo); verga
#     de madeira sobre misulas e PEITO DE CHAMINE em 3 recuos de pedra (fuligem subindo) ate o oitao do fundo.
#   FOLE (oeste, dentro): fole de couro em gota sobre cavalete, bico de ferro na lateral da fornalha, balancim com
#     corrente e argola; caixa de carvao com pa; sacos de carvao.
#   LESTE (dentro): cocho de tempera (agua, cintas de ferro), cabideiro de parede com tenazes e martelos, banco com lingotes.
#   ALA OESTE: casa do kit (vm_kit.house) geminada ao salao: LOJA DA FORJA (vitrine, toldo, placa com picareta).
#   TELHEIRO LESTE (x 15..32, z -52,4..-78,4): aberto na frente e no lado da levada; MARTELO-PILAO de madeira (cabo de
#     17 com cabeca de ferro, cavalete do pivo, bigorna sobre cepo) erguido por 3 CAMES no eixo da RODA D'AGUA (centro
#     (36; 9,4; -66), r 7,5, eixo X, na levada x 33..39). Mancais nos muros da levada e cavalete do eixo.
#   CHAMINE (0, -86): soco 16 x 15,6 ate 40, fuste 13 ate 68, fuste 11 ate 86 (fuligem so no topo), cinta,
#     CAMARA DE FOGO com 4 pilares de fuligem e vaos largos (brasas + linguas de fogo Neon recuadas: le "brasa no topo"
#     do spawn), laje-lintel e CAPA elevada sobre 4 calcos ate ~95 (fresta da fumaca). Nada de telhado de torre nem
#     misula de castelo. A fumaca e VFX (VFX_Chimney_Smoke_Emitter na fresta).
#   PROPS (fora): 2 suportes de picaretas a venda (cabeca apoiada no travessao entalhado, cabo pendurado), sacos de
#     carvao, caixote com lingotes, barris; lanternas de ferro nos pilares (luz NightOnly L_VM_Lamp_Frg*); estandartes
#     vermelhos com a bigorna nos pilares (leem de longe).
#   LARGO (o V2b deixou para o V2a): paralelepipedo do kit da boca da rua norte (z -36,4) ate as frentes, meio-fio na
#     grama; chao do Ignis PLANO (topo das pedras <= 7,03; a colisao e o piso 7,0 do vm_col).
#   MATERIAIS: 1 novo (Metal_VM_Steel); o resto reaproveita nomes do lobby (teto global de 110 materiais do export).
#   Nada parecido com minerio: carvao so dentro de sacos/caixa/fornalha, metal so em barras e ferramentas.
#
# CONTRATO DO IGNIS (golem novo, outra sessao): Root (-0,9; 7; -60,7) olhando +Z. ENVOLTORIA LIVRE X -9,9..6,1,
#   Y 7..31, Z -64,7..-52,7 (nada desta zona: nem malha nem COL) e chao livre e plano em 7 de z -52,7 a -40. O golem,
#   a bigorna dele e as colisoes deles sao da sessao Ignis. Entre a frente aberta e o jogador nao ha parede nem coluna.
#
# PECAS MOVEIS = o MESMO mecanismo do lobby atual (fm_water/export_vfx): marcadores VFX_Waterwheel_Rotate (pivot, axis,
#   rpm, R, half_w) e VFX_TripHammer (pivot, axis, cams, cam_len, cam_x, low_axle) com as props que o export_vfx le;
#   aqui a geometria movel ja sai em OBJETOS PROPRIOS (props 'source'): VM_Frg_Wheel (roda + eixo + cames: gira em X) e
#   VM_Frg_TripHammer (cabo + cabeca + cintas, oscila no pivo). Ate o V3 elas exportam paradas, como estatico.
#
# MARCADORES (acrescimo pontual sobre o vm_core, documentado): o vm_core cria os da forja nas posicoes do V0; markers()
#   daqui MOVE ForgeChimney, VFX_Chimney_Smoke_Emitter, VFX_Hearth_Fire, VFX_Waterwheel_Rotate, VFX_TripHammer para a
#   forja nova e CRIA VFX_Anvil_Sparks, VFX_Forge_Sparks, VFX_Quench_Steam e VFX_Wheel_Splash (os do lobby atual).
#   NPC_Ignis / INTERACT_Ignis / PLAYER_INTERACT_Ignis / IGNIS_Anvil / LETREIRO_Ignis nao sao tocados (contrato).
#
# uso: o build_vm.py chama build() depois do vm_trecho e cameras() depois das cameras do trecho.
#   blender -b --factory-startup --python vm_forge.py -- test <saida.blend>        build do lobby + forja (scratch)
#   blender -b --factory-startup <x.blend> --python vm_forge.py -- render <pasta> [CAM...] [--roblox] [--sem-golem]
#   blender -b --factory-startup <x.blend> --python vm_forge.py -- report [json]    orcamento da forja
#   python -B vm_forge.py sheet <prev> <rbx> <pasta_saida>                          folhas renders/v2/forja
import sys, os, math, json
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
try:
    import bpy
except ImportError:
    bpy = None

if bpy is not None:
    import bmesh
    import vm_lib as VL
    from mathutils import Vector
    import vm_layout as L
    import fm_lib
    from fm_lib import MB, S, MATS
    from fm_parts import Frame
    import fm_parts as FP
    import vm_kit as K
    from vm_kit import bx, bb, ext, loft, lathe, sub, even, pillow, stone_face, CORE

    # material NOVO da forja (1 linha; as cores existentes nao sao tocadas). O resto reaproveita nomes que o lobby ja
    # usa: o export tem teto GLOBAL de 110 materiais (no V0+V1+forja ficou em 110) - fuligem/carvao = junta do kit,
    # couro = tabua, sacos = lona do toldo, cocho = agua do canal, dentro da oficina = pedra cinza e forro de tabuas
    FMATS = {
        "Metal_VM_Steel":   (S(158, 164, 172), 0.4, 0.7, 0, None, 0.0),  # cabecas de picareta, lingotes de aco
    }
    for _k, _v in FMATS.items():
        MATS.setdefault(_k, _v)

    W0 = Frame(0.0, 0.0, 0.0, 0.0)

# ------------------------------------------------------------------ materiais (nomes)
ST = "Stone_VM_Warm"            # pedra da forja (mesmo nome do kit: a paleta quente do V2b vale aqui tambem)
MOR = "Stone_VM_Mortar"
SOOT = "Stone_VM_Mortar"        # fuligem / carvao / forro da boca (junta escura do kit)
T = "Wood_VM_Timber"
PLK = "Wood_VM_Plank"
PL = "Plaster_VM_Cream"
RA, RB = "Roof_VM_Terracotta", "Roof_VM_Terracotta_B"
IRON = "Metal_VM_Iron"
STEEL = "Metal_VM_Steel"
BRONZE = "Metal_VM_Bronze"
GLOW = "Forge_Glow_VM"
LEATHER = "Wood_VM_Plank"       # lados do fole (claros contra as tabuas escuras)
SACK = "Cloth_VM_Cream"         # sacos de lona
WATER = "Water_VM"
COB, JOINT = "Stone_Paving_VM_Cob", "Stone_Paving_VM_Joint"
STI = "Stone_VM_Grey"           # pedra de dentro (salao, fornalha, peito de chamine, piso)
PLI = "Wood_VM_Plank"           # dentro: forro de tabuas entre as vigas (oficina escura e quente)
RED = "Cloth_VM_Red"

# ------------------------------------------------------------------ planta da forja (Roblox)
Y0 = 7.0                                    # piso (contrato do Ignis)
HX0, HX1 = -17.0, 15.0                      # salao: faces externas das paredes laterais
WT = 1.4                                    # espessura das paredes
IX0, IX1 = HX0 + WT, HX1 - WT               # faces internas (-15,6 / 13,6)
HZF = -50.0                                 # ponta das paredes laterais (frente)
HZB = -77.0                                 # face interna do fundo
HZO = HZB - WT                              # face externa do fundo (-78,4)
HXC = (HX0 + HX1) / 2                       # -1
GH = 8.0                                    # base de pedra ate 15
EAVE = 34.6                                 # frechal / topo da verga
PZ, PS = -51.2, 2.8                         # pilares da frente: centro em z, lado
PXS = (-16.0, 14.0)
LINT0 = 32.0                                # verga 32 .. 34,6 (fora da envoltoria em z; acima da cabeca vista da praca)
PITCH = 48.0
# fornalha
FXC, FW = -0.9, 16.0
FZF = -71.4                                 # face da fornalha
FTOP = 19.4
MHW, MSILL, MSPR, MDEP, MRING = 4.0, 9.0, 13.0, 4.0, 1.3     # boca: meio vao, peitoril, nascenca, fundo, aduela
# telheiro leste + roda + pilao
SX0, SX1 = 15.0, 31.8
SZF, SZB = -52.4, -78.4
SEAVE = 15.4
WX, WY, WZ = 36.0, 9.4, -66.0               # = L.WHEEL
WR = 7.5
WHW = 1.6                                   # meia largura da roda (aros em x 34,4 / 37,6)
AX0, AX1 = 21.2, 40.9                       # eixo (madeira) do cavalete interno ate o mancal leste
CAM_X, CAM_LEN = 24.5, 1.6
HPIV = (24.5, 12.2, -73.5)                  # pivo do martinete
HHEAD = (24.5, 10.0, -57.4)                 # centro da cabeca de ferro
HANVIL_TOP = 8.65
# chamine
CHX, CHZ = 0.0, -86.0
CH_BASE_TOP = 40.0
CH_TOP = 94.7                               # topo da laje-lintel da camara de fogo (a capa sobe ate ~97,3)


# ================================================================== utilitarios (Roblox)
def P(x, y, z):
    """ponto Roblox (x, y, z) -> Vector Blender"""
    return VL.B(x, z, y)


def fr(x, z, y, fx, fz):
    """Frame do kit: origem (x, z) na cota y, +y local = direcao (fx, fz) Roblox"""
    return K.frame_r(x, z, y, fx, fz)


def rb(mb, x0, x1, y0, y1, z0, z1, m):
    """caixa alinhada em coordenadas ROBLOX"""
    bb(mb, W0, x0, x1, -z0, -z1, y0, y1, m)


def colr(area, lo, hi):
    return VL.colr(area, lo, hi)


def face_frame(a, b, y, n):
    """parede de a=(x,z) a b=(x,z) com normal n=(nx,nz) para FORA: Frame no meio, +y = normal; e o comprimento"""
    mx, mz = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    return fr(mx, mz, y, n[0], n[1]), math.hypot(b[0] - a[0], b[1] - a[1]), (mx, mz), (-n[1], n[0])


def lx(c, u, x, z):
    """coordenada local x (ao longo da parede) de um ponto Roblox"""
    return (x - c[0]) * u[0] + (z - c[1]) * u[1]


def big_stone(mb, a, b, y0, y1, n, m=ST, holes=(), seed=0, lod=0, m2=None, p2=0.0, size=1.0):
    """pedra arredondada do kit em fiadas MAIORES (base da forja: 'pedra arredondada grande')"""
    F, Ln, c, u = face_frame(a, b, y0, n)
    course = (1.35 * size, 2.1 * size)
    length = (1.9 * size, 3.6 * size)
    stone_face(mb, F, -Ln / 2, Ln / 2, -0.3, y1 - y0, m, holes=holes, seed=seed, lod=lod, course=course,
               length=length, m2=m2, p2=p2)
    return F, Ln, c, u


def ashlar(mb, a, b, y0, y1, n, m=ST, seed=0, course=(1.7, 2.3), length=(2.8, 4.6), m2=None, p2=0.0, cut=0.2,
           back=-0.62):
    """cantaria da chamine: fiadas de blocos chanfrados (pillow do kit), poucos cantos cortados (26 tris por bloco)"""
    F, Ln, c, u = face_frame(a, b, y0, n)
    r = K.rng("ashlar", seed)
    x0, x1 = -Ln / 2, Ln / 2
    z, k = -0.2, 0
    H = y1 - y0
    while z < H - 0.25:
        h = r.uniform(*course)
        if H - (z + h) < 0.9:
            h = H - z
        x = x0
        first = True
        while x < x1 - 0.2:
            ln = r.uniform(*length) * (0.55 if first and k % 2 else 1.0)
            first = False
            x2 = min(x1, x + ln)
            if x1 - x2 < 1.2:
                x2 = x1
            mm = m2 if (m2 and r.random() < p2) else m
            ct = (r.randint(0, 1), r.uniform(0.12, 0.3), r.uniform(0.12, 0.3)) if r.random() < cut else None
            pillow(mb, F, x + 0.07, x2 - 0.07, z + 0.07 + r.uniform(0, 0.06), z + h - 0.07, back,
                   r.uniform(-0.05, 0.08), mm, c=0.3, cut=ct)
            x = x2
        z += h
        k += 1
    return F


def cut_x(ob, xc, keep_less=True):
    """apaga as faces da malha com centro alem do plano x = xc (Roblox; a malha e cortada no plano)"""
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(xc, 0, 0), plane_no=(1, 0, 0))
    kill = [f for f in bm.faces if (f.calc_center_median().x > xc + 1e-4) == keep_less]
    bmesh.ops.delete(bm, geom=kill, context="FACES")
    bmesh.ops.dissolve_degenerate(bm, dist=1e-4, edges=bm.edges[:])
    bm.to_mesh(me)
    bm.free()
    return len(kill)


def cut_top(ob, x0, x1, z0, z1):
    """fura o TOPO do chao (faces para cima) na caixa Roblox (mesma rotina do vm_trecho): o piso da forja assenta"""
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    for co, no in (((x0, 0, 0), (1, 0, 0)), ((x1, 0, 0), (1, 0, 0)), ((0, -z0, 0), (0, 1, 0)), ((0, -z1, 0), (0, 1, 0))):
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        bmesh.ops.bisect_plane(bm, geom=geom, plane_co=co, plane_no=no)
    bm.normal_update()
    kill = [f for f in bm.faces if f.normal.z > 0.9 and x0 + 1e-3 < f.calc_center_median().x < x1 - 1e-3 and
            -z1 + 1e-3 < f.calc_center_median().y < -z0 - 1e-3]
    bmesh.ops.delete(bm, geom=kill, context="FACES_ONLY")
    bmesh.ops.dissolve_degenerate(bm, dist=1e-4, edges=bm.edges[:])
    bad = [f for f in bm.faces if f.calc_area() < 1e-6]
    if bad:
        bmesh.ops.delete(bm, geom=bad, context="FACES_ONLY")
    bm.to_mesh(me)
    bm.free()
    return len(kill)


def join_into(dst, src):
    """junta src em dst (mesmos materiais = mesmas MeshParts)"""
    with bpy.context.temp_override(active_object=dst, object=dst, selected_objects=[dst, src],
                                   selected_editable_objects=[dst, src]):
        bpy.ops.object.join()
    return dst


# ================================================================== blockout do V0 sai
def drop_blockout():
    n = 0
    for o in list(bpy.data.objects):
        if o.name.startswith("VM_Frg_") or o.name.startswith("COL_Forge_"):
            bpy.data.objects.remove(o, do_unlink=True)
            n += 1
    tg = bpy.data.objects.get("VM_Ter_Ground")
    k = 0
    if tg:
        k = cut_top(tg, IX0, SX1, HZB - 0.6, HZF + 0.3) + cut_top(tg, SX0, SX1, SZB, SZF)
    print("FORJA: blockout do V0 removido (%d objetos/COL), chao furado sob o piso (%d faces)" % (n, k))


# ================================================================== SALAO
def hall_walls(mb):
    """paredes laterais e do fundo: miolo + pedra arredondada grande (base ate 15) + enxaimel ate 34,6.
    DENTRO (o que se ve pela frente aberta) = pedra cinza e FORRO DE TABUAS entre as vigas (oficina escura e quente: o
    Ignis le em silhueta contra a fornalha), 2 faixas altas com diagonais; FORA = faixas do kit acima das alas."""
    yb = Y0 + GH
    hb = (EAVE - yb) / 3.0
    hi = (EAVE - yb) / 2.0
    # miolos (junta escura na base, reboco em cima)
    for x0, x1 in ((HX0 + CORE, IX0 - CORE), (IX1 + CORE, HX1 - CORE)):
        rb(mb, x0, x1, Y0 - 0.3, yb, HZO + CORE, HZF, MOR)
        rb(mb, x0, x1, yb, EAVE, HZO + CORE, HZF, PL)
    rb(mb, IX0 - CORE, IX1 + CORE, Y0 - 0.3, yb, HZO + CORE, HZB - CORE, MOR)
    rb(mb, IX0 - CORE, IX1 + CORE, yb, EAVE, HZO + CORE, HZB - CORE, PL)
    # pedra: dentro (as 3 faces que se veem pela frente aberta), fora so a leste (dentro do telheiro) e o fundo
    big_stone(mb, (IX0, HZF), (IX0, HZB), Y0, yb, (1, 0), m=STI, seed="hW_in")
    big_stone(mb, (IX1, HZB), (IX1, HZF), Y0, yb, (-1, 0), m=STI, seed="hE_in")
    Fb, Lb, cb, ub = face_frame((IX1, HZB), (IX0, HZB), Y0, (0, 1))
    hx = sorted((lx(cb, ub, FXC - FW / 2, HZB), lx(cb, ub, FXC + FW / 2, HZB)))
    stone_face(mb, Fb, -Lb / 2, Lb / 2, -0.3, GH, STI, holes=[(hx[0] + 0.3, hx[1] - 0.3, -0.4, GH + 1.0)],
               seed="hB_in", course=(1.35, 2.1), length=(1.9, 3.6))
    big_stone(mb, (HX1, HZF), (HX1, SZB), Y0, yb, (1, 0), seed="hE_out", lod=2)
    big_stone(mb, (HX0, HZO), (HX1, HZO), Y0, yb, (0, -1), seed="hB_out", lod=2)
    big_stone(mb, (HX0, HZO), (HX0, -52.0 - WING_W["D"] - 0.2), Y0, yb, (-1, 0), seed="hW_out", lod=1)   # atras da ala
    # DENTRO: 2 faixas de 9,8 (montantes a ~4,6 com diagonais alternadas; janelas altas nas laterais)
    for k in range(2):
        y = yb + k * hi
        for (a, b, n) in (((IX0, HZF), (IX0, HZB), (1, 0)), ((IX1, HZB), (IX1, HZF), (-1, 0)),
                          ((IX1, HZB), (IX0, HZB), (0, 1))):
            F, Ln, c, u = face_frame(a, b, y, n)
            nbay = max(2, int(round(Ln / 4.6)))
            xs = [-Ln / 2 + Ln * i / nbay for i in range(nbay + 1)]
            if k == 1 and n[1] == 0:
                ks = ["win" if i % 2 == 1 else ("Dl" if i < nbay / 2 else "Dr") for i in range(nbay)]
            else:
                ks = ["Dl" if i % 2 == 0 else "Dr" for i in range(nbay)]
            K.upper_wall(mb, F, Ln, hi, PLI, xs, ks, dmb=None, seed=("hall_in", a, b, k), lod=1, shutters=False)
    # FORA: faixas 1 e 2 do kit (janelas) acima das alas; a faixa 0 (atras dos telhados da ala e do telheiro) e o fundo
    # (atras da chamine) so com frechais e montantes (o reboco e o do miolo)
    for k in range(3):
        y = yb + k * hb
        for (a, b, n) in (((HX0, HZO), (HX0, HZF), (-1, 0)), ((HX1, HZF), (HX1, HZO), (1, 0)),
                          ((HX0, HZO), (HX1, HZO), (0, -1))):
            F, Ln, c, u = face_frame(a, b, y, n)
            if n[0] < 0 and k == 0:
                continue                                   # atras da ala oeste (geminada): so o reboco do miolo
            if k == 0 or n[1] != 0:
                bb(mb, F, -Ln / 2, Ln / 2, -0.45, 0.2, hb - 0.44, hb, T)
                for x in even(-Ln / 2, Ln / 2, 4.6) + [-Ln / 2 + 0.28, Ln / 2 - 0.28]:
                    bb(mb, F, x - 0.25, x + 0.25, -0.45, 0.2, 0.0, hb - 0.4, T)
                continue
            rr = K.rng("hallbays", a, b, k)
            xs, ks = K.bays_for(Ln, "B", rr)
            K.upper_wall(mb, F, Ln, hb, PL, xs, ks, dmb=None, seed=("hall", a, b, k), lod=1, shutters=False)
    return yb


def hall_front(mb, pm):
    """pilares grossos sobre soco de pedra, verga dupla com cintas, maos-francesas, lanternas de ferro"""
    lights = []
    h = PS / 2
    c = 0.38
    poly = [(-h + c, -h), (h - c, -h), (h, -h + c), (h, h - c), (h - c, h), (-h + c, h), (-h, h - c), (-h, -h + c)]
    for i, px in enumerate(PXS):
        Fp = fr(px, PZ, Y0, 0, 1)
        K.through_stone(mb, Fp, -h - 0.55, h + 0.55, -h - 0.55, h + 0.55, -0.3, 1.5, ST, c=0.3)        # soco
        K.through_stone(mb, Fp, -h - 0.2, h + 0.2, -h - 0.2, h + 0.2, 1.4, 1.9, ST, c=0.16)
        ext(mb, Fp, poly, "z", 1.85, LINT0 - Y0, T)                                                  # pilar octog.
        for zz in (2.6, LINT0 - Y0 - 6.6):                                                          # cintas
            bb(mb, Fp, -h - 0.18, h + 0.18, -h - 0.18, h + 0.18, zz, zz + 0.45, IRON)
        # mao-francesa para dentro do vao (no plano da verga)
        s = 1 if px < HXC else -1
        mb.beam(P(px + s * h, LINT0 - 6.2, PZ), P(px + s * (h + 4.4), LINT0 - 0.05, PZ), 1.0, 1.0, T, 0.0)
        mb.beam(P(px - s * h, LINT0 - 3.4, PZ), P(px - s * (h + 1.4), LINT0 - 0.05, PZ), 0.8, 0.8, T, 0.0)
        # lanterna de ferro num braco, na face da frente do pilar (fora do vao)
        yl = 15.6
        mb.rod(P(px, yl, PZ + h), P(px, yl, PZ + h + 1.7), 0.09, IRON, 6)
        mb.rod(P(px, yl - 1.1, PZ + h), P(px, yl - 0.05, PZ + h + 1.2), 0.07, IRON, 6)
        Fl = fr(px, PZ + h + 1.5, Y0, 0, 1)
        p = K.lantern(pm, Fl, yl - Y0 - 2.6, hh=1.6, w=0.48)
        lights.append(("L_VM_Lamp_Frg%d" % (i + 1), p))
        banner(pm, px, PZ + h)
    # verga: viga principal (32..34) + frechal (34..34,6) mais fundo; cintas em U e cabecas de cavilha
    rb(mb, PXS[0] - h - 1.6, PXS[1] + h + 1.6, LINT0, LINT0 + 2.0, PZ - h, PZ + h, T)
    rb(mb, PXS[0] - h - 2.0, PXS[1] + h + 2.0, LINT0 + 2.0, EAVE, PZ - h - 0.2, PZ + h + 0.25, T)
    for x in (PXS[0], PXS[1], HXC - 6.0, HXC + 6.0):
        rb(mb, x - 0.45, x + 0.45, LINT0 - 0.1, LINT0 + 2.1, PZ + h, PZ + h + 0.12, IRON)
        rb(mb, x - 0.45, x + 0.45, LINT0 - 0.25, LINT0 + 0.02, PZ - h - 0.15, PZ + h + 0.12, IRON)
    return lights


ANVIL = [[(-2.5, 1.9), (3.2, 1.9), (3.3, 0.75), (1.55, 0.45), (-1.25, 0.5), (-2.7, 0.75)],
         [(-1.25, 0.5), (1.55, 0.45), (0.95, -0.75), (-0.65, -0.75)],
         [(-0.65, -0.75), (0.95, -0.75), (2.35, -1.55), (2.6, -2.25), (-2.3, -2.25), (-2.05, -1.55)],
         [(-4.6, 1.35), (-2.5, 1.9), (-2.7, 0.75)]]          # bigorna de perfil (mesma do medalhao da praca)


def banner(pm, x, zf, y1=30.6, y0=19.0, w=2.3):
    """ESTANDARTE vermelho no pilar (face da frente): vara de ferro, pano com ponta dupla, bigorna de bronze"""
    pm.rod(P(x - w / 2 - 0.35, y1 + 0.25, zf + 0.55), P(x + w / 2 + 0.35, y1 + 0.25, zf + 0.55), 0.1, IRON, 6)
    for s in (-1, 1):
        rb(pm, x + s * (w / 2 + 0.2) - 0.08, x + s * (w / 2 + 0.2) + 0.08, y1 - 0.1, y1 + 0.3, zf, zf + 0.6, IRON)
    F = fr(x, zf + 0.42, 0.0, 0, 1)
    pts = [(-w / 2, y1), (w / 2, y1), (w / 2, y0), (0.0, y0 + 1.1), (-w / 2, y0)]
    ext(pm, F, [(-a, b) for a, b in pts], "y", -0.07, 0.07, RED)
    sc = 0.3
    zc = y1 - 4.4
    for pc in ANVIL:
        ext(pm, F, [(-x * sc, zc + y * sc) for x, y in reversed(pc)], "y", 0.0, 0.24, BRONZE)
    bb(pm, F, -w / 2 + 0.25, w / 2 - 0.25, 0.0, 0.22, y1 - 1.0, y1 - 0.8, BRONZE)


def hall_roof(mb):
    """telhado do salao (cumeeira ao longo de Z, beiral maior na frente), oitoes e tesouras"""
    length = HZF - HZO
    span = HX1 - HX0
    Fr_ = fr(HXC, (HZF + HZO) / 2, EAVE, 0, 1)
    RF = sub(Fr_, 0.0, 0.0, 0.0, math.pi / 2)            # +x local = frente (+Z)
    ri = K.roof(mb, RF, length, span, PITCH, 1.3, (0.6, 2.6), RA, RB, seed="frg_hall", course=1.4)
    rise = ri["rise"]
    Fg = sub(RF, length / 2, 0.0, 0.0, -math.pi / 2)
    K.gable_wall(mb, Fg, span, rise, PL, window_=False, seed="frg_gF")
    Fgi = fr(HXC, HZF - 1.5, EAVE, 0, -1)                 # costas do oitao da frente (de dentro do salao)
    K.gable_wall(mb, Fgi, IX1 - IX0, (IX1 - IX0) / 2 * ri["tp"], PLI, party=True, seed="frg_gFi")
    Fb = sub(RF, -length / 2, 0.0, 0.0, math.pi / 2)
    K.gable_wall(mb, Fb, span, rise, PL, party=True, seed="frg_gB")
    # oitao do fundo por DENTRO (visto pela frente aberta): reboco + linha
    Fi = fr(HXC, HZB, EAVE, 0, 1)
    K.gable_wall(mb, Fi, IX1 - IX0, (IX1 - IX0) / 2 * ri["tp"], PLI, party=True, seed="frg_gBi")
    # tesouras: linha (acima da envoltoria: 33,4), pendural, escoras e pernas
    top = EAVE + rise - 1.25
    for z in (-57.5, -64.5, -71.5):
        rb(mb, IX0, IX1, EAVE - 1.2, EAVE, z - 0.55, z + 0.55, T)
        rb(mb, HXC - 0.45, HXC + 0.45, EAVE, top, z - 0.45, z + 0.45, T)
        for s in (-1, 1):
            xw = IX0 if s < 0 else IX1
            mb.beam(P(xw - s * 0.3, EAVE - 0.4, z), P(HXC + s * 0.5, top - 0.3, z), 0.8, 0.9, T, 0.0)
            mb.beam(P(HXC + s * 5.6, EAVE, z), P(HXC + s * 0.4, EAVE + rise * 0.55, z), 0.6, 0.6, T, 0.0)
        rb(mb, HXC - 0.62, HXC + 0.62, EAVE - 1.42, EAVE + 0.02, z - 0.72, z + 0.72, IRON)     # estribo
    # cumeeira interna (terca) ligando os pendurais
    rb(mb, HXC - 0.4, HXC + 0.4, top - 0.9, top, HZB, HZF, T)
    return ri, Fg


def gable_sign(mb, pm, Fg, rise):
    """PLACA DA BIGORNA no oitao da frente: quadro de tabuas com moldura escura, bigorna de bronze em relevo com 2
    martelos cruzados por cima, presa por 2 bracos de ferro (Y ~37..42, acima da verga: nao tapa o golem)"""
    w, h = 12.4, 4.8
    z0 = 2.6
    Fs = sub(Fg, 0.0, 0.32, 0.0)
    bb(pm, Fs, -w / 2, w / 2, 0.0, 0.32, z0, z0 + h, PLK)
    for (x0, x1, za, zb) in ((-w / 2 - 0.3, w / 2 + 0.3, z0 - 0.3, z0), (-w / 2 - 0.3, w / 2 + 0.3, z0 + h, z0 + h + 0.3),
                             (-w / 2 - 0.3, -w / 2, z0, z0 + h), (w / 2, w / 2 + 0.3, z0, z0 + h)):
        bb(pm, Fs, x0, x1, -0.05, 0.5, za, zb, T)
    for x in (-w / 2 + 2.1, w / 2 - 2.1):
        bb(pm, Fs, x - 0.12, x + 0.12, 0.32, 0.5, z0 + 0.1, z0 + h - 0.1, T)                 # ripas
    # bigorna (perfil) em pecas convexas (mesma forma do medalhao), escala 0,62, em +y (frente)
    sc = 0.62
    zc = z0 + h * 0.42
    for pc in ANVIL:
        ext(pm, Fs, [(-x * sc, zc + y * sc) for x, y in reversed(pc)], "y", 0.3, 0.62, BRONZE)
    # martelos cruzados sobre a bigorna
    for s in (-1, 1):
        a = (s * 2.6, zc + 1.55)
        b = (-s * 0.6, zc + 4.05)
        K.beam(pm, Fs, (a[0], 0.46, a[1]), (b[0], 0.46, b[1]), 0.22, 0.32, BRONZE)
        d = (b[0] - a[0], b[1] - a[1])
        ln = math.hypot(*d)
        ux, uz = d[0] / ln, d[1] / ln
        hx, hz = b[0] + ux * 0.1, b[1] + uz * 0.1
        K.beam(pm, Fs, (hx - uz * 0.75, 0.46, hz + ux * 0.75), (hx + uz * 0.75, 0.46, hz - ux * 0.75), 0.3, 0.62,
               BRONZE)
    for x in (-w / 2 + 1.0, w / 2 - 1.0):                                                    # bracos de ferro
        bb(pm, Fs, x - 0.12, x + 0.12, -0.2, 0.55, z0 + h + 0.25, z0 + h + 1.1, IRON)


# ================================================================== FORNALHA + peito de chamine
def arch(mb, F, hw, zs, ow, ztop, m, n=9, yb=-0.66, yf=0.2):
    """aduelas de um arco PLENO (raio hw, centro (0, zs)) ate o vao retangular (ow, ztop) do stone_face; chave saliente
    (mesma ideia do vm_kit.door)"""
    R = hw

    def hit(th):
        ct, st = math.cos(th), math.sin(th)
        t1 = (ztop - zs) / st if st > 1e-6 else 1e9
        t2 = (ow / abs(ct)) if abs(ct) > 1e-6 else 1e9
        t = min(t1, t2)
        return (ct * t, zs + st * t)
    edges = [math.pi * i / n for i in range(n + 1)]
    for i in range(n):
        a = edges[i] + (0.012 if i > 0 else 0.0)
        b = edges[i + 1] - (0.012 if i < n - 1 else 0.0)
        ha, hb_ = hit(a), hit(b)
        pts = [(R * math.cos(a), zs + R * math.sin(a)), ha]
        if abs(ha[0] - ow) < 1e-4 and abs(hb_[1] - ztop) < 1e-4:
            pts.append((ow, ztop))
        if abs(ha[1] - ztop) < 1e-4 and abs(hb_[0] + ow) < 1e-4:
            pts.append((-ow, ztop))
        pts += [hb_, (R * math.cos(b), zs + R * math.sin(b))]
        dz = 0.22 if i == n // 2 else 0.0
        ext(mb, F, pts, "y", yb, yf + dz, m)
    # ombreiras alternadas do peitoril a nascenca
    for s in (-1, 1):
        z, k = MSILL - Y0 - 0.1, 0
        while z < zs - 0.2:
            hh = 1.2 if k % 2 == 0 else 0.95
            z2 = min(zs, z + hh)
            if zs - z2 < 0.5:
                z2 = zs
            wj = (ow - hw) if k % 2 == 0 else (ow - hw) * 0.7
            xa, xb = s * hw, s * (hw + wj)
            pillow(mb, F, min(xa, xb) + 0.04, max(xa, xb) - 0.04, z + 0.05, z2 - 0.05, yb, yf, m, c=0.16)
            z = z2
            k += 1


def furnace(mb, im):
    """bloco da fornalha + boca acesa em moldura + verga e peito de chamine em 3 recuos"""
    x0, x1 = FXC - FW / 2, FXC + FW / 2
    # miolo em pedacos em volta do vao (o recesso fica oco: o fogo aparece)
    rb(mb, x0 + CORE, x1 - CORE, Y0 - 0.3, MSILL - 0.95, HZB, FZF - CORE, MOR)
    rb(mb, x0 + CORE, FXC - MHW - 0.75, Y0 - 0.3, FTOP, HZB, FZF - CORE, MOR)
    rb(mb, FXC + MHW + 0.75, x1 - CORE, Y0 - 0.3, FTOP, HZB, FZF - CORE, MOR)
    rb(mb, x0 + CORE, x1 - CORE, MSPR + MHW + 0.75, FTOP, HZB, FZF - CORE, MOR)
    rb(mb, FXC - MHW - 0.8, FXC + MHW + 0.8, Y0 - 0.3, FTOP, HZB, FZF - MDEP - 0.7, MOR)
    F = fr(FXC, FZF, Y0, 0, 1)                         # local x = -X Roblox (simetrico em volta de FXC)
    zs = MSPR - Y0
    ow = MHW + MRING
    ztop = zs + MHW + MRING
    zsill = MSILL - Y0
    stone_face(mb, F, -FW / 2, FW / 2, -0.3, FTOP - Y0, STI, holes=[(-ow, ow, zsill - 0.55, ztop)], seed="frn_F",
               course=(1.35, 2.1), length=(1.9, 3.6), m2=SOOT, p2=0.12)
    for s in (-1, 1):
        a = (FXC + s * FW / 2, FZF)
        b = (FXC + s * FW / 2, HZB)
        big_stone(mb, a if s < 0 else b, b if s < 0 else a, Y0, FTOP, (s, 0), m=STI, seed=("frn_S", s), lod=1)
    arch(mb, F, MHW, zs, ow, ztop, ST)
    # peitoril saliente (bancada de pedra) sob a boca
    K.through_stone(mb, F, -MHW - 0.9, MHW + 0.9, -0.6, 1.1, zsill - 0.55, zsill + 0.05, ST, c=0.14)
    # recesso forrado de fuligem (blocos: faces viradas para dentro do vao)
    D = MDEP
    im = mb                                            # recesso e fogo no objeto do salao (menos MeshParts)
    LR = MHW + 0.2                                     # forro 0,2 atras da face das aduelas (degrau, sem coplanar)
    for s in (-1, 1):
        bb(im, F, s * LR, s * (LR + 0.7), -D - 0.4, -0.3, zsill - 0.6, zs + 0.02, SOOT)
    for i in range(8):
        a0, a1 = math.pi * i / 8, math.pi * (i + 1) / 8
        ext(im, F, [(LR * math.cos(a0), zs + LR * math.sin(a0)), ((LR + 0.7) * math.cos(a0), zs + (LR + 0.7) * math.sin(a0)),
                    ((LR + 0.7) * math.cos(a1), zs + (LR + 0.7) * math.sin(a1)), (LR * math.cos(a1), zs + LR * math.sin(a1))],
            "y", -D - 0.4, -0.3, SOOT)
    bb(im, F, -LR, LR, -D - 0.4, -0.3, zsill - 0.9, zsill - 0.3, SOOT)                      # soleira interna
    # FOGO dentro da moldura: fundo aceso, leito de brasas, carvao por cima e linguas de fogo
    bb(im, F, -MHW, MHW, -D - 0.75, -D - 0.35, zsill - 0.1, zs + MHW, GLOW)
    bb(im, F, -MHW + 0.2, MHW - 0.2, -D - 0.35, -0.9, zsill - 0.1, zsill + 0.18, GLOW)
    r = K.rng("coal_mouth")
    for i in range(26):
        x = r.uniform(-MHW + 0.5, MHW - 0.5)
        y = r.uniform(-D + 0.3, -1.0)
        s = r.uniform(0.38, 0.68)
        im.ico(s, F.p(x, y, zsill + 0.12 + s * 0.3), SOOT, 1, (1.0, 0.85, 0.6), rot=(r.uniform(0, 3), 0, r.uniform(0, 3)))
    for (x, y, hh, rr, tilt) in ((-1.6, -2.4, 3.4, 0.95, 0.12), (0.4, -2.9, 4.4, 1.1, -0.08), (1.9, -2.2, 3.0, 0.85, -0.15),
                                 (-0.5, -1.9, 2.4, 0.75, 0.2), (2.9, -3.0, 2.2, 0.7, -0.2), (-2.9, -3.0, 2.6, 0.75, 0.18),
                                 (1.0, -3.3, 3.8, 0.9, 0.05)):
        im.cyl(rr, hh, F.p(x, y, zsill + 0.1 + hh / 2), F.r(tilt, 0, r.uniform(0, 1)), GLOW, 5, r2=0.04, bevel=0.0)
    # verga de madeira sobre misulas de pedra + peito de chamine em 3 recuos (fuligem crescente)
    rb(mb, x0 - 1.5, x1 + 1.5, FTOP, FTOP + 1.4, FZF - 0.6, FZF + 0.7, T)
    for s in (-1, 1):
        xm = FXC + s * (FW / 2 + 0.8)
        Fm = fr(xm, FZF + 0.1, Y0, 0, 1)
        K.through_stone(mb, Fm, -0.75, 0.75, -0.9, 0.6, FTOP - Y0 - 2.6, FTOP - Y0 - 0.02, STI, c=0.16)
    steps = [(FTOP + 1.4, 25.8, FW + 1.0, -71.0, 0.1), (25.8, 30.4, FW - 2.0, -72.8, 0.3), (30.4, 39.0, FW - 5.0, -74.4, 0.7)]
    for i, (ya, yb_, w, zf, p2) in enumerate(steps):
        xa, xb = FXC - w / 2, FXC + w / 2
        rb(mb, xa + CORE, xb - CORE, FTOP if i == 0 else ya, yb_, HZB, zf - CORE, MOR)
        big_stone(mb, (xb, zf), (xa, zf), ya, yb_, (0, 1), m=STI, seed=("brs", i), m2=SOOT, p2=p2)
        big_stone(mb, (xa, HZB), (xa, zf), ya, yb_, (-1, 0), m=STI, seed=("brsW", i), m2=SOOT, p2=p2, lod=1)
        big_stone(mb, (xb, zf), (xb, HZB), ya, yb_, (1, 0), m=STI, seed=("brsE", i), m2=SOOT, p2=p2, lod=1)
        # capa inclinada do recuo (agua) ate a face do recuo seguinte / parede
        zn = steps[i + 1][3] if i + 1 < len(steps) else HZB
        poly = [(-(zf + 0.35), yb_ - 0.1), (-zn + 0.1, yb_ - 0.1), (-zn + 0.1, yb_ + 0.9), (-(zf + 0.35), yb_ + 0.15)]
        ext(mb, W0, [(py, pz) for py, pz in poly], "x", xa - 0.3, xb + 0.3, STI)
    # luz do fogo (unica com sombra): na frente da boca
    return P(FXC, MSILL + 2.8, FZF + 1.6)


# ================================================================== FOLE, carvao, cocho, ferramentas (dentro)
def bellows(im, mb):
    """fole de couro em gota sobre cavalete (oeste), bico de ferro na lateral da fornalha, balancim com corrente"""
    xb0, xb1 = -15.2, -10.3            # corpo (fundo -> bico)
    zc = -69.0
    yb = 9.9                           # tabua de baixo
    # contorno em gota no plano (x, z): largo atras, estreito no bico
    outline = []
    for i in range(10):
        t = i / 9.0
        x = xb0 + (xb1 - xb0) * t
        half = 2.0 * math.sqrt(max(0.0, 1.0 - (t * 1.0) ** 2.2)) * (1.0 - 0.62 * t) + 0.55 * t
        outline.append((x, half))
    pts_r = [(x, zc + hw) for x, hw in outline] + [(x, zc - hw) for x, hw in reversed(outline)]

    def ytop(x):
        return 10.35 + (xb1 - x) * 0.42
    # tabuas (de baixo e de cima) e couro em 3 aneis (bojo no meio)
    bottom = [(x, z) for x, z in pts_r]
    ext(im, W0, [(x, -z) for x, z in bottom], "z", yb - 0.3, yb, T)
    rings = []
    for k, f in enumerate((0.0, 0.25, 0.5, 0.75, 1.0)):
        ring = []
        for x, z in bottom:
            yy = yb + (ytop(x) - yb) * f
            bul = (1.0, 1.14, 0.95, 1.14, 1.0)[k]
            ring.append(P(x, yy, zc + (z - zc) * bul))
        rings.append(ring)
    bm = im.bm
    V = [[bm.verts.new(p) for p in r] for r in rings]
    fs = []
    nn = len(bottom)
    for a, b in zip(V, V[1:]):
        for j in range(nn):
            j2 = (j + 1) % nn
            fs.append(bm.faces.new((a[j], a[j2], b[j2], b[j])))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    im._post([v for r in V for v in r], LEATHER, 0.0, 0, 1)
    top_b = [P(x, ytop(x) + 0.02, z) for x, z in bottom]
    top_t = [P(x, ytop(x) + 0.32, z) for x, z in bottom]
    Vb = [bm.verts.new(p) for p in top_b]
    Vt = [bm.verts.new(p) for p in top_t]
    fs = [bm.faces.new(list(reversed(Vb))), bm.faces.new(Vt)]
    for j in range(nn):
        j2 = (j + 1) % nn
        fs.append(bm.faces.new((Vb[j], Vb[j2], Vt[j2], Vt[j])))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    im._post(Vb + Vt, T, 0.0, 0, 1)
    for x in (xb0 + 1.0, xb0 + 2.6):                                         # travessas na tabua de cima
        rb(im, x - 0.18, x + 0.18, ytop(x) + 0.28, ytop(x) + 0.5, zc - 1.6, zc + 1.6, T)
    # bico de ferro ate a lateral da fornalha
    im.rod(P(xb1 - 0.3, 10.55, zc), P(FXC - FW / 2 - 0.05, 10.55, zc), 0.36, IRON, 8)
    im.cyl(0.55, 0.3, P(FXC - FW / 2 - 0.25, 10.55, zc), (0, math.pi / 2, 0), IRON, 8, bevel=0.0)
    # cavalete
    for x in (xb0 + 0.5, xb1 - 0.6):
        for z in (zc - 1.6, zc + 1.6):
            rb(mb, x - 0.3, x + 0.3, Y0, yb - 0.3, z - 0.3, z + 0.3, T)
        rb(mb, x - 0.32, x + 0.32, yb - 0.75, yb - 0.3, zc - 2.0, zc + 2.0, T)
    # balancim: poste na frente, braco comprido, corrente ate a tabua de cima, argola na ponta da frente
    px, pz = -13.4, -62.6
    rb(mb, px - 0.45, px + 0.45, Y0, 19.6, pz - 0.45, pz + 0.45, T)
    K.through_stone(mb, fr(px, pz, Y0, 0, 1), -0.8, 0.8, -0.8, 0.8, -0.2, 0.6, ST, c=0.15)
    mb.beam(P(px, 19.9, -71.5), P(px, 19.3, -57.8), 0.6, 0.7, T, 0.0)
    rb(mb, px - 0.55, px + 0.55, 19.2, 20.4, pz - 0.2, pz + 0.2, IRON)
    xr = -13.4
    for k in range(9):                                                        # corrente (elos alternados)
        y = 19.4 - 0.85 * k
        if y < ytop(xr) + 0.6:
            break
        if k % 2 == 0:
            rb(im, xr - 0.06, xr + 0.06, y - 0.42, y, -69.2, -68.8, IRON)
        else:
            rb(im, xr - 0.2, xr + 0.2, y - 0.42, y, -69.06, -68.94, IRON)
    for k in range(5):
        y = 19.0 - 0.8 * k
        rb(im, px - 0.06, px + 0.06, y - 0.4, y, -58.2, -57.8, IRON) if k % 2 == 0 else \
            rb(im, px - 0.2, px + 0.2, y - 0.4, y, -58.06, -57.94, IRON)
    im.cyl(0.55, 0.14, P(px, 14.6, -58.0), (math.pi / 2, 0, 0), IRON, 10, bevel=0.0)
    colr("FrgProps", (xb0 - 0.4, Y0, zc - 2.4), (FXC - FW / 2, ytop(xb0) + 0.6, zc + 2.4))
    colr("FrgProps", (px - 0.6, Y0, pz - 0.6), (px + 0.6, 19.6, pz + 0.6))


def sack(m, x, z, y, h=2.0, r=0.85, ang=0.0, lean=0.0, k=0):
    """SACO de lona com carvao: corpo achatado e irregular (aneis elipticos com ruido), gargalo amarrado com corda,
    boca dobrada e carvao aparecendo"""
    rr = K.rng("sack", round(x, 2), round(z, 2), k)
    F = sub(fr(x, z, y, 0, 1), 0, 0, 0, ang)
    sq = rr.uniform(0.72, 0.85)                       # achatado (saco cheio apoiado)
    prof = [(1.0, 0.0), (1.12, 0.22), (1.05, 0.55), (0.78, 0.78), (0.36, 0.9), (0.3, 0.97), (0.5, 1.06), (0.42, 1.1)]
    n = 9
    rings = []
    for i, (f, t) in enumerate(prof):
        ring = []
        for j in range(n):
            a = 2 * math.pi * j / n
            jit = 1.0 + (rr.uniform(-0.08, 0.08) if 0 < i < 4 else 0.0)
            ring.append((r * f * jit * math.cos(a), r * f * jit * sq * math.sin(a), h * t))
        rings.append(ring)
    loft(m, F, rings, SACK)
    lathe(m, F, (0, 0, 0), [(r * 0.38, h * 0.9), (r * 0.38, h * 0.97)], 8, T)          # corda
    m.ico(r * 0.36, F.p(0, 0, h * 1.07), SOOT, 1, (1.0, 1.0, 0.5))


def coal_bin(im):
    x0, x1, z0, z1 = -15.3, -11.3, -61.4, -55.6
    for a, b, c_, d in ((x0, x1, z0, z0 + 0.3), (x0, x1, z1 - 0.3, z1), (x0, x0 + 0.3, z0, z1), (x1 - 0.3, x1, z0, z1)):
        rb(im, a, b, Y0, Y0 + 1.7, c_, d, PLK)
    for x in (x0 - 0.15, x1 - 0.45):
        for z in (z0 - 0.15, z1 - 0.45):
            rb(im, x, x + 0.6, Y0, Y0 + 1.95, z, z + 0.6, T)
    r = K.rng("coalbin")
    rb(im, x0 + 0.3, x1 - 0.3, Y0 + 0.5, Y0 + 1.25, z0 + 0.3, z1 - 0.3, SOOT)
    for i in range(22):
        x = r.uniform(x0 + 0.6, x1 - 0.6)
        z = r.uniform(z0 + 0.6, z1 - 0.6)
        s = r.uniform(0.26, 0.42)
        d = min(1.0, math.hypot((x - (x0 + x1) / 2) / 2, (z - (z0 + z1) / 2) / 3))
        im.ico(s, P(x, Y0 + 1.2 + (1.0 - d) * 0.45, z), SOOT, 1, (1.0, 0.9, 0.6), rot=(r.uniform(0, 3), 0, r.uniform(0, 3)))
    # pa encostada
    im.rod(P(-11.0, Y0 + 0.6, -55.2), P(-11.6, Y0 + 5.8, -56.4), 0.12, T, 6)
    Fp = fr(-10.95, -55.1, Y0, 0.1, 1)
    K.beam(im, Fp, (0, 0, 0.1), (0, 0.05, 1.3), 0.12, 0.95, IRON)
    sack(im, -14.4, -53.7, Y0, h=2.1)
    sack(im, -12.6, -53.4, Y0, h=1.9, ang=0.6, k=1)
    sack(im, -14.6, -64.2, Y0, h=2.0, ang=1.2, k=2)
    colr("FrgProps", (x0, Y0, z0), (x1, Y0 + 2.4, z1))
    colr("FrgProps", (-15.4, Y0, -54.6), (-11.8, Y0 + 2.2, -52.6))


def quench_and_tools(im, mb):
    """cocho de tempera, cabideiro de ferramentas na parede leste, banco com lingotes (lado leste, fora da envoltoria)"""
    x0, x1, z0, z1 = 7.4, 12.8, -59.6, -55.6
    yt = Y0 + 2.4
    for a, b, c_, d in ((x0, x1, z0, z0 + 0.3), (x0, x1, z1 - 0.3, z1), (x0, x0 + 0.3, z0, z1), (x1 - 0.3, x1, z0, z1)):
        rb(im, a, b, Y0 + 0.5, yt, c_, d, PLK)
    rb(im, x0 + 0.3, x1 - 0.3, Y0 + 0.5, Y0 + 0.75, z0 + 0.3, z1 - 0.3, PLK)
    rb(im, x0 + 0.3, x1 - 0.3, Y0 + 0.75, yt - 0.35, z0 + 0.3, z1 - 0.3, WATER)
    for x in (x0 + 0.9, x1 - 0.9):
        rb(im, x - 0.15, x + 0.15, Y0 + 0.45, yt + 0.15, z0 - 0.16, z1 + 0.16, IRON)
    for x in (x0 + 0.2, x1 - 0.5):
        for z in (z0 + 0.2, z1 - 0.5):
            rb(im, x, x + 0.3, Y0, Y0 + 0.5, z, z + 0.3, T)
    # lamina mergulhando (barra quente) e tenaz apoiada na borda
    K.beam(im, W0, P(9.0, yt + 0.9, -57.3), P(10.6, yt - 0.6, -57.6), 0.18, 0.5, STEEL)
    for s in (-0.12, 0.12):
        im.rod(P(8.9, yt + 0.95, -57.3 + s), P(7.0, yt + 2.2, -56.6 + s * 3), 0.06, IRON, 6)
    colr("FrgProps", (x0, Y0, z0), (x1, yt, z1))
    # cabideiro na parede leste (face x 13,6)
    rb(mb, IX1 - 0.55, IX1, 13.8, 14.5, -70.2, -60.4, T)
    tools = [(-61.4, "tong"), (-63.2, "ham"), (-65.0, "tong"), (-66.8, "ham"), (-68.6, "tong")]
    for z, kind in tools:
        rb(im, IX1 - 1.0, IX1 - 0.5, 14.0, 14.3, z - 0.1, z + 0.1, T)            # cavilha
        if kind == "tong":
            for s in (-1, 1):
                im.rod(P(IX1 - 0.95, 14.0, z + s * 0.08), P(IX1 - 0.85, 9.6, z + s * 0.55), 0.07, IRON, 6)
            rb(im, IX1 - 1.05, IX1 - 0.75, 9.2, 9.7, z - 0.75, z + 0.75, IRON)
        else:
            im.rod(P(IX1 - 0.9, 14.0, z), P(IX1 - 0.9, 10.4, z), 0.12, T, 6)
            rb(im, IX1 - 1.25, IX1 - 0.55, 9.6, 10.5, z - 0.85, z + 0.85, IRON)
    # banco com lingotes (barras trapezoidais em camadas cruzadas)
    bx0, bx1, bz0, bz1 = 8.6, 13.0, -74.8, -72.0
    rb(im, bx0, bx1, Y0 + 1.5, Y0 + 1.85, bz0, bz1, PLK)
    for x in (bx0 + 0.2, bx1 - 0.5):
        for z in (bz0 + 0.2, bz1 - 0.5):
            rb(im, x, x + 0.3, Y0, Y0 + 1.5, z, z + 0.3, T)
    ingots(im, (bx0 + bx1) / 2, (bz0 + bz1) / 2, Y0 + 1.85, layers=3, along=(1, 0))
    colr("FrgProps", (bx0, Y0, bz0), (bx1, Y0 + 3.0, bz1))


def ingots(m, cx, cz, y, layers=3, n=4, mats=(IRON, BRONZE), along=(0, 1)):
    """LINGOTES: barras trapezoidais compridas empilhadas em piramide (n, n-1, ...), todas no mesmo sentido"""
    F0 = fr(cx, cz, y, along[0], along[1])
    for k in range(layers):
        nk = n - k
        for i in range(nk):
            off = (i - (nk - 1) / 2) * 0.82
            mm = mats[(i + k) % len(mats)]
            Fm = sub(F0, off, 0.0, k * 0.44)
            ext(m, Fm, [(-0.38, 0.0), (0.38, 0.0), (0.27, 0.44), (-0.27, 0.44)], "y", -1.15, 1.15, mm)


# ================================================================== PROPS de fora: picaretas a venda, sacos, lingotes
def pickaxe(m, F, x, head_m, hl=4.5, lean=0.0):
    """PICARETA pendurada: cabeca apoiada no travessao (o olho em z=0 local do F), cabo descendo. Cabeca em crescente
    com as pontas para os lados (le de frente), olho de ferro, cabo de madeira com empunhadura de couro."""
    Fp = sub(F, x, 0.0, 0.0)
    m.cyl(0.17, hl, Fp.p(0, 0.0, -hl / 2 + 0.5), Fp.r(lean, 0, 0), PLK, 6, bevel=0.0)
    m.cyl(0.31, 1.0, Fp.p(0, -math.sin(lean) * (hl - 0.9), -hl + 1.2), Fp.r(lean, 0, 0), T, 6, bevel=0.0)
    bb(m, Fp, -0.36, 0.36, -0.3, 0.3, -0.1, 0.75, head_m)
    top, bot = [], []
    n = 6
    for i in range(n + 1):
        t = -1 + 2 * i / n
        xx = 1.75 * t
        bulge = 0.55 * (1 - t * t)
        th = 0.12 + 0.42 * (1 - t * t)
        zc = 0.05 + bulge
        top.append((xx, zc + th / 2))
        bot.append((xx, zc - th / 2))
    for i in range(n):
        ext(m, Fp, [bot[i], bot[i + 1], top[i + 1], top[i]], "y", -0.22, 0.22, head_m)


def pick_rack(m, x, z, fx, fz, heads, seed=0):
    """SUPORTE DE PICARETAS A VENDA: 2 montantes, travessao entalhado (as cabecas apoiam nele), travessa de baixo,
    telhadinho de tabuas e placa com picareta"""
    F = fr(x, z, Y0, fx, fz)
    sp = 3.9                                   # cabeca de 3,5: uma picareta a cada 3,9 (nada encavalado)
    w = sp * len(heads) + 0.5
    for s in (-1, 1):
        bb(m, F, s * w / 2 - 0.5, s * w / 2 + 0.5, -0.5, 0.5, -0.1, 0.32, T)                          # sapata
        bb(m, F, s * w / 2 - 0.25, s * w / 2 + 0.25, -0.25, 0.25, 0.3, 6.6, T)
        K.beam(m, F, (s * w / 2, -0.3, 2.6), (s * w / 2, -1.8, 0.05), 0.3, 0.3)                      # escora
    bb(m, F, -w / 2 - 0.3, w / 2 + 0.3, -0.32, 0.32, 4.6, 5.05, T)                                   # travessao
    bb(m, F, -w / 2, w / 2, -0.55, -0.25, 1.2, 1.5, T)                                                 # travessa
    # telhadinho de tabuas (uma agua, caindo para a frente)
    for i in range(int(w / 0.9) + 2):
        xx = -w / 2 - 0.5 + i * 0.9
        bx(m, F, min(xx + 0.45, w / 2 + 0.5), 0.15, 7.1, 0.86, 2.6, 0.18, PLK, rx=-0.35)
    bb(m, F, -w / 2 - 0.6, w / 2 + 0.6, -0.95, -0.7, 6.6, 7.6, T)
    bb(m, F, -w / 2 - 0.6, w / 2 + 0.6, -0.25, 0.25, 6.6, 7.0, T)                                    # terca
    for i, hm in enumerate(heads):
        xx = -w / 2 + 0.25 + sp * (i + 0.5)
        pickaxe(m, sub(F, 0, 0, 5.05), xx, hm, hl=4.3 + 0.2 * ((i + seed) % 2))
    colr_rot("FrgProps", x, z, Y0 + 3.4, w + 1.0, 2.4, 6.8, -fz, fx)
    return F, w


def colr_rot(area, cx, cz, cy, sx, sz, sy, fx, fz):
    return VL.colr_rot(area, cx, cz, cy, sx, sz, sy, fx, fz)


def outside_props(pm):
    # suportes de picaretas: em frente a vitrine da loja (oeste) e na frente do telheiro (leste)
    pick_rack(pm, -20.8, -47.6, 0, 1, [STEEL, BRONZE, STEEL], seed=0)
    pick_rack(pm, 20.0, -48.6, 0, 1, [BRONZE, STEEL], seed=1)
    # sacos de carvao junto a porta da loja e no canto do telheiro
    for i, (x, z, a) in enumerate(((-33.4, -49.6, 0.2), (-31.8, -49.0, 1.1), (-32.7, -47.6, 2.0), (30.2, -50.6, 0.4),
                                   (28.7, -50.2, 1.4))):
        sack(pm, x, z, Y0, h=2.0 + 0.15 * (i % 2), ang=a, k=i)
    colr("FrgProps", (-34.4, Y0, -50.6), (-30.8, Y0 + 2.3, -46.6))
    colr("FrgProps", (27.6, Y0, -51.6), (31.2, Y0 + 2.3, -49.2))
    # caixote com lingotes e barris
    Fc = fr(25.4, -48.9, Y0, 0, 1)
    K.crate(pm, Fc, 0.0, 0.0, s=2.2, a=0.1)
    ingots(pm, 25.4, -48.9, Y0 + 2.2, layers=2, n=3)
    for (x, z) in ((31.6, -47.6), (30.0, -46.6)):
        K.barrel(pm, fr(x, z, Y0, 0, 1), 0.0, 0.0, h=2.3, r=0.9)
    colr("FrgProps", (24.2, Y0, -50.1), (26.6, Y0 + 2.9, -47.7))
    colr("FrgProps", (29.0, Y0, -48.6), (32.6, Y0 + 2.4, -45.6))


# ================================================================== ALA OESTE (loja da forja, casa do kit)
WING_W = dict(W=18.0, D=22.0, floors=2, gh=8.0, fh=6.0, jetty=(0.8, 0.0), ridge="y", pitch=54.0, eave=1.3, gable=1.0,
              plaster=PL, stone=ST, roof=(RA, RB), chimney=None, dormers=0, balcony=None, shop=True, party=("L",),
              door=dict(side="F", x=4.2), flowers="red", seed="FRG_WingW", lod=1, sign="pick")   # lod 1 = padrao das frentes do V2b


def wing_west(dm):
    x0, x1 = -35.0, HX0
    sp = K.spec_of(None, **WING_W)
    F = fr((x0 + x1) / 2, -52.0 - sp["D"] / 2, Y0, 0, 1)
    wm = MB("VM_Frg_WingW", "04_FORGE", detail="far", floor=-999)
    info = K.house(wm, F, sp, dmb=dm)
    ob = wm.finish()
    n = cut_x(ob, IX0 - 0.15)                    # o beiral geminado nao fura a parede do salao
    K.house_col("Forge", F, sp, info)
    return ob, info, n


# ================================================================== TELHEIRO LESTE + RODA + MARTELO-PILAO
def shed(mb):
    """telheiro aberto (frente e lado da levada) com o martelo-pilao; parede de pedra no fundo"""
    yt = SEAVE
    posts = [(19.4, SZF), (28.2, SZF), (SX1 - 0.55, SZF), (SX1 - 0.55, -61.0), (SX1 - 0.55, -71.0),
             (SX1 - 0.4, SZB + 0.75)]
    for (x, z) in posts:
        K.through_stone(mb, fr(x, z, Y0, 0, 1), -0.85, 0.85, -0.85, 0.85, -0.25, 0.7, ST, c=0.16)
        rb(mb, x - 0.55, x + 0.55, Y0 + 0.65, yt - 1.2, z - 0.55, z + 0.55, T)
        colr("FrgPost", (x - 0.6, Y0, z - 0.6), (x + 0.6, yt - 1.2, z + 0.6))
    rb(mb, SX0, SX1 + 0.1, yt - 1.2, yt, SZF - 0.6, SZF + 0.6, T)                              # frechal da frente
    rb(mb, SX1 - 1.1, SX1 + 0.05, yt - 1.2, yt, SZB, SZF + 0.6, T)                              # frechal da levada
    for (x, z) in posts[:2]:
        for s in (-1, 1):
            mb.beam(P(x + s * 0.5, yt - 4.0, z), P(x + s * 2.6, yt - 1.15, z), 0.55, 0.55, T, 0.0)
    for (x, z) in posts[3:]:
        for s in (-1, 1):
            mb.beam(P(x, yt - 4.0, z + s * 0.5), P(x, yt - 1.15, z + s * 2.6), 0.55, 0.55, T, 0.0)
    # parede do fundo (pedra ate o frechal) + oitao de tras
    rb(mb, SX0, SX1, Y0 - 0.3, yt, SZB + CORE, SZB + 1.0 - CORE, MOR)
    big_stone(mb, (SX0, SZB + 1.0), (SX1, SZB + 1.0), Y0, yt, (0, 1), seed="shB_in", lod=2)
    big_stone(mb, (SX1, SZB), (SX0, SZB), Y0, yt, (0, -1), seed="shB_out", lod=2)
    # telhado (cumeeira ao longo de Z), beiral oeste para dentro da parede do salao (sem furar o lado de dentro)
    xa, xb = SX0 + 1.0, SX1
    span = xb - xa
    length = SZF - SZB
    Fr_ = fr((xa + xb) / 2, (SZF + SZB) / 2, yt, 0, 1)
    RF = sub(Fr_, 0, 0, 0, math.pi / 2)
    ri = K.roof(mb, RF, length, span, 38.0, 1.2, (0.4, 1.4), RA, RB, seed="frg_shed", course=1.25)
    Fg = sub(RF, length / 2, 0, 0, -math.pi / 2)
    K.gable_wall(mb, Fg, span, ri["rise"], PL, window_=False, seed="frg_shG")
    Fb = sub(RF, -length / 2, 0, 0, math.pi / 2)
    K.gable_wall(mb, Fb, span, ri["rise"], PL, party=True, seed="frg_shGb")
    colr("Forge", (SX0, Y0, SZB), (SX1, yt + 0.5, SZB + 1.0))
    return ri


def mill_fixed(mb):
    """partes FIXAS do moinho: cavalete do eixo, mancais nos muros da levada, cavalete do pivo, bigorna sobre cepo"""
    # cavalete interno do eixo (x 21,6)
    for z in (WZ - 1.2, WZ + 1.2):
        rb(mb, 21.2, 22.0, Y0, WY + 0.9, z - 0.4, z + 0.4, T)
    rb(mb, 21.0, 22.2, WY - 1.2, WY - 0.6, WZ - 1.8, WZ + 1.8, T)
    rb(mb, 21.0, 22.2, WY + 0.6, WY + 1.1, WZ - 1.6, WZ + 1.6, IRON)
    # mancais de pedra sobre os muros da levada (x 32..33 e 39..40, topo 8,1) com capa de ferro
    for xm in (32.5, 39.5):
        Fm = fr(xm, WZ, Y0 + 1.1, 1, 0)
        K.through_stone(mb, Fm, -1.4, 1.4, -0.65, 0.65, -0.05, WY - 0.6 - (Y0 + 1.1), ST, c=0.14)
        rb(mb, xm - 0.6, xm + 0.6, WY - 0.65, WY + 0.75, WZ - 1.1, WZ - 0.6, IRON)
        rb(mb, xm - 0.6, xm + 0.6, WY - 0.65, WY + 0.75, WZ + 0.6, WZ + 1.1, IRON)
        rb(mb, xm - 0.6, xm + 0.6, WY + 0.6, WY + 1.0, WZ - 1.1, WZ + 1.1, IRON)
    # cavalete do pivo do martinete
    px, py, pz = HPIV
    for x in (px - 1.15, px + 1.15):
        rb(mb, x - 0.45, x + 0.45, Y0, py + 1.3, pz - 0.5, pz + 0.5, T)
        mb.beam(P(x, Y0, pz - 2.4), P(x, py - 1.0, pz - 0.4), 0.45, 0.45, T, 0.0)
    rb(mb, px - 1.7, px + 1.7, py + 1.3, py + 1.9, pz - 0.6, pz + 0.6, T)
    mb.rod(P(px - 1.75, py, pz), P(px + 1.75, py, pz), 0.22, IRON, 8)
    rb(mb, px - 1.7, px + 1.7, Y0, Y0 + 0.5, pz - 0.6, pz + 0.6, T)
    # bigorna do martinete: cepo + bloco de ferro (o golpe cai aqui; faiscas = VFX_Forge_Sparks)
    hx, hy, hz = HHEAD
    mb.cyl(1.35, 0.85, P(hx, Y0 + 0.42, hz), (0, 0, 0.3), T, 10, bevel=0.0)
    rb(mb, hx - 1.2, hx + 1.2, Y0 + 0.85, HANVIL_TOP, hz - 1.2, hz + 1.2, IRON)
    # COL: maquinario cercado (o jogador ve de frente, do largo, sem entrar)
    colr("FrgMill", (20.4, Y0, -76.4), (SX1 - 1.2, Y0 + 7.0, -54.8))
    colr("FrgMill", (WX - WHW - 0.6, Y0, WZ - WR - 0.6), (WX + WHW + 0.6, WY + WR + 0.6, WZ + WR + 0.6))


def wheel_moving():
    """RODA D'AGUA (gira em X no pivot (36; 9,4; -66)): 2 aros, 16 pas, 2 x 6 raios, cubo, EIXO ate o cavalete interno
    e os 3 CAMES que erguem o martinete. Objeto proprio VM_Frg_Wheel (props 'source' do VFX_Waterwheel_Rotate)."""
    m = MB("VM_Frg_Wheel", "04_FORGE", detail="far", floor=-999)
    Fw = fr(WX, WZ, 0.0, 1, 0)       # +y local = +X (eixo); local x = +Z; local z = Y
    nseg = 20
    for s in (-1, 1):
        for i in range(nseg):
            a0, a1 = 2 * math.pi * i / nseg, 2 * math.pi * (i + 1) / nseg
            r0, r1 = WR - 1.15, WR - 0.35
            ext(m, Fw, [(r0 * math.cos(a0), WY + r0 * math.sin(a0)), (r1 * math.cos(a0), WY + r1 * math.sin(a0)),
                        (r1 * math.cos(a1), WY + r1 * math.sin(a1)), (r0 * math.cos(a1), WY + r0 * math.sin(a1))],
                "y", s * WHW - 0.28, s * WHW + 0.28, T)
        for i in range(6):
            a = 2 * math.pi * (i + 0.25 * (s + 1)) / 6
            K.beam(m, Fw, (0.9 * math.cos(a), s * WHW, WY + 0.9 * math.sin(a)),
                   ((WR - 1.0) * math.cos(a), s * WHW, WY + (WR - 1.0) * math.sin(a)), 0.5, 0.5)
    for i in range(16):                                                     # pas
        a = 2 * math.pi * i / 16
        c = ((WR - 0.55) * math.cos(a), WY + (WR - 0.55) * math.sin(a))
        bx(m, Fw, c[0], 0.0, c[1], 0.32, 2 * WHW + 1.1, 1.9, PLK, ry=math.pi / 2 - a)
    # cubo + cintas
    m.cyl(1.25, 2 * WHW + 1.2, P(WX, WY, WZ), (0, math.pi / 2, 0), T, 10, bevel=0.0)
    for s in (-1, 1):
        m.cyl(1.45, 0.3, P(WX + s * (WHW + 0.2), WY, WZ), (0, math.pi / 2, 0), IRON, 10, bevel=0.0)
    # eixo (do cavalete interno ate o mancal leste) + colares nos mancais
    m.rod(P(AX0, WY, WZ), P(AX1, WY, WZ), 0.55, T, 10)
    for xm in (21.6, 32.5, 39.5):
        m.cyl(0.66, 0.35, P(xm + 0.9, WY, WZ), (0, math.pi / 2, 0), IRON, 10, bevel=0.0)
    # 3 cames (bracos de madeira com sapata de ferro) em 30, 150 e 270 graus: nenhum encosta no cabo em repouso
    Fc = fr(CAM_X, WZ, 0.0, 1, 0)
    for k in range(3):
        a = math.radians(30 + 120 * k)
        d = (math.cos(a), math.sin(a))
        K.beam(m, Fc, (0.0, 0.0, WY), (d[0] * (CAM_LEN - 0.3), 0.0, WY + d[1] * (CAM_LEN - 0.3)), 0.8, 0.62, T)
        tip = (d[0] * (CAM_LEN - 0.15), WY + d[1] * (CAM_LEN - 0.15))
        bx(m, Fc, tip[0], 0.0, tip[1], 0.7, 0.9, 0.5, IRON, ry=math.pi / 2 - a)
    return m.finish()


def hammer_moving():
    """MARTELO-PILAO (martinete): cabo de madeira (pivo ao norte, cabeca ao sul) + cabeca de ferro + cintas.
    Objeto proprio VM_Frg_TripHammer (props source do VFX_TripHammer); repouso = cabeca na bigorna."""
    m = MB("VM_Frg_TripHammer", "04_FORGE", detail="far", floor=-999)
    px, py, pz = HPIV
    hx, hy, hz = HHEAD
    a = P(px, py, pz - 1.3)
    b = P(hx, hy + 1.05, hz - 0.6)
    m.beam(a, b, 0.95, 1.15, T, 0.0)
    rb(m, hx - 1.0, hx + 1.0, HANVIL_TOP + 0.75, HANVIL_TOP + 2.65, hz - 1.15, hz + 1.15, IRON)
    FP.frustum(m, tuple(P(hx, HANVIL_TOP + 0.05, hz)), 1.5, 1.7, 2.0, 2.3, 0.72, IRON)
    d = (b - a).normalized()
    for t in (0.72, 0.86):
        c = a + (b - a) * t
        m.beam(c - d * 0.25, c + d * 0.25, 1.25, 1.45, IRON, 0.0)
    m.beam(a + (b - a) * 0.08 - d * 0.2, a + (b - a) * 0.08 + d * 0.2, 1.25, 1.45, IRON, 0.0)
    return m.finish()


# ================================================================== CHAMINE
def chimney(mb):
    """soco + 2 fustes em recuo (cantaria), misulas, coroa, camara de fogo (4 pilares + braseiro Neon recuado), chapeu de
    telha em piramide com cata-vento de bigorna"""
    cx, cz = CHX, CHZ
    # soco (encosta na parede do fundo do salao)
    bx0, bx1, bz0, bz1 = cx - 8.0, cx + 8.0, -94.0, HZO
    rb(mb, bx0 + CORE, bx1 - CORE, Y0 - 0.3, CH_BASE_TOP, bz0 + CORE, bz1, MOR)
    for (a, b, n, sd) in (((bx1, bz1), (bx1, bz0), (1, 0), "E"), ((bx0, bz0), (bx0, bz1), (-1, 0), "W"),
                          ((bx1, bz0), (bx0, bz0), (0, -1), "N")):
        ashlar(mb, a, b, Y0, CH_BASE_TOP, n, seed=("chB", sd), course=(2.6, 3.4), length=(4.6, 7.4), cut=0.1)
    FP.frustum(mb, tuple(P(cx, CH_BASE_TOP, (bz0 + bz1) / 2)), 16.6, 16.2, 13.4, 13.4, 1.6, ST)
    # fuste 1 (13) e fuste 2 (11), fuligem crescendo para cima
    y1a, y1b = CH_BASE_TOP + 1.6, 68.0
    y2a, y2b = 69.2, 86.0
    for (w, ya, yb, p2, tag) in ((13.0, y1a, y1b, 0.0, "1"), (11.0, y2a, 81.4, 0.0, "2a"), (11.0, 81.4, y2b, 0.85, "2b")):
        h = w / 2
        rb(mb, cx - h + CORE, cx + h - CORE, ya - 0.3, yb, cz - h + CORE, cz + h - CORE, MOR)
        for (a, b, n, sd) in (((cx + h, cz + h), (cx + h, cz - h), (1, 0), "E"), ((cx - h, cz - h), (cx - h, cz + h), (-1, 0), "W"),
                              ((cx + h, cz - h), (cx - h, cz - h), (0, -1), "N"), ((cx - h, cz + h), (cx + h, cz + h), (0, 1), "S")):
            y_ = max(ya, 50.0) if (sd == "S" and tag == "1") else ya       # abaixo de 50 o telhado do salao esconde
            ashlar(mb, a, b, y_, yb, n, seed=("ch", tag, sd), m2=SOOT, p2=p2, course=(2.6, 3.4), length=(4.4, 6.8),
                   cut=0.12)
    FP.frustum(mb, tuple(P(cx, y1b, cz)), 13.6, 13.6, 11.4, 11.4, 1.2, ST)
    # TOPO de CHAMINE (nao de torre): cinta de pedra, CAMARA DE FOGO com 4 pilares de fuligem e vaos largos onde se
    # veem as brasas e as linguas de fogo, laje-lintel e CAPA elevada sobre 4 calcos (fresta da fumaca)
    yc = y2b
    rb(mb, cx - 6.2, cx + 6.2, yc, yc + 0.8, cz - 6.2, cz + 6.2, ST)                       # cinta
    ya, yb = yc + 0.8, CH_TOP - 3.1                                                          # camara 86,8 .. 91,6
    for sx in (-1, 1):
        for sz in (-1, 1):
            x, z = cx + sx * 4.4, cz + sz * 4.4
            K.through_stone(mb, fr(x, z, ya, 0, 1), -1.1, 1.1, -1.1, 1.1, 0.0, yb - ya, SOOT, c=0.22)
    for k in range(4):                                                                       # misulas dos vaos
        Fs = sub(fr(cx, cz, 0.0, 0, 1), 0, 0, 0, k * math.pi / 2)
        for s_ in (-1, 1):
            bb(mb, Fs, s_ * 3.3 - 0.6, s_ * 3.3 + 0.6, 3.7, 5.4, yb - 0.9, yb, SOOT)
    rb(mb, cx - 3.0, cx + 3.0, ya - 0.2, yb, cz - 3.0, cz + 3.0, SOOT)                      # miolo escuro
    rb(mb, cx - 4.0, cx + 4.0, ya - 0.1, ya + 0.75, cz - 4.0, cz + 4.0, GLOW)               # leito de brasas
    r = K.rng("chim_fire")
    for k in range(14):                                                                      # linguas de fogo
        a = 2 * math.pi * k / 14 + r.uniform(-0.1, 0.1)
        rr = r.uniform(3.2, 3.8)
        hh = r.uniform(1.8, 3.3)
        mb.cyl(r.uniform(0.55, 0.8), hh, P(cx + math.cos(a) * rr, ya + 0.6 + hh / 2, cz + math.sin(a) * rr),
               (r.uniform(-0.15, 0.15), r.uniform(-0.15, 0.15), r.uniform(0, 1)), GLOW, 5, r2=0.05, bevel=0.0)
    rb(mb, cx - 6.0, cx + 6.0, yb, yb + 0.9, cz - 6.0, cz + 6.0, ST)                        # laje-lintel
    yl = yb + 0.9
    for sx in (-1, 1):
        for sz in (-1, 1):
            rb(mb, cx + sx * 3.6 - 0.55, cx + sx * 3.6 + 0.55, yl, yl + 1.4, cz + sz * 3.6 - 0.55, cz + sz * 3.6 + 0.55, ST)
    rb(mb, cx - 2.6, cx + 2.6, yl - 0.1, yl + 1.0, cz - 2.6, cz + 2.6, SOOT)                # boca do fumeiro
    rb(mb, cx - 5.2, cx + 5.2, yl + 1.4, yl + 2.2, cz - 5.2, cz + 5.2, ST)                  # capa
    FP.frustum(mb, tuple(P(cx, yl + 2.2, cz)), 9.0, 9.0, 7.6, 7.6, 0.5, ST)
    colr("Forge", (bx0, Y0, bz0), (bx1, CH_BASE_TOP, bz1))
    colr("Forge", (cx - 6.5, CH_BASE_TOP, cz - 6.5), (cx + 6.5, yl + 2.7, cz + 6.5))
    return yl + 2.7


# ================================================================== LARGO DA FORJA (o V2b deixou o largo para o V2a)
LARGO = (-35.0, SX1, -36.4, SZF)            # x0, x1, z sul (fim da rua norte do V2b), z norte (frentes)


def largo(pm):
    """adro em paralelepipedo do kit (mesma pedra da rua norte) da boca da rua ate as frentes da forja, PLANO: topo das
    pedras <= 7,03 no chao livre do Ignis (a colisao e o piso 7,0 do vm_col); meio-fio na borda com a grama"""
    import vm_trecho as TR
    x0, x1, zs, zn = LARGO
    st = bpy.data.objects.get("VM_Town_Streets")
    if st:                                                         # laje lisa do V0
        TR.drop_islands(st, lambda x, z: -27 < x < 25 and -51 < z < -35.5)
    pr = bpy.data.objects.get("VM_Town_Props")
    if pr:                                                         # barris do V0 no largo
        TR.drop_islands(pr, lambda x, z: -40 < x < 40 and -56 < z < -36)
    tg = bpy.data.objects.get("VM_Ter_Ground")
    if tg:
        cut_top(tg, x0, x1, zn, zs)

    def keep(x, yb):
        z = -yb
        if IX0 - 0.2 < x < IX1 + 0.2 and z < HZF + 0.15:          # piso da oficina
            return False
        if x < HX0 and z < -51.9:                                  # frente da loja (ala oeste)
            return False
        return True
    K.cobbles(pm, W0, x0, x1, [(-zs, 6.97), (-zn, 6.97)], seed="frg_largo", row=(2.0, 2.6), sw=(2.4, 3.4), keep=keep)
    for (a, b) in (((x0, zs), (-9.7, zs)), ((9.7, zs), (x1, zs)), ((x0, zs), (x0, -52.0))):
        d = (b[0] - a[0], b[1] - a[1])
        ln = math.hypot(*d)
        Fc = fr(a[0], a[1], 0.0, d[0] / ln, d[1] / ln)
        K.curb(pm, Fc, 0.0, 0.0, ln, lambda qx, qy: 6.97, seed=("frg_curb", a))


# ================================================================== piso
def floors(im):
    def keep_hall(x, yb):
        z = -yb
        if FXC - FW / 2 - 0.2 < x < FXC + FW / 2 + 0.2 and z < FZF + 0.2:
            return False
        return True
    K.cobbles(im, W0, IX0, IX1, [(-HZF + 0.15, 6.93), (-HZB, 6.93)], seed="frg_floor", row=(2.4, 3.1),
              sw=(2.8, 4.2), gap=0.2, keep=keep_hall, mats=(STI, STI), bed_m=SOOT)
    K.cobbles(im, W0, SX0 + 0.05, SX1 - 0.05, [(-SZF, 6.93), (-(SZB + 1.0), 6.93)], seed="frg_shedfloor",
              row=(2.6, 3.4), sw=(3.2, 4.8), gap=0.22, mats=(STI, STI), bed_m=SOOT, lod=0)


# ================================================================== marcadores
def _put(name, x, y, z, props=None, size=None):
    o = bpy.data.objects.get(name)
    if o is None:
        o = VL.mk(name, x, z, y, 0, 1, props)
    else:
        o.location = VL.B(x, z, y)
        for k, v in (props or {}).items():
            o[k] = v
    if size:
        o.empty_display_size = size
    return o


def markers(fire_light):
    bv = lambda x, y, z: tuple(round(c, 4) for c in VL.B(x, z, y))
    _put("ForgeChimney", CHX, CH_TOP, CHZ, {"nota": "AudioWorld: ambiente da chamine (camara de fogo da forja nova)"})
    _put("VFX_Chimney_Smoke_Emitter", CHX, CH_TOP + 1.5, CHZ, {"particle": "smoke", "rate": 6, "radius": 3.6,
         "nota": "fresta sob a capa elevada (boca do fumeiro); brasas na camara de fogo logo abaixo"})
    zf = FZF - MDEP / 2 - 0.2
    _put("VFX_Hearth_Fire", FXC, MSILL + 0.2, zf, {"particle": "fire", "size": [2 * MHW - 0.6, MDEP - 0.8, 3.2],
         "nota": "leito de brasas da boca da fornalha (largura x profundidade x altura das chamas)"})
    rx, ry, rz = L.IGNIS_ANVIL
    _put("VFX_Anvil_Sparks", rx + 0.5, ry + 3.9, rz, {"particle": "sparks",
         "nota": "faiscas a cada martelada do Ignis (topo da bigorna do golem, sessao Ignis)"})
    hx, hy, hz = HHEAD
    _put("VFX_Forge_Sparks", hx, HANVIL_TOP + 0.1, hz, {"particle": "sparks",
         "nota": "faiscas do martelo-pilao a cada golpe (evento 'martinete' do VFX_TripHammer)"})
    _put("VFX_Quench_Steam", 10.1, Y0 + 2.2, -57.6, {"particle": "steam", "size": [4.6, 0.2, 3.2],
         "nota": "vapor do cocho de tempera (barra mergulhada)"})
    _put("VFX_Waterwheel_Rotate", WX, WY, WZ, {
        "axis": "X", "rpm": 6, "R": WR, "raio": WR, "half_w": WHW, "pivot": bv(WX, WY, WZ), "axis_vec": (1.0, 0.0, 0.0),
        "source": "VM_Frg_Wheel",
        "note": "girar VM_Frg_Wheel (roda + eixo + cames) em torno de +X Blender no pivot: o fundo da roda anda com a "
                "agua da levada (para o norte, -Z Roblox)"})
    px, py, pz = HPIV
    _put("VFX_TripHammer", hx, hy, hz, {
        "anim": "martinete sobe/desce 1x por came (3 cames por volta da roda)", "source": "VM_Frg_TripHammer",
        "pivot": bv(px, py, pz), "axis": (1.0, 0.0, 0.0), "cams": 3, "cam_len": CAM_LEN, "cam_x": CAM_X,
        "low_axle": bv(CAM_X, WY, WZ), "cam_angles_deg": [30, 150, 270], "rest": 0.0, "lift": 0.16,
        "anvil_top": HANVIL_TOP})
    s = (2.6 - WY) / WR
    _put("VFX_Wheel_Splash", WX, 2.7, WZ + math.sqrt(max(0.0, 1 - s * s)) * WR, {"particle": "splash",
         "nota": "pas entrando na agua da levada (lado sul, a montante)"})


# ================================================================== build
def build():
    drop_blockout()
    hm = MB("VM_Frg_Hall", "04_FORGE", detail="far", floor=-999)
    pm = MB("VM_Frg_Props", "04_FORGE", detail="far", floor=-999)
    seen = {}

    def tick(tag):
        nh, npm = sum(len(f.verts) - 2 for f in hm.bm.faces), sum(len(f.verts) - 2 for f in pm.bm.faces)
        seen[tag] = (nh - seen.get("_h", 0), npm - seen.get("_p", 0))
        seen["_h"], seen["_p"] = nh, npm
    hall_walls(hm)
    tick("paredes")
    lights = hall_front(hm, pm)
    tick("frente")
    ri, Fg = hall_roof(hm)
    tick("telhado")
    gable_sign(hm, pm, Fg, ri["rise"])
    tick("placa")
    fire = furnace(hm, pm)
    tick("fornalha")
    bellows(pm, hm)
    coal_bin(pm)
    quench_and_tools(pm, hm)
    tick("interior")
    shed(hm)
    mill_fixed(hm)
    tick("telheiro")
    top = chimney(hm)
    tick("chamine")
    floors(pm)
    largo(pm)
    tick("pisos")
    outside_props(pm)
    tick("props")
    wing, winfo, ncut = wing_west(pm)
    tick("ala")
    print("FORJA tris por parte (salao, props):", {k: v for k, v in seen.items() if not k.startswith("_")},
          "ala oeste:", _tris(wing))
    hall = hm.finish()
    join_into(hall, wing)
    wheel = wheel_moving()
    ham = hammer_moving()
    props = pm.finish()
    # colisao do salao (paredes, fundo, pilares, fornalha + peito)
    colr("Forge", (HX0, Y0, HZO), (IX0, EAVE + 1.0, HZF))
    colr("Forge", (IX1, Y0, HZO), (HX1, EAVE + 1.0, HZF))
    colr("Forge", (IX0, Y0, HZO), (IX1, EAVE + 1.0, HZB))
    for px in PXS:
        colr("Forge", (px - PS / 2, Y0, PZ - PS / 2), (px + PS / 2, LINT0, PZ + PS / 2))
    colr("Forge", (HX0 - 2.0, LINT0, PZ - PS / 2), (HX1 + 2.0, EAVE, PZ + PS / 2))
    colr("Forge", (FXC - FW / 2 - 1.5, Y0, HZB), (FXC + FW / 2 + 1.5, FTOP + 1.4, FZF + 0.7))
    colr("Forge", (FXC - FW / 2 - 0.5, FTOP + 1.4, HZB), (FXC + FW / 2 + 0.5, 39.9, -71.0))
    for nm, p in lights:
        fm_lib.light(nm, "POINT", p, 60.0, (1.0, 0.74, 0.42), 0.3)
    fm_lib.light("L_Hearth_Fire_VM", "POINT", fire, 1600.0, (1.0, 0.48, 0.16), 1.6)
    markers(fire)
    for o in (hall, wheel, ham, props):
        o["vm_forge"] = 1
    for n, x, z, fx, fz in (("SCALE_F_Largo", 9.0, -45.0, -0.3, -1), ("SCALE_F_Loja", -29.0, -47.0, 0.3, -1),
                            ("SCALE_F_Telheiro", 27.0, -53.6, 0.2, -1)):
        VL.dummy(n, x, z, Y0, fx, fz)
    r = report(print_=True)
    print("FORJA: chamine ate Y %.1f; ala oeste com %d faces cortadas no beiral geminado" % (top, ncut))
    return r


# ================================================================== orcamento
def _tris(o):
    return sum(len(p.vertices) - 2 for p in o.data.polygons)


def report(print_=True, path=None):
    obs = sorted([o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("VM_Frg_")], key=lambda o: o.name)
    rows = {}
    for o in obs:
        mats = sorted({o.data.materials[p.material_index].name for p in o.data.polygons})
        rows[o.name] = {"tris": _tris(o), "materiais": len(mats), "lista": mats}
    tt = sum(r["tris"] for r in rows.values())
    mp = sum(r["materiais"] for r in rows.values())
    ncol = sum(1 for o in bpy.data.objects if o.name.startswith(("COL_Forge_", "COL_FrgProps_", "COL_FrgPost_",
                                                                  "COL_FrgMill_")))
    out = {"objetos": rows, "tris": tt, "meshparts_est": mp, "col": ncol, "teto": [70000, 45]}
    if print_:
        for k, r in rows.items():
            print("   %-22s %6d tris  %2d mat  %s" % (k, r["tris"], r["materiais"], ",".join(r["lista"])))
        print("FORJA orcamento: %d tris / ~%d MeshParts (antes do fatiamento/fold do export) / %d COL (teto 70k / 45)"
              % (tt, mp, ncol))
    if path:
        json.dump(out, open(path, "w", encoding="utf-8"), indent=1)
    return out


# ================================================================== cameras (Roblox: pos, alvo, lente)
def cams():
    c = {}
    c["CAM_VM_F_Spawn"] = ((0.0, L.Y_SPAWN + 8.0, 104.0), (0.0, 44.0, -75.0), 30)
    c["CAM_VM_F_Praca"] = ((6.0, L.Y_PAVE + 6.5, 22.0), (-1.0, 27.0, -66.0), 24)
    c["CAM_VM_F_Rua"] = ((3.0, Y0 + 6.5, -22.0), (-1.0, 26.0, -66.0), 20)
    c["CAM_VM_F_Largo"] = ((3.0, Y0 + 6.5, -41.0), (-1.0, 21.0, -66.0), 18)
    c["CAM_VM_F_Boca"] = ((7.0, Y0 + 5.5, -61.0), (-1.0, 12.0, -73.5), 20)
    c["CAM_VM_F_Fole"] = ((-3.5, Y0 + 6.0, -58.0), (-12.5, 11.0, -68.0), 20)
    c["CAM_VM_F_Leste"] = ((-5.0, Y0 + 6.0, -55.0), (11.0, 11.0, -64.0), 20)
    c["CAM_VM_F_Picaretas"] = ((-18.5, Y0 + 5.2, -39.0), (-22.0, 10.4, -48.0), 22)
    c["CAM_VM_F_Roda"] = ((44.0, Y0 + 6.5, -42.0), (31.0, 11.0, -64.0), 22)
    c["CAM_VM_F_Pilao"] = ((22.0, Y0 + 5.0, -49.6), (25.0, 9.6, -64.0), 20)
    c["CAM_VM_F_RodaLado"] = ((47.0, Y0 + 5.5, -72.0), (33.0, 10.0, -63.0), 22)
    c["CAM_VM_F_Chamine"] = ((12.0, Y0 + 6.5, -20.0), (0.0, 80.0, -86.0), 30)
    c["CAM_VM_F_ChamineTopo"] = ((30.0, 86.0, -58.0), (0.0, 90.0, -86.0), 30)
    c["CAM_VM_F_Air"] = ((62.0, 82.0, 4.0), (-2.0, 26.0, -68.0), 24)
    c["CAM_VM_F_Oeste"] = ((-12.0, Y0 + 6.0, -38.0), (-27.0, 13.0, -54.0), 20)
    return c


def cameras():
    for n, (loc, tgt, lens) in cams().items():
        fm_lib.camera(n, VL.B(loc[0], loc[2], loc[1]), VL.B(tgt[0], tgt[2], tgt[1]), lens)


# ================================================================== CLI
def _render(out, cams_, roblox=False, no_golem=False):
    if roblox:
        import fm_pv3
        fm_pv3.load()
        import fm_portals
        print("MODO roblox: %d materiais" % fm_lib.apply_preview("roblox"))
    os.makedirs(out, exist_ok=True)
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = 960, 540
    sc.render.resolution_percentage = 100
    sc.eevee.taa_render_samples = 16
    sc.render.image_settings.file_format = "JPEG"
    sc.render.image_settings.quality = 90
    g = bpy.data.objects.get("PREVIEW_Ignis")
    if g is not None:
        g.hide_render = no_golem
    if not cams_:
        cams_ = sorted(o.name for o in bpy.data.objects if o.type == "CAMERA" and o.name.startswith("CAM_VM_F_"))
    for cn in cams_:
        ob = bpy.data.objects.get(cn)
        if not ob:
            print("RENDER camera inexistente:", cn)
            continue
        sc.camera = ob
        sc.render.filepath = os.path.join(out, cn + ".jpg")
        bpy.ops.render.render(write_still=True)
        print("RENDER", cn)


def _sheet(prev, rbx, outdir):
    from PIL import Image, ImageDraw, ImageFont
    sys.path.insert(0, HERE)
    import vm_sheet as SH
    os.makedirs(outdir, exist_ok=True)
    groups = [
        ("FOLHA_forja_eixo.jpg", "Forja do Ignis V2a - do spawn, da praca, da rua norte e do largo (altura do jogador)",
         ["CAM_VM_F_Spawn", "CAM_VM_P_Spawn", "CAM_VM_F_Praca", "CAM_VM_F_Rua", "CAM_VM_F_Largo", "CAM_VM_P_Forja"]),
        ("FOLHA_forja_closes.jpg", "Forja do Ignis V2a - closes (golem oculto): boca, fole, lado leste, picaretas",
         ["CAM_VM_F_Boca", "CAM_VM_F_Fole", "CAM_VM_F_Leste", "CAM_VM_F_Picaretas", "CAM_VM_F_Oeste"]),
        ("FOLHA_forja_roda_chamine.jpg", "Forja do Ignis V2a - roda d'agua + martelo-pilao, chamine, vista aerea",
         ["CAM_VM_F_Roda", "CAM_VM_F_Pilao", "CAM_VM_F_RodaLado", "CAM_VM_F_Chamine", "CAM_VM_F_ChamineTopo",
          "CAM_VM_F_Air"]),
    ]
    for fn, title, cl in groups:
        rows = []
        for cn in cl:
            row = []
            for d, tag in ((prev, "PREVIA"), (rbx, "ROBLOX")):
                p = os.path.join(d, cn + ".jpg")
                if os.path.exists(p):
                    row.append(SH.label(SH.fit(p, 640), "%s  %s" % (tag, cn.replace("CAM_VM_", ""))))
            if row:
                rows.append(row)
        if rows:
            SH.compose(rows, os.path.join(outdir, fn), title)


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    cmd = argv[0] if argv else ""
    if cmd == "sheet":
        _sheet(argv[1], argv[2], argv[3])
    elif cmd == "test":
        import build_vm
        rep, dt = build_vm.build()
        if not any(o.get("vm_forge") for o in bpy.data.objects):
            build()
            cameras()
        out = argv[1]
        bpy.ops.wm.save_as_mainfile(filepath=out, compress=True)
        print("TEST OK -> %s (%.1fs)" % (out, dt))
    elif cmd == "render":
        cl = [a for a in argv[2:] if a.startswith("CAM_")]
        _render(argv[1], cl, roblox="--roblox" in argv, no_golem="--sem-golem" in argv)
    elif cmd == "report":
        report(True, argv[1] if len(argv) > 1 else None)
