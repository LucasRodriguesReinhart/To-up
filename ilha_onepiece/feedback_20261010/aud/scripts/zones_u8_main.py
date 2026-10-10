rows = collections.defaultdict(list)
J, I = np.nonzero(hit)
for j, i in zip(J, I):
    x, y, z = float(xs[i]), float(ys[j]), float(zv[j, i])
    rows[(zone(x, y, z), CATN[int(cat[j, i])])].append((j, i))

out = []  # zonas
for (zn, c), cells in rows.items():
    jj = np.array([a for a, b in cells])
    ii = np.array([b for a, b in cells])
    X, Y, Z = xs[ii], ys[jj], zv[jj, ii]
    dep = Z - zcb[jj, ii]
    voidn = int(np.sum(~np.isfinite(zcb[jj, ii])))
    ob = collections.Counter(meta["objs"][vo[a, b]] for a, b in cells).most_common(3)
    mt = collections.Counter(meta["mats"][vm[a, b]] for a, b in cells).most_common(2)
    out.append(dict(zona=zn, cat=c, area=round(len(cells) * ST * ST, 1), c=(round(float(X.mean()), 1), round(float(Y.mean()), 1)),
                    bbox=[float(X.min()), float(Y.min()), float(X.max()), float(Y.max())],
                    z=[round(float(Z.min()), 1), round(float(Z.max()), 1)],
                    queda_mediana=None if voidn == len(cells) else round(float(np.nanmedian(dep)), 1),
                    pct_ate_vazio=round(100.0 * voidn / len(cells)), objs=ob, mats=mt))
out.sort(key=lambda r: (r["cat"] != "chao", -r["area"]))
json.dump(out, open(PROJ + "/feedback_20261010/aud/U8_zonas.json", "w"), indent=1)
tot = collections.Counter()
for r in out:
    tot[r["cat"]] += r["area"]
print("TOTAL", dict(tot))
for r in out:
    if r["area"] >= 20:
        print("%-40s %-8s %7.1f c=%s bbox=%s z=%s queda=%s vazio=%d%% %s" % (
            r["zona"], r["cat"], r["area"], r["c"], [round(v) for v in r["bbox"]], r["z"], r["queda_mediana"],
            r["pct_ate_vazio"], [o[0] for o in r["objs"][:2]]))
