# draw_mundo.py - mundo.png: vista de cima VERDADEIRA (igual ao Top do Blender: +X Roblox para a direita, +Z Roblox
# para BAIXO), lobby, Ilhas 1-3, Ilha 4 (plano) e a direcao da area 5 (One Piece).
import sys, os, math
sys.dont_write_bytecode = True
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, FancyArrowPatch
from ds_geo import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mundo.png")
i1, i2, s3 = G.i1_polys(), G.i2_polys(), sg_polys()
W = world_polys()

fig, axes = plt.subplots(1, 2, figsize=(24, 12), gridspec_kw={"width_ratios": [1.2, 1]})
BG = "#161a2c"
fig.patch.set_facecolor(BG)


def P(ax, pts, fc, ec="none", lw=1.2, alpha=1.0, z=2, ls="-"):
    ax.add_patch(Polygon([(x, z_) for x, z_ in pts], closed=True, fc=fc, ec=ec, lw=lw, alpha=alpha, zorder=z, ls=ls))


def lab(ax, x, z, s, c="#e8e8f2", fs=9, w="normal", ha="left"):
    ax.text(x, z, s, color=c, fontsize=fs, fontweight=w, ha=ha, va="center", zorder=10, clip_on=True)


def dline(ax, A, B, label, c="#ffd75a", off=(10, 0)):
    best = (1e9, None, None)
    for p in A:
        for q in B:
            dd = math.hypot(p[0] - q[0], p[1] - q[1])
            if dd < best[0]:
                best = (dd, p, q)
    d_, p, q = best
    ax.plot([p[0], q[0]], [p[1], q[1]], color=c, lw=1.4, zorder=9)
    lab(ax, (p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], label % G.poly_dist(A, B), c, 8.5)


def dense_rect(r, step=10.0):
    x0, z0, x1, z1 = r[0][0], r[0][1], r[2][0], r[2][1]
    out = []
    xs = [x0 + (x1 - x0) * k / 60 for k in range(61)]
    zs = [z0 + (z1 - z0) * k / 60 for k in range(61)]
    out += [(x, z0) for x in xs] + [(x, z1) for x in xs] + [(x0, z) for z in zs] + [(x1, z) for z in zs]
    return out


def world(ax, detail):
    ax.set_facecolor(BG)
    P(ax, G.LOBBY["picos"], "#2e3442", "#78829a", 1.0, 1.0, 1)
    P(ax, G.LOBBY["nucleo"], "#3c4654", "#8c96aa", 1.0, 1.0, 2)
    P(ax, G.LOBBY["montanhas"], "#54604f", "#a0b4a0", 1.0, 1.0, 3)
    lab(ax, -630, 380, "LOBBY: bbox dos picos (x -650..660, z -710..408)", "#aab4c8", 8)
    lab(ax, -40, -10, "lobby", "#e6ebf0", 11, "bold")
    ax.add_patch(plt.Rectangle((-1024, 420 - 1024), 2048, 2048, fc="none", ec="#3e6a8a", lw=1.0, ls="--", zorder=1))
    lab(ax, -1010, 1430, "mar FAR_GROUND da Ilha 1 (x -1024..1024)", "#5f8fb3", 8)
    P(ax, i1["rim"], "#50823f", "#aadc8c"); P(ax, i1["bridge"], "#969696"); P(ax, i1["islet"], "#6e965a")
    lab(ax, -70, 470, "Ilha 1 Naruto", "#f0fae6", 10, "bold")
    for k in ("rim", "bridge", "islet", "arrival"):
        P(ax, i2[k], "#be9646" if k == "rim" else "#969696", "#f0d28c" if k == "rim" else "none")
    lab(ax, -470, 790, "Ilha 2 Dragon Ball", "#fff5dc", 10, "bold")
    P(ax, s3["rim"], "#5a508c", "#beaaff"); P(ax, s3["arrival"], "#a0a0aa"); P(ax, s3["bridge"], "#a0a0aa")
    P(ax, s3["islet"], "#78649e"); P(ax, s3["summon"], "#78649e")
    lab(ax, -1330, 700, "Ilha 3 Shadow Garden\n(nao se move)", "#ebe1ff", 10, "bold")
    # Ilha 4
    P(ax, W["bridge_in"], "#b48c5a", "#3a2a18", 0.8, 1, 4)
    P(ax, W["rim"], "#3f6e4c", "#d6ffd2", 1.8, 1, 4)
    P(ax, W["bridge_out"], "#b48c5a", "#3a2a18", 0.8, 1, 4)
    P(ax, W["pier"], "#8a8478", "#e0e0e0", 1.0, 1, 4)
    cl = [rbx(*p) for p in CLEARING]
    P(ax, cl, "#b08a5c", "none", 0, 0.9, 5)
    fg = [rbx(*p) for p in FORGE_TERR]
    P(ax, fg, "#6b6f78", "none", 0, 0.9, 5)
    ax.plot(A_RBX[0], A_RBX[2], "o", ms=7, color="#ff5050", zorder=11)
    ax.plot(GATE_DS_RBX[0], GATE_DS_RBX[2], "s", ms=6, color="#ff9a7a", zorder=11)
    a5, d5 = anchor_op()
    ax.plot(a5[0], a5[1], "o", ms=7, color="#5fd0ff", zorder=11)
    ax.add_patch(FancyArrowPatch((a5[0], a5[1]), (a5[0] + d5[0] * 280, a5[1] + d5[1] * 280), arrowstyle="-|>",
                                 mutation_scale=22, color="#5fd0ff", lw=2.4, zorder=11))
    c5 = (a5[0] + d5[0] * 350, a5[1] + d5[1] * 350)
    ax.add_patch(Circle(c5, 300, fc="none", ec="#5fd0ff", lw=1.2, ls="--", zorder=3))
    lab(ax, c5[0] - 210, c5[1] + 40, "espaco livre da area 5\nONE PIECE (r 300)", "#8fe0ff", 9.5, "bold")
    lab(ax, -1620, 1180, "Ilha 4\nDEMON SLAYER", "#e6ffe0", 11, "bold")
    if detail:
        ax.text(0.02, 0.98, "o ancora DS (vermelho): (-1534,5; 52,2; 962,4), frente (-0,766; 0; 0,643)\n"
                "[] portao DS aprovado (ilhota da SG): (-1513,0; 52,2; 944,5)\n"
                "o ancora One Piece (azul): (-2054,4; 80,2; 1551,8), frente (-0,574; 0; 0,819)\n"
                "[] portao One Piece (il_gate_op) na cabeceira de pedra: (-2044,1; 80,2; 1537,0)\n"
                "folgas (amarelo): borda Ilha 4 -> borda SG 188 | -> ilhota do portao DS 98 (= ponte de chegada de 100)\n"
                "-> Ilha 2 1102 | -> bbox dos picos do lobby 1139 | -> Ilha 1 1535",
                transform=ax.transAxes, color="#e8e8f2", fontsize=8.5, va="top", zorder=12,
                bbox=dict(fc="#20263c", ec="#4a5068"))
        dline(ax, W["rim"], s3["rim"], "%.0f (SG)", off=(25, 10))
        dline(ax, W["rim"], s3["islet"], "%.0f (ilhota)", off=(15, -22))
        dline(ax, W["rim"], i2["rim"], "%.0f ate a Ilha 2", off=(-60, 60))
        dline(ax, W["rim"], dense_rect(G.LOBBY["picos"]), "%.0f ate a bbox dos picos", off=(-60, 100))
    # eixo / rosa
    ax.set_aspect("equal")
    ax.invert_yaxis()          # +Z para baixo = vista de cima verdadeira
    ax.tick_params(colors="#9aa0b4", labelsize=8)
    for s in ax.spines.values():
        s.set_color("#4a5068")
    ax.set_xlabel("Roblox X", color="#9aa0b4"); ax.set_ylabel("Roblox Z (cresce para baixo)", color="#9aa0b4")
    ax.grid(color="#2a3048", lw=0.6, zorder=0)


ax = axes[0]
world(ax, False)
ax.set_xlim(-2700, 900); ax.set_ylim(2150, -850)
ax.set_title("MUNDO (vista de cima verdadeira, igual ao Top do Blender)", color="white", fontsize=13, fontweight="bold")
# radial
a5, d5 = anchor_op()
ax.plot([0, a5[0]], [-177, a5[1]], color="#6c6c96", lw=1, ls=":", zorder=2)
lab(ax, -1150, 600, "radial lobby -> saida (desvio 15 graus)", "#8a8ab4", 8)
ax.plot([-2600, -2100], [2050, 2050], color="white", lw=3)
lab(ax, -2600, 2000, "500 studs", "white", 9)

ax = axes[1]
world(ax, True)
ax.set_xlim(-2320, -1360); ax.set_ylim(1900, 680)
ax.set_title("Encaixe da Ilha 4 (zoom)", color="white", fontsize=13, fontweight="bold")
# marcos no zoom
for nm, (x, y), c in (("torii de entrada", TORII_IN, "#ff6a5a"), ("clareira", MINE_C, "#ffd8a0"),
                      ("forja", (0.0, 486.0), "#ffa040"), ("summon", SUMMON_TOWER, "#7aa8ff"),
                      ("torii de saida", TORII_OUT, "#ff6a5a")):
    q = rbx(x, y)
    ax.plot(q[0], q[1], "o", ms=5, color=c, zorder=12)
    lab(ax, q[0] + 8, q[1], nm, c, 8.5)
g = gate_op(); q = rbx(*g)
ax.plot(q[0], q[1], "s", ms=6, color="#5fd0ff", zorder=12); lab(ax, q[0] + 14, q[1] + 22, "portao One Piece", "#8fe0ff", 8)
f = dir_rbx(0, 1)
ax.add_patch(FancyArrowPatch((A_RBX[0], A_RBX[2]), (A_RBX[0] + f[0] * 90, A_RBX[2] + f[1] * 90), arrowstyle="-|>",
                             mutation_scale=16, color="#ff7070", lw=1.8, zorder=12))
lab(ax, -1600, 1110, "eixo local +Y (entrada -> forja)\n= frente da ancora (-0,766; 0; 0,643)", "#ff9a9a", 8)
ax.plot([-2290, -2190], [1870, 1870], color="white", lw=3)
lab(ax, -2290, 1845, "100 studs", "white", 9)
plt.subplots_adjust(left=0.04, right=0.99, top=0.95, bottom=0.06, wspace=0.08)
fig.savefig(OUT, dpi=110, facecolor=BG)
print("mundo.png ok", os.path.abspath(OUT))
