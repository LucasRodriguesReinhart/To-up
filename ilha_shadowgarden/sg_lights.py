# sg_lights - VESTIR / LUZES da Ilha 3 (Shadow Garden). ONDA 2 (2026-09-30, planta v4).
# Cada luz sai de uma fonte de verdade, pequena e sem sombra (no Roblox PointLight Shadows=false):
#   1. RUA (NightOnly pelo prefixo L_SGProp_ no export_sg.NIGHT_ONLY): os postes ACESOS do sg_props (praca, cruzamento
#      do P2, pe da escada leste, boca do beco oeste), com a luz no centro do vidro, e o foco do patio do sg_court
#      (COURT_LIGHTS). Os postes da porta do castelo e do pe da escada P1P2 ficam so no Neon: a porta ja tem a
#      L_SGCas_Door e o topo da escada o arco de ferro da vila (L_SGVil_Lamp_*).
#   2. CASAS (ativas de dia; o cluster do export nao chega nelas): 1 luz quente por andar. As 4 da lareira
#      (L_SGVil_House_H1/H2/H5/H7, sg_village_int) continuam; aqui entram as que faltam, nas posicoes que o agente da
#      vila propos (Roblox -> referencial do projeto por sg_layout.local_of_world). Cada uma substitui o
#      PREVIEW_L_SGVil_<casa>_<T|A> (luz de area so da previa) do mesmo andar.
# Orcamento (ER.BUDGET day_lights 48): prioridade portal da masmorra > salao > casas > lanternas da rua; as da rua ja
# sao NightOnly e nao contam de dia.
import sg_lib as SL
from sg_lib import light
import sg_layout as L
import sg_props as PR
import sg_court as CT

WARM = (1.0, 0.70, 0.42)
HOUSE_WARM = (1.0, 0.66, 0.36)                  # o mesmo tom da luz da lareira (sg_village_int.house_light)
P1, P2 = L.P1, L.P2
CAMS = {
    "CAM_SGLight_VilNight": ((24.0, -150.0, P2 + 9.0), (-40.0, -222.0, P1 + 2.0), 22),
    "CAM_SGLight_PH_StreetW": ((-30.0, -216.0, P1 + 5.5), (-120.0, -224.0, P1 + 5.0), 22),
    "CAM_SGLight_PH_P2Street": ((10.0, -84.0, P2 + 5.5), (-90.0, -88.0, P2 + 5.0), 22),
    "CAM_SGLight_Int_H3": ((100.0, -249.0, P1 + 6.0), (88.0, -264.0, P1 + 4.0), 20),
    "CAM_SGLight_Int_H5A": ((-58.0, -106.0, P2 + 19.0), (-74.0, -118.0, P2 + 15.0), 20),
}
EXTRA_ROUTES = {}
EXTRA_PROBES = []
MAX_STREET = 9                                  # teto das luzes de rua (NightOnly)
LAMP_E = 300.0

# casa -> (terreo, andar) em coordenadas do ROBLOX (X, Y, Z); None = sem luz nova (ja existe ou nao ha andar)
HOUSE_RBX = {
    "H1": (None, (-867.5, 57.2, 765.6)),
    "H2": (None, (-940.2, 55.2, 790.6)),
    "H3": ((-900.1, 39.7, 592.2), (-904.1, 55.2, 581.2)),
    "H4": ((-978.9, 39.7, 582.7), None),
    "H5": (None, (-1017.7, 63.2, 765.7)),
    "H6": ((-1059.8, 47.7, 826.5), None),
    "H7": (None, (-1068.9, 63.2, 774.8)),
}
HOUSE_E = 900.0                                 # Roblox ~ Range 14 / Brightness 0,86 (lareira: 260); = a previa da vila


def house_lights():
    out = []
    for nm, pair in HOUSE_RBX.items():
        for tag, p in zip(("T", "A"), pair):
            if p is None:
                continue
            x, y = L.local_of_world(p[0], -p[2])
            out.append(("L_SGVil_House_%s_%s" % (nm, tag), (round(x, 2), round(y, 2), p[1]), "PREVIEW_L_SGVil_%s_%s" % (nm, tag)))
    return out


def build():
    import bpy
    n = 0
    want = [("L_SGProp_%s" % name, PR.GLASS.get(name, (x, y, z + PR.LAMP_H)), LAMP_E, WARM, 0.4)
            for name, x, y, z, lit in PR.LAMPS if lit]
    want += [("L_SGProp_%s" % name, loc, e, col, rad) for name, loc, e, col, rad in CT.COURT_LIGHTS]
    for name, loc, e, col, rad in want:
        if n >= MAX_STREET:
            print("LIGHTS AVISO: teto de %d luzes de rua: %s fica sem luz" % (MAX_STREET, name))
            continue
        light(name, "POINT", loc, e, col, rad)
        n += 1
    nh = 0
    for name, loc, prev in house_lights():
        ob = bpy.data.objects.get(prev)
        if ob is not None:
            bpy.data.objects.remove(ob, do_unlink=True)
        light(name, "POINT", loc, HOUSE_E, HOUSE_WARM, 0.5)
        nh += 1
    print("LIGHTS rua=%d (NightOnly) casas=%d (de dia)" % (n, nh))
