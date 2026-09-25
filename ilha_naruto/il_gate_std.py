# il_gate_std - PADRAO TECNICO COMUM dos portoes de compra (COMPARTILHADO E CONGELADO; dono: integracao).
# Todos os portoes (Dragon Ball na ilha; Shadow Garden, Demon Slayer, One Piece e One Punch Man na galeria) usam:
#   - o MESMO vao livre (OPEN_W x OPEN_H), a mesma largura de piso (DECK_W) e a mesma profundidade de referencia;
#   - a MESMA logica de interacao e os MESMOS marcadores (relativos ao eixo do portao);
#   - o MESMO par de estados: LOCKED (barreira de energia + cadeado + colisao) e UNLOCKED (tudo isso some; sobra a
#     moldura com a passagem limpa e o efeito de abertura no marcador GATE_<k>_OpenFX).
# Cada portao desenha a PROPRIA moldura (silhueta, materiais, ornamento) em volta disto.
#
# Referencial do portao (G): origem = centro do vao no nivel do piso; +Y = direcao de quem ATRAVESSA (sai da ilha),
# -Y = lado de quem chega (onde fica a interacao), +X = direita de quem atravessa, Z para cima.
# Use gate_frame(gx, gy, gz, yaw).p(x, y, z) para converter local -> mundo.
#
# Contrato com o jogo (Roblox):
#   GATE_<k>_Barrier (MeshPart, Neon)  atributo gate_part="barrier" -> Transparency 1 ao desbloquear
#   GATE_<k>_Lock    (MeshPart)        atributo gate_part="lock"    -> some ao desbloquear
#   COL_Gate<k>Lock_001 (Part invisivel, col_kind="GateLock", gate=<k>) -> CanCollide false ao desbloquear
#   GATE_<k>_OpenFX  (marcador)        ponto dos efeitos de abertura (VFX diferente do bloqueado)
#   GATE_<k>_INTERACT (marcador)       ProximityPrompt / zona de compra (raio no atributo radius)
#   PURCHASE_UI_ANCHOR_<k> (marcador)  ancora do painel de preco (BillboardGui) - NADA de placa 3D com preco
import math
from mathutils import Vector
import il_lib as IL
from il_lib import MB, col_box, mk
from fm_parts import Frame

OPEN_W = 16.0        # vao livre
OPEN_H = 18.0        # altura livre
DECK_W = 18.0        # largura do piso/ponte que chega ao portao
DEPTH = 10.0         # profundidade de referencia da moldura (pode variar por portao)
INTERACT_D = 7.0     # interacao: 7 studs antes do plano da barreira
EXIT_D = 12.0        # saida: 12 depois
UI_Z = 14.0          # painel de preco: dentro do vao (acima do cadeado), a camera do jogador no prompt enxerga
KEYS = {"DB": "DragonBall", "ShadowGarden": "ShadowGarden", "DemonSlayer": "DemonSlayer", "OnePiece": "OnePiece",
        "OnePunchMan": "OnePunchMan"}
AREA_ID = {"DB": 2, "DemonSlayer": 3, "ShadowGarden": 4, "OnePiece": 5, "OnePunchMan": 6}
GALLERY_X0 = 640.0   # galeria dos portoes (fora da ilha, so para modelar/renderizar/exportar)
GALLERY_STEP = 130.0
GALLERY_Z = 16.2
GALLERY_ORDER = ["ShadowGarden", "DemonSlayer", "OnePiece", "OnePunchMan"]
# nucleo claro da energia (aneis e rachaduras sobre a barreira): le como energia, nao como disco chapado
import fm_lib as _fl


def gate_frame(gx, gy, gz, yaw):
    """yaw: rotacao Z tal que o +Y local aponta para quem atravessa"""
    return Frame(gx, gy, gz, yaw)


def gallery_slot(key):
    i = GALLERY_ORDER.index(key)
    return (GALLERY_X0 + GALLERY_STEP * i, 0.0, GALLERY_Z, 0.0)


# nucleo claro da energia TINGIDO por portao (identidade de cada um; no Roblox vira Neon)
CORE_TINT = {"DB": (255, 214, 120), "ShadowGarden": (206, 160, 255), "DemonSlayer": (255, 150, 120),
             "OnePiece": (140, 214, 255), "OnePunchMan": (255, 226, 140)}


def core_mat(key):
    name = "Energy_Core_%s_Glow" % key
    c = CORE_TINT.get(key, (255, 244, 214))
    _fl.MATS.setdefault(name, (_fl.S(*c), 0.3, 0.0, 2.0, _fl.S(*c), 0.0))
    return name


def outline(shape, n=None):
    """contorno 2D (u = x local, v = z local) do vao da barreira, anti-horario em (u, v)"""
    hw, h = OPEN_W / 2, OPEN_H
    if shape == "rect":
        return [(-hw, 0.0), (hw, 0.0), (hw, h), (-hw, h)]
    if shape == "arch":
        n = n or 14
        zs = h - hw
        pts = [(-hw, 0.0), (hw, 0.0), (hw, zs)]
        for i in range(1, n):
            a = math.pi * i / n
            pts.append((hw * math.cos(a), zs + hw * math.sin(a)))
        pts.append((-hw, zs))
        return pts
    n = n or 28
    r = min(hw, h / 2)
    return [(r * math.cos(2 * math.pi * i / n), h / 2 + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def plate(mb, F, pts2, y0, y1, mat, tint=None):
    """placa extrudada em Y local (y0 < y1): tampas n-gono + laterais, SEM faces internas, enrolamento explicito
    (tampa y0 com normal -Y, tampa y1 com +Y, laterais para fora). pts2 anti-horario em (u, v)."""
    bm = mb.bm
    va = [bm.verts.new(F.p(u, y0, v)) for u, v in pts2]
    vb = [bm.verts.new(F.p(u, y1, v)) for u, v in pts2]
    bm.faces.new(va)
    bm.faces.new(list(reversed(vb)))
    n = len(pts2)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((va[i], vb[i], vb[j], va[j]))
    mb._post(va + vb, mat, tint, 0, 1)


def barrier(key, F, mat, shape="arch", thick=0.5, lock_mat="Metal_Gold", rng=None):
    """barreira de energia (LOCKED) no plano y=0 do portao + cadeado dos dois lados + colisao de bloqueio.
    shape: 'rect' | 'arch' (retangulo + meio circulo no topo) | 'circle' (disco; os cantos ficam por conta da moldura
    do portao, p.ex. painel de pedra com vao redondo, + soleira de energia embaixo).
    A barreira e UMA placa fechada (normais certas: o Roblox descarta face de tras) + aneis e rachaduras do nucleo
    (tingido por portao) afastados 0,15 das faces."""
    hw, h = OPEN_W / 2, OPEN_H
    mb = MB("GATE_%s_Barrier" % key, "08_PURCHASE_GATES", rng, detail="hero")
    plate(mb, F, outline(shape), -thick / 2, thick / 2, mat)
    if shape == "circle":
        plate(mb, F, [(-hw, 0.0), (hw, 0.0), (hw, 1.2), (-hw, 1.2)], -thick / 2, thick / 2, mat)
    cm = core_mat(key)
    _energy_detail(mb, F, shape, thick, cm, rng)
    ob = mb.finish(recalc=False)
    ob["gate"] = key
    ob["gate_part"] = "barrier"
    ob["gate_state"] = "locked"
    # cadeado estilizado (corpo + alca), nos dois lados da barreira, com contorno brilhante no nucleo do portao
    lk = MB("GATE_%s_Lock" % key, "08_PURCHASE_GATES", rng, detail="hero")
    zl = h * 0.46
    for s in (-1, 1):
        y = s * (thick / 2 + 0.55)
        lk.box((3.2, 0.7, 2.7), F.p(0, y, zl), F.r(), lock_mat, 0.0)
        for sx in (-1, 1):
            lk.box((0.55, 0.55, 2.0), F.p(sx * 1.05, y, zl + 2.1), F.r(), lock_mat, 0.0)
        lk.box((2.65, 0.55, 0.55), F.p(0, y, zl + 3.0), F.r(), lock_mat, 0.0)
        lk.box((0.5, 1.0, 1.0), F.p(0, y, zl - 0.2), F.r(), "Metal_Dark", 0.0)
        lk.box((3.9, 0.3, 3.4), F.p(0, s * (thick / 2 + 0.2), zl), F.r(), cm, 0.0)       # halo do cadeado
    lo = lk.finish()
    lo["gate"] = key
    lo["gate_part"] = "lock"
    lo["gate_state"] = "locked"
    col = col_box("Gate%sLock" % key, (OPEN_W + 0.6, 1.4, h), F.p(0, 0, h / 2), F.r(), kind="GateLock")
    col["gate"] = key
    return ob, lo, col


def _energy_detail(mb, F, shape, thick, cm, rng):
    """2 aneis interrompidos + 6 rachaduras radiais em zigue-zague, secao >= 0,3, a 0,15 de cada face"""
    import random as _r
    rng = rng or _r.Random(7)
    hw, h = OPEN_W / 2, OPEN_H
    zc = h / 2 if shape != "arch" else h * 0.47
    rmax = min(hw, h / 2) * 0.88
    for s in (-1, 1):
        y = s * (thick / 2 + 0.15 + 0.15)
        for k, fr in enumerate((0.5, 0.9)):
            r = rmax * fr
            n = 12
            for i in range(n):
                if (i + k * 3) % 6 == 2:
                    continue
                a0 = 2 * math.pi * i / n
                a1 = 2 * math.pi * (i + 1) / n
                mb.beam(F.p(r * math.cos(a0), y, zc + r * math.sin(a0)), F.p(r * math.cos(a1), y, zc + r * math.sin(a1)),
                        0.3, 0.3, cm, 0.0)
        for j in range(6):
            a = 2 * math.pi * j / 6 + 0.35 + rng.uniform(-0.15, 0.15)
            pts = []
            for t in (0.14, 0.5, 0.95):
                rr = rmax * t
                aa = a + rng.uniform(-0.2, 0.2)
                pts.append(F.p(rr * math.cos(aa), y, zc + rr * math.sin(aa)))
            for p0, p1 in zip(pts, pts[1:]):
                mb.beam(p0, p1, 0.3, 0.3, cm, 0.0)


def markers(key, F, yaw, area_id=None):
    """os 5 marcadores obrigatorios + o do efeito de abertura, sempre nas mesmas posicoes relativas"""
    area_id = area_id if area_id is not None else AREA_ID.get(key, 0)
    mk("GATE_%s" % key, F.p(0, 0, 0), (0, 0, yaw), 4.0, "ARROWS",
       props={"open_w": OPEN_W, "open_h": OPEN_H, "deck_w": DECK_W, "area_id": area_id, "key": key})
    mk("GATE_%s_LOCKED" % key, F.p(0, 0, OPEN_H / 2), (0, 0, yaw), 2.0, "CUBE",
       props={"gate": key, "state_default": "locked"})
    mk("GATE_%s_INTERACT" % key, F.p(0, -INTERACT_D, 0.2), (0, 0, yaw), 2.0, "SPHERE",
       props={"gate": key, "radius": 10.0})
    mk("GATE_%s_EXIT" % key, F.p(0, EXIT_D, 0.2), (0, 0, yaw), 2.0, "ARROWS", props={"gate": key})
    mk("PURCHASE_UI_ANCHOR_%s" % key, F.p(0, -2.5, UI_Z), (0, 0, yaw + math.pi), 2.0, "SINGLE_ARROW",
       props={"gate": key, "faces": "approach", "ui": "BillboardGui preco/requisito"})
    mk("GATE_%s_OpenFX" % key, F.p(0, 0, OPEN_H / 2), (0, 0, yaw), 3.0, "SPHERE",
       props={"gate": key, "state": "unlocked", "fx": "abertura"})     # vai no export como marcador


def showcase_platform(key, F, length=46.0, width=38.0, z_top=0.0, m="Stone_Paving_Warm", side_m="Stone_Wall_Dark"):
    """plataforma neutra da galeria (so para modelar/renderizar os portoes fora da ilha); nao vai para a ilha.
    Topo do tabuleiro EXATAMENTE no nivel do portao (gz); a base tem 38 x 46 (os portoes tem ~34 de base)."""
    mb = MB("GATEGAL_%s_Platform" % key, "08_PURCHASE_GATES", None, detail="near")
    mb.box((width, length, 3.0), F.p(0, 0, z_top - 1.9), F.r(), side_m, 0.2)
    mb.box((DECK_W, length + 0.2, 0.4), F.p(0, 0, z_top - 0.2), F.r(), m, 0.05)
    mb.finish()
    col_box("GateGal%s" % key, (width, length, 3.0), F.p(0, 0, z_top - 1.5), F.r())
