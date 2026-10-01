# fm_blockout - volumes cinza para validar composicao/escala; cada bloco some quando o modulo final existe
import sys
from fm_lib import MB, D
import fm_layout as L


def build():
    b = MB("BLK_Volumes", "01_BLOCKOUT")
    f = L.FLOOR
    has = lambda m: m in sys.modules
    if not has("fm_forge"):
        x0, y0, x1, y1 = L.FORGE_HALL
        b.box2((x0, y0, f), (x1, y1, f + 24), "BLK_Grey", 0.0)
        for w in (L.FORGE_WING_L, L.FORGE_WING_R):
            b.box2((w[0], w[1], f), (w[2], w[3], f + 18), "BLK_Grey", 0.0)
        b.cyl(9, 96, (L.CHIMNEY[0], L.CHIMNEY[1], f + 48), (0, 0, 0), "BLK_Grey", 16, bevel=0)
    if not has("fm_water"):
        m = L.MILL
        b.box2((m[0], m[1], f), (m[2], m[3], f + 16), "BLK_Grey", 0.0)
        b.cyl(L.WHEEL_R, 2.5, (L.WHEEL_C[0], L.WHEEL_C[1], 11), (0, D(90), 0), "BLK_Grey", 16, bevel=0)
    if not has("fm_buildings"):
        s = L.SHOP
        b.box2((s[0], s[1], f), (s[2], s[3], f + 14), "BLK_Grey", 0.0)
    if not has("fm_portals"):
        for px in L.PORTAL_X:
            b.box2((px - 10, L.PORTAL_Y - 1.5, L.TERR), (px + 10, L.PORTAL_Y + 1.5, L.TERR + 24), "BLK_Grey", 0.0)
    b.finish()
