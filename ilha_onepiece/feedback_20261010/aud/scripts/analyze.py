# analyze.py - U8 (chao visual sem colisao alcancavel) a partir de grid.npz (raios do audit_rays.py)
import sys, json, math, collections
sys.dont_write_bytecode = True
import numpy as np
PROJ = r"C:/Users/lucas/OneDrive/Desktop/To up/ilha_onepiece"
sys.path.insert(0, PROJ)
import op_layout as L

JUMP = 7.2          # JumpPower 50 padrao do Roblox (~7,2 studs)
BODY = 5.0
TOL = 1.5           # colisao ate 1,5 abaixo do chao visual = OK
NEAR = 6.0          # alcance horizontal

g = np.load("grid.npz")
meta = json.load(open("meta.json"))
xs, ys = g["xs"], g["ys"]
zv, nv, vo, vm, zcb = g["zv"], g["nv"], g["vo"], g["vm"], g["zcb"]
ch, cbx = g["ch"], g["cbx"]
NY, NX = zv.shape
ST = float(xs[1] - xs[0])
mats = meta["mats"]
objs = meta["objs"]


def mcat(mi):
    if mi < 0:
        return "-"
    m = mats[mi]
    if m.startswith(("Leaf", "Flower")):
        return "copa"
    if m.startswith("Roof"):
        return "telhado"
    if m.startswith(("Glass", "Window", "Cloth", "Rope", "P_", "Energy", "Summon", "Crystal")) or "Glow" in m:
        return "outro"
    return "chao"


CAT = np.vectorize(mcat)(vm)

# ---------------- solidos por celula (uniao dos intervalos por caixa)
surf = {}      # (j,i) -> lista de (topo, teto_livre_acima)
for j in range(NY):
    for i in range(NX):
        hz = ch[j, i]
        ids = cbx[j, i]
        iv = collections.defaultdict(list)
        for z, b in zip(hz, ids):
            if b >= 0 and z == z:
                iv[int(b)].append(float(z))
        if not iv:
            continue
        ints = sorted([(min(v), max(v)) for v in iv.values()])
        # caixa com 1 hit so (truncada): assume base em 30
        ints = [(a if a < b else 30.0, b) for a, b in ints]
        u = []
        for a, b in ints:
            if u and a <= u[-1][1] + 0.05:
                u[-1] = (u[-1][0], max(u[-1][1], b))
            else:
                u.append((a, b))
        out = []
        for k, (a, b) in enumerate(u):
            ceil = u[k + 1][0] if k + 1 < len(u) else 1e9
            out.append((b, ceil))
        surf[(j, i)] = out


def free_intervals(j, i):
    s = surf.get((j, i))
    if not s:
        return [(-1e9, 1e9)]
    lo = [(-1e9, min(a for a, b in [(None, None)] if False) if False else None)]
    # intervalo abaixo do solido mais baixo: nao importa (ninguem anda dentro do solido) -> so os topos
    return s


def cell(x, y):
    return int(round((y - ys[0]) / ST)), int(round((x - xs[0]) / ST))


# ---------------- BFS de alcance (pula 7,2; corpo 5; cai qualquer altura)
start = cell(0.0, 24.0)
seen = set()
reach = collections.defaultdict(list)
q = collections.deque()
for k, (h, c) in enumerate(surf[start]):
    if abs(h - 84.2) < 1.0:
        q.append((start[0], start[1], k))
        seen.add((start[0], start[1], k))
voidfall = set()
NB = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
while q:
    j, i, k = q.popleft()
    h, c = surf[(j, i)][k]
    reach[(j, i)].append(h)
    for dj, di in NB:
        jj, ii = j + dj, i + di
        if not (0 <= jj < NY and 0 <= ii < NX):
            continue
        S = surf.get((jj, ii))
        if not S:
            voidfall.add((jj, ii))
            continue
        # o jogador entra na celula vizinha na altura h..h+JUMP: cai/sobe para o topo do intervalo livre que contem a passagem
        best = None
        for kk, (s, cc) in enumerate(S):
            if s <= h + JUMP and cc >= max(s, h) + BODY:
                if s >= h - 0.01 or True:
                    # se s < h e existe solido entre s e h na vizinha, o jogador para no solido mais alto <= h+JUMP
                    if best is None or s > S[best][0]:
                        best = kk
        if best is None:
            # passagem acima de todos os solidos (nenhum topo <= h+JUMP com folga) -> bloqueado
            continue
        s = S[best][0]
        if s < h - 0.01 and not any(ss <= h + JUMP and ss > s for ss, _ in S):
            pass
        if (jj, ii, best) not in seen:
            seen.add((jj, ii, best))
            q.append((jj, ii, best))

# ---------------- U8: chao visual andavel sem colisao
walk = (nv >= 0.7) & np.isfinite(zv)
okcol = np.isfinite(zcb) & (zv - zcb <= TOL)
miss = walk & ~okcol
R = int(round(NEAR / ST))
reachable = np.zeros_like(miss)
reach_h = np.full((NY, NX, 4), np.nan, np.float32)
for (j, i), hs in reach.items():
    hs = sorted(set(round(h, 2) for h in hs), reverse=True)[:4]
    reach_h[j, i, :len(hs)] = hs
offs = [(dj, di) for dj in range(-R, R + 1) for di in range(-R, R + 1) if dj * dj + di * di <= R * R]
for dj, di in offs:
    sh = np.full_like(reach_h, np.nan)
    j0, j1 = max(0, dj), NY + min(0, dj)
    i0, i1 = max(0, di), NX + min(0, di)
    sh[j0 - dj:j1 - dj, i0 - di:i1 - di] = reach_h[j0:j1, i0:i1]
    with np.errstate(invalid="ignore"):
        cond = np.any((zv[..., None] <= sh + JUMP) & (zv[..., None] >= sh - 25.0), axis=2)
    reachable |= cond
hit = miss & reachable

# ---------------- regioes (8-vizinhanca)
lab = np.zeros(zv.shape, np.int32)
regs = []
for j in range(NY):
    for i in range(NX):
        if hit[j, i] and lab[j, i] == 0:
            n = len(regs) + 1
            st = [(j, i)]
            lab[j, i] = n
            cells = []
            while st:
                a, b = st.pop()
                cells.append((a, b))
                for dj, di in NB:
                    aa, bb = a + dj, b + di
                    if 0 <= aa < NY and 0 <= bb < NX and hit[aa, bb] and lab[aa, bb] == 0:
                        lab[aa, bb] = n
                        st.append((aa, bb))
            regs.append(cells)


def where(x, y):
    for nm, poly, z in L.ROCKS:
        if L.point_in_poly(x, y, poly):
            return "rocha " + nm
    f = L.floor_name(x, y)
    if f:
        return "piso " + f
    if L.point_in_poly(x, y, L.SKULL_ROCK):
        return "caveira"
    if L.point_in_poly(x, y, L.ISLAND_RIM):
        return "dentro da borda (sem piso)"
    return "fora da borda"


out = []
for n, cells in enumerate(regs, 1):
    J = np.array([c[0] for c in cells])
    I = np.array([c[1] for c in cells])
    X, Y = xs[I], ys[J]
    Z = zv[J, I]
    dep = zv[J, I] - zcb[J, I]
    cats = collections.Counter(CAT[J, I])
    ob = collections.Counter(objs[vo[j, i]] for j, i in cells)
    mt = collections.Counter(mats[vm[j, i]] for j, i in cells)
    voidn = int(np.sum(~np.isfinite(zcb[J, I])))
    cx, cy = float(X.mean()), float(Y.mean())
    out.append(dict(id=n, cells=len(cells), area=round(len(cells) * ST * ST, 1), c=(round(cx, 1), round(cy, 1)),
                    bbox=(float(X.min()), float(Y.min()), float(X.max()), float(Y.max())),
                    z=(round(float(Z.min()), 1), round(float(Z.max()), 1)),
                    queda_med=None if voidn == len(cells) else round(float(np.nanmedian(dep)), 1),
                    sem_col_ate_o_vazio=voidn, cat=dict(cats), objs=ob.most_common(3), mats=mt.most_common(3),
                    onde=collections.Counter(where(float(x), float(y)) for x, y in zip(X[::3], Y[::3])).most_common(2)))
out.sort(key=lambda r: -r["area"])
json.dump(out, open("u8_regioes.json", "w"), indent=1, default=str)
np.savez_compressed("u8_masks.npz", walk=walk, miss=miss, hit=hit, lab=lab,
                    reach=np.isfinite(reach_h[..., 0]), cat=(CAT == "chao") * 1 + (CAT == "telhado") * 2 + (CAT == "copa") * 3)
tot = collections.Counter()
for r in out:
    for k, v in r["cat"].items():
        tot[k] += v * ST * ST
print("U8 regioes", len(out), "area por categoria", dict(tot))
print("U8 celulas alcancaveis", len(reach), "voidfall vizinhos", len(voidfall))
for r in out[:60]:
    if r["area"] >= 9:
        print(r["id"], r["area"], r["c"], r["bbox"], r["z"], "queda", r["queda_med"], "vazio", r["sem_col_ate_o_vazio"],
              r["cat"], r["objs"][:2], r["onde"])

# lista de superficies alcancaveis para o teste "dentro do modelo" (raio para cima no Blender)
pts = []
for (j, i), hs in reach.items():
    for h in set(round(h, 2) for h in hs):
        pts.append((float(xs[i]), float(ys[j]), float(h)))
np.save("reach_pts.npy", np.array(pts, np.float32))
print("reach_pts", len(pts))
