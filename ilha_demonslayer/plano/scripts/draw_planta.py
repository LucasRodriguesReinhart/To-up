# draw_planta.py - planta_ds.png: planta LOCAL da Ilha 4 (x direita = bambuzal/summon, y para cima = entrada -> forja)
import sys, os, math
sys.dont_write_bytecode = True
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, Rectangle, FancyArrowPatch
from matplotlib.lines import Line2D
from ds_geo import *
from ds_cams import CAMS

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "planta_ds.png")
BG = "#14182a"
fig, ax = plt.subplots(figsize=(17, 22))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
LV = {DECK: "#8a6a48", T0: "#6f7a64", T1: "#5d8a55", T2: "#7aa06a", T3: "#8a7fb8", T4: "#9a8f80"}


def P(pts, fc, ec="none", lw=1.0, z=2, alpha=1.0, ls="-", hatch=None):
    ax.add_patch(Polygon(pts, closed=True, fc=fc, ec=ec, lw=lw, zorder=z, alpha=alpha, ls=ls, hatch=hatch))


def T(x, y, s, c="#eef0f6", fs=9, w="normal", ha="center", z=20, rot=0):
    ax.text(x, y, s, color=c, fontsize=fs, fontweight=w, ha=ha, va="center", zorder=z, rotation=rot)


def ribbon(pts, hw):
    return G.ribbon(pts, hw)


# ilha (rim) + quilha sugerida
P(RIM, "#2f3a36", "#cfe8d0", 2.2, 1)
T(-150, 590, "borda do penhasco (topo)", "#a8c8aa", 8, ha="left")
# patamares
P(ENTRY_COURT, LV[T0], "#202020", 0.8, 3)
P(TRAIL_T1, LV[T1], "#202020", 0.8, 3)
P(VILLAGE_LOW, LV[T1], "#202020", 0.8, 3)
P(VILLAGE_HIGH, LV[T2], "#202020", 0.8, 3)
P(FORGE_TERR, LV[T4], "#202020", 0.8, 3)
P(SUMMON_PLAT, LV[T3], "#202020", 0.8, 4)
x0, y0, x1, y1 = CLIMB_LAND
P([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], LV[T3], "#202020", 0.8, 4)
P(CLEARING, "#b89a6c", "#3a2a18", 1.2, 4)
# rampa do bambuzal
P(ribbon(BAMBOO_RAMP, 5.0), "#8c7a5a", "none", 0, 5)
# bambuzal e arvores-marco (manchas)
for c, r in (((54, 40), 16), ((40, 92), 14), ((90, 104), 18), ((26, 120), 10)):
    ax.add_patch(Circle(c, r, fc="#7fae4a", ec="none", alpha=0.55, zorder=6))
T(84, 62, "BAMBUZAL", "#d8ffb0", 9, "bold")
for c, r in (((-40, 30), 12), ((34, 24), 9), ((-130, 400), 14), ((70, 560), 18), ((10, 575), 14), ((-30, 560), 12),
             ((-150, 200), 10), ((-30, 390), 9), ((150, 360), 10), ((116, 210), 9)):
    ax.add_patch(Circle(c, r, fc="#2f5a36", ec="#88c08a", lw=0.6, alpha=0.9, zorder=6))
# MiningZone + minerios
mx0, my0, mx1, my1 = MINE_RECT
ax.add_patch(Rectangle((mx0, my0), mx1 - mx0, my1 - my0, fc="none", ec="#ffd060", lw=1.8, ls="--", zorder=7))
pts, step = ore_points()
col = {"SUPERLEGENDARY": "#ff4fd8", "EPIC": "#b070ff", "UNCOMMON": "#5fb0ff", "COMMON": "#e8e2d0"}
for k, i, x, y in pts:
    ax.plot(x, y, "o", ms=3.4, color=col[k], zorder=8)
T(MINE_C[0], my0 - 7, "MiningZone_DemonSlayer 112 x 150 (piso T1 60,2) - 72 ORE_ (2 S / 10 E / 22 I / 38 C)",
  "#ffe08a", 8.5, "bold")
T(MINE_C[0], 150, "CLAREIRA (natural, ~40,5k studs2)\nantecampo de chegada", "#fff2d8", 9, "bold")
# agua
ax.plot([p[0] for p in FLUME], [p[1] for p in FLUME], color="#7a5a3a", lw=4, zorder=9)
ax.plot([p[0] for p in FLUME], [p[1] for p in FLUME], color="#6ab0ff", lw=1.6, zorder=10)
ax.plot([p[0] for p in TAILRACE], [p[1] for p in TAILRACE], color="#6ab0ff", lw=2.2, zorder=9)
ax.plot([p[0] for p in CHANNEL], [p[1] for p in CHANNEL], color="#6ab0ff", lw=2.2, zorder=9)
ax.add_patch(Circle(POND[:2], POND[2], fc="#3a6fb0", ec="#a8d0ff", lw=1, zorder=9))
ax.plot(*SPRING[:2], "^", ms=9, color="#6ab0ff", zorder=10)
ax.plot(CASCADE[0], CASCADE[1], "v", ms=10, color="#a8d0ff", zorder=10)
ax.plot(*SPILL, "v", ms=8, color="#a8d0ff", zorder=10)
T(118, 560, "nascente", "#a8d0ff", 8)
T(150, 432, "cascata unica\n(T4 -> lagoa, 20)", "#a8d0ff", 8, ha="left")
T(150, 392, "lagoa", "#a8d0ff", 8, ha="left")
T(150, 214, "sangradouro\n(sai pela ravina)", "#a8d0ff", 8, ha="left")
# casas
for nm, t, x, y, w, d, deg, z in HOUSES:
    ax.add_patch(Rectangle((x - w / 2, y - d / 2), w, d, fc="#e2d6bc", ec="#3a2818", lw=1.6, zorder=11))
    ax.add_patch(Rectangle((x - w / 2 - 1.6, y - d / 2 - 1.6), w + 3.2, d + 3.2, fc="none", ec="#2a3040", lw=1.0, zorder=11))
    T(x, y, nm, "#2a1a10", 8.5, "bold", z=21)
    T(x - w / 2 - 3, y + d / 2 + 4, t, "#f2e6c8", 7.5, ha="left")
ax.plot(*WELL, "s", ms=7, color="#c0b090", zorder=11)
T(WELL[0] + 8, WELL[1], "poco coberto", "#f2e6c8", 7.5, ha="left")
# forja
for k, (a, b, c, d, e, r) in FORGE.items():
    fc = {"hall": "#5a4030", "workshop": "#e2d6bc", "tower": "#a07050", "east": "#c8bba0"}[k]
    ax.add_patch(Rectangle((a, b), c - a, d - b, fc=fc, ec="#1a1008", lw=1.8, zorder=11))
fx, fy, fw, fh = FURNACE_MOUTH
ax.add_patch(Rectangle((fx - fw / 2, fy - 2.5), fw, 3, fc="#ff7a20", ec="#ffd080", lw=1.2, zorder=12))
ax.add_patch(Circle(WHEEL[:2], WHEEL[2] / 2, fc="none", ec="#d0a070", lw=2.2, zorder=12))
x0, y0, x1, y1 = FORGE_YARD
ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="none", ec="#ffb070", lw=1.0, ls=":", zorder=11))
T(0, 509, "FORJA (heroi)", "#ffd0a0", 11, "bold")
T(-52, 488, "oficina\n+ casa", "#2a1a10", 7.5)
T(0, 486, "salao da\nfornalha", "#ffe0c0", 7.5)
T(37, 493, "torre\nchamine", "#1a1008", 7)
T(63, 485, "ala leste", "#1a1008", 7)
T(92, 474, "roda d'agua", "#e0c090", 7.5)
T(12, 452, "patio de trabalho (bigorna, tina, estantes de laminas)", "#ffd8b0", 7.5)
T(-100, 400, "patio do carvao", "#e8e0d0", 8)
# summon
ax.add_patch(Circle(SUMMON_C, SUMMON_R, fc="none", ec="#c8b0ff", lw=1.4, ls="--", zorder=11))
ax.plot(*SUMMON_TOWER, "*", ms=20, color="#ffd060", mec="#5fa0ff", mew=1.5, zorder=12)
T(176, 340, "SUMMON (plato lateral, T3 70,2)\ntorre AMS: estrela + aneis + nucleo", "#d8c8ff", 8.5, "bold")
ax.add_patch(Circle((200, 318), 5, fc="#a07ad8", ec="none", zorder=11)); ax.add_patch(Circle((196, 280), 4, fc="#a07ad8", ec="none", zorder=11))
# glicinia (acentos: so 4)
for c in ((70, 128), (-104, 352), (200, 318), (196, 280)):
    ax.plot(*c, "D", ms=7, color="#c39bff", mec="white", mew=0.6, zorder=13)
# torii
for (x, y), deg in ((TORII_IN, 90.0), (TORII_OUT, EXIT_DEG)):
    a = math.radians(deg); ux, uy = math.cos(a), math.sin(a)
    ax.plot([x - uy * 9, x + uy * 9], [y + ux * 9, y - ux * 9], color="#e03a2a", lw=5, zorder=14, solid_capstyle="butt")
T(TORII_IN[0] + 20, TORII_IN[1] - 2, "torii de entrada", "#ff9a8a", 8.5, "bold", ha="left")
T(TORII_OUT[0] + 14, TORII_OUT[1] - 6, "torii de saida", "#ff9a8a", 8.5, "bold", ha="left")
# pontes e cabeceira
P(ribbon([PREV, (0.0, 0.0)], 9.0), "#9a7048", "#3a2a18", 1.0, 5)
T(16, -60, "ponte de chegada 100\n(52,2 -> 54,2, madeira escura,\nlanternas nos postes)", "#e8d0b0", 8, ha="left")
eb = [exit_point(0.0), exit_point(EXIT_BRIDGE_LEN)]
P(ribbon(eb, 9.0), "#9a7048", "#3a2a18", 1.0, 5)
W_ = world_polys()
ux, uy = exit_dir(); vx, vy = -uy, ux
pw, pd = PIER
c0, c1 = exit_point(EXIT_BRIDGE_LEN), exit_point(EXIT_BRIDGE_LEN + pd)
P([(c0[0] + vx * pw / 2, c0[1] + vy * pw / 2), (c1[0] + vx * pw / 2, c1[1] + vy * pw / 2),
   (c1[0] - vx * pw / 2, c1[1] - vy * pw / 2), (c0[0] - vx * pw / 2, c0[1] - vy * pw / 2)], "#8a8478", "#e0e0e0", 1.0, 5)
g = gate_op()
ax.plot([g[0] - vx * 10, g[0] + vx * 10], [g[1] - vy * 10, g[1] + vy * 10], color="#5fd0ff", lw=4, zorder=14)
an = exit_point(EXIT_BRIDGE_LEN + ANCHOR_OP_OFF)
ax.add_patch(FancyArrowPatch(an, (an[0] + ux * 40, an[1] + uy * 40), arrowstyle="-|>", mutation_scale=18,
                             color="#5fd0ff", lw=2.2, zorder=14))
T(g[0] + 26, g[1] + 2, "portao One Piece (il_gate_op)\nna cabeceira de pedra 30 x 30", "#8fe0ff", 8, ha="left")
T(an[0] + 20, an[1] + 30, "ISLAND_NEXT_ANCHOR_OnePiece\n(T4 80,2) -> ONE PIECE", "#8fe0ff", 8.5, "bold", ha="left")
T(-160, 640, "ponte de saida 56 (real, T4 80,2)", "#e8d0b0", 8, ha="left")
# escadas
for n, (fx_, fy_), deg, w, k, rise, tread, z in STAIRS:
    tx, ty, tz = stair_top(n)
    a = math.radians(deg); ux_, uy_ = math.cos(a), math.sin(a); vx_, vy_ = -uy_, ux_
    q = [(fx_ + vx_ * w / 2, fy_ + vy_ * w / 2), (tx + vx_ * w / 2, ty + vy_ * w / 2), (tx - vx_ * w / 2, ty - vy_ * w / 2),
         (fx_ - vx_ * w / 2, fy_ - vy_ * w / 2)]
    P(q, "#c8c0b0", "#202020", 0.8, 15, hatch="---")
    T((fx_ + tx) / 2 + vx_ * (w / 2 + 3) + (8 if deg == 90 else 0), (fy_ + ty) / 2 + vy_ * (w / 2 + 3) + (0 if deg == 90 else 6),
      "%s %dx%.2f" % (n, k, rise), "#ffffff", 7, ha="left" if deg == 90 else "center")
# ponte pequena do canal
ax.add_patch(Rectangle((122, 295), 10, 10, fc="#9a7048", ec="#3a2a18", lw=1, zorder=16))
T(110, 312, "pontezinha", "#e8d0b0", 7)
# rotas
RC = {"ENTRY->VILLAGE": "#ffcf5a", "ENTRY->CLEARING": "#ff8a3a", "ENTRY->CLEARING (bambuzal)": "#b6e65a",
      "CLEARING->FORGE": "#ff5050", "CLEARING->SUMMON": "#b090ff", "FORGE->ONE_PIECE_GATE": "#5fd0ff",
      "VILLAGE->FORGE (secundaria)": "#e0a0ff", "SHADOW_GATE->ENTRY": "#ffffff"}
for k, c in RC.items():
    v = ROUTES[k]
    ax.plot([p[0] for p in v], [p[1] for p in v], color=c, lw=2.4, alpha=0.9, zorder=17, ls="-")
    ax.add_patch(FancyArrowPatch(v[-2], v[-1], arrowstyle="-|>", mutation_scale=14, color=c, lw=2.4, zorder=17))
# lanternas nos nos (amostra)
for p in ((-10, 4), (10, 4), (-14, 58), (-38, 116), (-84, 232), (-60, 300), (16, 372), (30, 410), (30, 440),
          (126, 296), (150, 296), (-66, 376), (-104, 456), (-110, 540), (-88, 584), (-100, 584), (0, -40), (0, -80)):
    ax.plot(*p, "o", ms=4, color="#ffb84a", mec="#5a3a10", zorder=18)
# cameras
for n, (loc, tgt, lens) in CAMS.items():
    if not (-260 < loc[0] < 300 and -140 < loc[1] < 700):
        continue
    dx, dy = tgt[0] - loc[0], tgt[1] - loc[1]
    L_ = math.hypot(dx, dy) or 1
    c = "#00e0c0" if "PlayerHeight" in n else "#ff70d0"
    ax.add_patch(FancyArrowPatch(loc[:2], (loc[0] + dx / L_ * 22, loc[1] + dy / L_ * 22), arrowstyle="-|>",
                                 mutation_scale=12, color=c, lw=1.6, zorder=19))
    ax.plot(*loc[:2], "s", ms=4, color=c, zorder=19)
    T(loc[0] + 3, loc[1] - 5, n.replace("CAM_DS_", "").replace("PlayerHeight_", "PH_"), c, 6.5, ha="left")
# cotas
for (x, y), s in (((0, 26), "T0 54,2\npatio do torii"), ((-20, 90), "T1 60,2\ntrilha"), ((-100, 125), "T1 60,2\nvila baixa"),
                  ((-110, 230), "T2 66,2 vila alta"), ((12, 407), "T3 70,2\npatamar"), ((-120, 470), "T4 80,2"),
                  ((90, 448), "T4 80,2"), ((176, 268), "T3 70,2")):
    T(x, y, s, "#ffffff", 8, "bold")
# legenda
leg = [Line2D([0], [0], color=c, lw=3, label=k) for k, c in RC.items()]
leg += [Line2D([0], [0], marker="s", color="#ff70d0", lw=0, label="camera de QA"),
        Line2D([0], [0], marker="s", color="#00e0c0", lw=0, label="camera PlayerHeight"),
        Line2D([0], [0], marker="D", color="#c39bff", lw=0, label="glicinia (so 4 acentos)"),
        Line2D([0], [0], marker="o", color="#ffb84a", lw=0, label="lanterna em no de caminho"),
        Line2D([0], [0], marker="o", color="#e8e2d0", lw=0, label="ORE_ (comum..super: branco/azul/roxo/rosa)")]
for lv, c in LV.items():
    leg.append(Line2D([0], [0], color=c, lw=8, label="cota %.1f" % lv))
L = ax.legend(handles=leg, loc="lower right", fontsize=8, facecolor="#20263c", edgecolor="#4a5068", labelcolor="white")
L.set_zorder(30)
ax.set_aspect("equal")
ax.set_xlim(-250, 290); ax.set_ylim(-125, 715)
ax.tick_params(colors="#9aa0b4", labelsize=8)
for s in ax.spines.values():
    s.set_color("#4a5068")
ax.grid(color="#262c44", lw=0.5, zorder=0)
ax.set_xlabel("x local (+ = direita de quem chega: bambuzal, summon, roda d'agua)", color="#9aa0b4")
ax.set_ylabel("y local (+ = eixo do percurso: entrada -> clareira -> forja -> saida)", color="#9aa0b4")
ax.set_title("ILHA 4 DEMON SLAYER - planta (602 x 374 de topo, eixo longitudinal +Y; Roblox +Y local = (-0,766; 0; 0,643))",
             color="white", fontsize=13, fontweight="bold")
ax.plot([-240, -140], [-115, -115], color="white", lw=3, zorder=20)
T(-190, -106, "100 studs", "white", 9)
fig.savefig(OUT, dpi=100, facecolor=BG, bbox_inches="tight")
print("planta_ds.png ok", os.path.abspath(OUT))
