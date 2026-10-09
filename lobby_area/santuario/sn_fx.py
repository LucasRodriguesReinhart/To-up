# sn_fx.py - marcadores de VFX AMBIENTE (particulas criadas no Roblox pelo bloco VFX do montar, ver sn_lights):
# poeira dourada flutuando na praca, faiscas de runa nos estrados dos portais e no circulo do spawn, brilho dos
# cristais, folhas caindo de algumas copas, fumaca e brasas da cratera do martelo.
import math

import fm_lib
import sn_layout as L
from wb_lib import RB

COLL = "15_GAMEPLAY_MARKERS"


def mk(name, x, z, y, **props):
    fm_lib.marker(name, RB(x, z, y), (0, 0, 0), 1.0, "PLAIN_AXES", COLL, props)


def build(tree_spots=None):
    mk("VFX_Dust_Plaza", 0.0, 0.0, L.Y_PLAZA + 7.0, particle="dust", rate=6)
    mk("VFX_Dust_Forge", 0.0, -50.0, L.Y_PLAZA + 8.0, particle="dust", rate=3)
    mk("VFX_Rune_Spawn", L.SPAWN[0], L.SPAWN[1], L.Y_SPAWN + 0.6, particle="rune", rate=3)
    for i in range(len(L.PORTALS)):
        (x, z), (fx, fz) = L.portal_pos(i)
        mk("VFX_Rune_Portal%d" % (i + 1), x + fx * 9.0, z + fz * 9.0, L.Y_PORTAL + 0.4, particle="rune", rate=2)
    for k, (x, z, m, s) in enumerate(L.RUIN_CRYSTALS):
        mk("VFX_Sparkle_Crystal_%d" % k, x, z, L.Y_GRASS + 2.0 * s, particle="sparkle", rate=3)
    hx, hz = L.HAMMER["head"]
    mk("VFX_Hammer_Smoke", hx, hz, L.Y_GRASS + 1.0, particle="smoke_thin", rate=2)
    mk("VFX_Hammer_Embers", hx + 6.0, hz + 4.0, L.Y_GRASS + 0.6, particle="ember", rate=3)
    n = 0
    for nm, spots in (tree_spots or {}).items():
        if not nm.startswith(("oak", "ancient")):
            continue
        for (x, z, y, yaw, s) in spots[::6]:
            h = (46.0 if nm == "ancient" else 20.0) * s
            mk("VFX_Leaves_%s_%d" % (nm, n), x, z, y + h * 0.62, particle="leaves", rate=0.6, radius=h * 0.36)
            n += 1
    return n
