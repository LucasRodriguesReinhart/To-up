# fm_terrain_isles - SAIDA SUL do lobby para as ilhas do jogo (lobby ativo, 2026-09-24).
# O lobby fica na origem do place e as areas seguem em Roblox +z (= Blender -y): a Vila da Folha (Area 1) tem a praca
# de chegada a partir de Roblox z 222, com piso em y 6.0. O parapeito sul do spawn ganha um PORTAO (dois pilares com
# lanterna e verga de madeira) e dele sai uma PONTE de pedra na largura do portao:
#   trecho plano em z0 (mesmo piso do spawn; por baixo passa a colisao invisivel do corredor Lobby_Area1, topo y 0),
#   escadaria de 6 degraus (~1 cada) ate 6.2 e um patamar curto que encosta na praca da ilha.
# Muretas com colisao alta dos dois lados (ninguem cai no vazio), pilares com lanterna no meio do trecho plano,
# pilares de apoio descendo para o vazio. So materiais que o lobby ja usa e nenhuma luz nova (luzes de dia no teto).

import random
from fm_lib import MB, D, col_box, col_box2
from fm_parts import stairs, stone_parapet, lantern, pave_poly
import fm_layout as L

C = "02_TERRAIN"
AREA = "Isles"
PAR_H, PAR_W, COL_TOP = 2.4, 1.8, 12.0      # mureta igual a do spawn (colisao ate z 12: nao vira atalho)


def _parapet(mb, pts, col_top=COL_TOP, rng=None):
    """stone_parapet com a colisao ate a cota absoluta col_top (mesma regra das muretas do spawn)"""
    import bpy
    import fm_lib
    n0 = fm_lib._COL_COUNT.get(AREA, 0)
    stone_parapet(mb, AREA, pts, h=PAR_H, w=PAR_W, rng=rng)
    for i in range(n0 + 1, fm_lib._COL_COUNT.get(AREA, 0) + 1):
        o = bpy.data.objects.get("COL_%s_%03d" % (AREA, i))
        if o is None:
            continue
        zb = o.location.z - o.scale.z / 2
        if col_top > zb + PAR_H:
            o.scale.z = col_top - zb
            o.location.z = zb + o.scale.z / 2


def _pillar(mb, x, y, z0, h, s=2.6):
    """pilar de pedra clara com soco e capitel escuros"""
    mb.box((s + 0.5, s + 0.5, 0.8), (x, y, z0 + 0.4), (0, 0, 0), "Stone_Dark", 0.15)
    mb.box((s, s, h - 1.4), (x, y, z0 + 0.8 + (h - 1.4) / 2), (0, 0, 0), "Stone_Light", 0.15)
    mb.box((s + 0.6, s + 0.6, 0.6), (x, y, z0 + h - 0.3), (0, 0, 0), "Stone_Dark", 0.12)
    col_box(AREA, (s + 0.5, s + 0.5, COL_TOP - z0), (x, y, z0 + (COL_TOP - z0) / 2))


def build(rng=None):
    rng = rng or random.Random(2209)
    gw = L.ISLES_GATE_HW
    y0 = L.SPAWN_PAD[1]                     # borda sul do spawn (-118)
    ys = L.ISLES_STAIRS_Y0                  # pe da escadaria (-194)
    n, rise, run = L.ISLES_STAIRS_N, L.ISLES_STAIRS_RISE, L.ISLES_STAIRS_RUN
    yt = ys - n * run                       # topo da escadaria (-218)
    ye = L.ISLES_END_Y                      # praca da Area 1 (-222)
    zt = n * rise                           # 6.2
    mb = MB("TER_Isles_Bridge", C, rng)

    # ---- tabuleiro plano (piso z0, mesmo acabamento do spawn) + faixa escura nas bordas
    mb.box2((-gw - PAR_W, ys, -2.4), (gw + PAR_W, y0, L.SPAWN_Z - 0.35), "Stone_Dark", 0.2)
    pave_poly(mb, [(-gw, ys), (gw, ys), (gw, y0), (-gw, y0)], L.SPAWN_Z - 0.35, rng, tile=2.8, h=0.35)
    col_box2(AREA, (-gw, ys, -6.0), (gw, y0 + 0.5, L.SPAWN_Z))
    # ---- muretas do trecho plano, interrompidas por um pilar com lanterna no meio de cada lado
    ym = (y0 + ys) / 2
    for sx in (-1, 1):
        x = sx * (gw + PAR_W / 2)
        _parapet(mb, [(x, y0), (x, ym + 1.6)], rng=rng)
        _parapet(mb, [(x, ym - 1.6), (x, ys)], rng=rng)
        _pillar(mb, x, ym, L.SPAWN_Z, 3.6, s=2.4)
        lantern(mb, (x, ym, L.SPAWN_Z), post=False, arm=False, h=3.0, lights=False)

    # ---- escadaria ate a ilha (sobe para o sul = -y), banzos laterais como guarda-corpo
    stairs(mb, AREA, (0.0, ys, L.SPAWN_Z), D(-90), 2 * gw, n, rise, run, "Stone_Light", "Stone_Dark", stringers=True)
    mb.box2((-gw - PAR_W, yt, -2.4), (gw + PAR_W, ys, L.SPAWN_Z), "Stone_Dark", 0.2)     # laje sob os degraus
    # ---- patamar que encosta na praca de chegada da ilha
    mb.box2((-gw - PAR_W, ye, -2.4), (gw + PAR_W, yt + 0.2, zt - 0.35), "Stone_Dark", 0.2)
    pave_poly(mb, [(-gw, ye), (gw, ye), (gw, yt + 0.2), (-gw, yt + 0.2)], zt - 0.35, rng, tile=2.8, h=0.35)
    col_box2(AREA, (-gw, ye - 0.5, zt - 3.0), (gw, yt + 0.2, zt))
    for sx in (-1, 1):
        x = sx * (gw + PAR_W / 2)
        _parapet(mb, [(x, yt + 0.2), (x, ye)], col_top=zt + COL_TOP, rng=rng)

    # ---- pilares de apoio descendo para o vazio (tronco de piramide: largo em cima, afina embaixo)
    for yy in (y0 - 22.0, y0 - 50.0, ys + 4.0, yt + 6.0):
        top = L.SPAWN_Z - 2.4 if yy > ys else -2.4
        for sx in (-1, 1):
            x = sx * (gw - 3.0)
            mb.box((4.4, 5.0, 1.2), (x, yy, top - 0.6), (0, 0, 0), "Stone_Dark", 0.15)
            mb.box((3.4, 4.0, 40.0), (x, yy, top - 21.2), (0, 0, 0), "Stone_Dark", 0.1)
            mb.box((2.4, 3.0, 14.0), (x, yy, top - 48.2), (0, 0, 0), "Stone_Dark", 0.1)

    # ---- portao no parapeito sul do spawn (os pilares ficam fora da abertura de 2*gw); mesmo objeto da ponte: os
    # materiais repetidos nao viram MeshParts a mais no Roblox
    g = mb
    for sx in (-1, 1):
        x = sx * (gw + 1.3)
        _pillar(g, x, y0, L.SPAWN_Z, 11.0)
        lantern(g, (x, y0, L.SPAWN_Z), post=False, arm=False, h=10.4, lights=False)     # caixa assenta no capitel
    # verga de madeira + tabuas de telhadinho (le como portao, nao como moldura)
    g.box((2 * gw + 6.4, 1.4, 1.1), (0.0, y0, L.SPAWN_Z + 9.6), (0, 0, 0), "Wood_Dark", 0.12)
    g.box((2 * gw + 7.6, 2.6, 0.45), (0.0, y0, L.SPAWN_Z + 10.4), (0, 0, 0), "Wood_Plank", 0.08)
    for sx in (-1, 1):
        g.box((1.0, 1.0, 2.2), (sx * (gw * 0.55), y0, L.SPAWN_Z + 8.2), (0, 0, D(45)), "Wood_Dark", 0.08)
    ob = mb.finish()
    print("ILHAS: ponte y %.0f..%.0f (plano ate %.0f, escada ate %.0f em z %.2f), portao em y %.0f, largura %.0f" % (
        y0, ye, ys, yt, zt, y0, 2 * gw))
    return ob
