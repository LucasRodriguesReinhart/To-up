import sys, json, collections
sys.dont_write_bytecode = True
import numpy as np
PROJ = r"C:/Users/lucas/OneDrive/Desktop/To up/ilha_onepiece"
sys.path.insert(0, PROJ)
import op_layout as L
ln = np.load("lines.npz"); meta = json.load(open("meta.json"))
pts = []
for ax in ("x", "y"):
    F, R = ln[ax+"_fixed"], ln[ax+"_run"]
    Z, C, N, O = ln[ax+"_Z"], ln[ax+"_C"], ln[ax+"_N"], ln[ax+"_O"]
    for a, f in enumerate(F):
        for b in range(0, len(R), 1):
            x, y = (float(R[b]), float(f)) if ax == "x" else (float(f), float(R[b]))
            z = Z[a, b]
            if not np.isfinite(z) or N[a, b] < 0.7:
                continue
            if np.isfinite(C[a, b]) and z - C[a, b] <= 1.5:
                continue
            nm = L.floor_name(x, y)
            if nm is None:
                continue
            zf = L.zone_of(x, y)
            if abs(z - zf) > 1.2:
                continue
            # ignora entalhes de escada (a escada tem rampa propria) e o convés
            if any(L.point_in_poly(x, y, __import__("op_col").stair_footprint(s, pad=0.0)) for s, *_ in L.STAIRS) if False else False:
                continue
            pts.append((x, y, float(z), nm, meta["objs"][int(O[a, b])], bool(np.isfinite(C[a, b]))))
# cluster 4
cl = []
for p in pts:
    for c in cl:
        if abs(c["x1"] - p[0]) <= 4 and abs(c["y1"] - p[1]) <= 4 or (c["x0"]-4 <= p[0] <= c["x1"]+4 and c["y0"]-4 <= p[1] <= c["y1"]+4):
            c["n"] += 1; c["x0"] = min(c["x0"], p[0]); c["x1"] = max(c["x1"], p[0]); c["y0"] = min(c["y0"], p[1]); c["y1"] = max(c["y1"], p[1])
            c["objs"][p[4]] += 1; c["void"] += (not p[5]); c["z"] = p[2]; c["piso"] = p[3]
            break
    else:
        cl.append(dict(n=1, x0=p[0], x1=p[0], y0=p[1], y1=p[1], z=p[2], piso=p[3], objs=collections.Counter([p[4]]), void=int(not p[5])))
cl.sort(key=lambda c: -c["n"])
out = []
for c in cl:
    out.append(dict(piso=c["piso"], z=round(c["z"], 2), bbox=[round(c["x0"], 1), round(c["y0"], 1), round(c["x1"], 1), round(c["y1"], 1)],
                    amostras=c["n"], ate_o_vazio=c["void"], objs=c["objs"].most_common(2)))
json.dump(out, open(PROJ + "/feedback_20261010/aud/U5_buracos_colisao_no_piso.json", "w"), indent=1)
print("amostras", len(pts), "grupos", len(out))
for o in out[:45]:
    print(o)
