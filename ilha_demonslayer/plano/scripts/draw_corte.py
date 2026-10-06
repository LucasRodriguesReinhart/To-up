# draw_corte.py - corte_ds.png: corte LONGITUDINAL desdobrado ao longo do percurso principal
# ancora SG -> ponte -> torii -> trilha -> clareira -> subida -> forja -> caminho de saida -> torii -> ponte -> portao OP
import sys, os, math
sys.dont_write_bytecode = True
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle
from ds_geo import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "corte_ds.png")
BG = "#14182a"
st = {n: stair_top(n) for n, *_ in STAIRS}
eb1 = exit_point(EXIT_BRIDGE_LEN)
g = gate_op()
an = exit_point(EXIT_BRIDGE_LEN + ANCHOR_OP_OFF)
# (x, y, z, rotulo)
PATH = [((0.0, -100.0), DECK, "ancora SG\n(WORLD_FROM_PREV)"), ((0.0, 0.0), T0, ""), ((0.0, 8.0), T0, "torii de entrada"),
        ((-12.0, 40.0), T0, ""), ((-12.0, 54.4), T1, "escada Trilha"), ((-8.0, 96.0), T1, "trilha"),
        ((0.0, 140.0), T1, "borda da clareira"), ((20.0, 200.0), T1, ""), ((40.0, 255.0), T1, "centro da MiningZone"),
        ((16.0, 330.0), T1, ""), ((16.0, 377.0), T1, "pe da subida"), ((16.0, 400.4), T3, "SubidaA"),
        ((30.0, 414.0), T3, "patamar 70,2"), ((30.0, 437.4), T4, "SubidaB"), ((10.0, 452.0), T4, "patio da forja"),
        ((0.0, 468.0), T4, "boca da fornalha"), ((-40.0, 446.0), T4, ""), ((-104.0, 452.0), T4, ""),
        ((-114.0, 496.0), T4, "caminho de saida"), ((-110.0, 540.0), T4, ""), ((-100.0, 572.0), T4, ""),
        ((-95.0, 594.0), T4, "torii de saida /\nISLAND_EXIT"), (eb1, T4, "fim da ponte de saida"),
        (g, T4, "portao One Piece"), (an, T4, "ISLAND_NEXT_\nANCHOR_OnePiece")]
s = [0.0]
for a, b in zip(PATH, PATH[1:]):
    s.append(s[-1] + math.hypot(b[0][0] - a[0][0], b[0][1] - a[0][1]))
S = dict()
for (p, z, lb), si in zip(PATH, s):
    if lb:
        S[lb] = (si, z)
fig, ax = plt.subplots(figsize=(28, 14))
fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
VX = 1.0


def box(x0, x1, z0, z1, fc, ec="#101010", lw=1.0, zo=5, alpha=1.0, hatch=None):
    ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, fc=fc, ec=ec, lw=lw, zorder=zo, alpha=alpha, hatch=hatch))


def T(x, z, t, c="#eef0f6", fs=8.5, w="normal", ha="center", rot=0, zo=20):
    ax.text(x, z, t, color=c, fontsize=fs, fontweight=w, ha=ha, va="center", rotation=rot, zorder=zo)


# mar de nuvens
ax.axhspan(-80, SEA_CLOUD, color="#2a3352", zorder=0)
T(40, SEA_CLOUD - 8, "mar de nuvens (cliente) -60", "#8a9ac8", 8, ha="left")
# massa da ilha (do torii ate o torii de saida) com quilha
i0 = s[1]; i1 = S["torii de saida /\nISLAND_EXIT"][0] + 8
prof = [(si, z) for (p, z, lb), si in zip(PATH, s) if i0 <= si <= i1]
under = [(i1, T4 - 40), (i1 - 60, -10), (i0 + (i1 - i0) * 0.55, -34), (i0 + 80, -18), (i0, T0 - 30)]
ax.add_patch(Polygon(prof + under, closed=True, fc="#3a3f4c", ec="#9aa4b8", lw=1.4, zorder=2))
T(i0 + (i1 - i0) * 0.5, 0, "massa rochosa (Tier C a mais de 12 abaixo do piso): estratos horizontais, musgo nas quinas, quilha ate ~-34",
  "#c0c8d8", 9)
# perfil andavel
ax.plot([q[0] for q in zip(s)], [z for (p, z, lb) in PATH], color="#ffd060", lw=2.6, zorder=10)
# pontes
box(s[0], s[1], DECK - 3.0, DECK, "#8a6040", zo=6)
for k in range(0, 100, 20):
    box(s[0] + k + 8, s[0] + k + 10, DECK - 40 + k * 0.0, DECK - 3, "#5a4030", zo=5)
x_ex0 = S["torii de saida /\nISLAND_EXIT"][0]; x_ex1 = S["fim da ponte de saida"][0]
box(x_ex0, x_ex1, T4 - 3, T4, "#8a6040", zo=6)
x_an = S["ISLAND_NEXT_\nANCHOR_OnePiece"][0]
ax.add_patch(Polygon([(x_ex1, T4), (x_an, T4), (x_an - 4, T4 - 18), (x_ex1 + 12, T4 - 70), (x_ex1 + 4, T4 - 20)],
                     closed=True, fc="#6a665e", ec="#c0c0c0", zorder=6))
T((x_ex1 + x_an) / 2, T4 - 30, "cabeceira\nde pedra", "#e0e0e0", 7.5)
# torii
for lb in ("torii de entrada", "torii de saida /\nISLAND_EXIT"):
    x, z = S[lb]
    box(x - 1, x + 1, z, z + 16, "#c83a2a", zo=12)
    box(x - 4, x + 4, z + 15, z + 17, "#202024", zo=12)
# portao OP
x, z = S["portao One Piece"]; box(x - 1.5, x + 1.5, z, z + 27, "#c08850", zo=12); T(x, z + 32, "portao OP\n(timao ~27)", "#8fe0ff", 8)
# clareira: minerios (oficiais, so indicacao de altura)
xc0, xc1 = S["borda da clareira"][0], S["pe da subida"][0]
for k in range(10):
    xx = xc0 + 30 + k * (xc1 - xc0 - 60) / 9
    box(xx - 1.5, xx + 1.5, T1, T1 + 5, "#d0c8b0", zo=8, alpha=0.5)
T((xc0 + xc1) / 2, T1 + 12, "CLAREIRA LIVRE (nada colidivel ate piso+12 na MiningZone)\nminerios oficiais (nao modelados)",
  "#ffe0a0", 9, "bold")
# forja (projetada no corte)
xf = S["boca da fornalha"][0]
box(xf - 2, xf + 34, T4, T4 + 3, "#4a4848", zo=7)                             # soco de pedra escura
box(xf, xf + 32, T4 + 3, T4 + 13, "#e2d6bc", zo=7)                             # parede reboco + madeira
ax.add_patch(Polygon([(xf - 8, T4 + 13), (xf + 40, T4 + 13), (xf + 16, T4 + 24)], closed=True, fc="#343a48",
                     ec="#101010", zorder=8))
box(xf - 1, xf + 1.5, T4, T4 + 9, "#ff7a20", zo=9)
box(xf + 22, xf + 36, T4, T4 + 44, "#a87858", zo=6)                            # torre-chamine (projetada)
ax.add_patch(Polygon([(xf + 19, T4 + 44), (xf + 39, T4 + 44), (xf + 29, T4 + 52)], closed=True, fc="#343a48", zorder=7))
box(xf + 27, xf + 31, T4 + 50, T4 + 60, "#5a5250", zo=7)
T(xf + 29, T4 + 66, "torre-chamine 140,2\n(ponto mais alto)", "#ffb070", 8.5, "bold")
T(xf + 16, T4 + 28, "salao da fornalha\ncumeeira 104,2", "#ffd0a0", 8)
# summon (projetado, fora do percurso)
xs_ = S["centro da MiningZone"][0] + 70
box(xs_ - 12, xs_ + 12, T1, T3, "#6a6290", zo=3, alpha=0.6)
box(xs_ - 4, xs_ + 4, T3, T3 + 40, "#2a3050", zo=3, alpha=0.7)
T(xs_, T3 + 47, "torre do summon ~115\n(projetada; plato T3 70,2)", "#c8b0ff", 8)
# vila (projetada)
xv = S["trilha"][0] + 30
for dx_, z0 in ((0, T1), (40, T1), (80, T2)):
    box(xv + dx_ - 8, xv + dx_ + 8, z0, z0 + 9, "#e2d6bc", zo=3, alpha=0.55)
    ax.add_patch(Polygon([(xv + dx_ - 11, z0 + 9), (xv + dx_ + 11, z0 + 9), (xv + dx_, z0 + 16)], closed=True,
                         fc="#343a48", alpha=0.6, zorder=3))
T(xv + 40, T2 + 20, "vila (projetada, a esquerda)", "#e8dcc0", 8)
# linhas de visada
xe = S["torii de entrada"][0] - 30
ax.plot([xe, xf + 29], [DECK + 1 + 5.5, T4 + 60], color="#ff9a6a", lw=1, ls="--", zorder=9)
T(xe + 40, 100, "visada da ponte: a torre-chamine aparece por cima do torii e da vila", "#ff9a6a", 8, ha="left")
ax.plot([S["escada Trilha"][0], S["pe da subida"][0]], [T1 + 5.5, T1 + 5.5], color="#a0ffa0", lw=1, ls=":", zorder=9)
T(S["escada Trilha"][0] + 10, T1 + 3, "do topo da escada Trilha o jogador ve o piso da clareira no mesmo nivel", "#a0ffa0", 7.5,
  ha="left")
# cotas
for z, nm in ((DECK, "DECK 52,2"), (T0, "T0 54,2"), (T1, "T1 60,2"), (T2, "T2 66,2"), (T3, "T3 70,2"), (T4, "T4 80,2")):
    ax.axhline(z, color="#3a4260", lw=0.6, ls=":", zorder=1)
    T(-20, z, nm, "#c8d0e8", 8, ha="right")
# rotulos do percurso
for lb, (x, z) in S.items():
    ax.plot(x, z, "o", ms=4, color="#ffd060", zorder=11)
    off = {"fim da ponte de saida": -6, "portao One Piece": -12, "ISLAND_NEXT_\nANCHOR_OnePiece": -20,
           "SubidaA": -5, "patamar 70,2": -6, "SubidaB": -5, "patio da forja": -11, "boca da fornalha": -17}.get(lb, -6)
    T(x, z + off, lb, "#ffffff", 7.5, rot=0)
# capitulos
CH = [("ENTRADA\nsilenciosa", s[0], S["escada Trilha"][0]), ("TRILHA / VILA\nhabitavel", S["escada Trilha"][0], S["borda da clareira"][0]),
      ("CLAREIRA\ngameplay", S["borda da clareira"][0], S["pe da subida"][0]), ("SUBIDA", S["pe da subida"][0], S["SubidaB"][0]),
      ("FORJA\ncalor e oficio", S["SubidaB"][0], S["caminho de saida"][0] - 20),
      ("SAIDA\npromessa do proximo mundo", S["caminho de saida"][0] - 20, x_an)]
for nm, a, b in CH:
    ax.annotate("", (a, 156), (b, 156), arrowprops=dict(arrowstyle="<->", color="#8a9ac8"))
    T((a + b) / 2, 164, nm, "#c8d4ff", 9, "bold")
ax.set_xlim(-60, x_an + 30); ax.set_ylim(-80, 172)
ax.set_aspect(2.5)
ax.tick_params(colors="#9aa0b4", labelsize=8)
for sp in ax.spines.values():
    sp.set_color("#4a5068")
ax.set_xlabel("distancia ao longo do percurso principal (studs, desdobrado)", color="#9aa0b4")
ax.set_ylabel("Z absoluto = Y do Roblox", color="#9aa0b4")
ax.set_title("ILHA 4 DEMON SLAYER - corte longitudinal (vertical exagerado 2,5x): sobe 28 da ancora (52,2) ao terraco da forja (80,2); "
             "percurso ancora -> portao OP = %.0f studs" % x_an, color="white", fontsize=12, fontweight="bold")
fig.savefig(OUT, dpi=100, facecolor=BG, bbox_inches="tight")
print("corte_ds.png ok; comprimento %.0f" % x_an, {k.replace("\n", " "): round(v[0]) for k, v in S.items()})
