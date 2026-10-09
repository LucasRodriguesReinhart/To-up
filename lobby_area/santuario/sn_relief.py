# sn_relief.py (copia adaptada do wb_terrain2 para o Santuario) - PAISAGEM DE FUNDO (ref/crops/fundo.png + casas_esq.png): um anel de RELEVO continuo em volta do
# lago (heightfield), com margem de grama, colinas onduladas com COLCHA DE CAMPOS (verde, dourado, terra lavrada) e
# BOSQUES de pinheiro, e ao fundo uma CORDILHEIRA alta (mais alta ao norte, atras da forja) com rocha nas encostas
# ingremes e NEVE nos picos. Fatiado em setores (MeshPart <= 2048 studs) e por material.
import math
import random

import bmesh
import numpy as np
import sn_lib as SL
import sn_layout as L
from wb_lib import RB, V
W = SL

R0, R1 = 410.0, 1500.0            # raio interno (dentro do lago) e externo
NR, NA = 58, 216                  # aneis radiais x passos angulares
SECTORS = 8


from sn_hills_tex import Noise, HILL_SPAN  # noqa: E402


def height(xs, zs, N):
    """altura (Y Roblox) nos pontos (x, z) do anel"""
    r = np.hypot(xs, zs)
    a = np.arctan2(zs, xs)
    north = np.clip(-np.sin(a), 0, 1)              # -z = norte (atras da forja)
    shore = np.clip((r - 420.0) / 50.0, 0, 1)
    hills_m = np.clip((r - 440.0) / 120.0, 0, 1) * np.clip((900.0 - r) / 200.0, 0, 1)
    mtn_m = np.clip((r - 720.0) / 260.0, 0, 1)
    hx, hz = xs / 160.0, zs / 160.0
    hills = 14.0 + 52.0 * N.fbm(hx + 40, hz + 40, 4) * (0.7 + 0.6 * north)
    mx, mz = xs / 330.0, zs / 330.0
    peaks = N.ridged(mx + 90, mz + 90, 5)
    mtn = (120.0 + 380.0 * peaks ** 1.4) * (0.65 + 0.55 * north)
    h = L.Y_WATER - 6.0 + (8.0 + 0.0) * shore
    h = h + hills * hills_m * shore + mtn * mtn_m
    return h


MTN_V = 650.0          # altura (Y) que vira v = 1 na rampa pintada da serra
MTN_U = 5.0            # repeticoes da rampa numa volta


def _mat_of(xm, zm, ym, slope, rm, f1, f2):
    if rm > 640 and (ym > 105 or slope > 27):
        return "SN_Mountain"
    return "SN_Hills"


def build(coll="02_TERRAIN"):
    """anel de relevo: colinas suaves em 3 verdes + bosque (cor solida, sombreado suave) e a serra com a rampa pintada
    (rocha azulada, neve descendo pelas ravinas). Bosques de pinheiros estilizados nos trechos de floresta."""
    N = Noise(4242)
    rs = np.concatenate([np.linspace(R0, 470.0, 7, endpoint=False), np.geomspace(470.0, R1, NR - 7)])
    an = np.linspace(0, 2 * math.pi, NA, endpoint=False)
    A, Rr = np.meshgrid(an, rs)
    X = Rr * np.cos(A)
    Z = Rr * np.sin(A)
    X = X + (N.v(X / 37.0, Z / 37.0) - 0.5) * (Rr * 0.01)
    Z = Z + (N.v(Z / 41.0 + 5, X / 41.0 + 5) - 0.5) * (Rr * 0.01)
    Y = height(X, Z, N)
    # picos arredondados: suaviza a altura (media dos vizinhos, 2 passadas) so na serra
    for _ in range(2):
        Ys = Y.copy()
        Ys[1:-1, :] = (Y[:-2, :] + 2 * Y[1:-1, :] + Y[2:, :]) / 4
        Ys = (np.roll(Ys, 1, axis=1) + 2 * Ys + np.roll(Ys, -1, axis=1)) / 4
        w = np.clip((Rr - 640.0) / 120.0, 0, 1)
        Y = Y * (1 - w) + Ys * w
    fld = N.v(X / 70.0 + 300, Z / 70.0 + 300)
    fld2 = N.fbm(X / 90.0 + 500, Z / 90.0 + 500, 3)
    objs = []
    per = NA // SECTORS
    r_ = random.Random(9)
    trees = []
    for s in range(SECTORS):
        b = W.Build("WB_Bg_Relief_%d" % s, coll)
        groups = {}
        for j in range(NR - 1):
            for ii in range(per):
                i = s * per + ii
                i2 = (i + 1) % NA
                idx = [(j, i), (j, i2), (j + 1, i2), (j + 1, i)]
                p = [(X[a, c], Z[a, c], Y[a, c]) for (a, c) in idx]
                vs = [RB(x, z, y) for (x, z, y) in p]
                nrm = (vs[1] - vs[0]).cross(vs[3] - vs[0])
                if nrm.length < 1e-6:
                    continue
                nrm.normalize()
                slope = math.degrees(math.acos(min(1.0, abs(nrm.z))))
                ym = sum(q[2] for q in p) / 4
                xm = sum(q[0] for q in p) / 4
                zm = sum(q[1] for q in p) / 4
                rm = math.hypot(xm, zm)
                mat = _mat_of(xm, zm, ym, slope, rm, (fld[j, i] + fld[j + 1, i2]) / 2, fld2[j, i])
                if mat == "SN_Hills" and fld2[j, i] > 0.6 and rm < 1050 and r_.random() < 0.6:
                    trees.append((xm, zm, ym))
                groups.setdefault(mat, []).append((p, vs))
        for mat, faces in groups.items():
            bm = bmesh.new()
            uvl = bm.loops.layers.uv.new("UVMap")
            vmap = {}
            for (p, vs) in faces:
                bv = []
                for (q, v) in zip(p, vs):
                    k = (round(q[0], 3), round(q[1], 3))
                    if k not in vmap:
                        vmap[k] = bm.verts.new(v)
                    bv.append(vmap[k])
                try:
                    f = bm.faces.new(bv)
                except ValueError:
                    continue
                if f.normal.z < 0:
                    f.normal_flip()
                if mat == "SN_Hills":
                    for lp in f.loops:
                        co = lp.vert.co
                        lp[uvl].uv = (0.5 + co.x / HILL_SPAN, 0.5 + (-co.y) / HILL_SPAN)
                if mat == "SN_Mountain":
                    angs = [math.atan2(-lp.vert.co.y, lp.vert.co.x) % (2 * math.pi) for lp in f.loops]
                    if max(angs) - min(angs) > math.pi:
                        angs = [t + 2 * math.pi if t < math.pi else t for t in angs]
                    for lp, t in zip(f.loops, angs):
                        lp[uvl].uv = (t / (2 * math.pi) * MTN_U, min(1.0, max(0.0, lp.vert.co.z / MTN_V)))
            b.mesh(bm, mat, keep_uv=True)
        objs += b.finish(smooth_angle=75.0)
    # bosques: pinheiros estilizados (3 cones empilhados, copa escura embaixo e clara em cima)
    bt = W.Build("WB_Bg_Forest", coll)
    for (x, z, y) in trees[:240]:
        for k in range(r_.randint(2, 3)):
            px, pz = x + r_.uniform(-14, 14), z + r_.uniform(-14, 14)
            hh = r_.uniform(20, 34) * (math.hypot(px, pz) / 600.0) ** 0.35
            b0 = RB(px, pz, y - 1.5)
            for t, (z0, z1, rr, mat) in enumerate(((0.12, 0.62, 0.26, "SN_PineFarDark"), (0.40, 0.84, 0.20, "SN_PineFar"),
                                                    (0.64, 1.0, 0.13, "SN_PineFarLight"))):
                bt.cyl(b0 + V((0, 0, hh * z0)), b0 + V((0, 0, hh * z1)), hh * rr, mat, seg=6, r1=0.02)
    objs += bt.finish()
    print("RELEVO: %d objetos, %d bosques" % (len(objs), len(trees)))
    return objs
