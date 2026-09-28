# sg_lights - VESTIR / LUZES da Ilha 3 (Shadow Garden): ate 6 luzes, SO nos trechos de rota que ficaram escuros a
# noite nos renders (nada dentro de predio: cada zona ja tem as suas). Cada luz sai de uma lanterna de verdade do
# sg_props (poste aceso): quente, pequena, sem sombra (no Roblox PointLight Shadows=false).
#   - praca: o par do norte, ao pe da escada P1->P2 (a vila deixou esse trecho para o vestir);
#   - rua do P2 no oeste (entre as casas, a caminho do mirante da cachoeira);
#   - fim da rua leste do P1 (mirante da cachoeira leste).
import sg_lib as SL
from sg_lib import light
import sg_layout as L
import sg_props as PR

WARM = (1.0, 0.70, 0.42)
CAMS = {
    "CAM_SGLight_PH_P2West": ((-96.0, -46.0, L.P2 + 5.2), (-40.0, -46.0, L.P2 + 4.0), 22),
    "CAM_SGLight_PH_P1East": ((60.0, -121.0, L.P1 + 5.2), (130.0, -110.0, L.P1 + 3.0), 22),
    "CAM_SGLight_PH_P1SouthW": ((-26.0, -128.0, L.P1 + 5.2), (-60.0, -160.0, L.P1 + 2.0), 22),
}
EXTRA_ROUTES = {}
EXTRA_PROBES = []
MAX_LIGHTS = 6


def build():
    n = 0
    for name, x, y, z, lit in PR.LAMPS:
        if not lit:
            continue
        if n >= MAX_LIGHTS:
            print("LIGHTS AVISO: teto de %d luzes: %s fica sem luz" % (MAX_LIGHTS, name))
            continue
        light("L_SGProp_%s" % name, "POINT", (x, y, z + PR.LAMP_H), 300.0, WARM, 0.4)
        n += 1
    print("LIGHTS luzes=%d" % n)
