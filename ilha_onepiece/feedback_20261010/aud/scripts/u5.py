# u5.py - vaos (U5) nas linhas finas (passo 0,2, linhas a cada 3 em X e em Y), so na faixa do jogador
#   A) VAO DE COLISAO: chao visual continuo (|dz| < 0,6) mas a colisao some (ou cai > 1,5) numa faixa 0,6..6 entre 2
#      lados com colisao OK -> o pe afunda / a perna entra / cai pela fresta
#   B) FRESTA VISUAL: o visual afunda > 0,8 (ou ve o vazio) numa faixa 0,2..4 entre 2 lados de chao na mesma cota
#      (|dz| < 0,6) -> fresta/buraco aparente
import sys, json, collections
sys.dont_write_bytecode = True
import numpy as np
PROJ = r"C:/Users/lucas/OneDrive/Desktop/To up/ilha_onepiece"
sys.path.insert(0, PROJ)
import op_layout as L

g = np.load("grid.npz")
mk = np.load("u8_masks.npz")
ln = np.load("lines.npz")
meta = json.load(open("meta.json"))
xs, ys = g["xs"], g["ys"]
reach = mk["reach"]
STG = 1.5


def reach_at(x, y):
    i = int(round((x - xs[0]) / STG))
    j = int(round((y - ys[0]) / STG))
    j0, j1, i0, i1 = max(0, j - 1), j + 2, max(0, i - 1), i + 2
    return bool(reach[j0:j1, i0:i1].any())


FS = 0.2
res = []
for ax in ("x", "y"):
    fixed, run = ln[ax + "_fixed"], ln[ax + "_run"]
    Z, N, M, O, C = ln[ax + "_Z"], ln[ax + "_N"], ln[ax + "_M"], ln[ax + "_O"], ln[ax + "_C"]
    for a, f in enumerate(fixed):
        z, n, c, m, o = Z[a], N[a], C[a], M[a], O[a]
        walk = np.isfinite(z) & (n >= 0.7)
        colok = np.isfinite(c) & (z - c <= 1.5) & (z - c >= -1.5)
        good = walk & colok
        nrun = len(run)
        # --- A) vao de colisao
        k = 0
        while k < nrun:
            if good[k] or not walk[k]:
                k += 1
                continue
            s = k
            while k < nrun and walk[k] and not good[k]:
                k += 1
            e = k                      # [s, e)
            w = (e - s) * FS
            if s > 0 and e < nrun and good[s - 1] and good[e] and 0.6 <= w <= 6.0:
                zs = z[s:e]
                if abs(z[s - 1] - z[e]) < 0.6 and np.nanmax(np.abs(zs - z[s - 1])) < 0.6:
                    x0 = float(run[s]) if ax == "x" else float(f)
                    y0 = float(f) if ax == "x" else float(run[s])
                    xm = float(run[(s + e) // 2]) if ax == "x" else float(f)
                    ym = float(f) if ax == "x" else float(run[(s + e) // 2])
                    if reach_at(xm, ym):
                        dep = float(np.nanmax(z[s:e] - np.where(np.isfinite(c[s:e]), c[s:e], -1e3)))
                        res.append(dict(tipo="A_colisao", eixo=ax, x=round(xm, 1), y=round(ym, 1), z=round(float(z[s - 1]), 2),
                                        largura=round(w, 2), queda=round(min(dep, 999), 1),
                                        obj=meta["objs"][int(o[(s + e) // 2])], mat=meta["mats"][int(m[(s + e) // 2])]))
        # --- B) fresta visual
        k = 1
        while k < nrun - 1:
            if not walk[k - 1]:
                k += 1
                continue
            zl = z[k - 1]
            if np.isfinite(z[k]) and z[k] > zl - 0.8:
                k += 1
                continue
            s = k
            while k < nrun and (not np.isfinite(z[k]) or z[k] < zl - 0.8) and (k - s) * FS <= 4.2:
                k += 1
            e = k
            w = (e - s) * FS
            if e < nrun and walk[e] and abs(z[e] - zl) < 0.6 and 0.2 <= w <= 4.0:
                xm = float(run[(s + e) // 2]) if ax == "x" else float(f)
                ym = float(f) if ax == "x" else float(run[(s + e) // 2])
                if reach_at(xm, ym) and L.point_in_poly(xm, ym, L.ISLAND_RIM):
                    zs = z[s:e]
                    dep = float(zl - np.nanmin(zs)) if np.isfinite(zs).any() else 999.0
                    seevoid = bool((~np.isfinite(zs)).any())
                    res.append(dict(tipo="B_fresta", eixo=ax, x=round(xm, 1), y=round(ym, 1), z=round(float(zl), 2),
                                    largura=round(w, 2), fundo=round(dep, 1), ve_vazio=seevoid,
                                    lado_obj=meta["objs"][int(o[s - 1])], lado_mat=meta["mats"][int(m[s - 1])],
                                    fundo_obj=meta["objs"][int(o[(s + e) // 2])] if o[(s + e) // 2] >= 0 else "-",
                                    colisao_ok=bool(good[s - 1] and good[e])))
            k = max(k, s + 1)

# agrupa ocorrencias proximas (8 studs) por tipo
def cluster(items, r=8.0):
    cl = []
    for it in items:
        for c in cl:
            if abs(c["x"] - it["x"]) <= r and abs(c["y"] - it["y"]) <= r and c["tipo"] == it["tipo"]:
                c["n"] += 1
                c["pts"].append(it)
                break
        else:
            cl.append(dict(tipo=it["tipo"], x=it["x"], y=it["y"], n=1, pts=[it]))
    for c in cl:
        P = c["pts"]
        c["x"] = round(sum(p["x"] for p in P) / len(P), 1)
        c["y"] = round(sum(p["y"] for p in P) / len(P), 1)
        c["z"] = P[0]["z"]
        c["largura_max"] = max(p["largura"] for p in P)
        c["objs"] = collections.Counter(p.get("obj") or p.get("fundo_obj") for p in P).most_common(2)
        c["lado"] = collections.Counter(p.get("lado_obj", p.get("obj")) for p in P).most_common(2)
        c["piso"] = L.floor_name(c["x"], c["y"])
        if c["tipo"] == "B_fresta":
            c["fundo_max"] = max(p["fundo"] for p in P)
            c["ve_vazio"] = any(p["ve_vazio"] for p in P)
        else:
            c["queda_max"] = max(p["queda"] for p in P)
        del c["pts"]
    return cl


A = [r for r in res if r["tipo"] == "A_colisao"]
B = [r for r in res if r["tipo"] == "B_fresta"]
cA, cB = cluster(A), cluster(B)
cA.sort(key=lambda c: -c["n"])
cB.sort(key=lambda c: -c["n"])
json.dump(dict(A=cA, B=cB, brutos=len(res)), open(PROJ + "/feedback_20261010/aud/U5_vaos.json", "w"), indent=1)
print("A (vao de colisao) ocorrencias", len(A), "grupos", len(cA))
for c in cA[:30]:
    print(" A n=%d (%.1f,%.1f) z=%.1f larg<=%.1f queda<=%.1f piso=%s %s" % (c["n"], c["x"], c["y"], c["z"], c["largura_max"], c["queda_max"], c["piso"], c["objs"]))
print("B (fresta visual) ocorrencias", len(B), "grupos", len(cB))
for c in cB[:40]:
    print(" B n=%d (%.1f,%.1f) z=%.1f larg<=%.1f fundo<=%.1f vazio=%s piso=%s lado=%s fundo=%s" % (
        c["n"], c["x"], c["y"], c["z"], c["largura_max"], c["fundo_max"], c["ve_vazio"], c["piso"], c["lado"], c["objs"]))
