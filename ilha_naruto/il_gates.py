# il_gates - galeria dos 4 portoes de compra que NAO ficam nesta ilha (Shadow Garden, Demon Slayer, One Piece,
# One Punch Man). Cada um mora no proprio modulo il_gate_<k>.py com build_gate(gx, gy, gz, yaw) e segue o padrao
# comum il_gate_std (vao, barreira, cadeado, colisao de bloqueio, marcadores). Aqui so posicionamos em fila, fora da
# ilha (x >= 640), sobre plataformas neutras, para modelar, renderizar e exportar como assets separados.
# (dono: integracao)
import os, math, importlib
import il_gate_std as GS

HERE = os.path.dirname(os.path.abspath(__file__))
MODS = {"ShadowGarden": "il_gate_sg", "DemonSlayer": "il_gate_ds", "OnePiece": "il_gate_op",
        "OnePunchMan": "il_gate_opm"}


def _cams():
    cams = {}
    for key in GS.GALLERY_ORDER:
        gx, gy, gz, yaw = GS.gallery_slot(key)
        cams["CAM_Gate_%s" % key] = ((gx - 20.0, gy - 42.0, gz + 14.0), (gx, gy, gz + 11.0), 22)
        cams["CAM_Gate_%s_Back" % key] = ((gx + 18.0, gy + 40.0, gz + 12.0), (gx, gy, gz + 10.0), 22)
        cams["CAM_Gate_%s_Player" % key] = ((gx + 3.0, gy - 22.0, gz + 6.5), (gx, gy, gz + 9.0), 18)
    x0 = GS.GALLERY_X0 + GS.GALLERY_STEP * 1.5
    cams["CAM_Gates_Lineup"] = ((x0, -250.0, 70.0), (x0, 0.0, 14.0), 24)
    return cams


CAMS = _cams()


def build():
    for key in GS.GALLERY_ORDER:
        gx, gy, gz, yaw = GS.gallery_slot(key)
        F = GS.gate_frame(gx, gy, gz, yaw)
        GS.showcase_platform(key, F)
        m = MODS[key]
        if not os.path.exists(os.path.join(HERE, m + ".py")):
            print("il_gates: %s.py ainda nao existe" % m)
            continue
        importlib.import_module(m).build_gate(gx, gy, gz, yaw)
