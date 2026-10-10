import sys, json, collections
sys.dont_write_bytecode = True
import numpy as np
import zones_u8 as Z   # reaproveita zone()
P = np.load("reach_pts.npy"); R = np.load("inside.npy"); m2 = json.load(open("meta2.json"))
sel = R[:, 0] >= 0
grp = collections.defaultdict(list)
for (x, y, h), (d, back, oi, mi) in zip(P[sel], R[sel]):
    mat = m2["mats"][int(mi)]
    fam = "rocha/terreno" if mat.startswith(("Cliff", "Grass", "Dirt")) or m2["objs"][int(oi)].startswith("OP_Ter") else ("telhado" if mat.startswith("Roof") else ("copa" if mat.startswith(("Leaf", "Flower")) else "construcao/prop"))
    zn = Z.zone(float(x), float(y), float(h))
    grp[(zn, fam, ("corpo_dentro" if d >= 1.5 else "pe_afunda") if back > 0 else "cabeca_dentro")].append((x, y, h, d, m2["objs"][int(oi)]))
out = []
for k, v in grp.items():
    a = np.array([(p[0], p[1], p[2], p[3]) for p in v])
    out.append(dict(zona=k[0], fam=k[1], tipo=k[2], area=round(len(v) * 2.25, 1), c=[round(float(a[:, 0].mean()), 1), round(float(a[:, 1].mean()), 1)],
                    bbox=[round(float(a[:, 0].min())), round(float(a[:, 1].min())), round(float(a[:, 0].max())), round(float(a[:, 1].max()))],
                    h=[round(float(a[:, 2].min()), 1), round(float(a[:, 2].max()), 1)], dist_med=round(float(np.median(a[:, 3])), 2),
                    objs=collections.Counter(p[4] for p in v).most_common(2)))
out.sort(key=lambda r: -r["area"])
json.dump(out, open(Z.PROJ + "/feedback_20261010/aud/U8b_dentro_do_visual.json", "w"), indent=1)
for r in out[:40]:
    if r["area"] >= 9:
        print("%-34s %-16s %-22s %7.1f c=%s bbox=%s h=%s d=%s %s" % (r["zona"], r["fam"], r["tipo"], r["area"], r["c"], r["bbox"], r["h"], r["dist_med"], [o[0] for o in r["objs"]]))
