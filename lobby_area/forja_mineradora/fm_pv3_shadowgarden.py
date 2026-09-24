# fm_pv3_shadowgarden - portal Shadow Garden v3 (passe final): "ARCO DA LUA"
# UM objeto iconico: arco gotico ogival de pedra negra polida, agora na altura da familia (extradorso em T+30,
# remate prata ate ~T+31). A CABECA DA OGIVA E VAZADA: acima da nascenca so ha ceu, o aro da espiral e a LUA
# CRESCENTE acesa, que recorta contra o fundo e se apoia no topo do oculo por uma haste prata curta. Abaixo da
# nascenca, os cantos entre o oculo e as jambas sao fechados (preto-violeta fosco, soleira prata na nascenca) e
# seguram o anel da espiral.
# Lua: placa prata fina por tras (0.13 de contorno) + corpo violeta aceso + faixa lilas + borda interna lavanda
# (gradiente em 3 passos que tambem vale no Roblox: 3 pecas Neon). Filete fino aceso na borda do vao (violeta com
# nucleo lilas, abaixo da lua na hierarquia: espiral > lua > chamas > filete).
# Base de lajes octogonais de marmore negro (espelhos de 0.55). Props com proposito, fora do disco em A/B/C/G:
#   esq: candelabro PRATA de 3 velas pretas, chamas lisas (bulbo lavanda + lingua violeta), luz violeta curta;
#   dir: roseira seca cinza-violeta (tronco torcido, 3 galhos >= 1.0 de espessura + graveto), 3 rosas lisas em
#        espiral com miolo aceso, junto ao pilar direito e por fora dele.
# Costas: friso prata na ogiva, nichos nas 3 faces dos pilares, tambor da espiral fechado em preto fosco com aro prata
# e lua prata em relevo raso; a lua da frente e prata por tras.
# Brilhos num objeto proprio SEM sombra (no Roblox: Neon, CastShadow=false). Sem texto, nada solto.
#
# PLANO (studs; x relativo a px, z relativo a T):
#   espiral        centro (0, 11.2), r 7.5 (fixa)   anel de pedra r 7.74..8.22 + labio prata
#   vao            meia-largura 9.1; filete (borda interna) r RI-0.08..RI+0.10, nucleo RI-0.04..RI+0.05
#   ogiva          nascenca z 13.5, faixa 1.5, extradorso no apice z 30.0 (RI resolvido), remate ate ~30.95
#   pilares        x 9.1..12.3, capitel ate 12.9, plinto 8.7..12.7; pinaculo 1.0 com topo ~21.4
#   lua            R 3.3 (r 0.9R, d 0.4R, abre a 50 graus), centro (1.3, 23.62), z 20.3..26.6; folga 1.3 do filete
#   props          candelabro (-12.2, PY-4.6) | roseira (12.6, PY-3.3)   (fora do disco em A_Hero, B, C e G_Far)
import math
from mathutils import Vector
import bmesh
import bpy
import fm_lib
from fm_lib import D, col_box, col_box2, light
import fm_portal_kit as K
from fm_portal_kit import V
import fm_layout as L
from fm_parts import frustum

_M = fm_lib.MATS.setdefault
S = fm_lib.S
_M("P_SG_Obsidian", ((0.0105, 0.0082, 0.0180), 0.16, 0.0, 0, None, 0.05))   # #1a1624 pedra negra polida (arco)
_M("P_SG_Marble",   ((0.030, 0.027, 0.040), 0.50, 0.0, 0, None, 0.06))     # marmore negro brunido (lajes)
_M("P_SG_Violet",   ((0.0080, 0.0038, 0.0210), 0.92, 0.0, 0, None, 0.03))  # preto-violeta FOSCO (cantos, nichos, verso)
_M("P_SG_Silver",   ((0.46, 0.48, 0.55), 0.28, 0.0, 0, None, 0.03))        # prata clara fria (~#B4B8C4)
_M("P_SG_Deadwood", ((0.068, 0.058, 0.084), 0.80, 0.0, 0, None, 0.05))     # madeira seca cinza-violeta (#4A4451)
_M("P_SG_Rose",     ((0.122, 0.021, 0.402), 0.50, 0.0, 0, None, 0.04))     # petalas violeta (#6228AA)
# brilhos (nome *_Glow = Neon sem sombra no Roblox; a cor BASE e a cor que o Roblox recebe).
# Preview (AgX Punchy, exposicao 0.45, medido em design/emit_cal.py): violeta (0.3, 0, 1) x 1.3 -> #8A63D0;
# lavanda (0.45, 0.16, 1) x 2.6 -> ~#BCA8E1. Emissao <= 3. As 3 cores Neon ficam a > 70 (sRGB) uma da outra: o fold
# de Neon do export_roblox (FOLD_DIST_NEON) nao junta os passos do gradiente da lua.
_M("P_SG_Moon_Glow", (S(139, 92, 246), 1.0, 0.0, 1.3, (0.30, 0.0, 1.0), 0.0))     # violeta saturado #8B5CF6
_M("P_SG_Lilac_Glow", (S(184, 155, 250), 1.0, 0.0, 1.9, (0.36, 0.06, 1.0), 0.0))   # lilas (passo do meio) #B89BFA
_M("P_SG_Core_Glow", (S(230, 218, 255), 1.0, 0.0, 2.6, (0.45, 0.16, 1.0), 0.0))   # lavanda quase branca #E6DAFF

KEY = "ShadowGarden"
IDX = L.PORTAL_KEYS.index(KEY)          # posicao na fileira pela ordem do jogo (area 4)
C = "06_PORTALS"
A = "Portal"
T = L.TERR
PY = L.PORTAL_Y
Y0 = L.FLIGHT2_Y1
SZ = T + 11.2

OBS, MAR, VIO, SIL, GL = "P_SG_Obsidian", "P_SG_Marble", "P_SG_Violet", "P_SG_Silver", "P_Shadow_Glow"
DW, ROSE, MOON, CORE, LIL = "P_SG_Deadwood", "P_SG_Rose", "P_SG_Moon_Glow", "P_SG_Core_Glow", "P_SG_Lilac_Glow"

# arco
AI = 9.1            # meia-largura do vao
W = 1.5             # largura radial da faixa
ZS = T + 13.5       # nascenca
EXT = 30.0          # extradorso no apice (z relativo a T)
_HO = EXT - (ZS - T)
RI = (_HO * _HO - W * W + AI * AI) / (2 * (W + AI))     # raio do intradorso que poe o extradorso em EXT
CO = RI - AI        # deslocamento do centro de cada arco (lado oposto)
YF, YB = PY - 1.3, PY + 1.7     # frente / costas da faixa
XP = 12.3           # face externa do pilar
FI_IN, FI_OUT = -0.08, 0.1      # filete (offset radial sobre RI)
FC_IN, FC_OUT = -0.04, 0.05     # nucleo do filete
FY0, FY1 = PY - 1.47, PY - 1.0  # filete em y (0.06 a frente do pilar, 0.17 a frente da faixa)
RING_R, RING_W = 7.98, 0.48     # anel de pedra do oculo (r 7.74..8.22)
PIN_W = 1.0         # fuste do pinaculo
PIN_X = AI + W + 0.7 + PIN_W / 2    # centro do pinaculo (face interna 0.7 alem do extradorso na nascenca)
TY0, TY1 = PY - 0.8, PY + 1.2   # cantos fechados do timpano

# lua (design/moonfit.py: maior lua com folga >= 0.95 do filete e 0.9 do anel; aqui com margem)
MOON_R = 3.3
MOON_r, MOON_d, MOON_TH = 0.9 * MOON_R, 0.4 * MOON_R, D(50)
MOON_DX, MOON_DZ = 1.3, 12.42           # centro relativo a (px, SZ)
MOON_RIM = 0.13                         # contorno prata (placa de tras)
MOON_EDGE, MOON_MID = 0.2, 0.5        # faixa lavanda / lilas na borda interna (gradiente em 3 passos)

_TRIS = []


def _tri_count(*mbs):
    return sum(len(f.verts) - 2 for m in mbs for f in m.bm.faces)


def _mark(label, *mbs):
    _TRIS.append((label, _tri_count(*mbs)))


def apex(r):
    return ZS + math.sqrt(r * r - CO * CO)


def arc_half(r, side, n=16):
    """pontos (x, z) relativos a px de um lado da ogiva (side=-1 esquerdo): da nascenca ate a ponta"""
    a1 = math.acos(CO / r)
    cx = -side * CO
    out = []
    for i in range(n + 1):
        t = a1 * i / n
        ang = t if side > 0 else math.pi - t
        out.append((cx + math.cos(ang) * r, ZS + math.sin(ang) * r))
    out[-1] = (0.0, apex(r))
    return out


def lancet_path(e, zbot, n=12):
    """contorno do vao deslocado de e sobre o intradorso: jamba esq (de zbot a nascenca) + ogiva + jamba dir"""
    pts = [(-(AI + e), zbot)] + arc_half(RI + e, -1, n) + list(reversed(arc_half(RI + e, 1, n)[:-1]))
    return pts + [(AI + e, zbot)]


def lancet_half(ai, ri, zs, r, side, n=10):
    """meia ogiva generica (x relativo, z): vao ai, raio ri, nascenca zs, raio da curva r (ri ou ri + largura)"""
    co = ri - ai
    a1 = math.acos(co / r)
    out = []
    for i in range(n + 1):
        t = a1 * i / n
        ang = t if side > 0 else math.pi - t
        out.append((-side * co + math.cos(ang) * r, zs + math.sin(ang) * r))
    out[-1] = (0.0, zs + math.sqrt(r * r - co * co))
    return out


def niche(mb, c, z0, zs, u, nrm, ai=0.8, ri=1.9, w=0.3, n=4):
    """arco cego (eco da ogiva) numa face de pilar: moldura fina de pedra + fundo preto-violeta.
    c = centro da base na face (Vector), u = direcao horizontal da face, nrm = normal para fora da face."""
    c, u, nrm = Vector(c), Vector(u).normalized(), Vector(nrm).normalized()
    li, lo = lancet_half(ai, ri, zs, ri, -1, n), lancet_half(ai, ri, zs, ri + w, -1, n)
    ri_, ro_ = lancet_half(ai, ri, zs, ri, 1, n), lancet_half(ai, ri, zs, ri + w, 1, n)
    inner = [(-ai, z0)] + li + list(reversed(ri_[:-1])) + [(ai, z0)]
    outer = [(-ai - w, z0)] + lo + list(reversed(ro_[:-1])) + [(ai + w, z0)]

    def P3(q, off):
        return V(c.x, c.y, 0.0) + u * q[0] + V(0, 0, q[1]) + nrm * off
    band3(mb, [P3(q, 0.0) for q in inner], [P3(q, 0.0) for q in outer], nrm * 0.2, nrm * -0.05, OBS, 0.0)
    K.plate(mb, inner, V(c.x, c.y, 0.0) + nrm * 0.03, u, (0, 0, 1), 0.1, VIO)


def ring_closed(mb, c, R, u, v, w, h, m, n=44):
    """aro fechado SEM costura (secao w radial x h na normal do plano (u, v))"""
    c, u, v = Vector(c), Vector(u).normalized(), Vector(v).normalized()
    nrm = u.cross(v).normalized()
    bm = mb.bm
    prof = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
    rings = []
    for i in range(n):
        a = math.tau * i / n
        rd = u * math.cos(a) + v * math.sin(a)
        rings.append([bm.verts.new(c + rd * (R + pr) + nrm * pn) for pr, pn in prof])
    fs = []
    for i in range(n):
        r0, r1 = rings[i], rings[(i + 1) % n]
        for j in range(4):
            j2 = (j + 1) % 4
            fs.append(bm.faces.new((r0[j], r0[j2], r1[j2], r1[j])))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    mb._post([q for r in rings for q in r], m, None, 0, 1)


def band3(mb, inner, outer, off0, off1, m, bevel=0.2):
    """faixa entre duas polilinhas 3D (mesmo numero de pontos) extrudada entre os deslocamentos off0 e off1"""
    bm = mb.bm
    fi = [bm.verts.new(p + off0) for p in inner]
    fo = [bm.verts.new(p + off0) for p in outer]
    bi = [bm.verts.new(p + off1) for p in inner]
    bo = [bm.verts.new(p + off1) for p in outer]
    fs = []
    for k in range(len(inner) - 1):
        fs.append(bm.faces.new((fi[k], fo[k], fo[k + 1], fi[k + 1])))
        fs.append(bm.faces.new((bi[k + 1], bo[k + 1], bo[k], bi[k])))
        fs.append(bm.faces.new((fi[k + 1], bi[k + 1], bi[k], fi[k])))
        fs.append(bm.faces.new((fo[k], bo[k], bo[k + 1], fo[k + 1])))
    fs.append(bm.faces.new((fi[0], bi[0], bo[0], fo[0])))
    fs.append(bm.faces.new((fo[-1], bo[-1], bi[-1], fi[-1])))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    mb._post(fi + fo + bi + bo, m, None, bevel, 1, angle=0.6)


def band(mb, inner, outer, y0, y1, m, bevel=0.2):
    """faixa extrudada em Y entre duas polilinhas (x, z) absolutas com o mesmo numero de pontos"""
    band3(mb, [V(p[0], 0.0, p[1]) for p in inner], [V(p[0], 0.0, p[1]) for p in outer], V(0, y0, 0), V(0, y1, 0), m,
          bevel)


def oct_poly(x0, x1, y0, y1, cf, cb=None):
    cb = cf if cb is None else cb
    return [(x0 + cf, y0), (x1 - cf, y0), (x1, y0 + cf), (x1, y1 - cb), (x1 - cb, y1), (x0 + cb, y1), (x0, y1 - cb),
            (x0, y0 + cf)]


def _dedup(pts):
    out = []
    for p in pts:
        if not out or (abs(p[0] - out[-1][0]) + abs(p[1] - out[-1][1])) > 1e-4:
            out.append(p)
    if len(out) > 2 and (abs(out[0][0] - out[-1][0]) + abs(out[0][1] - out[-1][1])) < 1e-4:
        out.pop()
    return out


def offset_poly(pts, e):
    """desloca um poligono convexo anti-horario de e para fora (e < 0: para dentro)"""
    pts = _dedup(pts)
    n = len(pts)
    out = []
    for i in range(n):
        p0, p1, p2 = Vector((*pts[i - 1], 0)), Vector((*pts[i], 0)), Vector((*pts[(i + 1) % n], 0))
        d0, d1 = (p1 - p0).normalized(), (p2 - p1).normalized()
        n0, n1 = Vector((d0.y, -d0.x, 0)), Vector((d1.y, -d1.x, 0))
        b = (n0 + n1).normalized()
        q = p1 + b * (e / max(b.dot(n0), 0.3))
        out.append((q.x, q.y))
    return out


def loop_band(mb, poly, e_out, e_in, z0, z1, m):
    """moldura fechada (filete) na borda de um poligono convexo: de poly+e_out a poly-e_in, de z0 a z1"""
    outer, inner = offset_poly(poly, e_out), offset_poly(poly, -e_in)
    bm = mb.bm
    n = len(outer)
    ob = [bm.verts.new((p[0], p[1], z0)) for p in outer]
    ot = [bm.verts.new((p[0], p[1], z1)) for p in outer]
    ib = [bm.verts.new((p[0], p[1], z0)) for p in inner]
    it = [bm.verts.new((p[0], p[1], z1)) for p in inner]
    fs = []
    for i in range(n):
        j = (i + 1) % n
        fs.append(bm.faces.new((ob[i], ob[j], ot[j], ot[i])))
        fs.append(bm.faces.new((it[i], it[j], ib[j], ib[i])))
        fs.append(bm.faces.new((ot[i], ot[j], it[j], it[i])))
        fs.append(bm.faces.new((ib[i], ib[j], ob[j], ob[i])))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    mb._post(ob + ot + ib + it, m, None, 0, 1)


def col_oct(x0, x1, y0, y1, cf, cb, z0, z1):
    """octogono alongado (chanfro cf na frente, cb atras) = cruz de 2 caixas"""
    col_box2(A, (x0, y0 + cf * 0.5, z0), (x1, y1 - cb * 0.5, z1))
    k = max(cf, cb) * 0.6
    col_box2(A, (x0 + k, y0, z0), (x1 - k, y1, z1))


def crescent_pts(R, r, d, theta, n=60):
    """lua crescente 2D: circulo R menos circulo r deslocado d na direcao theta (mordida)"""
    ui = (R * R - r * r + d * d) / (2 * d)
    vi = math.sqrt(max(R * R - ui * ui, 1e-6))
    phi = math.atan2(vi, ui)
    psi = math.atan2(vi, ui - d)
    pts = []
    for i in range(n + 1):
        a = phi + (math.tau - 2 * phi) * i / n
        pts.append((math.cos(a) * R, math.sin(a) * R))
    ni = max(8, int(round(n * (math.tau - 2 * psi) * r / ((math.tau - 2 * phi) * R))))
    for i in range(1, ni):
        a = (math.tau - psi) - (math.tau - 2 * psi) * i / ni
        pts.append((d + math.cos(a) * r, math.sin(a) * r))
    c, s = math.cos(theta), math.sin(theta)
    return [(u * c - v * s, u * s + v * c) for u, v in pts]


def crescent_edge_pts(R, ri, ro, d, theta, n=26):
    """faixa na borda INTERNA (mordida) do crescente de raio externo R: entre os circulos ri e ro concentricos a
    mordida (centro em d), recortada pelo circulo R. Mesma rotacao theta de crescent_pts."""
    def inter(rb):
        u = (R * R - rb * rb + d * d) / (2 * d)
        return u, math.sqrt(max(R * R - u * u, 1e-9))
    ut, vt = inter(ri)
    us, vs = inter(ro)
    pt = math.atan2(vt, ut - d)
    ps = math.atan2(vs, us - d)
    pts = []
    for i in range(n + 1):
        a = pt + (math.tau - 2 * pt) * i / n
        pts.append((d + math.cos(a) * ri, math.sin(a) * ri))
    for i in range(n + 1):
        a = (math.tau - ps) - (math.tau - 2 * ps) * i / n
        pts.append((d + math.cos(a) * ro, math.sin(a) * ro))
    c, s = math.cos(theta), math.sin(theta)
    return [(u * c - v * s, u * s + v * c) for u, v in pts]


def _fil_clear(u, v):
    """folga de um ponto (x relativo, z relativo a SZ) ate a borda interna do filete da ogiva (ou da jamba)"""
    z = v + SZ
    rf = RI + FI_IN
    if z < ZS:
        return rf - CO - abs(u)
    h = z - ZS
    return min(rf - math.hypot(u - CO, h), rf - math.hypot(u + CO, h))


def _smooth_from(mb, n0):
    for f in list(mb.bm.faces)[n0:]:
        f.smooth = True


def flame(gmb, base, h=1.9, r=0.42, twist=0.2, n=10):
    """chama LISA em gota continua: o terco de baixo e o miolo lavanda (nasce fino no pavio, incha), o resto e a
    lingua violeta que continua a MESMA silhueta ate a ponta levemente torcida (sem degrau: le como uma chama so,
    clara embaixo e roxa na ponta). Formas de revolucao suaves, sombreamento liso: nada de cristal."""
    b = Vector(base)

    def axis(f):
        return b + V(twist * h * f * f * math.cos(f * 2.6), twist * h * 0.6 * f * f * math.sin(f * 2.6), h * f)
    n0 = len(gmb.bm.faces)
    bz = [0.0, 0.07, 0.17, 0.28, 0.4]
    br = [0.2, 0.66, 0.88, 0.8, 0.3]
    K.loft(gmb, [axis(f) for f in bz], [K.circ(max(r * p, 0.03), n) for p in br], CORE, True, up=(1, 0, 0))
    tz = [0.3, 0.44, 0.6, 0.76, 0.9, 1.0]
    tr = [0.8, 0.68, 0.5, 0.3, 0.13, 0.02]
    K.loft(gmb, [axis(f) for f in tz], [K.circ(max(r * p, 0.02), n) for p in tr], MOON, True, up=(1, 0, 0))
    _smooth_from(gmb, n0)


def candelabrum(mb, gmb, x, y, z, h, yaw=0.0, reach=1.3):
    """candelabro de PRATA (le contra o pilar preto): base octogonal, pe conico, haste com no, bracos em J girados
    `yaw`, pratos, velas pretas, chamas lisas. Devolve a lista das pontas das chamas."""
    ca, sa = math.cos(yaw), math.sin(yaw)

    def R(dx, dz):
        return V(dx * ca, dx * sa, dz)
    mb.cyl(1.05, 0.3, (x, y, z + 0.15), (0, 0, D(22.5)), SIL, 8, bevel=0.06)
    mb.cyl(0.85, 0.65, (x, y, z + 0.62), (0, 0, D(22.5)), SIL, 8, r2=0.4, bevel=0.0)
    ht = z + h
    mb.cyl(0.36, h - 0.95, (x, y, z + 0.95 + (h - 0.95) / 2), (0, 0, 0), SIL, 8, r2=0.3, bevel=0.0)
    mb.cyl(0.62, 0.55, (x, y, z + h * 0.45), (0, 0, D(22.5)), SIL, 8, bevel=0.08)
    tops = [V(x, y, ht)]
    p0 = V(x, y, ht - 1.5)
    mb.cyl(0.52, 0.5, p0, (0, 0, D(22.5)), SIL, 8, bevel=0.0)
    for sx in (-1, 1):
        pts = [p0, p0 + R(sx * reach * 0.46, -0.4), p0 + R(sx * reach * 0.9, 0.05), p0 + R(sx * reach, 0.9)]
        K.taper_tube(mb, pts, [0.32, 0.3, 0.28, 0.27], SIL, 8, up=(-sa, ca, 0))
        tops.append(p0 + R(sx * reach, 0.9))
    tips = []
    for i, t in enumerate(tops):
        mb.cyl(0.5, 0.26, t + V(0, 0, 0.13), (0, 0, 0), SIL, 8, r2=0.62, bevel=0.0)
        ch = 1.1 if i == 0 else 0.8
        mb.cyl(0.29, ch, t + V(0, 0, 0.26 + ch / 2), (0, 0, 0), VIO, 8, bevel=0.0)
        fh = 2.2 if i == 0 else 1.8
        flame(gmb, t + V(0, 0, 0.26 + ch - 0.04), fh, 0.44, twist=(0.16 if i != 2 else -0.16))
        tips.append(t + V(0, 0, 0.26 + ch + fh))
    return tips


def _cr(pts, sub=3):
    """polilinha suave (Catmull-Rom) passando pelos pontos de controle"""
    P = [Vector(p) for p in pts]
    P = [P[0] * 2 - P[1]] + P + [P[-1] * 2 - P[-2]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for j in range(sub):
            t = j / sub
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t +
                              (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t))
    out.append(P[-2])
    return out


def rose(mb, gmb, c, axis, s=1.0, twist=0.0, ns=30):
    """rosa LISA em espiral: uma fita de petalas enrolada 2 voltas em torno do miolo (as voltas de dentro altas e
    fechadas, as de fora mais baixas e abertas para fora, borda de cima ondulada = petalas), miolo lavanda aceso no
    centro e calice fechando por baixo. Paredes da fita com sombreamento liso e bordas finas chapadas (a quina da
    borda nao entorta a normal da parede: nada de facetas de cristal)."""
    c = Vector(c)
    ax = Vector(axis).normalized()
    ref = Vector((0, 0, 1)) if abs(ax.z) < 0.9 else Vector((1, 0, 0))
    e1 = ax.cross(ref).normalized()
    e2 = ax.cross(e1).normalized()
    bm = mb.bm
    turns, th = 2.0, 0.08 * s
    rows = []
    for i in range(ns + 1):
        t = i / ns
        a = twist + turns * math.tau * t
        rd = e1 * math.cos(a) + e2 * math.sin(a)
        rr = s * (0.15 + 0.6 * t)
        rb, rt = rr * 0.55, rr * (1.0 + 0.25 * t)
        hb = s * (0.1 - 0.08 * t)
        ht = s * (0.9 - 0.38 * t + 0.05 * math.cos(3.0 * (a - twist)) * t)
        ib = c + ax * hb + rd * rb
        it = c + ax * ht + rd * rt
        rows.append([bm.verts.new(ib), bm.verts.new(it), bm.verts.new(it + rd * th), bm.verts.new(ib + rd * th)])
    fs, walls = [], []
    for r0, r1 in zip(rows, rows[1:]):
        for j in range(4):
            j2 = (j + 1) % 4
            f = bm.faces.new((r0[j], r0[j2], r1[j2], r1[j]))
            fs.append(f)
            if j in (0, 2):         # parede de dentro (ib-it) e de fora (ot-ob); bordas (1, 3) ficam chapadas
                walls.append(f)
    fs.append(bm.faces.new(rows[0]))
    fs.append(bm.faces.new(list(reversed(rows[-1]))))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    mb._post([v for r in rows for v in r], ROSE, None, 0, 1)
    for f in walls:
        if f.is_valid:
            f.smooth = True
    n1 = len(mb.bm.faces)
    K.loft(mb, [c - ax * (0.1 * s), c + ax * (0.08 * s), c + ax * (0.2 * s)],
           [K.circ(0.14 * s, 8, twist), K.circ(0.4 * s, 8, twist), K.circ(0.36 * s, 8, twist)], ROSE, True,
           up=tuple(e1))
    _smooth_from(mb, n1)
    n0 = len(gmb.bm.faces)
    bpts = [c + ax * (h * s) for h in (0.22, 0.44, 0.6, 0.7)]
    profs = [K.circ(0.07 * s, 8, twist), K.circ(0.12 * s, 8, twist), K.circ(0.1 * s, 8, twist),
             K.circ(0.04 * s, 8, twist)]
    K.loft(gmb, bpts, profs, CORE, True, up=tuple(e1))
    _smooth_from(gmb, n0)


def twisted_trunk(mb, pts, radii, m, lobes=3, amp=0.15, turns=0.7, n=10):
    """tronco retorcido: loft de um perfil de `lobes` lobos que gira `turns` voltas ao subir"""
    profs = []
    N = len(pts)
    for i in range(N):
        f = i / (N - 1)
        ph = math.tau * turns * f
        r = radii[i]
        pr = []
        for k in range(n):
            a = math.tau * k / n
            rr = r * (1.0 + amp * (1.0 - 0.5 * f) * math.cos(lobes * a + ph))
            pr.append((math.cos(a) * rr, math.sin(a) * rr))
        profs.append(pr)
    n0 = len(mb.bm.faces)
    K.loft(mb, pts, profs, m, True, up=(1, 0, 0))
    _smooth_from(mb, n0)


def rose_tree(mb, gmb, x, y, z):
    """roseira seca cinza-violeta no plano dos pilares, por fora do pilar direito: raizes curtas mergulhando na laje,
    tronco torcido (r 0.72 -> 0.48), forquilha em z ~3; galho A sobe (um pouco para fora), galho B sobe abrindo para
    dentro (na frente do pilar), galho C baixo para dentro e para a frente, graveto seco sem flor para fora e para
    tras. Galhos com 1.0 de espessura na base, afinando em curva. 3 rosas lisas nas pontas (frente e cima)."""
    import fm_veg_kit as VK
    B = V(x, y, z)
    n0 = len(mb.bm.faces)

    def P_(dx, dy, dz):
        return B + V(dx, dy, dz)

    def limb(ctrl, r0, r1, n=6, sub=2, tip=False):
        pts = _cr([P_(*c) for c in ctrl], sub)
        m = len(pts) - 1
        rad = [(r0 + (r1 - r0) * (i / m) ** 1.1) for i in range(m + 1)]
        VK.ttube(mb, pts, rad, DW, n=n, tip=tip, cap0=True, cap1=not tip)
        return pts
    for a, ln in ((D(10), 0.72), (D(110), 0.85), (D(200), 1.0), (D(290), 0.9)):
        ca, sa = math.cos(a), math.sin(a)
        VK.ttube(mb, [B + V(ca * 0.3, sa * 0.3, 0.9), B + V(ca * 0.8 * ln, sa * 0.8 * ln, 0.25),
                      B + V(ca * 1.15 * ln, sa * 1.15 * ln, -0.25)], [0.5, 0.3, 0.12], DW, n=6, cap0=True)
    tr = [(0, 0, -0.4), (0.04, 0.0, 1.0), (0.1, 0.02, 2.1), (0.12, -0.02, 3.2)]
    trunk = _cr([P_(*c) for c in tr], 2)
    nt = len(trunk)
    twisted_trunk(mb, trunk, [(0.72 - 0.26 * (i / (nt - 1)) ** 0.8) for i in range(nt)], DW, n=10)
    ga = limb([(0.1, 0.0, 2.7), (0.3, -0.05, 3.8), (0.55, -0.1, 4.9), (0.62, -0.2, 6.0), (0.45, -0.3, 7.0),
               (0.28, -0.35, 7.7)], 0.5, 0.22)
    gb = limb([(0.06, 0.02, 2.8), (-0.2, 0.0, 3.9), (-0.65, -0.08, 5.0), (-0.95, -0.15, 6.2), (-1.05, -0.25, 7.3),
               (-0.95, -0.3, 8.1)], 0.5, 0.22)
    gc = limb([(0.04, 0.0, 1.9), (-0.42, -0.3, 2.6), (-0.82, -0.62, 3.4), (-1.0, -0.86, 4.25)], 0.46, 0.22)
    limb([(0.08, 0.05, 2.3), (0.5, 0.25, 2.9), (0.78, 0.42, 3.7), (0.88, 0.52, 4.5)], 0.26, 0.05, 6, 2, tip=True)
    ta = tuple(ga[6] - B)
    limb([ta, (ta[0] + 0.3, ta[1] + 0.05, ta[2] + 0.5), (ta[0] + 0.38, ta[1] + 0.08, ta[2] + 1.15)], 0.2, 0.05, 6,
         2, tip=True)
    tb = tuple(gb[5] - B)
    limb([tb, (tb[0] - 0.4, tb[1] + 0.05, tb[2] + 0.35), (tb[0] - 0.62, tb[1] + 0.05, tb[2] + 0.95)], 0.19, 0.05, 6,
         2, tip=True)
    _smooth_from(mb, n0)
    for g, sz, tw in ((ga, 1.0, 0.3), (gb, 1.15, 1.1), (gc, 1.05, 2.0)):
        tip, pre = g[-1], g[-3]
        d = (tip - pre).normalized()
        axis = (d + Vector((0, -0.8, 0.7))).normalized()       # olha para a frente e para cima
        rose(mb, gmb, tip - d * 0.12, axis, sz, tw)
    return [ga[-1], gb[-1], gc[-1]]


def _glow_unlit(names):
    """Blender (preview rico): brilho = so emissao (base preta, sem especular) -> cor chapada luminosa, sem lado de
    sombra. A cor base registrada em MATS (e a diffuse_color do material) continua sendo a cor do Neon no Roblox."""
    if fm_lib.PREVIEW == "roblox":
        return
    for nm in names:
        m = fm_lib.mat(nm)
        if m is None or not m.use_nodes:
            continue
        nt = m.node_tree
        bs = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
        if bs is None:
            continue
        col, rough, metal, emit, ecol, var = fm_lib.MATS[nm]
        for lk in list(bs.inputs["Base Color"].links):
            nt.links.remove(lk)
        bs.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1.0)
        bs.inputs["Roughness"].default_value = 1.0
        if "Specular IOR Level" in bs.inputs:
            bs.inputs["Specular IOR Level"].default_value = 0.0
        for lk in list(bs.inputs["Emission Color"].links):
            nt.links.remove(lk)
        bs.inputs["Emission Color"].default_value = (*(ecol or col), 1.0)
        bs.inputs["Emission Strength"].default_value = emit
        m.diffuse_color = (*col, 1.0)


def _matte(name, spec=0.0, rough=1.0):
    """Blender: corta o especular de um material deste portal (espiral, marmore, verso fosco)"""
    m = bpy.data.materials.get(name)
    if m is None or not m.use_nodes:
        return
    for n in m.node_tree.nodes:
        if n.type == "BSDF_PRINCIPLED":
            n.inputs["Roughness"].default_value = rough
            if "Specular IOR Level" in n.inputs:
                n.inputs["Specular IOR Level"].default_value = spec


def build(rng):
    import fm_portals as P
    px = L.PORTAL_X[IDX]
    _TRIS.clear()

    def X(dx):
        return px + dx
    mb = K.LeanMB("PORTAL_ShadowGarden_MoonArch", C, rng, vcap=2)
    gmb = K.LeanMB("PORTAL_ShadowGarden_Glow", C, rng, vcap=1)      # brilhos: objeto sem sombra

    # ---------------------------------------------------------------- base: lajes octogonais de marmore negro
    t1 = (X(-13.6), X(13.6), Y0 + 1.2, PY + 5.6, 3.2, 3.0)
    mb.prism(oct_poly(*t1[:6]), T - 0.35, T + 0.45, MAR, 0.2)
    col_oct(*t1, T - 1.0, T + 0.45)
    t2 = (X(-8.6), X(8.6), Y0 + 3.8, PY + 1.4, 2.4, 0.0)
    mb.prism(oct_poly(*t2[:6]), T + 0.4, T + 1.0, MAR, 0.15)
    col_oct(*t2, T - 1.0, T + 1.0)
    t3 = (X(-7.0), X(7.0), Y0 + 6.4, PY + 0.4, 2.0, 0.0)
    mb.prism(oct_poly(*t3[:6]), T + 0.95, T + 1.55, MAR, 0.15)
    col_oct(*t3, T - 1.0, T + 1.55)
    for tt, ztop in ((t1, T + 0.45), (t2, T + 1.0), (t3, T + 1.55)):
        loop_band(mb, oct_poly(*tt[:6]), 0.05, 0.24, ztop - 0.09, ztop + 0.06, SIL)
    _mark("base", mb, gmb)

    # ---------------------------------------------------------------- jambas / pilares, capiteis, pinaculos
    zb = T + 0.45
    for s in (-1, 1):
        xin, xout = X(s * AI), X(s * XP)
        xc = (xin + xout) / 2
        wd = abs(xout - xin)
        ym = (YF + YB) / 2 + 0.1
        dep = YB - YF + 0.4
        mb.box((wd + 0.8, 4.4, 1.2), (xc, PY + 0.2, zb + 0.6), (0, 0, 0), OBS, 0.25)            # plinto
        pl = [(xc - (wd + 0.8) / 2, PY - 2.0), (xc + (wd + 0.8) / 2, PY - 2.0), (xc + (wd + 0.8) / 2, PY + 2.4),
              (xc - (wd + 0.8) / 2, PY + 2.4)]
        loop_band(mb, pl, 0.05, 0.3, zb + 1.1, zb + 1.26, SIL)                                   # filete do plinto
        mb.box((wd, dep, ZS - 1.2 - (zb + 1.2)), (xc, ym, (zb + 1.2 + ZS - 1.2) / 2), (0, 0, 0), OBS, 0.2)
        niche(mb, (xc, ym - dep / 2), zb + 1.9, ZS - 4.8, (1, 0, 0), (0, -1, 0), 0.95, 2.2)      # arco cego (frente)
        niche(mb, (xc, ym + dep / 2), zb + 1.9, ZS - 4.8, (1, 0, 0), (0, 1, 0), 0.95, 2.2)       # arco cego (costas)
        niche(mb, (xout, ym), zb + 1.9, ZS - 4.8, (0, -s, 0), (s, 0, 0), 1.0, 2.3)                # arco cego (lado)
        mb.box((wd + 0.4, dep + 0.3, 0.4), (xc + s * 0.12, ym, ZS - 1.35), (0, 0, 0), SIL, 0.1)  # colar prata
        mb.box((wd + 0.6, dep + 0.6, 1.2), (xc + s * 0.3, ym, ZS - 0.6), (0, 0, 0), OBS, 0.25)   # capitel
        # pinaculo curto no ombro (vao limpo ate a faixa) + anel e bola prata
        xpn = X(s * PIN_X)
        mb.box((PIN_W, PIN_W, 3.8), (xpn, PY + 0.3, ZS + 1.9), (0, 0, 0), OBS, 0.18)
        mb.box((PIN_W + 0.45, PIN_W + 0.45, 0.4), (xpn, PY + 0.3, ZS + 3.7), (0, 0, 0), SIL, 0.1)
        frustum(mb, (xpn, PY + 0.3, ZS + 3.9), PIN_W + 0.15, PIN_W + 0.15, 0.1, 0.1, 3.5, OBS)
        n_ = len(mb.bm.faces)
        mb.ico(0.3, (xpn, PY + 0.3, ZS + 3.9 + 3.5 + 0.12), SIL, 1)
        _smooth_from(mb, n_)
    # pilar + capitel (ate a nascenca; pinaculos e faixa ficam fora do alcance do jogador)
    col_box2(A, (X(-XP - 0.6), PY - 1.9, T), (X(-AI), PY + 2.4, ZS))
    col_box2(A, (X(AI), PY - 1.9, T), (X(XP + 0.6), PY + 2.4, ZS))
    _mark("pilares", mb, gmb)

    # ---------------------------------------------------------------- a ogiva (faixa unica, das nascencas a ponta)
    li, lo = arc_half(RI, -1), arc_half(RI + W, -1)
    ri, ro = arc_half(RI, 1), arc_half(RI + W, 1)
    inner = [(X(u), z) for u, z in li] + [(X(u), z) for u, z in reversed(ri[:-1])]
    outer = [(X(u), z) for u, z in lo] + [(X(u), z) for u, z in reversed(ro[:-1])]
    band(mb, inner, outer, YF, YB, OBS, 0.2)
    zap_i = apex(RI)
    zap_o = apex(RI + W)
    # friso prata fino acompanhando o extradorso, na frente E nas costas (desenha a silhueta da ogiva nos 360)
    hr = RI + W - 0.36
    for yy in (YF - 0.07, YB + 0.07):
        hpath = [V(X(u), yy, z) for u, z in arc_half(hr, -1, 10)]
        hpath += [V(X(u), yy, z) for u, z in reversed(arc_half(hr, 1, 10)[:-1])]
        mb.sweep(hpath, [(-0.14, -0.14), (0.14, -0.14), (0.14, 0.14), (-0.14, 0.14)], SIL, True, up=(0, 1, 0))
    # remate prata no apice: base de 4 faces que abraca o bico + bola (le em G_Far; topo ~T+30.95)
    ym_ = (YF + YB) / 2
    frustum(mb, (px, ym_, zap_o - 0.55), 0.95, 0.95, 0.3, 0.3, 0.85, SIL)
    mb.ico(0.36, (px, ym_, zap_o + 0.58), SIL, 2)
    _mark("ogiva", mb, gmb)

    # filete fino aceso na borda interna (jamba + ogiva), apoiado no plinto: violeta + nucleo lavanda  [brilho]
    zf = zb + 1.26
    fin = [(X(u), z) for u, z in lancet_path(FI_IN, zf)]
    fout = [(X(u), z) for u, z in lancet_path(FI_OUT, zf)]
    band(gmb, fin, fout, FY0, FY1, MOON, 0.0)
    cin = [(X(u), z) for u, z in lancet_path(FC_IN, zf + 0.05)]
    cout = [(X(u), z) for u, z in lancet_path(FC_OUT, zf + 0.05)]
    band(gmb, cin, cout, FY0 - 0.04, FY0 + 0.2, LIL, 0.0)
    _mark("filete", mb, gmb)

    # ---------------------------------------------------------------- cantos fechados do timpano (ate a nascenca)
    rh = 7.6
    a_top = 180.0 - math.degrees(math.asin((ZS - SZ) / rh))
    n = 16
    swl = [(math.cos(D(270 - (270 - a_top) * i / n)) * rh, SZ + math.sin(D(270 - (270 - a_top) * i / n)) * rh)
           for i in range(n + 1)]
    left = [(-(AI + 0.3), zb + 0.45), (0.0, zb + 0.45)] + swl + [(-(AI + 0.3), ZS)]
    right = [(-u, z) for (u, z) in reversed(left)]
    for poly in (left, right):
        K.plate(mb, poly, V(px, (TY0 + TY1) / 2, 0.0), (1, 0, 0), (0, 0, 1), TY1 - TY0, VIO)
    xs_top = math.sqrt(RING_R ** 2 - (ZS - SZ) ** 2)
    for s_ in (-1, 1):      # soleira prata na nascenca (arremata o topo dos cantos, alinhada ao capitel)
        mb.box2((X(s_ * (xs_top - 0.1)), TY0 - 0.08, ZS - 0.14), (X(s_ * (AI + 0.05)), TY1 + 0.08, ZS + 0.1), SIL,
                0.05)
    # oculo: anel fino de obsidiana (r 7.74..8.22) + labio prata para dentro do anel
    ring_closed(mb, V(px, PY - 0.45, SZ), RING_R, (1, 0, 0), (0, 0, 1), RING_W, 1.7, OBS, n=36)
    ring_closed(mb, V(px, PY - 1.36, SZ), 7.82, (1, 0, 0), (0, 0, 1), 0.24, 0.27, SIL, n=32)
    # colisao: cantos baixos + OMBROS (entre a cruz do tambor e o pilar, ate a nascenca) + cruz do prato/tambor
    for s_ in (-1, 1):
        col_box2(A, (X(s_ * 4.0), TY0 + 0.05, zb), (X(s_ * AI), TY1 + 0.05, T + 4.7))
        col_box2(A, (X(s_ * 7.8), TY0 + 0.05, T + 4.7), (X(s_ * AI), TY1 + 0.05, ZS))
    for hx, hz in ((5.35, 5.35), (6.95, 2.87), (2.87, 6.95)):
        col_box2(A, (X(-hx), PY + 0.2, SZ - hz), (X(hx), PY + 2.3, SZ + hz))
    _mark("timpano+oculo", mb, gmb)

    # ---------------------------------------------------------------- lua crescente na cabeca vazada
    moon = [(u + MOON_DX, v + MOON_DZ) for u, v in crescent_pts(MOON_R, MOON_r, MOON_d, MOON_TH, 34)]
    R2, r2 = MOON_R - MOON_RIM, MOON_r + MOON_RIM
    body = [(u + MOON_DX, v + MOON_DZ) for u, v in crescent_pts(R2, r2, MOON_d, MOON_TH, 32)]
    mid = [(u + MOON_DX, v + MOON_DZ) for u, v in crescent_edge_pts(R2, r2 - 0.01, r2 + MOON_MID, MOON_d,
                                                                     MOON_TH, 16)]
    edge = [(u + MOON_DX, v + MOON_DZ) for u, v in crescent_edge_pts(R2, r2 - 0.02, r2 + MOON_EDGE, MOON_d,
                                                                      MOON_TH, 16)]
    K.plate(mb, moon, V(px, PY + 0.25, SZ), (1, 0, 0), (0, 0, 1), 0.4, SIL, 0.0)       # placa prata PY+0.05..0.45
    K.plate(gmb, body, V(px, PY - 0.175, SZ), (1, 0, 0), (0, 0, 1), 0.55, MOON, 0.0)   # corpo violeta PY-0.45..0.10
    K.plate(gmb, mid, V(px, PY - 0.19, SZ), (1, 0, 0), (0, 0, 1), 0.56, LIL, 0.0)      # passo lilas PY-0.47..0.09
    K.plate(gmb, edge, V(px, PY - 0.2, SZ), (1, 0, 0), (0, 0, 1), 0.58, CORE, 0.0)     # borda lavanda PY-0.49..0.09
    # haste prata: do topo do oculo ao ponto mais baixo da lua (com um no em bola) -> a lua se apoia no anel
    pm = min(moon, key=lambda q: math.hypot(q[0], q[1]))
    dv = Vector((pm[0], 0.0, pm[1])).normalized()
    ls = math.hypot(pm[0], pm[1])
    ycs = PY - 0.1
    a_ = V(px, ycs, SZ) + dv * 7.95
    b_ = V(px, ycs, SZ) + dv * (ls + 0.4)
    K.taper_tube(mb, [a_, b_], [0.3, 0.22], SIL, 8, up=(0, 1, 0))
    n_ = len(mb.bm.faces)
    mb.ico(0.36, V(px, ycs, SZ) + dv * ((RING_R + RING_W / 2 + ls) / 2), SIL, 1)
    _smooth_from(mb, n_)
    fc = [_fil_clear(u, v) for u, v in moon]
    print("LUA ShadowGarden: z %.2f..%.2f (ponta int %.2f ext %.2f) folga ao filete min %.2f, ao anel %.2f, "
          "RI %.3f" % (min(v for _, v in moon) + SZ - T, max(v for _, v in moon) + SZ - T, zap_i - T, zap_o - T,
                       min(fc), ls - (RING_R + RING_W / 2), RI))
    mc = V(px + MOON_DX - 1.0, PY - 3.2, SZ + MOON_DZ - 0.8)
    lm = light("L_P_ShadowGarden_Moon", "POINT", tuple(mc), 420, (0.55, 0.22, 1.0), 1.2)
    lm.data.use_shadow = False
    if hasattr(lm.data, "specular_factor"):
        lm.data.specular_factor = 0.3
    lm["rbx_range"] = 10.0
    lm["rbx_shadows"] = False
    _mark("lua", mb, gmb)

    # ---------------------------------------------------------------- props: candelabro (esq) | roseira (dir)
    cx_, cy_ = X(-12.2), PY - 4.6
    cyaw = D(40)
    tips = candelabrum(mb, gmb, cx_, cy_, zb, 7.2, yaw=cyaw, reach=1.3)
    col_box2(A, (cx_ - 1.05, cy_ - 1.05, T - 0.5), (cx_ + 1.05, cy_ + 1.05, zb + 0.95))           # base
    col_box2(A, (cx_ - 0.5, cy_ - 0.5, zb + 0.95), (cx_ + 0.5, cy_ + 0.5, zb + 5.0))              # haste
    fz = max(t.z for t in tips) - 1.0
    lc = light("L_P_ShadowGarden_Candles", "POINT", (cx_ + 0.5, cy_ - 1.3, fz), 300, (0.6, 0.25, 1.0), 0.3)
    lc.data.use_shadow = False
    if hasattr(lc.data, "specular_factor"):
        lc.data.specular_factor = 0.0
    lc["rbx_range"] = 8.0
    lc["rbx_shadows"] = False
    _mark("candelabro", mb, gmb)
    tx, ty = X(12.6), PY - 3.3
    rose_tree(mb, gmb, tx, ty, zb)
    col_box2(A, (tx - 0.8, ty - 0.8, T - 0.5), (tx + 0.8, ty + 0.8, zb + 3.2))                    # tronco
    col_box2(A, (tx - 2.0, ty - 1.9, zb + 3.2), (tx - 0.2, ty - 0.2, zb + 5.1))                   # rosa baixa
    _mark("roseira", mb, gmb)

    # ---------------------------------------------------------------- costas + espiral
    # verso do tambor FECHADO e FOSCO (preto-violeta), aro prata na borda e lua prata em relevo raso
    ring_closed(mb, V(px, PY + 2.3, SZ), 7.56, (1, 0, 0), (0, 0, 1), 0.55, 0.4, SIL, n=28)
    K.plate(mb, crescent_pts(3.9, 3.51, 1.56, D(50), 28), V(px, PY + 2.33, SZ + 0.6), (1, 0, 0), (0, 0, 1), 0.2,
            SIL, 0.0)
    P.swirl(KEY, px, "P_Shadow_Swirl", mb, VIO, rim_y=-0.6)
    _mark("costas+espiral", mb, gmb)
    ob = mb.finish()
    gob = gmb.finish()
    gob.visible_shadow = False          # brilho nao projeta sombra (no Roblox: Neon, CastShadow=false)
    _glow_unlit([MOON, CORE, LIL])
    _matte("P_Shadow_Swirl", 0.0, 1.0)
    _matte(VIO, 0.0, 1.0)
    for nm in [m.name for m in ob.data.materials if m and m.name.startswith(MAR)]:
        _matte(nm, 0.15, 0.55)
    prev = 0
    parts = []
    for lab, t in _TRIS:
        parts.append("%s=%d" % (lab, t - prev))
        prev = t
    print("TRIS ShadowGarden: " + " ".join(parts) + " total=%d" % prev)
    xs = [v.co.x for o in (ob, gob) for v in o.data.vertices]
    ys = [v.co.y for o in (ob, gob) for v in o.data.vertices]
    zs = [v.co.z for o in (ob, gob) for v in o.data.vertices]
    print("LOTE ShadowGarden: x %.2f..%.2f (px%+.2f..%+.2f) y %.2f..%.2f z %.2f..%.2f" % (
        min(xs), max(xs), min(xs) - px, max(xs) - px, min(ys), max(ys), min(zs) - T, max(zs) - T))


# ======================================================================================================================
# DRESSING DA ESCADA (lance 2) - "BALAUSTRADA DA LUA": objeto PORTAL_ShadowGarden_Stairs (o chamador cria e fecha o MB)
# Faixa do terraco ao lado do poco: y 86.0..99.4, 7.8 <= |x - px| <= 13.9, apoiado em z = T. Um motivo so, espelhado:
#   balaustrada gotica BAIXA de obsidiana na borda do poco (so ela, receita One Piece): soco, arcada de arcos ogivais
#   sobre colunelos (eco da ogiva e dos nichos do portal), corrimao com friso prata; nas duas cabeceiras, um pilar com
#   COROA BAIXA (colar prata, piramide curta de obsidiana, bola prata = eco dos pinaculos do portal), 0.7 embaixo e
#   0.85 no alto. Vista da escada (H_Stairs, camera no ledge em (px, 60, T-3)):
#     - a coroa do alto fica abaixo de T+4.3 (teto ST_CROWN_MAX): nao sobe ate os bracos/velas do candelabro do
#       portal nem ate a copa da roseira;
#     - o pilar-guia fica em y 87.2 (e nao 88.2): assim a coroa e o colar dele saem da faixa de tela da vela esquerda do
#       candelabro do portal em vez de encostar no prato dela.
#   Nada de candelabro/chama no dressing: a peca de luz desta chegada e a do portal.
# So materiais da paleta do portal (obsidiana + prata). Nao usa o rng e passa tint fixo (nao consome o rng compartilhado).
# PLANO (|x - px|, y; z relativo a T):
#   soco        x 8.0..8.9, y 86.85..99.4, z -0.1..0.4
#   pilar-guia  (8.45, 87.2) 0.7 x 0.7 ate 3.3 + colar prata ate 3.42 + coroa 0.7 ate ~3.97 (cabeceira de baixo)
#   pilarete    (8.45, 98.9) 1.0 x 1.0 ate 3.3 + colar prata ate 3.46 + coroa 0.85 ate ~4.13 (cabeceira do alto)
#   arcada      entre as faces 87.55..98.4: ST_NA arcos (nascenca 1.0, corrimao 3.0, friso prata ate 3.14)
#   colisao     uma caixa por lado cobrindo a balaustrada inteira (a cabeceira de baixo ainda cai dentro da colisao do
#               muro alto, UpperWall, y 80..88; nenhuma caixa extra)
ST_TINT = 0.0
ST_X = 8.45                     # eixo da balaustrada (face interna do soco em 8.0)
ST_YP, ST_PW = 87.2, 0.7        # pilar-guia da cabeceira de baixo
ST_YN, ST_NW = 98.9, 1.0        # pilarete da cabeceira do alto
ST_ZC, ST_ZS, ST_ZR, ST_ZN = 0.4, 1.0, 3.0, 3.3      # topo do soco, nascenca, corrimao, topo dos pilares
ST_NA, ST_CW, ST_TH = 4, 0.34, 0.3                  # arcos, colunelo, espessura do painel
ST_CROWN_MAX = 4.3              # teto das coroas (rel T): abaixo dos bracos do candelabro do portal vistos do ledge


def _st_ball(mb, c, r, m, n=6):
    """bola lisa barata (2 aneis x n + polos, sombreamento suave): remate de prata"""
    c = Vector(c)
    bm = mb.bm
    n0 = len(bm.faces)
    rings = []
    for la in (D(-35), D(35)):
        rr, zz = math.cos(la) * r, math.sin(la) * r
        rings.append([bm.verts.new(c + V(math.cos(math.tau * k / n) * rr, math.sin(math.tau * k / n) * rr, zz))
                      for k in range(n)])
    bot, top = bm.verts.new(c - V(0, 0, r)), bm.verts.new(c + V(0, 0, r))
    fs = []
    for k in range(n):
        j = (k + 1) % n
        fs.append(bm.faces.new((bot, rings[0][j], rings[0][k])))
        fs.append(bm.faces.new((rings[0][k], rings[0][j], rings[1][j], rings[1][k])))
        fs.append(bm.faces.new((rings[1][k], rings[1][j], top)))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    mb._post([v for rg in rings for v in rg] + [bot, top], m, ST_TINT, 0, 1)
    _smooth_from(mb, n0)


def _st_crown(mb, x, y, z, w, k=1.0):
    """coroa BAIXA do pilar de largura w (eco dos pinaculos do portal, mas atarracada): piramide curta de obsidiana e
    bola prata, a partir de z (topo do colar prata). k = escala (1.0 no pilarete do alto, ~0.7 no pilar-guia).
    Devolve o topo (z absoluto)."""
    hp, rb = 0.52 * k, 0.17 * k
    mb.cyl((w - 0.08) * 0.7071, hp, (x, y, z + hp / 2), (0, 0, D(45)), OBS, 4, r2=0.08 * k, bevel=0.0, tint=ST_TINT)
    zb = z + hp + 0.6 * rb          # a bola assenta na ponta (a ponta entra ~0.4 rb nela)
    _st_ball(mb, (x, y, zb), rb, SIL)
    return zb + rb


def _st_arcade(mb, x, ya, yb, y0, y1):
    """painel de obsidiana (corrimao) com o intradorso de ST_NA arcos ogivais recortado embaixo, de ya a yb (as pontas
    ficam dentro dos pilaretes), arcos entre as faces y0..y1 + colunelos entre os arcos + friso prata no topo"""
    span = (y1 - y0 - (ST_NA - 1) * ST_CW) / ST_NA
    ai = span / 2
    ri = 1.5 * ai
    zs, zr = T + ST_ZS, T + ST_ZR
    lo, hi = (ya, yb) if ya < yb else (yb, ya)
    bottom = [(lo, zs)]
    for k in range(ST_NA):
        yc = y0 + ai + k * (span + ST_CW)
        arch = lancet_half(ai, ri, zs, ri, -1, 3) + list(reversed(lancet_half(ai, ri, zs, ri, 1, 3)))[1:]
        bottom += [(yc + u, z) for u, z in arch]
        if k < ST_NA - 1:       # colunelo sob a junta entre dois arcos
            yk = yc + ai + ST_CW / 2
            mb.box((ST_CW, ST_CW, ST_ZS - ST_ZC + 0.05), (x, yk, T + (ST_ZC + ST_ZS + 0.05) / 2), (0, 0, 0), OBS, 0.0,
                   tint=ST_TINT)
    poly = bottom + [(hi, zs), (hi, zr), (lo, zr)]
    K.plate(mb, poly, V(x, 0.0, 0.0), (0, 1, 0), (0, 0, 1), ST_TH, OBS, 0.0, tint=ST_TINT)
    mb.box((ST_TH + 0.22, hi - lo, 0.14), (x, (lo + hi) / 2, zr + 0.07), (0, 0, 0), SIL, 0.0, tint=ST_TINT)


def stairs(mb, px, rng):
    """dressing da faixa ao lado do lance 2 (ver o cabecalho acima). `rng` nao e usado (geometria fixa)."""
    n0 = len(mb.bm.faces)
    y_lo, y_hi = ST_YP - ST_PW / 2, ST_YN + ST_NW / 2
    ztop = []
    for s in (-1, 1):
        xb = px + s * ST_X
        # soco continuo (do pilar-guia ao pilarete do alto)
        mb.box((0.9, y_hi - y_lo, ST_ZC + 0.1), (xb, (y_lo + y_hi) / 2, T + (ST_ZC - 0.1) / 2), (0, 0, 0), OBS, 0.0,
               tint=ST_TINT)
        # cabeceira de baixo: pilar-guia + colar prata + coroa 0.7
        mb.box((ST_PW, ST_PW, ST_ZN), (xb, ST_YP, T + ST_ZN / 2), (0, 0, 0), OBS, 0.0, tint=ST_TINT)
        mb.box((ST_PW + 0.14, ST_PW + 0.14, 0.12), (xb, ST_YP, T + ST_ZN + 0.06), (0, 0, 0), SIL, 0.0, tint=ST_TINT)
        ztop.append(_st_crown(mb, xb, ST_YP, T + ST_ZN + 0.12, ST_PW, 0.7))
        # cabeceira do alto: pilarete + colar prata + coroa baixa (0.85)
        mb.box((ST_NW, ST_NW, ST_ZN), (xb, ST_YN, T + ST_ZN / 2), (0, 0, 0), OBS, 0.12, tint=ST_TINT)
        mb.box((ST_NW + 0.2, ST_NW + 0.2, 0.16), (xb, ST_YN, T + ST_ZN + 0.08), (0, 0, 0), SIL, 0.0, tint=ST_TINT)
        ztop.append(_st_crown(mb, xb, ST_YN, T + ST_ZN + 0.16, ST_NW, 0.85))
        # arcada + corrimao entre as faces do pilar-guia e do pilarete
        _st_arcade(mb, xb, ST_YP, ST_YN, ST_YP + ST_PW / 2, ST_YN - ST_NW / 2)
        # colisao: uma caixa para a balaustrada inteira, pilares inclusive (centro em y < 99.5: conta como escada)
        col_box2(A, (px + s * 7.98, y_lo, T), (px + s * 8.95, y_hi, T + ST_ZN))
    assert max(ztop) - T <= ST_CROWN_MAX + 1e-6, "coroa acima do teto (%.2f)" % (max(ztop) - T)
    vs = mb.bm.verts
    dx = [abs(v.co.x - px) for v in vs]
    print("LOTE_ESCADA ShadowGarden: |x-px| %.2f..%.2f y %.2f..%.2f z %.2f..%.2f (rel T) tris=%d coroas=%s" % (
        min(dx), max(dx), min(v.co.y for v in vs), max(v.co.y for v in vs), min(v.co.z for v in vs) - T,
        max(v.co.z for v in vs) - T, sum(len(f.verts) - 2 for f in list(mb.bm.faces)[n0:]),
        ", ".join("%.2f" % (z - T) for z in ztop)))
