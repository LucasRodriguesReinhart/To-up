# sg_cave - ZONA CAVE da Ilha 3 (Shadow Garden): o SALAO SOMBRIO ("Cova da Ordem", a bat-caverna gotica da ordem das
# sombras) embaixo do castelo + a TORRE DO POCO e a ESCADA CARACOL abaixo de z 44 (e os degraus/nucleo/corrimao da
# escada inteira, de 54,6 a 6,6). build() substitui sg_blockout.cave (inclusive as colisoes dos volumes e as luzes).
# Prefixo SG_Cave_, colecao 17_DUNGEON (dono 'cave' no export). Onda 1 (agente 1c) da reforma grande, 2026-09-30.
# Planta, colisoes andaveis (sg_col: piso, rio, ponte, estrado, escadaria, galeria, passarelas, ponte suspensa, rampa
# helicoidal, guarda do poco) e marcadores (sg_core) sao da onda 0 e NAO mudam; aqui so o visual + a colisao dos
# PROPRIOS volumes (paredes/teto da casca, base da torre, pilares, arcadas, portal, forja, sala do mapa).
#
# Leitura do salao (quem desce pela caracol e sai na galeria, olhando o sul):
#   - ROCHA BRUTA: paredes e abobada em BLOCOS FRATURADOS de basalto (colunas de rumo vertical com diaclases escuras,
#     bancos duro/mole, planos de fratura dirigidos: labio, quina partida, sub-cava), a parede se inclina para dentro
#     acima da faixa em que o jogador anda (abobada irregular); teto em lajes facetadas com grupos de estalactites.
#   - ESTRUTURA DA ORDEM: Torre do Poco em cantaria (16 faces, fiadas com junta em V, base rusticada, cornija na
#     galeria, janelas em arco mostrando a ultima volta, cinta de misulas onde entra na rocha); galeria sobre arcada;
#     escadaria de 24 degraus com guardas de pedra; nave de 3 pares de pilares antigos com arcos transversais no eixo;
#     passarelas de pedra sobre misulas de ferro e a ponte suspensa de ferro e madeira sobre o rio escuro.
#   - BASE SECRETA: forja (fornalha com boca acesa contida, chamine para a rocha, bigorna, bancada, cabides de armas,
#     tina, baus) e sala do mapa (mesa com a ILHA EM RELEVO, estantes, armaduras); estandartes rasgados (so o crescente);
#     cristais violeta SO em aglomerados presos nas paredes em volta do portal.
#   - PORTAL (foco): nicho monumental de aduelas antigas sobre pilares, anel de aduelas com as runas do alfabeto unico
#     (sg_court.RUNE_SEGS), vortice, estrado de 2 degraus e a MOLDURA DE PEDRA da placa de horario (DUNGEON_UI).
# Tiers: A = portal, escada, galeria, forja, mapa (perto do jogador); B = pilares, torre, passarelas; C = rocha alta,
# teto, fundo escuro (massas simples, sem chanfro).
import math, random
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import sg_lib as SL
from sg_lib import MB, col_box, col_box2, light, ngon_col, box_walls_col
import fm_lib
import sg_layout as L
import sg_emblem as EM
import build_sg as B

S = fm_lib.S
# ------------------------------------------------------------------ materiais (1 novo: a cantaria ANTIGA da ordem, o
# mesmo tom de ruina da dungeon aprovada; o resto e paleta da ilha e do blockout)
NEW_MATS = {"Stone_SGDunRuin": (S(80, 74, 102), 0.85, 0.0, 0, None, 0.08)}
for _k, _v in NEW_MATS.items():
    fm_lib.MATS.setdefault(_k, _v)
fm_lib.MATS.setdefault("Stone_SGCaveRock", (S(34, 30, 48), 0.9, 0.0, 0, None, 0.08))
fm_lib.MATS.setdefault("Crystal_SGCave", (S(62, 42, 108), 0.3, 0.0, 0, None, 0.04))
fm_lib.MATS.setdefault("SG_CaveVoid_Glow", (S(46, 26, 104), 0.3, 0.0, 1.0, S(56, 30, 124), 0.0))

try:                                             # o ALFABETO UNICO da ilha (obeliscos, dungeon, portal)
    import sg_court as _CT
    RUNE_SEGS = _CT.RUNE_SEGS
except Exception:                                # copia fiel (sg_court em edicao nao derruba a cova)
    _ST = ((0.0, -0.38), (0.0, 0.38))
    RUNE_SEGS = (
        (_ST, ((0.0, 0.38), (0.24, 0.16)), ((0.0, 0.12), (0.24, -0.1))),
        (_ST, ((0.0, 0.2), (0.22, 0.02)), ((0.22, 0.02), (0.0, -0.16))),
        (_ST, ((0.0, 0.38), (-0.24, 0.16)), ((0.0, 0.14), (-0.24, -0.08))),
        (_ST, ((0.0, -0.22), (-0.22, 0.06)), ((0.0, -0.22), (0.22, 0.06))),
        (_ST, ((0.0, 0.22), (-0.22, -0.06)), ((0.0, 0.22), (0.22, -0.06))),
        (_ST, ((0.0, 0.06), (-0.22, -0.12)), ((-0.22, -0.12), (0.0, -0.3))),
        (_ST, ((0.0, 0.38), (0.22, 0.2)), ((0.0, -0.12), (-0.22, -0.32))),
        (_ST, ((0.0, 0.26), (0.24, 0.1)), ((0.24, 0.1), (0.24, -0.22))),
        (((-0.17, -0.38), (-0.17, 0.38)), ((0.17, -0.38), (0.17, 0.38)), ((-0.17, 0.14), (0.17, -0.1))),
    )

C = "17_DUNGEON"
RK, RKD, RKL = "Stone_SGCaveRock", "Cliff_Rock_SG_Dark", "Cliff_Rock_SG"   # junta/sombra, corpo, topo ao luar
RUIN, CS, BL, FL = "Stone_SGDunRuin", "Stone_SG_Castle", "Stone_SG_Block", "Stone_SG_Floor"
OB, MBK, BI, WD = "Stone_SG_Obsidian", "Stone_SG_MarbleBlack", "Metal_SG_BlackIron", "Wood_SG_Dark"
CL, PALE, GLW, CORE = "Cloth_SG_Purple", "Stone_SG_MoonPale", "Lantern_Glow", "SG_LampCore_Glow"
VG, VOID, CRY, CRYG = "SG_Violet_Glow", "SG_CaveVoid_Glow", "Crystal_SGCave", "SG_Crystal_Glow"

X0, Y0, X1, Y1 = L.CAVE
ZF, ZT = L.CAVE_FLOOR, L.CAVE_TOP
ZG = L.CAVE_GALLERY_Z
TC = L.SPIRAL_C
UPZ = Vector((0.0, 0.0, 1.0))


_SHARED = {}


def smb():
    """pedaco da ESTRUTURA do salao: cada chamada abre um MB (casco convexo rapido em bmesh pequeno); no fim do build
    os pedacos viram UM objeto SG_Cave_Build (1 MeshPart por material no salao inteiro, nao 1 por objeto x material)"""
    import inspect
    fn = inspect.stack()[1].function
    mb = MB("SG_Cave_Build_%02d_%s" % (len(_SHARED.setdefault("parts", [])), fn), C,
            random.Random(940 + len(_SHARED["parts"])), detail="near")
    _SHARED["parts"].append(mb)
    return mb


def join_parts(name="SG_Cave_Build"):
    import bpy
    obs = [o for o in (mb.finish() for mb in _SHARED.pop("parts", [])) if o is not None]
    print("CAVE partes: %s" % ", ".join("%s %d" % (o.name[15:], sum(len(p.vertices) - 2 for p in o.data.polygons))
                                        for o in obs))
    if not obs:
        return None
    with bpy.context.temp_override(active_object=obs[0], object=obs[0], selected_objects=obs,
                                   selected_editable_objects=obs):
        bpy.ops.object.join()
    ob = obs[0]
    ob.name = name
    ob.data.name = name
    return ob


# ==================================================================== solidos (idioma da dungeon aprovada)
def _dedupe3(pts, tol=2e-3):
    out = []
    for p in pts:
        p = Vector(p)
        if all((p - q).length > tol for q in out):
            out.append(p)
    return out


def hull(mb, pts, m, face_m=None):
    """solido convexo dos pontos; face_m(normal, centro) -> material (ou None) por face"""
    bm = mb.bm
    vs = [bm.verts.new(p) for p in _dedupe3(pts)]
    if len(vs) < 4:
        for v in vs:
            bm.verts.remove(v)
        return []
    res = bmesh.ops.convex_hull(bm, input=vs, use_existing_faces=False)
    junk = list({v for v in res["geom_interior"] + res["geom_unused"] if isinstance(v, bmesh.types.BMVert)})
    if junk:
        bmesh.ops.delete(bm, geom=junk, context="VERTS")
    for _ in range(4):
        fs = {f for v in vs if v.is_valid for f in v.link_faces}
        bad = [f for f in fs if f.calc_area() < 2e-5]
        if not bad:
            break
        es = list({min(f.edges, key=lambda e: e.calc_length()) for f in bad})
        bmesh.ops.collapse(bm, edges=es, uvs=False)
    keep = [v for v in vs if v.is_valid]
    if len(keep) < 4:
        return []
    faces = mb._post(keep, m, None, 0, 1)
    if face_m:
        cache = {}
        for f in faces:
            mm = face_m(f.normal, f.calc_center_median())
            if mm:
                if mm not in cache:
                    cache[mm] = mb._mi_for(mm)
                f.material_index = cache[mm]
    return faces


def clip(pts, n, c):
    """poliedro convexo dos pontos recortado pelo semiespaco n.p <= c (exato)"""
    n = Vector(n)
    tmp = bmesh.new()
    tv = [tmp.verts.new(p) for p in _dedupe3(pts)]
    res = bmesh.ops.convex_hull(tmp, input=tv, use_existing_faces=False)
    edges = [e for e in res["geom"] if isinstance(e, bmesh.types.BMEdge)]
    out = [v.co.copy() for v in tmp.verts if v.link_edges and n.dot(v.co) <= c + 1e-6]
    for e in edges:
        a, b = e.verts[0].co, e.verts[1].co
        da, db = n.dot(a) - c, n.dot(b) - c
        if (da < -1e-6 < 1e-6 < db) or (db < -1e-6 < 1e-6 < da):
            out.append(a.lerp(b, da / (da - db)))
    tmp.free()
    return _dedupe3(out, 0.01)


def cut(pts, nw, dep):
    """plano de FRATURA: tira 'dep' do canto mais externo na direcao nw"""
    nw = Vector(nw).normalized()
    top = max(nw.dot(Vector(p)) for p in pts)
    return clip(pts, nw, top - dep)


def cbox_pts(c, ax, ay, az, sx, sy, sz, ch):
    c, ax, ay, az = Vector(c), Vector(ax), Vector(ay), Vector(az)
    hx, hy, hz = sx / 2.0, sy / 2.0, sz / 2.0
    ch = max(0.0, min(ch, hx * 0.45, hy * 0.45, hz * 0.45))
    out = []
    for i in (-1, 1):
        for j in (-1, 1):
            for k in (-1, 1):
                if ch < 1e-4:
                    out.append(c + ax * (i * hx) + ay * (j * hy) + az * (k * hz))
                    continue
                for a, b, d in ((ch, 0, 0), (0, ch, 0), (0, 0, ch)):
                    out.append(c + ax * (i * (hx - a)) + ay * (j * (hy - b)) + az * (k * (hz - d)))
    return out


def cbox(mb, c, ax, ay, az, sx, sy, sz, m, ch=0.1, cuts=(), face_m=None):
    """bloco orientado chanfrado; cuts = [(normal LOCAL, recuo)] = fraturas / quinas quebradas dirigidas"""
    c, ax, ay, az = Vector(c), Vector(ax).normalized(), Vector(ay).normalized(), Vector(az).normalized()
    pts = cbox_pts(c, ax, ay, az, sx, sy, sz, ch)
    for nl, dep in cuts:
        pts = cut(pts, ax * nl[0] + ay * nl[1] + az * nl[2], dep)
    return hull(mb, pts, m, face_m)


def abox(mb, p0, p1, m, ch=0.1, cuts=()):
    """caixa alinhada aos eixos por cantos, chanfrada (hull)"""
    p0, p1 = Vector(p0), Vector(p1)
    c = (p0 + p1) / 2
    return cbox(mb, c, (1, 0, 0), (0, 1, 0), (0, 0, 1), abs(p1.x - p0.x), abs(p1.y - p0.y), abs(p1.z - p0.z), m, ch,
                cuts)


def obox3(mb, c, ax, ay, az, sx, sy, sz, m):
    c = Vector(c)
    ax, ay, az = Vector(ax), Vector(ay), Vector(az)
    hx, hy, hz = ax * (sx / 2.0), ay * (sy / 2.0), az * (sz / 2.0)
    bm = mb.bm
    V = {}
    for i in (0, 1):
        for j in (0, 1):
            for k in (0, 1):
                V[i, j, k] = bm.verts.new(c + hx * (2 * i - 1) + hy * (2 * j - 1) + hz * (2 * k - 1))
    for f in (((0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)), ((1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)),
              ((0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)), ((0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0)),
              ((0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)), ((0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1))):
        bm.faces.new([V[q] for q in f])
    fs = mb._post(list(V.values()), m, None, 0, 1)
    bmesh.ops.recalc_face_normals(bm, faces=list(fs))


def bar(mb, a, b, w, h, m, up=None):
    """barra retangular de a ate b (secao w lateral x h 'para cima')"""
    a, b = Vector(a), Vector(b)
    d = b - a
    if d.length < 1e-4:
        return
    ax = d.normalized()
    u = Vector(up) if up is not None else UPZ
    if abs(ax.dot(u)) > 0.95:
        u = Vector((1.0, 0.0, 0.0)) if abs(ax.x) < 0.9 else Vector((0.0, 1.0, 0.0))
    side = ax.cross(u).normalized()
    upv = side.cross(ax).normalized()
    obox3(mb, (a + b) / 2, ax, side, upv, d.length, w, h, m)


def lathe_ax(mb, o, ax, prof, m, n=6, ph=0.0):
    """revolucao em torno de um eixo qualquer; prof = [(raio, distancia)], raio 0 = polo"""
    o, ax = Vector(o), Vector(ax).normalized()
    ref = Vector((0.0, 0.0, 1.0)) if abs(ax.z) < 0.9 else Vector((1.0, 0.0, 0.0))
    e1 = ax.cross(ref).normalized()
    e2 = ax.cross(e1).normalized()
    bm = mb.bm
    rows = []
    for r, d in prof:
        if r < 1e-5:
            rows.append([bm.verts.new(o + ax * d)])
        else:
            rows.append([bm.verts.new(o + ax * d + (e1 * math.cos(ph + 2 * math.pi * i / n) +
                                                    e2 * math.sin(ph + 2 * math.pi * i / n)) * r) for i in range(n)])
    faces = []
    for A_, B_ in zip(rows, rows[1:]):
        if len(A_) == 1 and len(B_) == 1:
            continue
        for i in range(n):
            j = (i + 1) % n
            if len(A_) == 1:
                faces.append(bm.faces.new((A_[0], B_[i], B_[j])))
            elif len(B_) == 1:
                faces.append(bm.faces.new((A_[i], A_[j], B_[0])))
            else:
                faces.append(bm.faces.new((A_[i], A_[j], B_[j], B_[i])))
    for R_ in (rows[0], rows[-1]):
        if len(R_) > 2:
            faces.append(bm.faces.new(R_))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    return mb._post([v for r in rows for v in r], m, None, 0, 1)


def _pl(c, u, v, n, a, r, d):
    return c + u * (math.cos(a) * r) + v * (math.sin(a) * r) + n * d


def ring3(mb, c, u, v, n, r0, r1, d0, d1, m, seg=28):
    bm = mb.bm
    A_ = [2 * math.pi * k / seg for k in range(seg)]
    iF = [bm.verts.new(_pl(c, u, v, n, a, r0, d1)) for a in A_]
    iB = [bm.verts.new(_pl(c, u, v, n, a, r0, d0)) for a in A_]
    oF = [bm.verts.new(_pl(c, u, v, n, a, r1, d1)) for a in A_]
    oB = [bm.verts.new(_pl(c, u, v, n, a, r1, d0)) for a in A_]
    for i in range(seg):
        j = (i + 1) % seg
        bm.faces.new((oF[i], oF[j], iF[j], iF[i]))
        bm.faces.new((iB[i], iB[j], oB[j], oB[i]))
        bm.faces.new((iF[i], iF[j], iB[j], iB[i]))
        bm.faces.new((oB[i], oB[j], oF[j], oF[i]))
    mb._post(iF + iB + oF + oB, m, None, 0, 1)


def disc3(mb, c, u, v, n, r, d0, d1, m, seg=28):
    bm = mb.bm
    A_ = [2 * math.pi * k / seg for k in range(seg)]
    Fv = [bm.verts.new(_pl(c, u, v, n, a, r, d1)) for a in A_]
    Bv = [bm.verts.new(_pl(c, u, v, n, a, r, d0)) for a in A_]
    bm.faces.new(Fv)
    bm.faces.new(list(reversed(Bv)))
    for i in range(seg):
        j = (i + 1) % seg
        bm.faces.new((Fv[j], Fv[i], Bv[i], Bv[j]))
    mb._post(Fv + Bv, m, None, 0, 1)


def vortex_arms(mb, c, u, v, n, R, d0, d1, m, arms=6, twist=2.9, seg=16):
    """bracos da espiral do vortice (fitas que afinam nas pontas) + nucleo"""
    bm = mb.bm
    for k in range(arms):
        th0 = 2 * math.pi * k / arms
        LF, RF, LB, RB = [], [], [], []
        for i in range(seg + 1):
            t = i / seg
            r = 0.9 + (R - 0.9) * t
            th = th0 + twist * t
            w = 0.35 + 2.4 * t * (1.0 - t)
            dl = (w / 2.0) / r
            LF.append(bm.verts.new(_pl(c, u, v, n, th - dl, r, d1)))
            RF.append(bm.verts.new(_pl(c, u, v, n, th + dl, r, d1)))
            LB.append(bm.verts.new(_pl(c, u, v, n, th - dl, r, d0)))
            RB.append(bm.verts.new(_pl(c, u, v, n, th + dl, r, d0)))
        for i in range(seg):
            bm.faces.new((LF[i], RF[i], RF[i + 1], LF[i + 1]))
            bm.faces.new((LB[i + 1], RB[i + 1], RB[i], LB[i]))
            bm.faces.new((LF[i + 1], LB[i + 1], LB[i], LF[i]))
            bm.faces.new((RF[i], RB[i], RB[i + 1], RF[i + 1]))
        bm.faces.new((LF[0], LB[0], RB[0], RF[0]))
        bm.faces.new((RF[-1], RB[-1], LB[-1], LF[-1]))
        mb._post(LF + RF + LB + RB, m, None, 0, 1)
    disc3(mb, c, u, v, n, 1.3, d0, d1 + 0.05, m, 12)


def rune(mb, o, ea, eb, en, k, sc, m, dep=0.05, w=0.1):
    """runa k do alfabeto unico com centro em o, no plano (ea lateral, eb 'cima'), saltando 'dep' ao longo de en"""
    o, ea, eb, en = Vector(o), Vector(ea).normalized(), Vector(eb).normalized(), Vector(en).normalized()
    ww = w * sc
    for (a0, b0), (a1, b1) in RUNE_SEGS[k % len(RUNE_SEGS)]:
        p0 = o + ea * (a0 * sc) + eb * (b0 * sc)
        p1 = o + ea * (a1 * sc) + eb * (b1 * sc)
        d = p1 - p0
        ax = d.normalized()
        ay = en.cross(ax).normalized()
        obox3(mb, (p0 + p1) / 2 + en * (dep / 2), ax, ay, en, d.length + ww, ww, dep, m)


def crescent(mb, c, u, v, n, R, d0, d1, m, k=10):
    """CRESCENTE da ordem (so a lua, sem anel): lua de raio R e sombra deslocada; pontas para +u. Casca fechada."""
    c, u, v, n = Vector(c), Vector(u), Vector(v), Vector(n)
    R1, c2, sr = R, 0.27 * R / 0.62, 0.52 * R / 0.62          # proporcoes do sg_emblem (lua / sombra)
    x = (R1 * R1 - sr * sr + c2 * c2) / (2 * c2)
    y = math.sqrt(max(0.0, R1 * R1 - x * x))
    a1 = math.atan2(y, x)
    b1 = math.atan2(y, x - c2)
    outer = [(R1 * math.cos(a1 + (2 * math.pi - 2 * a1) * i / k), R1 * math.sin(a1 + (2 * math.pi - 2 * a1) * i / k))
             for i in range(k + 1)]
    inner = [(c2 + sr * math.cos(-b1 - (2 * math.pi - 2 * b1) * i / k), sr * math.sin(-b1 - (2 * math.pi - 2 * b1) * i / k))
             for i in range(k + 1)]
    loop = outer + inner[1:-1]
    shift = -(x - R1) / 2.0                          # caixa do crescente centrada em c (pontas para +u)
    bm = mb.bm
    F_ = [bm.verts.new(c + u * (a + shift) + v * b + n * d1) for a, b in loop]
    B_ = [bm.verts.new(c + u * (a + shift) + v * b + n * d0) for a, b in loop]
    fs = [bm.faces.new(F_), bm.faces.new(list(reversed(B_)))]
    N_ = len(loop)
    for i in range(N_):
        j = (i + 1) % N_
        fs.append(bm.faces.new((F_[j], F_[i], B_[i], B_[j])))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    mb._post(F_ + B_, m, None, 0, 1)


def chain_lite(mb, p0, p1, sag, m=BI, pitch=0.9):
    """corrente de ferro leve: elos vazados de 4 barras alternando deitado/em pe (catenaria parabolica)"""
    p0, p1 = Vector(p0), Vector(p1)
    n = max(3, int((p1 - p0).length / pitch))
    pts = [p0.lerp(p1, i / n) + Vector((0.0, 0.0, -4.0 * sag * (i / n) * (1.0 - i / n))) for i in range(n + 1)]
    hw, wr = 0.24, 0.14
    for i in range(n):
        a, b = pts[i], pts[i + 1]
        ax = (b - a).normalized()
        hl = (b - a).length * 0.5 + 0.12
        s0 = ax.cross(UPZ)
        s0 = s0.normalized() if s0.length > 1e-3 else Vector((1.0, 0.0, 0.0))
        s = s0 if i % 2 == 0 else ax.cross(s0).normalized()
        nn = ax.cross(s).normalized()
        c = (a + b) / 2
        for sg in (-1, 1):
            obox3(mb, c + s * (sg * hw), ax, s, nn, 2 * hl, wr, wr, m)
            obox3(mb, c + ax * (sg * (hl - wr / 2)), s, ax, nn, 2 * hw + wr, wr, wr, m)


# ==================================================================== ROCHA BRUTA: paredes
# parede = COLUNAS de basalto (diaclases verticais continuas, fenda escura de 0,4) cortadas em BANCOS (duro grosso /
# mole fino recuado); cada bloco e um casco com a face interna INCLINADA (a parede se debruca para dentro acima da faixa
# em que o jogador anda) e 1-2 PLANOS DE FRATURA dirigidos pelo indice (labio no topo, quina lateral partida, sub-cava).
# Faces: corpo RKD, topo dos bancos ao luar RKL, fendas e bordas de baixo RK (sombra).
WALLS = {"W": ((X0, Y0), (0.0, 1.0), (1.0, 0.0), Y1 - Y0), "E": ((X1, Y1), (0.0, -1.0), (-1.0, 0.0), Y1 - Y0),
         "S": ((X1, Y0), (-1.0, 0.0), (0.0, 1.0), X1 - X0), "N": ((X0, Y1), (1.0, 0.0), (0.0, -1.0), X1 - X0)}
COLW = (11.0, 14.8, 9.2, 13.0, 16.4, 10.1, 13.7, 11.6, 15.4)
ROW_LOW = (7.4, 3.6, 8.2, 4.0, 6.8, 3.4, 7.8, 3.8)      # abaixo de ~22 (duro, mole, duro, mole...)
ROW_HIGH = (13.4, 16.8, 14.6)
Z_LOW, Z_HIGH, Z_ROCK_TOP = -13.5, 21.5, 43.4
BACK = -3.4                                      # plano de fundo das fendas (atras da face da parede)


def wall_pt(side, s, p, z):
    (ox, oy), (tx, ty), (nx, ny), ln = WALLS[side]
    return Vector((ox + tx * s + nx * p, oy + ty * s + ny * p, z))


def p_allow(side, x, y, z):
    """protrusao maxima da rocha para DENTRO do retangulo do salao em (x, y, z): 0,5 onde o jogador anda encostado
    (piso, passarelas e galeria ate a altura do pulo); acima disso a parede se debruca (abobada irregular)"""
    zs = 3.0
    lean = 0.5
    if side in ("W", "E"):
        if 146.0 <= y <= 310.0:
            zs = 21.0                            # passarelas / galeria a 6,6 (+ pulo)
        if y < 146.0:
            zs = 4.0                             # forja / sala do mapa: a rocha cobre a chamine e as estantes
    elif side == "S":
        ax = abs(x)
        if ax < 28.5:
            return 0.5 if z < 36.0 else 0.5 + min(9.0, (z - 36.0) * 0.9)   # o portal fica na frente; rocha em cima
        if ax < 44.0:
            zs, lean = -12.0, 0.36                # rocha que abraca os pilares do portal (arco natural de basalto)
    if z <= zs:
        return 0.5
    return 0.5 + min(11.0, (z - zs) * lean)


def _h(i, j, k=0):
    """variacao DIRIGIDA (deterministica por indice, nada sorteado): 0..1"""
    return (math.sin(i * 12.9898 + j * 78.233 + k * 37.719) * 43758.5453) % 1.0


def rock_face_m(tv):
    t3 = Vector((tv[0], tv[1], 0.0))

    def f(nrm, ctr):
        if nrm.z > 0.72:
            return RKL
        if nrm.z < -0.55 or abs(nrm.dot(t3)) > 0.86:
            return RK
        return None
    return f


def _rows(seed, off=0.0, zh=Z_HIGH):
    out = []
    z, i = Z_LOW - off, seed % len(ROW_LOW)
    while z < zh - 0.5:
        h = ROW_LOW[i % len(ROW_LOW)] * (0.85 + 0.3 * _h(seed, i, 21))
        z1 = min(zh, z + h)
        if zh - z1 < 1.6:
            z1 = zh
        out.append((z, z1, (i % 2) == 1, False))
        z, i = z1, i + 1
    i = seed
    while z < Z_ROCK_TOP - 0.5:
        h = ROW_HIGH[i % len(ROW_HIGH)]
        z1 = min(Z_ROCK_TOP, z + h)
        if Z_ROCK_TOP - z1 < 3.0:
            z1 = Z_ROCK_TOP
        out.append((z, z1, False, True))
        z, i = z1, i + 1
    return out


def _cols(ln, seed, merge=1):
    out = []
    s, i = -9.0, seed
    while s < ln + 9.0:
        w = sum(COLW[(i + k) % len(COLW)] for k in range(merge))
        out.append((s, min(ln + 9.0, s + w)))
        s, i = s + w, i + merge
    return out


def wall_block(mb, side, ci, ri, s0, s1, z0, z1, soft, high, fm):
    (ox, oy), tv, nv, ln = WALLS[side]
    if z1 < ZF + 0.6:
        return 0                                                     # todo abaixo do piso (escondido)
    sm = (s0 + s1) / 2
    mid = wall_pt(side, sm, 0.0, 0.0)
    ends = [wall_pt(side, s, 0.0, 0.0) for s in (s0, s1)]
    if side == "N" and math.hypot(mid.x - TC[0], mid.y - TC[1]) < 19.0 and z0 < ZT:
        return 0                                                     # a torre do poco sai da rocha aqui
    if side == "S" and abs(mid.x) < 27.0 and z1 < 33.5:
        return 0                                                     # atras do nicho do portal (fica escondido)

    def allow(z):
        return min(p_allow(side, e.x, e.y, z) for e in ends)
    f = 0.62 + 0.38 * _h(ci, 3, ord(side))                          # quanto esta coluna se debruca
    rib = (1.6 if ci % 5 == 2 else (-1.4 if ci % 7 == 4 else 0.0))   # costela saliente / baia recuada
    low_rec = (0.0, 1.1, 0.35, 1.8, 0.7)[(ci * 3 + ri) % 5] + (0.9 if soft else 0.0)

    def target(z):
        a = allow(z)
        if a <= 0.51:
            return min(a, 0.5 - low_rec + 0.5 * f)
        return min(a, 0.5 + (a - 0.5) * f + rib - (0.8 if soft else 0.0))
    g, gz = 0.2, 0.12
    za, zb = z0 + gz, z1 - gz
    pb, pt = max(-2.6, target(za)), max(-2.6, target(zb))
    pb = min(pb, allow(za))
    pt = min(max(pt, pb - 0.6), allow(zb))
    sa, sb = s0 + g, s1 - g
    pts = [wall_pt(side, s, p, z) for s in (sa, sb) for p, z in ((BACK - 0.6, za), (BACK - 0.6, zb), (pb, za), (pt, zb))]
    t3, n3 = Vector((tv[0], tv[1], 0.0)), Vector((nv[0], nv[1], 0.0))
    h = zb - za
    k = (ci + 2 * ri + ord(side)) % 4
    c = min(1.6, 0.28 * h, 0.3 * (s1 - s0))
    if k == 0:
        pts = cut(pts, n3 + UPZ, c * 0.8)                          # labio do banco quebrado
    elif k == 1:
        pts = cut(pts, n3 + t3 * 0.9, c)                           # quina lateral partida
    elif k == 2:
        pts = cut(pts, n3 - UPZ * 0.8, c * 0.7)                    # sub-cava (a face de baixo some na sombra)
    else:
        pts = cut(pts, n3 - t3 * 0.8, c * 0.8)
        pts = cut(pts, n3 + UPZ * 1.3, c * 0.45)
    if not high and (ci + ri) % 3 == 0:
        pts = cut(pts, n3 + UPZ * 0.35 + t3 * 0.2, 0.35)           # face interna com 2 planos (nada chapado)
    hull(mb, pts, RKD, fm)
    return 1


# ORGAO DE BASALTO (a assinatura da ilha): colunas hexagonais em favo encostadas na parede, onde o piso e livre;
# mais altas junto da rocha, descendo em degraus para o salao, topos inclinados. (lado, s0, s1, avanco, altura)
ORGANS = [("S", 12.0, 32.0, 4.4, 10.5), ("S", 148.0, 168.0, 4.4, 9.5), ("N", 6.0, 40.0, 5.0, 12.0),
          ("N", 138.0, 172.0, 5.0, 11.0), ("W", 136.0, 178.0, 4.2, 9.0), ("E", 68.0, 110.0, 4.2, 9.0)]


def basalt_organ(mb, side, s0, s1, pmax, hmax, gi):
    r = 1.45
    dx, dy = 2 * r * math.cos(math.radians(30.0)), 1.5 * r
    n = 0
    j = 0
    p = -0.6
    while p < pmax - 0.4:
        s = s0 + (dx / 2 if j % 2 else 0.0)
        while s < s1:
            e = 1.0 - abs((s - (s0 + s1) / 2) / ((s1 - s0) / 2)) ** 2
            h = hmax * (0.55 + 0.45 * e) - p * 1.55 + 1.6 * (_h(int(s * 3), j, gi) - 0.5)
            if h > 1.2:
                c = wall_pt(side, s, p, 0.0)
                tilt = (_h(int(s * 5), j, gi + 7) - 0.5) * 0.5
                ph = math.radians(30.0)
                ring0 = [Vector((c.x + r * math.cos(ph + q * math.pi / 3), c.y + r * math.sin(ph + q * math.pi / 3), ZF - 0.3))
                         for q in range(6)]
                ring1 = [Vector((v.x, v.y, ZF + h + tilt * (v.x - c.x) - 0.35 * tilt * (v.y - c.y))) for v in ring0]
                hull(mb, [v.lerp(c, 0.04) for v in ring0] + [Vector((v.x, v.y, v.z)) + (Vector((c.x, c.y, v.z)) - v) * 0.06
                                                             for v in ring1], RKD, _organ_m)
                n += 1
            s += dx
        p += dy
        j += 1
    a, b = wall_pt(side, s0, -1.0, 0.0), wall_pt(side, s1, pmax, 0.0)
    col_box2("SG_CaveOrgan", (min(a.x, b.x), min(a.y, b.y), ZF), (max(a.x, b.x), max(a.y, b.y), ZF + hmax))
    return n


def _organ_m(nrm, ctr):
    return RKL if nrm.z > 0.7 else None


def rock_walls():
    n = 0
    for si, side in enumerate(("W", "E", "S", "N")):
        (ox, oy), tv, nv, ln = WALLS[side]
        mb = MB("SG_Cave_Rock_" + side, C, random.Random(900 + si), detail="far", floor=-999)
        fm = rock_face_m(tv)
        for ci, (s0, s1) in enumerate(_cols(ln, si * 2)):
            rows = _rows(si * 3 + ci, 4.2 * _h(ci, si, 11), Z_HIGH + 6.0 * (_h(ci, si, 12) - 0.5))
            for ri, (z0, z1, soft, high) in enumerate(rows):
                n += wall_block(mb, side, ci, ri, s0, s1, z0, z1, soft, high, fm)
        for gi, (gside, s0, s1, pmax, hmax) in enumerate(ORGANS):
            if gside == side:
                n += basalt_organ(mb, side, s0, s1, pmax, hmax, gi)
        # fundo das fendas (escuro): um plano atras dos blocos
        hull(mb, [wall_pt(side, s, p, z) for s in (-9.0, ln + 9.0) for p in (BACK, BACK - 0.4)
                  for z in (Z_LOW, Z_ROCK_TOP)], RK)
        mb.finish()
    return n


# ==================================================================== ROCHA BRUTA: abobada
# lajes facetadas numa grade de cantos deslocados (planta irregular), cada laje com quilha no meio e degrau proprio
# (escarpas de fratura entre vizinhas); a abobada desce junto das paredes (encontra a parede que se debruca) e sobe no
# meio. Colar de rocha em volta da torre, a FENDA NE de onde sai a queda (WATER_CaveFall_Lip) e grupos de estalactites.
FALL = (72.0, 222.0, 35.0)                       # borda da bica da queda (marcador WATER_CaveFall_Lip)
STAL = [(-44.0, 128.0, 4, 1.1), (40.0, 144.0, 3, 1.25), (-60.0, 212.0, 5, 1.0), (14.0, 176.0, 3, 0.8),
        (58.0, 256.0, 4, 1.15), (-34.0, 262.0, 3, 0.95), (50.0, 108.0, 3, 1.0), (-68.0, 106.0, 4, 1.2),
        (-4.0, 142.0, 2, 0.85), (-14.0, 236.0, 3, 1.0), (34.0, 298.0, 3, 0.85), (-62.0, 300.0, 4, 1.05),
        (78.0, 178.0, 3, 1.0), (-80.0, 168.0, 3, 1.0), (30.0, 206.0, 2, 0.9), (-24.0, 188.0, 3, 1.1)]


def ceil_zb(x, y):
    dw = max(0.0, min(X1 - abs(x), y - Y0, Y1 - y))
    d = 2.2 + 8.5 * max(0.0, 1.0 - dw / 44.0) + 2.6 * _h(round(x / 9.0), round(y / 9.0), 7)
    zb = 41.2 - d
    if 64.0 < x < 80.0 and 204.0 < y < 226.0:
        zb = max(zb, 38.0)                       # a queda desce livre ate o rio
    return max(zb, 25.0)


def ceiling():
    mb = MB("SG_Cave_Ceiling", C, random.Random(931), detail="far", floor=-999)
    fm = rock_face_m((1.0, 0.0))
    nx, ny = 10, 12
    xs = [X0 - 6.0 + (X1 - X0 + 12.0) * i / nx for i in range(nx + 1)]
    ys = [Y0 - 6.0 + (Y1 - Y0 + 12.0) * j / ny for j in range(ny + 1)]
    cor = {}
    for i, x in enumerate(xs):
        for j, y in enumerate(ys):
            if 0 < i < nx and 0 < j < ny:
                x += (_h(i, j, 1) - 0.5) * 8.0
                y += (_h(i, j, 2) - 0.5) * 8.0
            cor[i, j] = (x, y)
    ztop = ZT + 1.2
    for i in range(nx):
        for j in range(ny):
            q = [cor[i, j], cor[i + 1, j], cor[i + 1, j + 1], cor[i, j + 1]]
            cx = sum(p[0] for p in q) / 4
            cy = sum(p[1] for p in q) / 4
            if math.hypot(cx - TC[0], cy - TC[1]) < 24.0:
                continue
            dz = (_h(i, j, 5) - 0.5) * 3.2                       # degrau proprio da laje (escarpa)
            keel = 1.2 + 1.6 * _h(i, j, 6)
            pts = []
            for x, y in q:
                sx, sy = x + (cx - x) * 0.03, y + (cy - y) * 0.03      # junta aberta entre as lajes
                pts.append(Vector((sx, sy, ztop)))
                pts.append(Vector((sx, sy, min(ztop - 1.0, ceil_zb(x, y) + dz))))
            zc = min(p.z for p in pts) - keel
            if 64.0 < cx < 80.0 and 204.0 < cy < 226.0:
                zc = max(zc, 37.5)
            ox, oy = (_h(i, j, 8) - 0.5) * 6.0, (_h(i, j, 9) - 0.5) * 6.0
            pts.append(Vector((cx + ox, cy + oy, max(zc, 24.0))))
            hull(mb, pts, RKD, fm)
    # colar de rocha em volta da torre (a torre entra na abobada acima da cinta de misulas)
    for k in range(12):
        a0, a1 = math.radians(30.0 * k - 1.0), math.radians(30.0 * k + 31.0)
        zb = 37.4 + 1.6 * _h(k, 1, 3)
        pts = []
        for a in (a0, a1):
            for r in (17.4, 29.0):
                pts.append(Vector((TC[0] + r * math.cos(a), TC[1] + r * math.sin(a), ztop)))
            pts.append(Vector((TC[0] + 18.8 * math.cos(a), TC[1] + 18.8 * math.sin(a), zb)))
            pts.append(Vector((TC[0] + 27.0 * math.cos(a), TC[1] + 27.0 * math.sin(a), zb - 2.0 - 1.4 * _h(k, 2, 3))))
        hull(mb, pts, RKD, fm)
    # fenda NE: a massa que pende da abobada e a bica de pedra da queda (a agua e do Roblox)
    fx, fy, fz = FALL
    hull(mb, [Vector((x, y, z)) for x, y, z in ((fx - 7.0, fy + 0.6, fz + 1.2), (fx + 7.5, fy + 0.6, fz + 1.4),
                                                  (fx - 8.0, fy + 11.0, fz + 3.2), (fx + 8.0, fy + 10.0, fz + 2.4),
                                                  (fx - 9.0, fy - 1.0, ztop), (fx + 9.0, fy - 1.0, ztop),
                                                  (fx - 10.0, fy + 13.0, ztop), (fx + 10.0, fy + 13.0, ztop),
                                                  (fx + 1.0, fy + 5.0, fz - 0.4))], RKD, fm)
    for s in (-1, 1):                                                   # faces da bica (canal de 4)
        abox(mb, (fx + s * 2.0 - 0.6, fy - 1.3, fz - 0.9), (fx + s * 2.0 + 0.6, fy + 3.0, fz + 1.4), RKD, 0.0,
             cuts=[((0, -1, 1), 0.5)])
    abox(mb, (fx - 2.6, fy - 1.1, fz - 0.9), (fx + 2.6, fy + 3.0, fz), RKD, 0.0)
    # fundo escuro acima das juntas (furo quadrado no poco)
    hx0, hy0, hx1, hy1 = TC[0] - 19.5, TC[1] - 19.5, TC[0] + 19.5, TC[1] + 19.5
    for p0, p1 in (((X0 - 8, Y0 - 8), (X1 + 8, hy0)), ((X0 - 8, hy1), (X1 + 8, Y1 + 8)), ((X0 - 8, hy0), (hx0, hy1)),
                   ((hx1, hy0), (X1 + 8, hy1))):
        abox(mb, (p0[0], p0[1], ztop - 0.2), (p1[0], p1[1], ztop + 0.25), RK, 0.0)
    # estalactites em grupos (penduradas no fundo da laje: raio para cima)
    bvh = BVHTree.FromBMesh(mb.bm)
    ns = 0
    for gi, (gx, gy, cnt, sc) in enumerate(STAL):
        for k in range(cnt):
            a = 2.4 * k + gi
            rr = 0.0 if k == 0 else 2.2 + 1.4 * _h(gi, k, 4)
            x, y = gx + rr * math.cos(a), gy + rr * math.sin(a)
            hit = bvh.ray_cast(Vector((x, y, 12.0)), Vector((0.0, 0.0, 1.0)), 60.0)
            if hit[0] is None:
                continue
            z0 = hit[0].z
            Ls = sc * (8.5 if k == 0 else 3.5 + 4.0 * _h(gi, k, 5))
            r = sc * (1.7 if k == 0 else 0.8 + 0.6 * _h(gi, k, 6))
            ph = a * 0.7
            ring = lambda rad, z: [Vector((x + rad * math.cos(ph + q * math.pi / 3), y + rad * math.sin(ph + q * math.pi / 3), z))
                                   for q in range(6)]
            tip = Vector((x + 0.25 * r, y - 0.2 * r, z0 - Ls))
            hull(mb, ring(r, z0 + 1.2) + ring(r * 0.62, z0 - Ls * 0.38), RKD, fm)
            hull(mb, ring(r * 0.64, z0 - Ls * 0.36) + [tip], RKD)
            ns += 1
    mb.finish()
    return ns


# ==================================================================== PISO: lajes, eixo processional, rio e ponte
# piso = lajes grandes de rocha (Tier C, fiadas irregulares) com junta aberta ate o fundo 0,35 abaixo (piso sobre piso
# >= 0,3); o EIXO (estrado -> ponte -> escadaria) em lajes de 2 tons com friso; rio escuro com leito de pedra e meio-fio;
# ponte de pedra no eixo (calcada sobre o rio, talha-mares, guardas com rufo e 4 marcos com tocha).
PX0, PY0, PX1, PY1, PLEV, PBOT = L.CAVE_POOL
BW = L.CAVE_POOL_BRIDGE_W / 2
FORGE_PF = (-88.0, 132.0, -58.0, 190.0)          # plataforma da forja (+1,6; degraus a leste)
MAP_PF = (58.0, 132.0, 88.0, 190.0)              # plataforma da sala do mapa (+1,6; degraus a oeste)
PF_Z = ZF + 1.6
NAVE_Y = (128.0, 168.0, 240.0)                   # pares de pilares antigos (x +-26) com arco transversal
NAVE_X = 26.0
FLOOR_EXCL = [(PX0 - 0.2, PY0 - 1.2, PX1 + 0.2, PY1 + 1.2), (-8.6, 116.0, 8.6, PY0), (-8.6, PY1, 8.6, 224.0),
              (-9.6, 223.8, 9.6, 274.0), (-16.6, 90.0, 16.6, 120.0), (-28.8, Y0 - 2.0, 28.8, 106.0),
              (X0 - 2.0, 130.0, -54.2, 192.0), (54.2, 130.0, X1 + 2.0, 192.0), (-20.0, 302.0, 20.0, Y1 + 2.0)]
STALAG = [(-84.0, 100.0, 3), (84.0, 102.0, 3), (-87.0, 316.0, 2), (87.0, 312.0, 2)]


def rect_sub(r, cutters):
    out = [r]
    for c in cutters:
        nxt = []
        for a in out:
            ax0, ay0, ax1, ay1 = a
            cx0, cy0, cx1, cy1 = c
            if cx0 >= ax1 or cx1 <= ax0 or cy0 >= ay1 or cy1 <= ay0:
                nxt.append(a)
                continue
            if cy0 > ay0:
                nxt.append((ax0, ay0, ax1, cy0))
            if cy1 < ay1:
                nxt.append((ax0, cy1, ax1, ay1))
            yy0, yy1 = max(ay0, cy0), min(ay1, cy1)
            if cx0 > ax0:
                nxt.append((ax0, yy0, cx0, yy1))
            if cx1 < ax1:
                nxt.append((cx1, yy0, ax1, yy1))
        out = nxt
    return out


def torch_cup(mb, p, out, h=1.0):
    """tocha de FERRO: chapa na face, braco, cesto de ferro e chama pequena em gota (so ela emite).
    p = ponto na face, out = normal para fora (horizontal)"""
    p, out = Vector(p), Vector((out[0], out[1], 0.0)).normalized()
    sd = UPZ.cross(out).normalized()
    obox3(mb, p + out * 0.08, out, sd, UPZ, 0.16, 0.7, 1.1, BI)
    tip = p + out * 0.75 + UPZ * 0.3
    bar(mb, p + out * 0.1 - UPZ * 0.2, tip, 0.14, 0.14, BI)
    c = tip + out * 0.12
    EM._lathe(mb, (c.x, c.y, c.z - 0.05), [(0.1, 0.0), (0.34 * h, 0.32 * h), (0.3 * h, 0.4 * h)], BI, 6,
              caps=(True, False))
    EM._lathe(mb, (c.x, c.y, c.z + 0.12 * h), [(0.0, 0.0), (0.2 * h, 0.2 * h), (0.11 * h, 0.5 * h), (0.0, 0.78 * h)],
              GLW, 5)


def floor():
    mb = smb()
    # fundo das juntas (0,35 abaixo do piso)
    for p0, p1 in (((X0 - 2, Y0 - 2), (X1 + 2, PY0)), ((X0 - 2, PY1), (X1 + 2, Y1 + 2)),
                   ((X0 - 2, PY0), (PX0, PY1)), ((PX1, PY0), (X1 + 2, PY1))):
        abox(mb, (p0[0], p0[1], ZF - 1.2), (p1[0], p1[1], ZF - 0.35), RK, 0.0)
    # lajes de rocha em fiadas irregulares (juntas desencontradas)
    DEP = (13.5, 17.0, 12.0, 15.5, 18.5, 14.0)
    WID = (14.0, 19.0, 12.5, 17.0, 21.0, 13.0, 16.5)
    y, r = Y0 - 1.0, 0
    npl = 0
    while y < Y1 + 1.0:
        d = DEP[r % len(DEP)]
        y1 = min(Y1 + 1.0, y + d)
        x, k = X0 - 1.0 - 4.0 * (r % 3), r * 2
        while x < X1 + 1.0:
            w = WID[k % len(WID)]
            x1 = min(X1 + 1.0, x + w)
            for a in rect_sub((x + 0.15, y + 0.15, x1 - 0.15, y1 - 0.15), FLOOR_EXCL):
                if a[2] - a[0] > 1.2 and a[3] - a[1] > 1.2:
                    abox(mb, (a[0], a[1], ZF - 0.35), (a[2], a[3], ZF), RKD if (k + r) % 5 else RK, 0.0)
                    npl += 1
            x, k = x1, k + 1
        y, r = y1, r + 1

    # EIXO processional (estrado -> ponte -> escadaria): lajes de 2 tons, friso de marmore negro nas bordas
    def axis_paving(ya, yb, tread=3.2, friso=True):
        yy, i = ya, 0
        while yy < yb - 0.3:
            y2 = min(yb, yy + tread)
            cuts = [-8.0, -4.0, 0.0, 4.0, 8.0] if i % 2 == 0 else [-8.0, -6.0, -2.0, 2.0, 6.0, 8.0]
            for a, b in zip(cuts, cuts[1:]):
                edge = abs(a) > 7.0 or abs(b) > 7.0
                abox(mb, (a + 0.1, yy + 0.1, ZF - 0.35), (b - 0.1, y2 - 0.1, ZF), MBK if edge else FL, 0.0)
            yy, i = y2, i + 1
        for s in ((-1, 1) if friso else ()):                            # friso lateral
            abox(mb, (min(s * 8.0, s * 8.6) + 0.02, ya + 0.05, ZF - 0.35), (max(s * 8.0, s * 8.6) - 0.02, yb - 0.05, ZF),
                 MBK, 0.0)
    axis_paving(119.6, PY0 - 1.0)
    axis_paving(PY0 - 1.0, PY1 + 1.0, friso=False)
    axis_paving(PY1 + 1.0, 223.9, 1.5)
    # leito do rio e meio-fio de pedra (o fio explica a guarda invisivel do sg_col)
    abox(mb, (PX0 - 0.2, PY0 - 0.4, PBOT - 1.0), (PX1 + 0.2, PY1 + 0.4, PBOT), RK, 0.0)
    for yy, sgn in ((PY0, -1), (PY1, 1)):
        for a, b in ((PX0, -BW - 0.6), (BW + 0.6, PX1)):
            x, i = a, 0
            while x < b - 0.5:
                x2 = min(b, x + (4.6 if i % 2 else 5.4))
                y0_, y1_ = (yy - 0.7, yy + 0.9) if sgn < 0 else (yy - 0.9, yy + 0.7)
                abox(mb, (x + 0.08, y0_, PBOT - 0.3), (x2 - 0.08, y1_, ZF + 1.0), RUIN, 0.0,
                     cuts=[((0, 1 if sgn < 0 else -1, 1), 0.45 if i % 3 == 0 else 0.2), ((0, sgn, 1), 0.12)])
                x, i = x2, i + 1
    for s in (-1, 1):                                                   # cabeceiras do rio junto das paredes
        x0_ = s * PX1
        yy, i = PY0 - 0.7, 0
        while yy < PY1 + 0.7:
            y2 = min(PY1 + 0.7, yy + 4.9)
            abox(mb, (x0_ - 0.9, yy + 0.08, PBOT - 0.3), (x0_ + 0.9, y2 - 0.08, ZF + 1.0), RUIN, 0.0,
                 cuts=[((-s, 0, 1), 0.3), ((s, 0, 1), 0.12)])
            yy, i = y2, i + 1
        col_box2("SG_CaveKerb", (x0_ - 0.9, PY0, PBOT), (x0_ + 0.9, PY1, ZF + 1.0))
    # estalagmites SO junto das paredes (fora das rotas), com colisao do grupo
    for gi, (gx, gy, cnt) in enumerate(STALAG):
        for k in range(cnt):
            a = 2.1 * k + gi
            rr = 0.0 if k == 0 else 2.3 + 0.8 * _h(gi, k, 1)
            x, y = gx + rr * math.cos(a), gy + rr * math.sin(a)
            h = (7.5 if k == 0 else 2.8 + 3.0 * _h(gi, k, 2))
            r = (1.8 if k == 0 else 0.8 + 0.5 * _h(gi, k, 3))

            def ring(rad, z, x=x, y=y, ph=a):
                return [Vector((x + rad * math.cos(ph + q * math.pi / 3), y + rad * math.sin(ph + q * math.pi / 3), z))
                        for q in range(6)]
            hull(mb, ring(r, ZF - 0.3) + ring(r * 0.6, ZF + h * 0.4), RKD)
            hull(mb, ring(r * 0.62, ZF + h * 0.38) + [Vector((x - 0.2 * r, y + 0.2 * r, ZF + h))], RKD)
        col_box2("SG_CaveStalag", (gx - 3.2, gy - 3.2, ZF), (gx + 3.2, gy + 3.2, ZF + 6.0))
    return npl


def bridge():
    """ponte de pedra do eixo: calcada sobre o rio (corpo de cantaria antiga), talha-mares, guardas de pedra com rufo e
    4 marcos (os 2 do norte com tocha de ferro)"""
    mb = smb()
    ya, yb = PY0 - 1.0, PY1 + 1.0
    abox(mb, (-BW - 0.6, ya, PBOT - 0.4), (BW + 0.6, yb, ZF - 0.5), RUIN, 0.0)
    for s in (-1, 1):
        for yc in (PY0 + 6.0, (PY0 + PY1) / 2, PY1 - 6.0):              # talha-mares (proa em cunha)
            hull(mb, [Vector((s * (BW + 0.5), yc + dy, z)) for dy in (-1.6, 1.6) for z in (PBOT - 0.4, ZF - 0.9)] +
                 [Vector((s * (BW + 2.4), yc, z)) for z in (PBOT - 0.4, ZF - 1.3)], RUIN)
        # guarda: blocos + rufo (a guarda invisivel do sg_col esta em x +-(BW + 0,5))
        x0_, x1_ = (s * BW, s * (BW + 1.1)) if s > 0 else (s * (BW + 1.1), s * BW)
        y, i = PY0 + 0.4, 0
        while y < PY1 - 0.5:
            y2 = min(PY1 - 0.4, y + 3.1)
            abox(mb, (x0_ + 0.05, y + 0.06, ZF - 0.4), (x1_ - 0.05, y2 - 0.06, ZF + 1.2), RUIN, 0.0,
                 cuts=[((0, 1, 1), 0.1), ((0, -1, 1), 0.1)])
            y, i = y2, i + 1
        abox(mb, (x0_ - 0.12, PY0 + 0.3, ZF + 1.2), (x1_ + 0.12, PY1 - 0.3, ZF + 1.62), OB, 0.08)
        for yy in (PY0 - 0.6, PY1 + 0.6):                               # marcos nas cabeceiras
            abox(mb, (x0_ - 0.25, yy - 0.95, ZF - 0.4), (x1_ + 0.25, yy + 0.95, ZF + 2.6), RUIN, 0.1)
            abox(mb, (x0_ - 0.45, yy - 1.15, ZF + 2.6), (x1_ + 0.45, yy + 1.15, ZF + 3.05), OB, 0.08)
            if yy > PY1:
                torch_cup(mb, ((x0_ + x1_) / 2, yy + 1.15, ZF + 1.8), (0.0, 1.0), 1.0)
# ==================================================================== NAVE: pilares antigos e arcos transversais
def nave():
    mb = smb()
    spring = 22.0
    for y in NAVE_Y:
        for s in (-1, 1):
            x = s * NAVE_X
            abox(mb, (x - 3.7, y - 3.7, ZF - 0.3), (x + 3.7, y + 3.7, ZF + 1.4), OB, 0.14)
            abox(mb, (x - 3.2, y - 3.2, ZF + 1.4), (x + 3.2, y + 3.2, ZF + 2.4), RUIN, 0.1,
                 cuts=[((1, 0, 1), 0.3), ((-1, 0, 1), 0.3), ((0, 1, 1), 0.3), ((0, -1, 1), 0.3)])
            z, i = ZF + 2.4, 0
            while z < spring - 2.3:                                     # fuste em tambores (fiada alterna 5,0 / 4,7)
                z2 = min(spring - 2.2, z + (4.3 if i % 2 == 0 else 3.9))
                hw_ = 2.5 if i % 2 == 0 else 2.35
                abox(mb, (x - hw_, y - hw_, z), (x + hw_, y + hw_, z2), RUIN, 0.0,
                     cuts=[((1, 1, 0), 0.25), ((1, -1, 0), 0.25), ((-1, 1, 0), 0.25), ((-1, -1, 0), 0.25)])
                z, i = z2, i + 1
            hull(mb, [Vector((x + a * 2.5, y + b * 2.5, spring - 2.2)) for a in (-1, 1) for b in (-1, 1)] +
                 [Vector((x + a * 3.2, y + b * 3.2, spring - 0.8)) for a in (-1, 1) for b in (-1, 1)], RUIN)
            abox(mb, (x - 3.4, y - 3.4, spring - 0.8), (x + 3.4, y + 3.4, spring), OB, 0.1)
            torch_cup(mb, (x - s * 2.5, y, ZF + 9.0), (-s, 0.0), 1.1)
            col_box2("SG_CaveNave", (x - 3.0, y - 3.0, ZF), (x + 3.0, y + 3.0, spring))
        # arco segmental (aduelas com junta aberta) entre os capiteis: embute na abobada
        half, rise = NAVE_X - 2.7, 11.0
        R = (half * half + rise * rise) / (2 * rise)
        zc = spring + rise - R
        a0 = math.atan2(spring - zc, -half)
        a1 = math.atan2(spring - zc, half)
        nv = 11
        for k in range(nv):
            t0, t1 = a0 + (a1 - a0) * k / nv, a0 + (a1 - a0) * (k + 1) / nv
            g = 0.2 / R
            key = k == nv // 2
            ext = (3.9 if key else (2.7 if k % 2 else 3.25))                # extradorso em dente (le a aduela)
            dy = 2.2 + (0.3 if key else 0.0)
            pts = []
            for t in (t0 + g if k else t0, t1 - g if k < nv - 1 else t1):
                for r in (R, R + ext):
                    for yy in (y - dy, y + dy):
                        pts.append(Vector((r * math.cos(t), yy, zc + r * math.sin(t))))
            if k in (0, nv - 1):                                        # a aduela de arranque assenta no abaco
                pts = [Vector((p.x, p.y, max(p.z, spring))) for p in pts]
            tm = (t0 + t1) / 2
            rv = Vector((math.cos(tm), 0.0, math.sin(tm)))
            for sy in (-1.0, 1.0):
                pts = cut(pts, rv + Vector((0.0, sy * 1.2, 0.0)), 0.32)          # quinas vivas chanfradas: a junta le
                pts = cut(pts, -rv + Vector((0.0, sy * 1.2, 0.0)), 0.22)
            hull(mb, pts, RUIN)


# ==================================================================== TORRE DO POCO (abaixo de z 44) e ESCADA CARACOL
# Torre: 16 faces (vertices R 14,3 / 18,3: apotema 14,03 / 17,95), cantaria em fiadas de 6,3 com JUNTA EM V por
# dentro (quem desce ve de perto) e por fora (so na face sul, a que aparece no salao); base rusticada com talude e
# CORNIJA na cota da galeria; janelas em arco nas cotas da ULTIMA VOLTA (a escada aparece de dentro do salao); o arco de
# saida (12 x 18) no sul; cinta de misulas onde a torre entra na abobada. Acima de 44 a casca e do sg_castle (1a).
# Escada: 59 degraus em cunha de pedra (piso centrado na rampa helicoidal da onda 0: o pe fica a +-0,4 do piso),
# focinho, espelho de 0,8 e intradorso helicoidal; patamares; NUCLEO esculpido (fuste com aneis e a moldura helicoidal
# que acompanha a descida); corrimao de ferro no lado da parede com misulas; tochas de ferro a cada 1/4 de volta.
TR_IN, TR_OUT = 14.3, 18.3
SECW = 22.5
A0, A1, NST = L.SPIRAL_A0, L.SPIRAL_A1, L.SPIRAL_N
DA = (A1 - A0) / NST
CZ = [6.3 + 6.3 * k for k in range(6)] + [44.0]      # fiadas da parede (6,3 .. 44)
Z_CORBEL = 35.0                                        # cinta de misulas (a torre entra na abobada acima)
JCH = 0.2                                             # junta em V


def zr(a):
    """cota do piso da escada (linha da rampa) no parametro a (graus, A0..A1)"""
    return L.SPIRAL_TOP_Z - L.SPIRAL_RISE * (a - A0) / DA


def pr(a, rv):
    """raio do 16-gono (vertices em multiplos de 22,5) na direcao a"""
    d = ((a - SECW / 2) % SECW) - SECW / 2
    return rv * math.cos(math.radians(SECW / 2)) / math.cos(math.radians(d))


def tp(a, r, z):
    t = math.radians(a)
    return Vector((TC[0] + r * math.cos(t), TC[1] + r * math.sin(t), z))


def tvis(a):
    a %= 360.0
    return a >= 156.0 or a <= 24.0                    # metade sul (a norte fica na rocha)


def stair_params(th):
    th %= 360.0
    return [p for p in (th - 360.0, th, th + 360.0) if A0 <= p <= A1]


def tower_openings():
    """(centro, meia-abertura em graus, peitoril, arranque, flecha, tipo)"""
    ops = []
    h = 20.0
    while pr(270.0 - h, TR_IN) * math.sin(math.radians(h)) < 6.35:
        h += 0.25
    ops.append((270.0, h, CZ[0], ZG + L.SECRET_ARCH[1] - 6.3, 6.3, "exit"))
    for c in (190.0, 226.0, 321.0):
        sills, ceils = [], []
        a = c - 12.5
        while a <= c + 12.5 + 1e-6:
            ps = sorted(stair_params(a))
            lo = ps[-1]                                            # a passagem mais baixa da escada neste angulo
            if zr(lo) > ZG + 12.0:                                 # vao livre embaixo dela: janela ABAIXO
                sills.append(ZG + 1.8)
                ceils.append(zr(lo) - 1.9)
            else:                                                  # janela ACIMA da ultima volta
                sills.append(zr(lo) + 1.3)
                ceils.append(zr(ps[-2]) - 1.9 if len(ps) > 1 else 40.0)
            a += 2.5
        sill = max(sills)
        crown = min(min(ceils) - 1.0, Z_CORBEL - 2.6)
        rise = 3.9
        ops.append((c, 12.5, sill, crown - rise, rise, "win"))
    return ops


def _op_at(ops, a):
    for o in ops:
        if o[0] - o[1] < a < o[0] + o[1]:
            return o
    return None


def _op_top(o, a):
    c, h, sill, spring, rise, kind = o
    u = (a - c) / h
    return spring + rise * math.sqrt(max(0.0, 1.0 - u * u))


def tower_piece(mb, a0, a1, zb0, zb1, zt0, zt1, chb, cht, outer_detail, m=CS):
    """pedaco da parede entre os angulos a0, a1; base zb (em a0, a1), topo zt; junta em V (chb/cht) nas fiadas"""
    pts = []
    for a, zb, zt in ((a0, zb0, zt0), (a1, zb1, zt1)):
        ri, ro = pr(a, TR_IN), pr(a, TR_OUT)
        for r, sgn, det in ((ri, 1.0, True), (ro, -1.0, outer_detail)):
            if cht and det:
                pts += [tp(a, r + sgn * JCH, zt), tp(a, r, zt - JCH)]
            else:
                pts.append(tp(a, r, zt))
            if chb and det:
                pts += [tp(a, r + sgn * JCH, zb), tp(a, r, zb + JCH)]
            else:
                pts.append(tp(a, r, zb))
    hull(mb, pts, m)


def tower(mb, ops):
    # ---- base rusticada (talude, 3 fiadas de almofada e cornija na cota da galeria)
    for k in range(16):
        a0, a1 = SECW * k, SECW * (k + 1)
        am = (a0 + a1) / 2
        if not tvis(am):
            hull(mb, [tp(a, r, z) for a in (a0, a1) for r in (6.0, pr(a, TR_OUT + 0.5)) for z in (ZF - 0.3, CZ[0])], CS)
            continue
        hull(mb, [tp(a, r, z) for a in (a0, a1) for r, z in ((6.0, ZF - 0.3), (pr(a, TR_OUT + 1.5), ZF - 0.3),
                                                             (pr(a, TR_OUT + 1.5), ZF + 1.1), (pr(a, TR_OUT + 0.8), ZF + 2.3),
                                                             (6.0, ZF + 2.3))], OB)
        for z0, z1 in ((ZF + 2.3, ZF + 7.1), (ZF + 7.1, ZF + 11.9), (ZF + 11.9, ZF + 16.6)):
            pts = []
            for a in (a0 + 0.35, a1 - 0.35):
                ro = pr(a, TR_OUT + 0.55)
                pts += [tp(a, 6.0, z0), tp(a, 6.0, z1), tp(a, ro - 0.45, z0), tp(a, ro, z0 + 0.45), tp(a, ro, z1 - 0.45),
                        tp(a, ro - 0.45, z1)]
            hull(mb, pts, CS)
            hull(mb, [tp(a, r, z) for a in (a0, a1) for r in (6.4, pr(a, TR_OUT + 0.1)) for z in (z0 + 0.3, z1 - 0.3)],
                 CS)
        hull(mb, [tp(a, r, z) for a in (a0, a1) for r, z in ((6.0, ZF + 16.6), (pr(a, TR_OUT + 0.6), ZF + 16.6),
                                                             (pr(a, TR_OUT + 1.2), ZF + 17.4), (pr(a, TR_OUT + 1.4), ZF + 18.0),
                                                             (pr(a, TR_OUT + 1.4), CZ[0]), (6.0, CZ[0]))], RUIN)
    # ---- parede em fiadas, recortada pelas aberturas (arcos por segmentos de ~4 graus)
    br = {SECW * k for k in range(17)}
    for c, h, *_ in ops:
        n = max(2, int(math.ceil(2 * h / 5.0)))
        br |= {c - h + 2 * h * i / n for i in range(n + 1)}
    br = sorted(b for b in br if -1e-6 <= b <= 360.0 + 1e-6)
    npc = 0
    for a0, a1 in zip(br, br[1:]):
        if a1 - a0 < 0.05:
            continue
        am = (a0 + a1) / 2
        vis = tvis(am)
        o = _op_at(ops, am)
        for ci, (z0, z1) in enumerate(zip(CZ, CZ[1:])):
            chb, cht = ci > 0, z1 < 43.9
            if not o:
                tower_piece(mb, a0, a1, z0, z0, z1, z1, chb, cht, vis)
                npc += 1
                continue
            c, h, sill, spring, rise, kind = o
            if sill > z0 + 0.05:
                tower_piece(mb, a0, a1, z0, z0, min(z1, sill), min(z1, sill), chb, cht and sill >= z1, vis)
                npc += 1
            t0, t1 = _op_top(o, a0), _op_top(o, a1)
            if min(t0, t1) < z1 - 0.05:
                tower_piece(mb, a0, a1, max(z0, t0), max(z0, t1), z1, z1, chb and max(t0, t1) <= z0, cht, vis)
                npc += 1
    # ---- molduras das aberturas (aduelas, ombreiras em cunhal e peitoril; 0,3 salientes e 0,15 para dentro do vao)
    for o in ops:
        c, h, sill, spring, rise, kind = o
        R_ = TR_OUT
        ai = math.degrees(0.15 / R_)
        ae = math.degrees(1.35 / R_)
        nv = 9 if kind == "exit" else 7
        for k in range(nv):
            q0, q1 = math.pi * k / nv + 0.012, math.pi * (k + 1) / nv - 0.012
            pts = []
            for q in (q0, q1):
                for hh, rr in ((h - ai, rise - 0.15), (h + ae + (0.25 if k == nv // 2 else 0.0),
                                                        rise + 1.35 + (0.35 if k == nv // 2 else 0.0))):
                    a = c + hh * math.cos(q)
                    z = spring + rr * math.sin(q)
                    for r in (pr(a, R_) - 0.7, pr(a, R_) + 0.3):
                        pts.append(tp(a, r, z))
            hull(mb, pts, RUIN)
        z, i = (sill + 0.12 if kind == "win" else CZ[0]), 0
        while z < spring - 0.4:                                   # ombreiras em cunhal alternado
            z2 = min(spring, z + (2.4 if i % 2 == 0 else 1.9))
            wq = math.degrees((1.5 if i % 2 == 0 else 0.95) / R_)
            for s in (-1, 1):
                aa, ab_ = c + s * (h - ai), c + s * (h + wq)
                hull(mb, [tp(a, r, zz) for a in (aa, ab_) for r in (pr(a, R_) - 0.7, pr(a, R_) + 0.25)
                          for zz in (z + 0.06, z2 - 0.06)], RUIN)
            z, i = z2, i + 1
        if kind == "win":
            aa, ab_ = c - h - 1.2, c + h + 1.2
            hull(mb, [tp(a, r, zz) for a in (aa, ab_) for r in (pr(a, TR_IN) + 0.2, pr(a, R_) + 0.45)
                      for zz in (sill - 0.6, sill + 0.12)], RUIN)
    # ---- cinta de misulas onde a torre entra na rocha
    zc0 = Z_CORBEL
    for k in range(16):
        a0, a1 = SECW * k, SECW * (k + 1)
        if not tvis((a0 + a1) / 2):
            continue
        hull(mb, [tp(a, r, z) for a in (a0, a1) for r in (pr(a, TR_OUT - 0.5), pr(a, TR_OUT + 1.2))
                  for z in (zc0, zc0 + 1.3)], RUIN)
        am = a0 + SECW / 2
        hull(mb, [tp(am + s * 2.2, r, z) for s in (-1, 1) for r, z in ((pr(am, TR_OUT) - 0.2, zc0 - 2.6),
                                                                       (pr(am, TR_OUT) - 0.2, zc0),
                                                                       (pr(am, TR_OUT) + 1.0, zc0))], RUIN)
    return npc


def spiral_stairs(ms, mi, ops):
    """degraus, patamares, piso do fundo, nucleo esculpido, corrimao de ferro, misulas, tochas e guardas das janelas.
    ms = pedra (degraus, patamares, nucleo); mi = ferro e chamas"""
    rn, rw = 2.6, 14.25
    T = 1.5
    for k in range(1, NST):
        ac = A0 + k * DA
        zt = L.SPIRAL_TOP_Z - L.SPIRAL_RISE * k
        ab, af = ac - DA / 2, ac + DA / 2
        pts = []
        for r in (rn, rw):
            dn = math.degrees(0.16 / r)
            pts += [tp(ab - 0.3, r, zt), tp(af + dn, r, zt), tp(af + dn, r, zt - 0.16), tp(af, r, zt - 0.34),
                    tp(af, r, zt - 0.4 - T), tp(ab - 0.3, r, zt + 0.4 - T)]
        hull(ms, pts, BL)
    # patamar de topo (setor do arco secreto) e piso do fundo do poco (lajes em cunha, junta 0,35 abaixo)
    la0, la1 = L.SPIRAL_LANDING[0], A0 + DA / 2
    n = 5
    for i in range(n):
        a0, a1 = la0 + (la1 - la0) * i / n, la0 + (la1 - la0) * (i + 1) / n
        hull(ms, [tp(a, r, z) for a in (a0 + 0.2, a1 - 0.2) for r in (rn, rw) for z in (L.SPIRAL_TOP_Z - 1.6,
                                                                                       L.SPIRAL_TOP_Z)], FL)
    hull(ms, [tp(22.5 * i, pr(22.5 * i, TR_IN + 0.3), z) for i in range(16) for z in (ZG - 1.2, ZG - 0.35)], BL)
    for i in range(16):
        a0, a1 = 22.5 * i + 0.4, 22.5 * (i + 1) - 0.4
        hull(ms, [tp(a, r, z) for a in (a0, a1) for r in (rn, pr(a, TR_IN) - 0.05) for z in (ZG - 0.35, ZG)], FL)
    # soleira da saida (so ate a face interna: nada coplanar com o piso do poco)
    abox(ms, (-6.25, TC[1] - 18.0 + 0.05, ZG - 0.9), (6.25, TC[1] - TR_IN * math.cos(math.radians(11.25)) - 0.05, ZG),
         OB, 0.06)
    # NUCLEO: fuste octogonal com base, aneis a cada 12 e capitel; moldura helicoidal esculpida acompanhando a descida
    z_top = L.SPIRAL_TOP_Z + 20.0
    prof = [(4.2, ZG - 0.05), (4.2, ZG + 0.7), (3.7, ZG + 1.2), (3.2, ZG + 1.7), (3.0, ZG + 1.8)]
    zb_ = ZG + 12.0
    while zb_ < z_top - 4.0:
        prof += [(3.0, zb_ - 0.35), (3.35, zb_ - 0.1), (3.35, zb_ + 0.35), (3.0, zb_ + 0.6)]
        zb_ += 12.0
    prof += [(3.0, z_top - 2.8), (3.5, z_top - 2.2), (4.3, z_top - 1.0), (4.3, z_top), (0.0, z_top)]
    EM._lathe(ms, (TC[0], TC[1], 0.0), prof, RUIN, 8, math.pi / 8, caps=(True, False))
    samples = [A0 + DA * 0.5 + (A1 - A0 - DA) * i / 84 for i in range(85)]
    band = [tp(a, 3.28, zr(a) + 2.9) for a in samples]
    ms.sweep(band, [(-0.22, -0.28), (0.22, -0.28), (0.22, 0.28), (-0.22, 0.28)], RUIN, True, None)
    # CORRIMAO de ferro no lado da parede (para antes do arco de saida; nas janelas vira guarda)
    rail_s = [a for a in samples if a <= 600.0]
    rail = [tp(a, 13.65, zr(a) + 3.1) for a in rail_s]
    mi.sweep(rail, [(-0.16, -0.12), (0.16, -0.12), (0.16, 0.12), (-0.16, 0.12)], BI, True, None)
    for a in rail_s[::4]:
        th = a % 360.0
        z = zr(a)
        o = _op_at(ops, th)
        if o and o[2] - 0.5 < z + 3.1 < _op_top(o, th) + 0.5:
            bar(mi, tp(a, 13.65, z - 0.1), tp(a, 13.65, z + 3.0), 0.16, 0.16, BI)         # montante na janela
        else:
            bar(mi, tp(a, pr(th, TR_IN) + 0.1, z + 2.55), tp(a, 13.65, z + 3.0), 0.14, 0.14, BI)
            obox3(mi, tp(a, pr(th, TR_IN) - 0.03, z + 2.5), Vector((math.cos(math.radians(a)), math.sin(math.radians(a)), 0.0)),
                  Vector((-math.sin(math.radians(a)), math.cos(math.radians(a)), 0.0)), UPZ, 0.1, 0.5, 0.8, BI)
    a_end = rail_s[-1]
    bar(mi, tp(a_end, 13.65, ZG - 0.1), tp(a_end, 13.65, zr(a_end) + 3.4), 0.22, 0.22, BI)
    # guarda das janelas (2 travessas entre as ombreiras, na face interna)
    for c, h, sill, spring, rise, kind in ops:
        if kind != "win":
            continue
        for zz in (sill + 1.2, sill + 2.5):
            pts = [tp(c - h + 2 * h * i / 6, pr(c - h + 2 * h * i / 6, TR_IN) + 0.3, zz) for i in range(7)]
            mi.sweep(pts, [(-0.1, -0.1), (0.1, -0.1), (0.1, 0.1), (-0.1, 0.1)], BI, True, None)
        for i in (1, 3, 5):
            a = c - h + 2 * h * i / 6
            bar(mi, tp(a, pr(a, TR_IN) + 0.3, sill), tp(a, pr(a, TR_IN) + 0.3, sill + 2.6), 0.14, 0.14, BI)
    # TOCHAS de ferro a cada 1/4 de volta (na parede, fora das aberturas)
    nt = 0
    for j in range(8):
        p = A0 + 45.0 + 90.0 * j
        th = p % 360.0
        z = zr(p) + 5.0
        o = _op_at(ops, th)
        if o and o[2] - 1.5 < z < _op_top(o, th) + 2.0:
            continue
        r = pr(th, TR_IN)
        torch_cup(mi, tp(th, r, z), (-math.cos(math.radians(th)), -math.sin(math.radians(th))), 1.0)
        nt += 1
    return nt


def tower_and_spiral():
    ops = tower_openings()
    mt = smb()
    npc = tower(mt, ops)
    ms = smb()
    mi = smb()
    nt = spiral_stairs(ms, mi, ops)
    # colisao da BASE macica da torre (fundo do poco = piso a 6,6) e das ombreiras da saida
    ngon_col("SG_CaveTower", TC[0], TC[1], 16, TR_OUT + 1.4, ZF - 0.5, ZG, rot0=0.0)
    for s in (-1, 1):
        col_box2("SG_CaveTowerJamb", (s * 6.3, TC[1] - TR_OUT - 1.5, ZG), (s * 10.5, TC[1] - TR_IN + 0.2, ZG + 18.0))
    print("CAVE torre: aberturas %s pedacos %d tochas %d" % ([(o[0], round(o[2], 1), round(o[3] + o[4], 1)) for o in ops],
                                                           npc, nt))
    return ops


def preview_shaft():
    """SO PARA A PREVIA quando o castelo 2x ainda e blockout: a casca do poco acima de 44 (dono sg_castle) para o
    render do topo da escada ler. PREVIEW_ nao vai para o export."""
    if B.zone_ready("castle"):
        return
    mb = MB("PREVIEW_CaveShaftAbove", "00_REFERENCE", random.Random(969), detail="far", floor=-999)
    ztp = L.SPIRAL_TOP_Z
    aw = 26.5
    for k in range(32):
        a0, a1 = 11.25 * k, 11.25 * (k + 1)
        am = (a0 + a1) / 2
        spans = [(44.0, ztp + 20.0)]
        if abs(((am - 270.0 + 180.0) % 360.0) - 180.0) < aw:
            spans = [(44.0, ztp - 0.2), (ztp + L.SECRET_ARCH[1], ztp + 20.0)]
        for z0, z1 in spans:
            hull(mb, [tp(a, r, z) for a in (a0, a1) for r in (pr(a, TR_IN), pr(a, TR_OUT)) for z in (z0, z1)], CS)
    mb.finish()


# ==================================================================== ferro: guarda-corpo (montantes + travessas corridas)
def iron_rail(mb, pts, z, h=3.2, step=4.0, pickets=0.0):
    """guarda de ferro sobre o piso z ao longo da polilinha pts (xy): montantes a cada ~step (0,1 enterrados), 3
    travessas CORRIDAS por trecho reto (sem emenda por vao) e, opcional, balaustres finos a cada 'pickets'"""
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        a, b = Vector((ax, ay, 0.0)), Vector((bx, by, 0.0))
        ln = (b - a).length
        if ln < 0.3:
            continue
        d = (b - a) / ln
        n = max(1, int(round(ln / step)))
        for i in range(n + 1):
            p = a + d * (ln * i / n)
            obox3(mb, Vector((p.x, p.y, z + (h + 0.35) / 2 - 0.1)), d, Vector((-d.y, d.x, 0.0)), UPZ, 0.3, 0.3,
                  h + 0.45, BI)
        for zz, hh in (((z + h, 0.22), (z + h * 0.52, 0.14), (z + 0.4, 0.14)) if pickets else ((z + h, 0.22), (z + h * 0.5, 0.14))):
            obox3(mb, Vector(((ax + bx) / 2, (ay + by) / 2, zz)), d, Vector((-d.y, d.x, 0.0)), UPZ, ln, 0.26 if hh > 0.2
                  else 0.14, hh, BI)
        if pickets > 0:
            m = int(ln / pickets)
            for i in range(1, m):
                if i % max(1, int(round(step / pickets))) == 0:
                    continue
                p = a + d * (ln * i / m)
                obox3(mb, Vector((p.x, p.y, z + 0.4 + (h - 0.4) / 2)), d, Vector((-d.y, d.x, 0.0)), UPZ, 0.12, 0.12,
                      h - 0.4, BI)


def iron_lantern(mb, base, h=7.0):
    """poste de ferro com lanterna de gaiola (4 montantes, tampa, chama em gota): so ferro + chama"""
    x, y, z = base
    EM._lathe(mb, (x, y, z), [(0.55, 0.0), (0.55, 0.25), (0.3, 0.45), (0.18, 1.2), (0.14, h - 1.9), (0.22, h - 1.75),
                              (0.14, h - 1.6)], BI, 6, caps=(False, True))
    zb = z + h - 1.6
    EM._lathe(mb, (x, y, zb), [(0.1, 0.0), (0.62, 0.18), (0.55, 0.28)], BI, 6, caps=(True, False))
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        bar(mb, (x + 0.52 * math.cos(a), y + 0.52 * math.sin(a), zb + 0.2),
            (x + 0.52 * math.cos(a), y + 0.52 * math.sin(a), zb + 1.55), 0.1, 0.1, BI)
    EM._lathe(mb, (x, y, zb + 1.5), [(0.7, 0.0), (0.7, 0.1), (0.3, 0.55), (0.12, 0.8), (0.0, 1.05)], BI, 4, math.pi / 4)
    EM._lathe(mb, (x, y, zb + 0.35), [(0.0, 0.0), (0.26, 0.28), (0.14, 0.7), (0.0, 1.0)], GLW, 5)
    return Vector((x, y, zb + 0.9))


# ==================================================================== GALERIA, arcada e ESCADARIA
GY0 = L.CAVE_GALLERY[1]                          # 274 (borda sul da galeria)
GY1 = TC[1] - L.SPIRAL_R_OUT                      # 304 (encosta no pe do poco)
ARC_X = (12.5, 32.0, 52.0, 72.0)                 # pilares da arcada sob a borda da galeria
BACK_X = (40.0, 72.0)                            # pilares do fundo (y 302..304)


def seg_arch_pts(xa, xb, spring, rise, ext, y0, y1, k, n):
    half = (xb - xa) / 2
    R = (half * half + rise * rise) / (2 * rise)
    zc = spring + rise - R
    xc = (xa + xb) / 2
    t0 = math.atan2(spring - zc, -half)
    t1 = math.atan2(spring - zc, half)
    q0, q1 = t0 + (t1 - t0) * k / n, t0 + (t1 - t0) * (k + 1) / n
    g = 0.12 / R
    q0, q1 = (q0 + g if k else q0), (q1 - g if k < n - 1 else q1)
    ex = ext + (0.35 if k == n // 2 else (0.0 if k % 2 else 0.3))
    pts = [Vector((xc + r * math.cos(q), y, zc + r * math.sin(q))) for q in (q0, q1) for r in (R, R + ex)
           for y in (y0, y1)]
    qm = (q0 + q1) / 2
    rv = Vector((math.cos(qm), 0.0, math.sin(qm)))
    pts = cut(pts, rv + Vector((0.0, -1.2, 0.0)), 0.22)
    pts = cut(pts, -rv + Vector((0.0, -1.2, 0.0)), 0.16)
    return pts, (xc, zc, R)


def gallery():
    mg = smb()
    zb = ZG - 1.5
    # corpo da laje e lajes de 2 tons em cima (junta 0,35 abaixo do piso)
    abox(mg, (X0 - 0.5, GY0, zb), (X1 + 0.5, GY1, ZG - 0.35), BL, 0.0)
    y, r = GY0, 0
    while y < GY1 - 0.2:
        y2 = min(GY1, y + 6.0)
        x, k = X0 - 0.5 - (3.75 if r % 2 else 0.0), 0
        while x < X1 + 0.5:
            x2 = min(X1 + 0.5, x + 7.5)
            xa = max(x, X0 - 0.5)
            if x2 - xa > 0.6:
                abox(mg, (xa + 0.1, y + 0.1, ZG - 0.35), (x2 - 0.1, y2 - 0.1, ZG), MBK if (k + r) % 4 == 0 else FL, 0.0)
            x, k = x2, k + 1
        y, r = y2, r + 1
    # cornija da borda sul e do fundo (sob a guarda)
    for xa, xb in ((X0, -8.7), (8.7, X1)):
        hull(mg, [Vector((x, y_, z)) for x in (xa, xb) for y_, z in ((GY0 - 0.02, ZG - 0.36), (GY0 - 0.65, ZG - 0.36),
                                                                    (GY0 - 0.65, ZG - 0.9), (GY0 - 0.2, ZG - 1.4),
                                                                    (GY0 - 0.02, ZG - 1.7))], RUIN)
    for xa, xb in ((X0, -6.3), (6.3, X1)):
        hull(mg, [Vector((x, y_, z)) for x in (xa, xb) for y_, z in ((GY1 + 0.02, ZG - 0.36), (GY1 + 0.55, ZG - 0.36),
                                                                    (GY1 + 0.55, ZG - 0.9), (GY1 + 0.02, ZG - 1.6))], RUIN)
    # ARCADA sob a borda: pilares com soco e imposta, arcos segmentais de aduelas e timpanos ate a laje
    ya, yb = GY0 + 0.3, GY0 + 3.7
    xs = []
    for x in ARC_X:
        xs += [-x, x]
    xs = sorted(xs)
    for x in xs:
        abox(mg, (x - 2.0, ya - 0.3, ZF - 0.3), (x + 2.0, yb + 0.3, ZF + 1.3), OB, 0.0, cuts=[((0, -1, 1), 0.3)])
        z, i = ZF + 1.3, 0
        while z < -2.4:
            z2 = min(-2.3, z + 5.3)
            abox(mg, (x - 1.5, ya, z), (x + 1.5, yb, z2), RUIN, 0.0, cuts=[((0, -1, 1), 0.16), ((0, -1, -1), 0.16)])
            z, i = z2, i + 1
        abox(mg, (x - 1.9, ya - 0.25, -2.3), (x + 1.9, yb + 0.25, -1.5), OB, 0.0, cuts=[((0, -1, -1), 0.3)])
        col_box2("SG_CaveArcade", (x - 1.6, ya, ZF), (x + 1.6, yb, zb))
    spans = [(-X1 + 0.6, xs[0] - 1.5)] + [(a + 1.5, b - 1.5) for a, b in zip(xs, xs[1:])] + [(xs[-1] + 1.5, X1 - 0.6)]
    for xa, xb in spans:
        span = xb - xa
        rise = min(4.7, span * 0.3)
        nv = 9 if span > 18 else 7
        for k in range(nv):
            pts, (xc, zc, R) = seg_arch_pts(xa, xb, -1.5, rise, 1.3, ya, yb, k, nv)
            hull(mg, pts, RUIN)
        for k in range(5):                                                        # timpano ate a laje
            x0_, x1_ = xa + span * k / 5, xa + span * (k + 1) / 5
            zz = [zc + math.sqrt(max(0.0, (R + 1.3) ** 2 - (xx - xc) ** 2)) - 0.2 for xx in (x0_, x1_)]
            if min(zz) >= zb - 0.05:
                continue
            hull(mg, [Vector((x0_, y_, max(-1.5, zz[0]))) for y_ in (ya + 0.25, yb - 0.25)] +
                 [Vector((x1_, y_, max(-1.5, zz[1]))) for y_ in (ya + 0.25, yb - 0.25)] +
                 [Vector((xx, y_, zb)) for xx in (x0_, x1_) for y_ in (ya + 0.25, yb - 0.25)], BL)
    for x in BACK_X:
        for s in (-1, 1):
            xx = s * x
            abox(mg, (xx - 1.8, GY1 - 2.1, ZF - 0.3), (xx + 1.8, GY1 + 0.3, ZF + 1.3), OB, 0.0, cuts=[((0, -1, 1), 0.3)])
            abox(mg, (xx - 1.4, GY1 - 1.8, ZF + 1.3), (xx + 1.4, GY1, zb), RUIN, 0.0,
                 cuts=[((1, -1, 0), 0.2), ((-1, -1, 0), 0.2)])
            col_box2("SG_CaveArcade", (xx - 1.5, GY1 - 1.8, ZF), (xx + 1.5, GY1, zb))
    # guardas de ferro (borda sul com balaustres: a vista do "uau" passa por ela; fundo e passarelas: montantes)
    cw = L.CAVE_CATWALKS
    sw = L.CAVE_STAIR_W / 2 + 0.6
    iron_rail(mg, [(cw[0][2] + 0.3, GY0 + 0.35), (-sw - 1.0, GY0 + 0.35)], ZG, 3.2, 3.0)
    iron_rail(mg, [(sw + 1.0, GY0 + 0.35), (cw[1][0] - 0.3, GY0 + 0.35)], ZG, 3.2, 3.0)
    iron_rail(mg, [(X0 + 0.6, GY1 - 0.35), (-6.4, GY1 - 0.35)], ZG, 3.2, 5.6)
    iron_rail(mg, [(6.4, GY1 - 0.35), (X1 - 0.6, GY1 - 0.35)], ZG, 3.2, 5.6)
    # lanterna da galeria (a luz L_SGCave_Gallery): poste de ferro da ordem no eixo, ao lado da saida da torre
    iron_lantern(mg, (-9.5, GY1 - 3.2, ZG), 7.5)
    col_box2("SG_CaveProp", (-10.1, GY1 - 3.8, ZG), (-8.9, GY1 - 2.6, ZG + 7.0))
def grand_stair():
    """escadaria de 24 (2 lances de 12, patamar de 6): degraus de pedra com focinho em 3 pecas desencontradas,
    massa cheia ate o piso, guardas de pedra inclinadas com rufo de obsidiana e dados nas pontas"""
    mb = smb()
    w = L.CAVE_STAIR_W / 2
    TH, NOSE = 0.26, 0.12
    lx0, ly0, lx1, ly1, lz = L.CAVE_LANDING
    for fi, (nm, foot, n, rise, tread) in enumerate(L.CAVE_STAIRS):
        fx, fy, fz = foot
        for i in range(n):
            ztop = fz + rise * (i + 1)
            y0 = fy + tread * i
            abox(mb, (-w, y0, ZF - 0.3), (w, y0 + tread + 0.02, ztop - TH), BL, 0.0)
            cuts = [-w, -w / 3, w / 3, w] if i % 2 == 0 else [-w, -w * 0.62, 0.0, w * 0.62, w]
            for a, b in zip(cuts, cuts[1:]):
                abox(mb, (a + (0.04 if a > -w else 0.0), y0 - NOSE, ztop - TH), (b - (0.04 if b < w else 0.0),
                          y0 + tread + 0.01, ztop), BL, 0.0, cuts=[((0, -1, 1), 0.07)])
        # guardas (a guarda invisivel do sg_col fica em x +-8,6, 1,2 de largura)
        k = rise / tread
        ya, yb = fy - 0.9, fy + tread * n
        for s in (-1, 1):
            xa, xb = (w, w + 1.4) if s > 0 else (-w - 1.4, -w)
            za, zb_ = fz + 3.3 + 0.9 * k * 0.0, fz + rise * n + 3.3
            hull(mb, [Vector((x, y_, z)) for x in (xa, xb) for y_, z in ((ya, ZF - 0.3), (yb, ZF - 0.3),
                                                                        (ya, fz + 2.9), (yb, zb_ - 0.4))], RUIN)
            hull(mb, [Vector((x, y_, z)) for x in (xa - 0.15, xb + 0.15) for y_, z in ((ya - 0.1, fz + 2.85),
                                                                                    (yb + 0.1, zb_ - 0.45))] +
                 [Vector((x, y_, z + 0.45)) for x in (xa - 0.15, xb + 0.15) for y_, z in ((ya - 0.1, fz + 2.85),
                                                                                       (yb + 0.1, zb_ - 0.45))], OB)
            if fi == 0:                                                           # dados no pe da escadaria
                abox(mb, (xa - 0.5, ya - 2.2, ZF - 0.3), (xb + 0.5, ya + 0.1, ZF + 4.4), RUIN, 0.12)
                abox(mb, (xa - 0.7, ya - 2.4, ZF + 4.4), (xb + 0.7, ya + 0.3, ZF + 4.9), OB, 0.08)
                torch_cup(mb, ((xa + xb) / 2, ya - 2.2, ZF + 2.6), (0.0, -1.0), 1.1)
    # patamar
    abox(mb, (lx0, ly0, ZF - 0.3), (lx1, ly1, lz - 0.35), BL, 0.0)
    for i, (a, b) in enumerate(((-w, -w / 2), (-w / 2, 0.0), (0.0, w / 2), (w / 2, w))):
        abox(mb, (a + 0.08, ly0 + 0.08, lz - 0.35), (b - 0.08, ly1 - 0.08, lz), MBK if i in (0, 3) else FL, 0.0)
    for s in (-1, 1):
        xa, xb = (w, w + 1.4) if s > 0 else (-w - 1.4, -w)
        abox(mb, (xa, ly0 - 0.05, ZF - 0.3), (xb, ly1 + 0.05, lz + 2.9), RUIN, 0.1)
        abox(mb, (xa - 0.15, ly0 - 0.1, lz + 2.9), (xb + 0.15, ly1 + 0.1, lz + 3.35), OB, 0.08)
# ==================================================================== PASSARELAS e PONTE SUSPENSA (+ estandartes)
def cloth_banner(mc, mp, x, y, ztop, w=5.0, h=12.5, seed=0):
    """estandarte RASGADO da ordem (so o crescente): pano ondulado com espessura, barra de baixo rasgada em pontas de
    comprimentos diferentes e um rasgo lateral; crescente palido (sem brilho) no terco de cima; verga de ferro"""
    nx, nz = 5, 7
    th = 0.12
    tear = [0.86, 0.97, 0.78, 1.0, 0.9, 0.83]            # comprimento de cada coluna (rasgado)
    tear = tear[seed % 2:] + tear[:seed % 2]
    F, Bk = [], []
    bm = mc.bm
    for i in range(nx + 1):
        u = -w / 2 + w * i / nx
        cF, cB = [], []
        for j in range(nz + 1):
            t = j / nz
            hh = h * (t if j < nz else tear[i])
            if j == nz - 1:
                hh = min(hh, h * tear[i] - 0.4)
            wave = 0.0 if abs(u) < w * 0.3 else 0.22 * math.sin(u * 1.9 + seed) * min(1.0, hh / 3.0)
            cF.append(bm.verts.new((x + u, y + wave + th / 2, ztop - hh)))
            cB.append(bm.verts.new((x + u, y + wave - th / 2, ztop - hh)))
        F.append(cF)
        Bk.append(cB)
    fs = []
    for i in range(nx):
        for j in range(nz):
            fs.append(bm.faces.new((F[i][j], F[i + 1][j], F[i + 1][j + 1], F[i][j + 1])))
            fs.append(bm.faces.new((Bk[i][j + 1], Bk[i + 1][j + 1], Bk[i + 1][j], Bk[i][j])))
    for j in range(nz):
        fs.append(bm.faces.new((F[0][j + 1], Bk[0][j + 1], Bk[0][j], F[0][j])))
        fs.append(bm.faces.new((F[nx][j], Bk[nx][j], Bk[nx][j + 1], F[nx][j + 1])))
    for i in range(nx):
        fs.append(bm.faces.new((F[i][0], Bk[i][0], Bk[i + 1][0], F[i + 1][0])))
        fs.append(bm.faces.new((F[i + 1][nz], Bk[i + 1][nz], Bk[i][nz], F[i][nz])))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    mc._post([v for c in F + Bk for v in c], CL, None, 0, 1)
    crescent(mc, (x, y + th / 2, ztop - h * 0.3), Vector((1, 0, 0)), Vector((0, 0, 1)), Vector((0, 1, 0)), w * 0.3,
             -0.05, 0.1, PALE)
    mp.cyl(0.14, w + 0.9, (x, y, ztop + 0.12), (0, math.pi / 2, 0), m=BI, n=6, bevel=0.0)
    for s in (-1, 1):
        EM._lathe(mp, (x + s * (w / 2 + 0.45), y, ztop + 0.12), [(0.0, -0.25), (0.22, -0.1), (0.2, 0.15), (0.0, 0.3)],
                  BI, 6)


def walkways():
    mw = smb()
    zg = ZG
    hx0, hy0, hx1, hy1 = L.CAVE_HANGING_BRIDGE
    for s in (-1, 1):
        xw, xi = s * X1, s * 80.0                                        # parede / borda interna
        xa, xb = min(xw, xi), max(xw, xi)
        y, k = 150.0, 0
        while y < GY0 - 0.1:
            y2 = min(GY0, y + 6.2)
            if y2 - y > 0.5:
                abox(mw, (xa + 0.1, y + 0.08, zg - 0.78), (xb - 0.1, y2 - 0.08, zg), FL, 0.0,
                     cuts=[((-s, 0, 1), 0.1)])
            # misula de ferro (juntas alternadas): viga sob a laje + escora diagonal ate a rocha
            if k % 2:
                y, k = y2, k + 1
                continue
            obox3(mw, Vector(((xw + xi) / 2, y, zg - 0.95)), Vector((1, 0, 0)), Vector((0, 1, 0)), UPZ, 10.0, 0.45,
                  0.5, BI)
            bar(mw, (xw - s * 0.2, y, zg - 7.2), (xi - s * 0.9, y, zg - 1.1), 0.34, 0.34, BI, up=(0, 1, 0))
            obox3(mw, Vector((xw - s * 0.05, y, zg - 7.2)), Vector((1, 0, 0)), Vector((0, 1, 0)), UPZ, 0.3, 1.0, 1.4, BI)
            y, k = y2, k + 1
        obox3(mw, Vector((xi - s * 0.15, (150.0 + GY0) / 2, zg - 0.95)), Vector((0, 1, 0)), Vector((1, 0, 0)), UPZ,
              GY0 - 150.0, 0.3, 1.3, BI)                                  # longarina da borda
        rx = xi - s * 0.35
        iron_rail(mw, [(xw - s * 0.5, 150.35), (rx, 150.35), (rx, hy0 - 0.3)], zg, 3.2, 5.6)
        iron_rail(mw, [(rx, hy1 + 0.3), (rx, GY0 - 0.2)], zg, 3.2, 5.6)
    # ponte suspensa: tabuas atravessadas sobre 2 longarinas de ferro, travessas, tirantes ate a rocha
    for yy in (hy0 + 0.3, hy1 - 0.3):
        obox3(mw, Vector((0.0, yy, zg - 0.9)), Vector((1, 0, 0)), Vector((0, 1, 0)), UPZ, hx1 - hx0 + 1.0, 0.6, 1.1, BI)
    x, i = hx0, 0
    while x < hx1 - 0.2:
        x2 = min(hx1, x + 3.0)
        abox(mw, (x + 0.1, hy0 + 0.05, zg - 0.35), (x2 - 0.1, hy1 - 0.05, zg), WD, 0.0)
        x, i = x2, i + 1
    for xx in range(-70, 71, 14):
        obox3(mw, Vector((float(xx), (hy0 + hy1) / 2, zg - 1.2)), Vector((0, 1, 0)), Vector((1, 0, 0)), UPZ,
              hy1 - hy0 + 0.6, 0.5, 0.5, BI)
    for xx in (-60.0, -30.0, 0.0, 30.0, 60.0):
        for yy in (hy0 + 0.3, hy1 - 0.3):
            ztop = min(ceil_zb(xx, yy) + 3.0, ZT + 1.0)
            mw.cyl(0.16, ztop - zg, (xx, yy, (zg + ztop) / 2), m=BI, n=6, bevel=0.0)
            EM._lathe(mw, (xx, yy, zg - 0.4), [(0.0, 0.0), (0.34, 0.1), (0.3, 0.55), (0.0, 0.7)], BI, 4)
    iron_rail(mw, [(hx0 + 0.4, hy0 + 0.3), (hx1 - 0.4, hy0 + 0.3)], zg, 3.2, 5.8)
    iron_rail(mw, [(hx0 + 0.4, hy1 - 0.3), (hx1 - 0.4, hy1 - 0.3)], zg, 3.2, 5.8)
    # 4 estandartes rasgados pendurados na face norte da ponte (para quem chega pela galeria)
    for j, xx in enumerate((-60.0, -40.0, 40.0, 60.0)):
        bw_ = 3.8 if j in (1, 2) else 3.2
        cloth_banner(mw, mw, xx, hy1 + 0.75, zg - 1.4, bw_, 12.5 if j in (1, 2) else 10.5, j)
        for s in (-1, 1):                                                # alcas de ferro presas na longarina
            bar(mw, (xx + s * (bw_ / 2 + 0.3), hy1 - 0.1, zg - 0.6), (xx + s * (bw_ / 2 + 0.3), hy1 + 0.75, zg - 1.2),
                0.12, 0.12, BI)
    # correntes de ferro penduradas da ponte (baus, correntes: o ar de base secreta)
    for xx, ln in ((-50.0, 6.0),):
        chain_lite(mw, (xx, hy0 - 0.4, zg - 1.0), (xx, hy0 - 0.4, zg - 1.0 - ln), 0.0)
# ==================================================================== PORTAL DA MASMORRA (o foco do salao)
# nicho monumental: pilares de cantaria antiga (soco de obsidiana, fiadas, imposta), ARCO de 17 aduelas grandes que
# entra na rocha, fecho com o CRESCENTE; timpano de obsidiana no fundo com a MOLDURA DE PEDRA da placa de horario
# (DUNGEON_UI, 22 x 6, a placa do jogo fica DENTRO dela) e, na frente, o ANEL de aduelas com as runas do alfabeto unico
# e o VORTICE (disco escuro + espiral, objeto proprio para girar no jogo) sobre o estrado de 2 degraus.
PPX, PPY = L.CAVE_PORTAL
DX0, DY0, DX1, DY1, DZ = L.CAVE_DAIS
PR_IN = L.CAVE_PORTAL_R
PZC = DZ + PR_IN                                  # centro do anel (o vortice toca o estrado)
ARCH_R, ARCH_SPR, PIER_X = 22.0, 8.9, 22.0
UI_Z, UI_W, UI_H = DZ + 2.0 * PR_IN + 6.0, 22.0, 6.0      # = marcador DUNGEON_UI (centro da placa)
UI_Y = PPY - 1.0
TYMP_Y = UI_Y - 1.6                               # face do timpano (a placa do jogo fica na frente dela)


def portal():
    mp = smb()
    u, v, n = Vector((1.0, 0.0, 0.0)), Vector((0.0, 0.0, 1.0)), Vector((0.0, 1.0, 0.0))
    yf = PPY + 4.5                                                   # face da frente dos pilares e do arco
    yb = Y0 - 1.0                                                    # entra na rocha
    # estrado: corpo, lajes de 2 tons, 2 degraus pelo norte, circulo de runas embutido na frente do anel
    abox(mp, (DX0, DY0, ZF - 0.3), (DX1, DY1, DZ - 0.35), RUIN, 0.0)
    for i, (a, b) in enumerate(zip([DX0 + 4.0 * k for k in range(8)], [DX0 + 4.0 * (k + 1) for k in range(8)])):
        for j, (c0, c1) in enumerate(((DY0, 104.0), (104.0, DY1))):
            abox(mp, (a + 0.1, c0 + 0.1, DZ - 0.35), (b - 0.1, c1 - 0.1, DZ), MBK if (i + j) % 2 else OB, 0.0)
    for k, (y0_, y1_, zt) in enumerate(((DY1, DY1 + 1.8, DZ), (DY1 + 1.8, DY1 + 3.6, DZ - 0.8))):
        abox(mp, (DX0, y0_, ZF - 0.3), (DX1, y1_ + 0.02, zt - 0.26), RUIN, 0.0)
        cuts = [DX0, -8.0, 0.0, 8.0, DX1] if k == 0 else [DX0, -12.0, -4.0, 4.0, 12.0, DX1]
        for a, b in zip(cuts, cuts[1:]):
            abox(mp, (a + 0.05, y0_ - 0.12, zt - 0.26), (b - 0.05, y1_ + 0.01, zt), OB, 0.06)
    rc = Vector((PPX, 109.0, DZ - 0.02))
    for k in range(9):
        a = math.pi / 2 + 2 * math.pi * k / 9
        p = rc + Vector((math.cos(a) * 4.6, math.sin(a) * 4.6, 0.0))
        rune(mp, p, Vector((-math.sin(a), math.cos(a), 0.0)), Vector((math.cos(a), math.sin(a), 0.0)), UPZ, k, 1.3, VG,
             0.14, 0.11)
    # pilares do nicho
    for s in (-1, 1):
        xa, xb = (PIER_X, PIER_X + 5.0) if s > 0 else (-PIER_X - 5.0, -PIER_X)
        abox(mp, (xa - 0.6, yb, ZF - 0.3), (xb + 0.6, yf + 0.6, ZF + 1.8), OB, 0.14)
        z, i = ZF + 1.8, 0
        while z < ARCH_SPR - 1.0:
            z2 = min(ARCH_SPR - 0.9, z + (3.8 if i % 2 == 0 else 3.2))
            abox(mp, (xa, yb, z), (xb, yf, z2), RUIN, 0.2)
            z, i = z2, i + 1
        abox(mp, (xa - 0.5, yb, ARCH_SPR - 0.9), (xb + 0.5, yf + 0.5, ARCH_SPR), OB, 0.12)
        col_box2("SG_CavePortal", (xa - 0.2, Y0 - 2.0, ZF), (xb + 0.2, yf + 0.2, ARCH_SPR))
    # arco de aduelas (entra na rocha por tras) + fecho com o crescente
    nv = 17
    for k in range(nv):
        q0, q1 = math.pi * k / nv + 0.006, math.pi * (k + 1) / nv - 0.006
        key = k == nv // 2
        ext = 3.6 + (0.9 if key else 0.0)
        pts = [Vector((PPX + r * math.cos(q), y_, ARCH_SPR + r * math.sin(q))) for q in (q0, q1)
               for r in (ARCH_R, ARCH_R + ext) for y_ in (yb, yf + (0.5 if key else 0.0))]
        pts = cut(pts, Vector((0.0, 1.0, 0.0)) + Vector((math.cos((q0 + q1) / 2), 0.0, math.sin((q0 + q1) / 2))), 0.3)
        hull(mp, pts, RUIN)
    crescent(mp, (PPX, yf + 0.5, ARCH_SPR + ARCH_R + 2.3), Vector((1, 0, 0)), Vector((0, 0, 1)), Vector((0, 1, 0)), 1.3,
             -0.05, 0.14, PALE)
    # timpano de obsidiana (fundo do nicho, atras do anel e da placa)
    tp_pts = [Vector((x, y_, ZF - 0.3)) for x in (-PIER_X, PIER_X) for y_ in (TYMP_Y - 1.0, TYMP_Y)]
    for i in range(13):
        q = math.pi * i / 12
        for y_ in (TYMP_Y - 1.0, TYMP_Y):
            tp_pts.append(Vector((PPX + ARCH_R * math.cos(q), y_, ARCH_SPR + ARCH_R * math.sin(q))))
    hull(mp, tp_pts, OB)
    col_box2("SG_CavePortal", (-PIER_X, Y0 - 2.0, ZF), (PIER_X, TYMP_Y, ARCH_SPR + ARCH_R + 1.0))
    # MOLDURA DA PLACA DE HORARIO (DUNGEON_UI): vao 22,4 x 6,4 com fundo no timpano; cornija em cima, misulas embaixo
    hw, hh = UI_W / 2 + 0.2, UI_H / 2 + 0.2
    fb = 1.3
    yfr = UI_Y + 0.8
    for x0_, z0_, x1_, z1_ in ((-hw - fb, UI_Z - hh - fb, hw + fb, UI_Z - hh), (-hw - fb, UI_Z + hh, hw + fb, UI_Z + hh + fb),
                               (-hw - fb, UI_Z - hh, -hw, UI_Z + hh), (hw, UI_Z - hh, hw + fb, UI_Z + hh)):
        abox(mp, (x0_, TYMP_Y - 0.2, z0_), (x1_, yfr, z1_), RUIN, 0.14)
    hull(mp, [Vector((x, y_, z)) for x in (-hw - fb - 0.6, hw + fb + 0.6)
              for y_, z in ((TYMP_Y - 0.2, UI_Z + hh + fb), (yfr + 0.6, UI_Z + hh + fb),
                            (yfr + 0.6, UI_Z + hh + fb + 0.5), (TYMP_Y - 0.2, UI_Z + hh + fb + 1.0))], OB)
    for s in (-1, 1):
        hull(mp, [Vector((s * x, y_, z)) for x in (hw - 1.2, hw + fb) for y_, z in (
            (TYMP_Y - 0.2, UI_Z - hh - fb), (yfr + 0.4, UI_Z - hh - fb), (TYMP_Y - 0.2, UI_Z - hh - fb - 2.2))], RUIN)
    # ANEL: aro escuro, 22 aduelas com junta aberta, runas acesas em aduelas alternadas, fecho saliente, pes em consola
    c = Vector((PPX, PPY, PZC))
    ring3(mp, c, u, v, n, PR_IN - 0.3, PR_IN + 1.0, -0.9, 0.35, OB, 48)
    NVR = 22
    for k in range(NVR):
        a0 = math.pi / 2 + 2 * math.pi * (k - 0.5) / NVR + 0.012
        a1 = math.pi / 2 + 2 * math.pi * (k + 0.5) / NVR - 0.012
        if PZC + (PR_IN + 2.4) * max(math.sin(a0), math.sin(a1)) < DZ - 0.1:
            continue                                                          # enterrada no estrado
        key = k == 0
        r1 = PR_IN + 2.4 + (0.6 if key else 0.0)
        d1 = 0.9 + (0.45 if key else 0.0)
        pts = []
        for a in (a0, (a0 + a1) / 2, a1):
            for r in (PR_IN, r1):
                pts.append(_pl(c, u, v, n, a, r, -0.85))
                pts.append(_pl(c, u, v, n, a, r, d1 - 0.12))
                pts.append(_pl(c, u, v, n, a, r + (0.12 if r < PR_IN + 1.0 else -0.12), d1))
        hull(mp, pts, RUIN)
        am = (a0 + a1) / 2
        if k % 2 == 1 and PZC + (PR_IN + 1.2) * math.sin(am) > DZ + 0.8:
            radial = u * math.cos(am) + v * math.sin(am)
            tang = u * -math.sin(am) + v * math.cos(am)
            rune(mp, c + radial * (PR_IN + 1.2) + n * d1, tang, radial, n, k // 2, 1.25, VG, 0.05, 0.12)
    for sgn in (-1, 1):                                                       # pes em consola
        a = math.radians(-90.0 + sgn * 52.0)
        p = _pl(c, u, v, n, a, PR_IN + 1.6, -0.3)
        hull(mp, [Vector((p.x + dx, p.y + dy, z)) for dx in (-1.4, 1.4) for dy, z in ((-1.2, DZ - 0.05), (1.4, DZ - 0.05),
                                                                                  (1.1, p.z), (-1.2, p.z + 0.4))], OB)
    col_box2("SG_CavePortal", (-PR_IN - 2.8, TYMP_Y, DZ), (PR_IN + 2.8, PPY + 1.4, PZC + PR_IN + 3.2))
    # vortice: disco escuro (fundo) + espiral (objeto proprio com pivot/eixo para girar no jogo)
    md = smb()
    disc3(md, c, u, v, n, PR_IN + 0.05, -0.7, -0.5, VOID, 48)
    vf = MB("SG_Cave_PortalVortex", C, random.Random(993), detail="near")
    vortex_arms(vf, c, u, v, n, PR_IN - 0.4, -0.5, -0.32, VG, arms=6, twist=2.9)
    ob = vf.finish()
    ob["pivot"] = [round(c.x, 3), round(c.y, 3), round(c.z, 3)]
    ob["axis"] = [0.0, 1.0, 0.0]
    ob["rpm"] = 4.0
    ob["vfx"] = "espiral violeta do portal da masmorra no salao sombrio (gira no plano do disco)"


# ==================================================================== FORJA / OFICINA SECRETA (oeste)
def platform(mb, rect, step_east):
    """plataforma de oficina a +1,6 (lajes com junta 0,35 abaixo) e degrau de 0,8 ao longo da borda de dentro"""
    x0, y0, x1, y1 = rect
    abox(mb, (x0, y0, ZF - 0.3), (x1, y1, PF_Z - 0.35), BL, 0.0)
    y, r = y0, 0
    while y < y1 - 0.2:
        y2 = min(y1, y + 7.2)
        x = x0 - (3.0 if r % 2 else 0.0)
        while x < x1:
            x2 = min(x1, x + 6.0)
            xa = max(x, x0)
            if x2 - xa > 0.6:
                abox(mb, (xa + 0.1, y + 0.1, PF_Z - 0.35), (x2 - 0.1, y2 - 0.1, PF_Z), FL, 0.0)
            x = x2
        y, r = y2, r + 1
    sa, sb = (x1, x1 + 1.8) if step_east else (x0 - 1.8, x0)
    abox(mb, (sa, y0, ZF - 0.3), (sb, y1, ZF + 0.8), BL, 0.08)
    col_box2("SG_CavePlatform", (x0, y0, ZF - 1.0), (x1, y1, PF_Z))
    col_box2("SG_CavePlatform", (sa, y0, ZF - 1.0), (sb, y1, ZF + 0.8))


def sword(mb, base, dirv, side, L_=4.2):
    """espada de pe (ponta para baixo): lamina de ferro com ombro, guarda, punho de madeira e pomo"""
    base, dirv, side = Vector(base), Vector(dirv).normalized(), Vector(side).normalized()
    fw = dirv.cross(side).normalized()
    tip = base
    b0 = base + dirv * 0.6
    b1 = base + dirv * (L_ * 0.72)
    hull(mb, [tip] + [b0 + side * s * 0.22 + fw * t * 0.05 for s in (-1, 1) for t in (-1, 1)] +
         [b1 + side * s * 0.2 + fw * t * 0.06 for s in (-1, 1) for t in (-1, 1)], BI)
    g = base + dirv * (L_ * 0.74)
    obox3(mb, g, side, fw, dirv, 1.3, 0.24, 0.2, BI)
    bar(mb, g + dirv * 0.1, g + dirv * 1.0, 0.18, 0.18, WD, up=side)
    lathe_ax(mb, g + dirv * 1.0, dirv, [(0.0, 0.0), (0.2, 0.08), (0.16, 0.28), (0.0, 0.34)], BI, 5)


def forge():
    mb = smb()
    x0, y0, x1, y1 = FORGE_PF
    platform(mb, (X0 + 0.1, y0, x1, y1), True)
    z = PF_Z
    # FORNALHA: corpo em talude, boca em arco (brilho quente CONTIDO la dentro), coifa e chamine ate a rocha
    fx0, fx1, fy0, fy1 = X0 + 0.3, -76.5, 133.0, 147.0
    mx, my = fx1, (fy0 + fy1) / 2
    for ya_, yb_ in ((fy0, my - 2.2), (my + 2.2, fy1)):
        hull(mb, [Vector((x, y_, zz)) for y_ in (ya_, yb_) for x, zz in ((fx0, z), (fx1, z), (fx1 + 0.8, z + 0.01),
                                                                         (fx1 - 0.4, z + 6.4), (fx0, z + 6.4))], BL)
    hull(mb, [Vector((x, y_, zz)) for y_ in (my - 2.25, my + 2.25) for x, zz in ((fx0, z + 3.4), (fx1 - 0.2, z + 3.4),
                                                                              (fx1 - 0.4, z + 6.4), (fx0, z + 6.4))], BL)
    hull(mb, [Vector((x, y_, zz)) for y_ in (my - 2.3, my + 2.3) for x, zz in ((fx0, z), (fx1 - 2.4, z),
                                                                            (fx1 - 2.4, z + 3.5), (fx0, z + 3.5))], BL)
    for k in range(5):                                                   # arco da boca (aduelas de ruina)
        q0, q1 = math.pi * k / 5 + 0.02, math.pi * (k + 1) / 5 - 0.02
        hull(mb, [Vector((xx, my + rr * math.cos(q), z + 2.0 + rr * 0.75 * math.sin(q))) for q in (q0, q1)
                  for rr in (2.2, 3.1) for xx in (fx1 - 0.6, fx1 + 0.35)], RUIN)
    abox(mb, (fx1 - 1.6, my - 2.1, z + 0.05), (fx1 - 1.25, my + 2.1, z + 2.9), CORE, 0.0)          # brasa (recuada)
    for k, (dy, hh) in enumerate(((-1.3, 0.5), (-0.2, 0.7), (0.9, 0.45), (1.6, 0.35))):              # carvoes
        hull(mb, [Vector((fx1 - 1.2 + a, my + dy + b, z + 0.02)) for a in (-0.35, 0.35) for b in (-0.3, 0.3)] +
             [Vector((fx1 - 1.2, my + dy, z + hh))], OB)
    hull(mb, [Vector((x, y_, zz)) for x, y_, zz in
              ((fx0, fy0 - 0.4, z + 6.4), (fx1 + 0.3, fy0 - 0.4, z + 6.4), (fx0, fy1 + 0.4, z + 6.4), (fx1 + 0.3, fy1 + 0.4, z + 6.4),
               (fx0, fy0 + 3.0, z + 11.0), (fx0 + 6.5, fy0 + 3.0, z + 11.0), (fx0, fy1 - 3.0, z + 11.0),
               (fx0 + 6.5, fy1 - 3.0, z + 11.0))], BL)
    for (za, zb_, wa, wb) in ((z + 11.0, z + 21.0, 6.2, 5.2), (z + 21.0, 30.0, 4.8, 4.0)):
        hull(mb, [Vector((fx0, my + sy_ * w_ / 2 * 1.25, zz)) for zz, w_ in ((za, wa), (zb_, wb)) for sy_ in (-1, 1)] +
             [Vector((fx0 + w_, my + sy_ * w_ / 2 * 1.25, zz)) for zz, w_ in ((za, wa), (zb_, wb)) for sy_ in (-1, 1)],
             BL)
    abox(mb, (fx0, my - 3.6, z + 20.6), (fx0 + 5.5, my + 3.6, z + 21.4), RUIN, 0.0, cuts=[((1, 0, 1), 0.3)])
    for zz, w_ in ((z + 14.0, 5.9), (z + 18.0, 5.55), (z + 25.0, 4.55)):
        abox(mb, (fx0 + 0.25, my - w_ * 0.625 - 0.22, zz), (fx0 + w_ + 0.22, my + w_ * 0.625 + 0.22, zz + 0.45), BI, 0.0)
    col_box2("SG_CaveForge", (X0, fy0 - 0.4, PF_Z), (fx1 + 0.3, fy1 + 0.4, PF_Z + 6.4))
    # FOLE de madeira e couro ao lado da fornalha
    hull(mb, [Vector((xx, fy1 + 1.2 + dy, z + zz)) for xx in (-80.0, -85.0) for dy, zz in ((0.0, 1.0), (2.4, 1.0))] +
         [Vector((-85.0, fy1 + 1.2 + dy, z + 2.4)) for dy in (0.0, 2.4)], WD)
    # BIGORNA sobre o toco
    ax_, ay_ = -71.0, 158.0
    mb.cyl(1.3, 2.2, (ax_, ay_, z + 1.1), m=WD, n=8, bevel=0.0)
    zt = z + 2.2
    hull(mb, [Vector((ax_ + a * 1.2, ay_ + b * 1.0, zt)) for a in (-1, 1) for b in (-1, 1)] +
         [Vector((ax_ + a * 0.55, ay_ + b * 0.6, zt + 0.8)) for a in (-1, 1) for b in (-1, 1)], BI)
    hull(mb, [Vector((ax_ + a * 0.62, ay_ + b * 1.5, zt + zz)) for a in (-1, 1) for b in (-1, 1) for zz in (0.8, 1.65)], BI)
    hull(mb, [Vector((ax_ + a * 0.5, ay_ + 1.5, zt + zz)) for a in (-1, 1) for zz in (1.0, 1.65)] +
         [Vector((ax_, ay_ + 3.3, zt + 1.45))], BI)                                         # chifre
    col_box2("SG_CaveForge", (ax_ - 1.5, ay_ - 1.6, PF_Z), (ax_ + 1.5, ay_ + 3.3, zt + 1.7))
    # martelo e tenaz em cima da bigorna
    bar(mb, (ax_ + 0.2, ay_ - 1.2, zt + 1.75), (ax_ + 0.2, ay_ + 0.6, zt + 1.75), 0.14, 0.14, WD)
    abox(mb, (ax_ - 0.15, ay_ - 1.5, zt + 1.62), (ax_ + 0.55, ay_ - 1.0, zt + 2.0), BI, 0.03)
    # TINA de tempera
    abox(mb, (-74.5, 170.0, z), (-69.5, 172.6, z + 1.8), BL, 0.1)
    abox(mb, (-74.1, 170.4, z + 1.2), (-69.9, 172.2, z + 1.5), OB, 0.0)
    col_box2("SG_CaveForge", (-74.5, 170.0, PF_Z), (-69.5, 172.6, PF_Z + 1.8))
    # BANCADA encostada na rocha com ferramentas + painel de ferramentas
    bx0, bx1, by0, by1, bz = X0 + 0.6, X0 + 4.6, 151.0, 169.0, z + 3.3
    abox(mb, (bx0, by0, bz - 0.4), (bx1, by1, bz), WD, 0.06)
    for yy in (by0 + 0.5, by1 - 0.5):
        for xx in (bx0 + 0.5, bx1 - 0.5):
            abox(mb, (xx - 0.25, yy - 0.25, z), (xx + 0.25, yy + 0.25, bz - 0.4), WD, 0.04)
    abox(mb, (bx0 + 0.3, by0 + 0.3, z + 0.9), (bx1 - 0.3, by1 - 0.3, z + 1.2), WD, 0.03)
    abox(mb, (X0 + 0.2, by0 + 1.0, bz + 1.0), (X0 + 0.55, by1 - 1.0, bz + 4.2), WD, 0.04)
    for k in range(6):
        yy = by0 + 2.2 + k * 2.6
        bar(mb, (X0 + 0.6, yy, bz + 3.6), (X0 + 0.6, yy, bz + 1.5 + 0.3 * (k % 2)), 0.12, 0.12, BI)
        abox(mb, (X0 + 0.45, yy - 0.35, bz + 1.2 + 0.3 * (k % 2)), (X0 + 0.9, yy + 0.35, bz + 1.6 + 0.3 * (k % 2)), BI, 0.03)
    for k, yy in enumerate((by0 + 3.0, by0 + 8.0, by0 + 13.5)):
        bar(mb, (bx0 + 1.2, yy, bz + 0.1), (bx0 + 3.4, yy + 0.6, bz + 0.1), 0.18, 0.12, WD)
        abox(mb, (bx0 + 3.2, yy + 0.2, bz), (bx0 + 3.9, yy + 1.0, bz + 0.5), BI, 0.03)
    col_box2("SG_CaveForge", (X0, by0, PF_Z), (bx1, by1, bz))
    # CABIDES DE ARMAS (espadas de pe, lancas) e escudo redondo
    ry0, ry1 = 174.0, 186.0
    for xx in (X0 + 1.2, X0 + 3.4):
        for yy in (ry0, ry1):
            abox(mb, (xx - 0.25, yy - 0.25, z), (xx + 0.25, yy + 0.25, z + 5.2), WD, 0.04)
        abox(mb, (xx - 0.2, ry0, z + 4.6), (xx + 0.2, ry1, z + 5.0), WD, 0.03)
        abox(mb, (xx - 0.2, ry0, z + 1.2), (xx + 0.2, ry1, z + 1.55), WD, 0.03)
    for k in range(5):
        yy = ry0 + 1.4 + k * 2.3
        sword(mb, (X0 + 2.3, yy, z + 0.05), (0.0, 0.08 * (k % 2 - 0.5), 1.0), (0.0, 1.0, 0.0), 4.6)
    for yy in (ry0 + 0.6, ry1 - 0.6):
        bar(mb, (X0 + 2.3, yy, z), (X0 + 2.3, yy, z + 7.4), 0.16, 0.16, WD)
        hull(mb, [Vector((X0 + 2.3 + a, yy, z + 7.4)) for a in (-0.15, 0.15)] + [Vector((X0 + 2.3, yy + b, z + 7.4))
                                                                             for b in (-0.3, 0.3)] +
             [Vector((X0 + 2.3, yy, z + 8.6))], BI)
    col_box2("SG_CaveForge", (X0, ry0 - 0.5, PF_Z), (X0 + 4.2, ry1 + 0.5, PF_Z + 5.2))
    # BAUS de ferragem e caixas
    for cx_, cy_, rot in ((-66.5, 187.0, 0.0), (-81.0, 188.2, 0.0)):
        abox(mb, (cx_ - 1.9, cy_ - 1.1, z), (cx_ + 1.9, cy_ + 1.1, z + 1.7), WD, 0.06)
        hull(mb, [Vector((cx_ + a * 1.95, cy_ + b * 1.15, z + 1.7)) for a in (-1, 1) for b in (-1, 1)] +
             [Vector((cx_ + a * 1.95, cy_ + b * 0.6, z + 2.4)) for a in (-1, 1) for b in (-1, 1)], WD)
        for dx in (-1.2, 1.2):
            abox(mb, (cx_ + dx - 0.18, cy_ - 1.2, z + 0.1), (cx_ + dx + 0.18, cy_ + 1.2, z + 2.2), BI, 0.02)
        col_box2("SG_CaveForge", (cx_ - 2.0, cy_ - 1.2, PF_Z), (cx_ + 2.0, cy_ + 1.2, PF_Z + 2.4))
    for cx_, cy_, s_ in ((-73.5, 135.5, 2.2), (-70.6, 135.2, 1.6), (-72.4, 135.4, 1.3)):
        zz = z if s_ > 1.4 else z + 2.2
        abox(mb, (cx_ - s_ / 2, cy_ - s_ / 2, zz), (cx_ + s_ / 2, cy_ + s_ / 2, zz + s_), WD, 0.08)
    col_box2("SG_CaveForge", (-74.6, 134.2, PF_Z), (-69.8, 136.6, PF_Z + 2.2))
    # REBOLO de amolar (roda de pedra no cavalete) e BARRIS cintados
    gx_, gy_ = -65.0, 143.5
    for dy in (-0.9, 0.9):
        bar(mb, (gx_ - 1.2, gy_ + dy, z), (gx_, gy_ + dy, z + 2.6), 0.22, 0.22, WD)
        bar(mb, (gx_ + 1.2, gy_ + dy, z), (gx_, gy_ + dy, z + 2.6), 0.22, 0.22, WD)
    lathe_ax(mb, (gx_, gy_ - 0.35, z + 2.6), (0.0, 1.0, 0.0), [(1.35, 0.0), (1.45, 0.12), (1.45, 0.58), (1.35, 0.7)],
             BL, 10)
    bar(mb, (gx_, gy_ - 1.2, z + 2.6), (gx_, gy_ + 1.2, z + 2.6), 0.14, 0.14, BI)
    col_box2("SG_CaveForge", (gx_ - 1.5, gy_ - 1.2, PF_Z), (gx_ + 1.5, gy_ + 1.2, PF_Z + 4.0))
    for bx_, by_ in ((-62.3, 136.0), (-60.2, 138.6)):
        EM._lathe(mb, (bx_, by_, z), [(0.95, 0.0), (1.12, 0.8), (1.18, 1.4), (1.12, 2.0), (0.95, 2.8)], WD, 8,
                  caps=(False, True))
        for zz in (0.35, 2.35):
            EM._lathe(mb, (bx_, by_, z + zz), [(1.08, 0.0), (1.12, 0.1), (1.12, 0.22), (1.05, 0.3)], BI, 8,
                      caps=(False, False))
    col_box2("SG_CaveForge", (-63.4, 134.9, PF_Z), (-59.1, 139.7, PF_Z + 2.8))
    # corrente de icar pendurada da passarela sobre a bigorna
    chain_lite(mb, (-82.0, 160.0, ZG - 1.2), (-82.0, 160.0, PF_Z + 7.0), 0.0)
    abox(mb, (-82.3, 159.7, PF_Z + 6.2), (-81.7, 160.3, PF_Z + 7.05), BI, 0.03)
# ==================================================================== SALA DO MAPA (leste)
def map_relief(mb, cx, cy, ztop, s):
    """a ILHA em relevo na mesa: contorno do topo do penhasco (sg_layout.ISLAND_RIM) em escala, 2 patamares e o
    castelo com a torre-coroa"""
    rim = SL.ccw([(cx + x * s, cy + (y - 26.0) * s) for x, y in L.ISLAND_RIM[::5]])
    mb.prism(rim, ztop, ztop + 0.7, RKL)                                         # penhasco
    rim2 = SL.ccw([(cx + x * s * 0.9, cy + (y - 26.0) * s * 0.9 + 0.2) for x, y in L.ISLAND_RIM[::7]])
    mb.prism(rim2, ztop + 0.7, ztop + 0.95, "Grass_SG")                         # patamares baixos
    top = SL.ccw([(cx + x * s, cy + (y - 26.0) * s) for x, y in ((-150, -30), (150, -30), (150, 380), (-150, 380))])
    mb.prism(top, ztop + 0.95, ztop + 1.35, "Grass_SG")                          # P3 (castelo)
    zc_ = ztop + 1.35
    ccx, ccy = cx, cy + (164.0 - 26.0) * s
    abox(mb, (ccx - 104 * s, ccy - 103 * s, zc_), (ccx + 104 * s, ccy + 103 * s, zc_ + 1.5), CS, 0.03)
    abox(mb, (ccx - 38 * s, ccy + 98 * s, zc_), (ccx + 38 * s, ccy + 180 * s, zc_ + 2.4), CS, 0.03)
    for dx in (-116.0, 116.0):
        mb.cyl(20 * s, 2.6, (ccx + dx * s, cy + (72.0 - 26.0) * s, zc_ + 1.3), m=CS, n=8, bevel=0.0)
    lathe_ax(mb, (ccx, ccy + 139 * s, zc_ + 2.4), UPZ, [(30 * s, 0.0), (0.0, 2.6)], "Roof_SG_Navy", 8)
    for px_, py_ in ((0.0, -268.0), (-208.0, -222.0), (112.0, -86.0)):              # alfinetes: vila, invocacao, alquimia
        bar(mb, (cx + px_ * s, cy + (py_ - 26.0) * s, ztop + 0.3), (cx + px_ * s, cy + (py_ - 26.0) * s, ztop + 1.4),
            0.07, 0.07, BI)
        EM._lathe(mb, (cx + px_ * s, cy + (py_ - 26.0) * s, ztop + 1.4), [(0.0, 0.0), (0.16, 0.1), (0.0, 0.3)], PALE, 5)


def armor_stand(mb, x, y, z, face):
    """manequim com armadura: toco, cruz de madeira, peitoral, ombreiras, saia de laminas e elmo"""
    f = Vector((face[0], face[1], 0.0)).normalized()
    sd = UPZ.cross(f).normalized()
    p = Vector((x, y, z))
    abox(mb, (x - 0.9, y - 0.9, z), (x + 0.9, y + 0.9, z + 0.4), WD, 0.05)
    bar(mb, p + UPZ * 0.4, p + UPZ * 5.6, 0.3, 0.3, WD)
    bar(mb, p + UPZ * 5.0 - sd * 1.4, p + UPZ * 5.0 + sd * 1.4, 0.24, 0.24, WD)
    hull(mb, [p + UPZ * zz + sd * (s * w) + f * d for zz, w, d in ((3.2, 0.95, 0.55), (5.1, 1.25, 0.75)) for s in (-1, 1)] +
         [p + UPZ * zz + sd * (s * w) - f * 0.5 for zz, w in ((3.2, 0.95), (5.1, 1.2)) for s in (-1, 1)] +
         [p + UPZ * 4.4 + f * 0.95], BI)
    for s in (-1, 1):
        lathe_ax(mb, p + UPZ * 5.05 + sd * (s * 1.2), sd * s, [(0.62, 0.0), (0.7, 0.3), (0.45, 0.6), (0.0, 0.7)], BI, 6)
    for k in range(3):
        zz = 3.2 - 0.55 * k
        hull(mb, [p + UPZ * (zz - 0.55) + sd * (s * (1.0 + 0.08 * k)) + f * 0.6 for s in (-1, 1)] +
             [p + UPZ * zz + sd * (s * 0.95) + f * 0.55 for s in (-1, 1)] +
             [p + UPZ * (zz - 0.55) + sd * (s * (1.0 + 0.08 * k)) - f * 0.45 for s in (-1, 1)] +
             [p + UPZ * zz + sd * (s * 0.95) - f * 0.45 for s in (-1, 1)], BI)
    EM._lathe(mb, (x, y, z + 5.5), [(0.5, 0.0), (0.62, 0.35), (0.58, 0.95), (0.35, 1.3), (0.0, 1.4)], BI, 8)
    col_box2("SG_CaveMap", (x - 1.4, y - 1.4, z), (x + 1.4, y + 1.4, z + 6.0))


def maproom():
    mb = smb()
    x0, y0, x1, y1 = MAP_PF
    platform(mb, (x0, y0, X1 - 0.1, y1), False)
    z = PF_Z
    # MESA do mapa: tampo com moldura, 6 pernas torneadas, travessas; o mar escuro e a ilha em relevo
    tx, ty, tw, tl, th = 72.0, 161.0, 13.0, 21.0, 3.4
    abox(mb, (tx - tw / 2, ty - tl / 2, z + th - 0.5), (tx + tw / 2, ty + tl / 2, z + th), WD, 0.08)
    for s in (-1, 1):
        abox(mb, (tx - tw / 2 - 0.25, ty - tl / 2 - 0.25, z + th - 0.1), (tx + tw / 2 + 0.25, ty - tl / 2 + 0.35,
                                                                        z + th + 0.35), WD, 0.05)
        abox(mb, (tx - tw / 2 - 0.25, ty + tl / 2 - 0.35, z + th - 0.1), (tx + tw / 2 + 0.25, ty + tl / 2 + 0.25,
                                                                        z + th + 0.35), WD, 0.05)
        abox(mb, (tx + s * tw / 2 - 0.35 * (s > 0) - 0.25 * (s < 0), ty - tl / 2 + 0.35, z + th - 0.1),
             (tx + s * tw / 2 + 0.25 * (s > 0) + 0.35 * (s < 0), ty + tl / 2 - 0.35, z + th + 0.35), WD, 0.05)
    abox(mb, (tx - tw / 2 + 0.4, ty - tl / 2 + 0.4, z + th - 0.02), (tx + tw / 2 - 0.4, ty + tl / 2 - 0.4, z + th + 0.12),
         OB, 0.0)
    for xx in (tx - tw / 2 + 0.9, tx + tw / 2 - 0.9):
        for yy in (ty - tl / 2 + 0.9, ty, ty + tl / 2 - 0.9):
            EM._lathe(mb, (xx, yy, z), [(0.45, 0.0), (0.45, 0.3), (0.3, 0.5), (0.42, 1.1), (0.24, 1.8), (0.3, 2.6),
                                         (0.4, th - 0.5)], WD, 4, math.pi / 4, caps=(False, True))
    abox(mb, (tx - 0.2, ty - tl / 2 + 1.0, z + 0.8), (tx + 0.2, ty + tl / 2 - 1.0, z + 1.1), WD, 0.02)
    map_relief(mb, tx, ty, z + th + 0.12, 18.6 / 720.0)
    col_box2("SG_CaveMap", (tx - tw / 2 - 0.3, ty - tl / 2 - 0.3, PF_Z), (tx + tw / 2 + 0.3, ty + tl / 2 + 0.3, PF_Z + th))
    # ESTANTES de reliquias na rocha (sob a passarela): armacao, prateleiras, rolos de pergaminho e caixas
    for sy0, sy1 in ((136.0, 149.0), (172.0, 186.0)):
        xa, xb = X1 - 4.2, X1 - 0.3
        for yy in (sy0, sy1):
            abox(mb, (xa, yy - 0.3, z), (xb, yy + 0.3, z + 8.4), WD, 0.0)
        abox(mb, (xa - 0.2, sy0 - 0.5, z + 8.4), (xb, sy1 + 0.5, z + 8.9), WD, 0.0, cuts=[((-1, 0, 1), 0.2)])
        abox(mb, (xb - 0.25, sy0, z + 0.2), (xb, sy1, z + 8.4), WD, 0.0)
        for k in range(4):
            zz = z + 0.3 + 2.05 * k
            abox(mb, (xa, sy0 + 0.3, zz), (xb - 0.25, sy1 - 0.3, zz + 0.25), WD, 0.0)
            if k == 0:
                continue
            yy = sy0 + 0.9
            j = 0
            while yy < sy1 - 1.2:
                if (j + k) % 2 == 1:
                    abox(mb, (xa + 0.6, yy, zz + 0.25), (xb - 0.6, yy + 1.4 + 0.4 * (j % 2), zz + 1.25), WD, 0.0,
                         cuts=[((-1, 0, 1), 0.12)])                                                # caixa
                    yy += 2.4 + 0.4 * (j % 2)
                else:                                                           # feixe de rolos amarrado
                    ln = 2.4 + 0.5 * ((j * 3 + k) % 3)
                    for q, (dy_, dz_) in enumerate(((0.0, 0.0), (0.7, 0.0))):
                        mb.cyl(0.34, ln - 0.25 * q, (xa + 0.4 + ln / 2, yy + 0.36 + dy_, zz + 0.59 + dz_),
                               (0, math.pi / 2, 0), m=PALE, n=5, bevel=0.0)
                    yy += 2.6
                j += 1
        col_box2("SG_CaveMap", (xa - 0.2, sy0 - 0.5, PF_Z), (X1, sy1 + 0.5, PF_Z + 8.9))
    # armaduras da ordem
    armor_stand(mb, 62.5, 137.5, z, (-1.0, 0.0))
    armor_stand(mb, 62.5, 184.5, z, (-1.0, 0.0))
    # bau e caixas
    abox(mb, (80.5, 131.4 + 1.0, z), (84.5, 133.6 + 1.0, z + 1.7), WD, 0.06)
    for dx in (81.3, 83.7):
        abox(mb, (dx - 0.18, 132.3, z + 0.1), (dx + 0.18, 134.7, z + 1.8), BI, 0.02)
    col_box2("SG_CaveMap", (80.4, 132.3, PF_Z), (84.6, 134.7, PF_Z + 1.8))
    # lustre de ferro sobre a mesa (a luz L_SGCave_Map) preso por haste na rocha
    lz = z + 11.5
    mb.tube([(tx + 2.2 * math.cos(2 * math.pi * k / 12), ty + 2.2 * math.sin(2 * math.pi * k / 12), lz) for k in range(13)],
            0.12, BI, 4)
    mb.cyl(0.1, 26.0 - lz, (tx, ty, (lz + 26.0) / 2), m=BI, n=6, bevel=0.0)
    for k in range(6):
        a = 2 * math.pi * k / 6
        bar(mb, (tx, ty, lz + 0.9), (tx + 2.2 * math.cos(a), ty + 2.2 * math.sin(a), lz), 0.09, 0.09, BI)
        EM._lathe(mb, (tx + 2.2 * math.cos(a), ty + 2.2 * math.sin(a), lz + 0.1), [(0.0, 0.0), (0.16, 0.14), (0.08, 0.36),
                                                                                  (0.0, 0.55)], GLW, 5)
# ==================================================================== CRISTAIS (so presos nas paredes, em volta do portal)
CLUSTERS = [("S", -38.0, 4.0, 1.25, 4), ("S", -50.0, 17.0, 1.0, 3), ("S", -42.0, 29.0, 0.85, 3), ("S", 38.0, 7.0, 1.2, 4),
            ("S", 51.0, 20.0, 1.0, 3), ("S", 43.0, 31.0, 0.8, 3), ("S", -64.0, 11.0, 0.9, 3), ("S", 65.0, 25.0, 0.9, 3),
            ("W", 108.0, 12.0, 1.0, 3), ("E", 112.0, 8.0, 1.1, 4), ("W", 120.0, 27.0, 0.8, 3), ("E", 104.0, 24.0, 0.9, 3)]


def _frame3(d):
    d = Vector(d).normalized()
    ref = Vector((0.0, 0.0, 1.0)) if abs(d.z) < 0.9 else Vector((1.0, 0.0, 0.0))
    e1 = d.cross(ref).normalized()
    return d, e1, d.cross(e1).normalized()


def crystal_hex(mb, base, dirv, h, r, ph=0.0):
    d, e1, e2 = _frame3(dirv)
    b = Vector(base) - d * 0.6
    hb = h * 0.7 + 0.6

    def ring(o, rr):
        return [o + (e1 * math.cos(ph + k * math.pi / 3) + e2 * math.sin(ph + k * math.pi / 3)) * rr for k in range(6)]
    r1 = ring(b + d * hb, r * 0.86)
    hull(mb, ring(b, r) + r1, CRY)
    hull(mb, r1 + [b + d * (hb + h * 0.3) + (e1 * math.cos(ph) + e2 * math.sin(ph)) * (r * 0.22)], CRYG)


def crystals():
    mb = smb()
    bms, bvhs = {}, {}
    for side in ("S", "W", "E"):
        ob = bpy_obj("SG_Cave_Rock_" + side)
        if ob is None:
            continue
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        bvhs[side] = BVHTree.FromBMesh(bm)
        bms[side] = bm
    SPREAD = ((0.62, 0.5, 0.6), (0.46, 0.62, 2.6), (0.34, 0.55, 4.3), (0.28, 0.7, 5.4))
    nc = 0
    for ci, (side, s, z, sc, k) in enumerate(CLUSTERS):
        if side not in bvhs:
            continue
        if side == "S":
            o, dr = Vector((s, Y0 + 40.0, z)), Vector((0.0, -1.0, 0.0))
        elif side == "W":
            o, dr = Vector((X0 + 40.0, s, z)), Vector((-1.0, 0.0, 0.0))
        else:
            o, dr = Vector((X1 - 40.0, s, z)), Vector((1.0, 0.0, 0.0))
        hit = bvhs[side].ray_cast(o, dr, 80.0)
        if hit[0] is None:
            continue
        p, nrm = hit[0], Vector(hit[1])
        if nrm.dot(dr) > 0:
            nrm = -nrm
        d = (nrm + UPZ * 0.35 + Vector((0.2 * math.sin(ci * 1.7), 0.0, 0.0))).normalized()
        dd, e1, e2 = _frame3(d)
        base = p - nrm * 0.2
        pts = []
        R = 2.4 * sc
        for q in range(7):
            a = 2 * math.pi * q / 7
            rr = R * (1.0 + 0.22 * math.sin(q * 2.1 + 0.4))
            pts.append(base - dd * 0.25 + (e1 * math.cos(a) + e2 * math.sin(a)) * rr)
        for q in range(5):
            a = 2 * math.pi * q / 5 + 0.5
            pts.append(base + dd * (0.32 * R) + (e1 * math.cos(a) + e2 * math.sin(a)) * (R * 0.55))
        pts.append(base - dd * (0.9 * R))
        hull(mb, pts, RKD)                                               # calo de rocha (nada solto)
        h, r = 4.6 * sc, 0.7 * sc
        crystal_hex(mb, base + dd * 0.3, dd, h, r, 0.3)
        for i, (scl, ap, az) in enumerate(SPREAD[:max(0, k - 1)]):
            off = e1 * math.cos(az) + e2 * math.sin(az)
            crystal_hex(mb, base + dd * 0.3 + off * (r * 1.3), (dd + off * ap).normalized(), h * scl, r * scl * 1.1, 0.9 * i)
        nc += 1
    for bm in bms.values():
        bm.free()
    return nc


def bpy_obj(name):
    import bpy
    return bpy.data.objects.get(name)


# ==================================================================== luzes, colisao da casca, cameras, build
def lights():
    light("L_SGCave_Portal", "POINT", (PPX, PPY + 9.0, PZC + 1.0), 5200.0, (0.62, 0.40, 1.0), 3.0)
    light("L_SGCave_Forge", "POINT", (-74.2, 140.0, PF_Z + 2.4), 2400.0, (1.0, 0.52, 0.22), 1.2)
    light("L_SGCave_Map", "POINT", (72.0, 161.0, PF_Z + 10.6), 1500.0, (1.0, 0.72, 0.45), 1.2)
    light("L_SGCave_CrystalW", "POINT", (-40.0, Y0 + 14.0, 14.0), 1500.0, (0.55, 0.50, 1.0), 2.0)
    light("L_SGCave_CrystalE", "POINT", (40.0, Y0 + 14.0, 14.0), 1500.0, (0.55, 0.50, 1.0), 2.0)
    light("L_SGCave_Gallery", "POINT", (-9.5, GY1 - 3.2, ZG + 6.8), 1500.0, (1.0, 0.72, 0.45), 1.0)


def shell_col():
    wt = 2.0
    box_walls_col("SG_CaveWall", (X0, Y0, X1, Y1), ZF - 1.0, ZT, wt)
    sh = (TC[0] - L.SPIRAL_R_IN, TC[1] - L.SPIRAL_R_IN, TC[0] + L.SPIRAL_R_IN, TC[1] + L.SPIRAL_R_IN)
    for p0, p1 in (((X0, Y0, ZT), (X1, sh[1], ZT + 1.0)), ((X0, sh[3], ZT), (X1, Y1, ZT + 1.0)),
                   ((X0, sh[1], ZT), (sh[0], sh[3], ZT + 1.0)), ((sh[2], sh[1], ZT), (X1, sh[3], ZT + 1.0))):
        col_box2("SG_CaveCeil", p0, p1)


_E = ZG + 5.2
CAMS = {
    "CAM_SGCave_SpiralTop": ((-1.5, 304.0, L.SPIRAL_TOP_Z + 6.2), (9.0, 322.0, 43.0), 13),
    "CAM_SGCave_SpiralDown": ((TC[0] + 10.6 * math.cos(math.radians(125.0)), TC[1] + 10.6 * math.sin(math.radians(125.0)),
                               zr(485.0) + 5.2), (TC[0] + 9.0 * math.cos(math.radians(215.0)),
                                                  TC[1] + 9.0 * math.sin(math.radians(215.0)), zr(575.0) + 2.0), 13),
    "CAM_SGCave_Arrival": ((0.0, 298.0, _E + 1.6), (0.0, 150.0, -2.0), 15),
    "CAM_SGCave_Bridge": ((-84.0, 262.0, _E), (-20.0, 196.0, 4.0), 15),
    "CAM_SGCave_Forge": ((-45.0, 176.0, ZF + 7.2), (-78.0, 150.0, ZF + 3.0), 16),
    "CAM_SGCave_MapRoom": ((47.0, 178.0, ZF + 8.0), (73.0, 160.0, ZF + 3.5), 17),
    "CAM_SGCave_Portal": ((6.0, 158.0, ZF + 6.0), (0.0, 100.0, 7.5), 17),
    "CAM_SGCave_Overview": ((50.0, 294.0, 24.0), (-12.0, 150.0, -6.0), 13),
    "CAM_SGCave_TowerFromFloor": ((34.0, 262.0, ZF + 5.2), (0.0, 318.0, 14.0), 14),
}


def build():
    import time
    t0 = time.time()
    nb = rock_walls()
    ns = ceiling()
    npl = floor()
    bridge()
    nave()
    ops = tower_and_spiral()
    gallery()
    grand_stair()
    walkways()
    portal()
    forge()
    maproom()
    nc = crystals()
    join_parts()
    lights()
    shell_col()
    import os
    if os.environ.get("SG_CAVE_PREVIEW"):          # so para os renders da zona (nada disso vai para o export)
        preview_shaft()
        SL.dummy("SCALE_Dummy_CavePortal", 5.0, 111.0, DZ, math.pi / 2)
        SL.dummy("SCALE_Dummy_CaveForge", -64.0, 163.0, PF_Z, math.pi)
    print("CAVE build: blocos de rocha %d, estalactites %d, lajes %d, cristais %d (%.1fs)" % (nb, ns, npl, nc,
                                                                                            time.time() - t0))
