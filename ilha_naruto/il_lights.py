# il_lights - luzes de ambientacao da Ilha 1 (dono: integracao). As lanternas de rua (il_props.LAMP_SPOTS) ganham
# luz NOTURNA (prefixo L_Lantern_: o export marca NightOnly). De dia a ilha e iluminada pelo sol do Roblox; as luzes
# de dia ficam com os marcos (summon, portao DB, interiores), dentro do teto de luzes do export.
import il_lib as IL
from il_lib import light
import il_props


def build():
    n = 0
    for name, x, y, z in il_props.LAMP_SPOTS:
        light(name, "POINT", (x, y, z), 160, (1.0, 0.55, 0.3), 0.4)
        n += 1
    print("LIGHTS noturnas de rua=%d" % n)
