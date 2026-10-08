# vm_sheet.py - FOLHAS de avaliacao do lobby Vila Medieval (Python + PIL, sem Blender)
#   python vm_sheet.py ref   <pasta_previa> <pasta_roblox> <saida.jpg>   ref_01 | previa | roblox (CAM_VM_Ref_01)
#   python vm_sheet.py plan  <pasta_previa> <saida.jpg>                  planta aprovada | vista de cima (mesmo recorte)
#                                                                         | sobreposicao (planta a 45% por cima)
#   python vm_sheet.py jogador <pasta_previa> <pasta_roblox> <saida.jpg>  altura do jogador: previa | roblox por camera
#   python vm_sheet.py aereo <pasta_previa> <pasta_roblox> <saida.jpg>    vistas aereas: previa | roblox
import os, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "ref")
W = 960
FONT = "C:/Windows/Fonts/arialbd.ttf"
PLAYER = ["CAM_VM_P_Spawn", "CAM_VM_P_Praca", "CAM_VM_P_Rua", "CAM_VM_P_Forja", "CAM_VM_P_Loja", "CAM_VM_P_Ranking",
          "CAM_VM_P_Portais", "CAM_VM_P_Saida"]
AIR = ["CAM_VM_Air_Sul", "CAM_VM_Air_Oeste", "CAM_VM_Air_Norte"]


def label(im, text, size=22):
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, size)
    x0, y0, x1, y1 = d.textbbox((0, 0), text, font=f)
    d.rectangle((0, 0, x1 - x0 + 24, y1 - y0 + 16), fill=(12, 16, 34))
    d.text((12, 7 - y0), text, font=f, fill=(226, 232, 255))
    return im


def fit(path, w=W, h=None):
    im = Image.open(path).convert("RGB")
    if h is None:
        return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    s = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    l, t = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((l, t, l + w, t + h))


def compose(rows, out, title=None):
    gap = 8
    ncol = max(len(r) for r in rows)
    th = 44 if title else 0
    h = sum(max(x.height for x in r) for r in rows) + gap * (len(rows) + 1) + th
    wi = max(sum(x.width for x in r) + gap * (len(r) + 1) for r in rows)
    im = Image.new("RGB", (wi, h), (8, 10, 22))
    if title:
        d = ImageDraw.Draw(im)
        d.text((gap + 4, 10), title, font=ImageFont.truetype(FONT, 24), fill=(240, 240, 255))
    y = gap + th
    for r in rows:
        x = gap
        for k in r:
            im.paste(k, (x, y))
            x += k.width + gap
        y += max(k.height for k in r) + gap
    im.save(out, quality=88)
    print("folha:", out, im.size)


def ref_sheet(dp, dr, out):
    h = 540
    row = [label(fit(os.path.join(REF, "ref_01_estilo_vila.jpg"), W, h), "REFERENCIA ref_01"),
           label(fit(os.path.join(dp, "CAM_VM_Ref_01.jpg"), W, h), "V0 BLOCKOUT  PREVIA  CAM_VM_Ref_01")]
    rows = [row]
    rb = os.path.join(dr, "CAM_VM_Ref_01.jpg")
    if os.path.exists(rb):
        rows.append([label(fit(os.path.join(dp, "CAM_VM_P_Spawn.jpg"), W, h), "PREVIA  spawn (forja = marco no eixo)"),
                     label(fit(rb, W, h), "V0 BLOCKOUT  ROBLOX  CAM_VM_Ref_01")])
    compose(rows, out, "Lobby Vila Medieval V0 - rua curva (rua de chegada das ilhas) x ref_01")


def plan_sheet(dp, out):
    pl = Image.open(os.path.join(REF, "planta_aprovada_v1.png")).convert("RGB")
    top = Image.open(os.path.join(dp, "CAM_VM_Plan.jpg")).convert("RGB").resize(pl.size, Image.LANCZOS)
    over = Image.blend(top, pl, 0.42)
    s = 0.62
    rows = [[label(pl.resize((round(pl.width * s), round(pl.height * s))), "PLANTA APROVADA v1"),
             label(top.resize((round(pl.width * s), round(pl.height * s))), "V0 vista de cima (mesmo recorte)"),
             label(over.resize((round(pl.width * s), round(pl.height * s))), "SOBREPOSICAO (planta 42%)")]]
    compose(rows, out, "Lobby Vila Medieval V0 - planta aprovada x blockout (norte = forja em cima; 0,316 stud/px)")


def pair_sheet(dp, dr, out, cams, title):
    rows = []
    for c in cams:
        a, b = os.path.join(dp, c + ".jpg"), os.path.join(dr, c + ".jpg")
        if not os.path.exists(a):
            continue
        n = c.replace("CAM_VM_", "")
        r = [label(fit(a, 640), "PREVIA  " + n)]
        if os.path.exists(b):
            r.append(label(fit(b, 640), "ROBLOX  " + n))
        rows.append(r)
    # duas cameras por linha (4 quadros) para a folha nao ficar alta demais
    rows2 = []
    for i in range(0, len(rows), 2):
        rows2.append(rows[i] + (rows[i + 1] if i + 1 < len(rows) else []))
    compose(rows2, out, title)


# ------------------------------------------------------------------ V1 (trecho praca -> ponte + kit)
T_CLOSES = ["CAM_VM_T_C_Fachada", "CAM_VM_T_C_Porta", "CAM_VM_T_C_Janela", "CAM_VM_T_C_Telhado", "CAM_VM_T_C_Loja",
            "CAM_VM_T_C_Rua", "CAM_VM_T_C_Ponte", "CAM_VM_T_C_Canal", "CAM_VM_T_C_Praca", "CAM_VM_T_C_Poste"]


def v1_jogador(dp, dr, out):
    rows = []
    for c, t in (("CAM_VM_T_PracaPonte", "praca -> ponte"), ("CAM_VM_T_PontePraca", "ponte -> praca")):
        rows.append([label(fit(os.path.join(dp, c + ".jpg"), W, 540), "PREVIA  " + t),
                     label(fit(os.path.join(dr, c + ".jpg"), W, 540), "ROBLOX  " + t)])
    compose(rows, out, "Lobby Vila Medieval V1 - trecho na altura do jogador (olho a +6,5; boneco 5,2)")


def v1_ref(dp, dr, out):
    h = 540
    rows = [[label(fit(os.path.join(REF, "ref_01_estilo_vila.jpg"), W, h), "REFERENCIA ref_01"),
             label(fit(os.path.join(dr, "CAM_VM_T_Ref.jpg"), W, h), "V1 ROBLOX  CAM_VM_T_Ref (camera equivalente)")],
            [label(fit(os.path.join(dp, "CAM_VM_T_Ref.jpg"), W, h), "V1 PREVIA  CAM_VM_T_Ref"),
             label(fit(os.path.join(dr, "CAM_VM_T_C_Praca.jpg"), W, h), "V1 ROBLOX  esquina da praca (carroca)")]]
    compose(rows, out, "Lobby Vila Medieval V1 - ref_01 x trecho final (rua do eixo, praca -> ponte)")


def v1_grid(d, cams, out, title, prefix="ROBLOX  ", w=640, per=3):
    tiles = []
    for c in cams:
        f = os.path.join(d, c + ".jpg")
        if os.path.exists(f):
            tiles.append(label(fit(f, w, round(w * 9 / 16)), prefix + c.replace("CAM_VM_T_", "").replace("CAM_", ""), 18))
    rows = [tiles[i:i + per] for i in range(0, len(tiles), per)]
    compose(rows, out, title)


# ------------------------------------------------------------------ V2b (a vila: vm_town)
V2_SHEETS = [
    ("FOLHA_spawn_praca_forja.jpg", ["CAM_VM_V2_SpawnPraca", "CAM_VM_V2_PracaForja", "CAM_VM_V2_RuaForja"],
     "spawn -> praca -> forja (eixo norte)"),
    ("FOLHA_loja.jpg", ["CAM_VM_V2_LojaFora", "CAM_VM_V2_LojaDentro"], "loja de mochilas: fora e dentro (vendedor = boneco)"),
    ("FOLHA_ranking.jpg", ["CAM_VM_V2_Ranking"], "ranking Top 100: palco, adro e salao (quadros = previa do script)"),
    ("FOLHA_portais.jpg", ["CAM_VM_V2_Portais", "CAM_VM_V2_PortaisDentro"], "patio dos portais (6 portais aprovados)"),
    ("FOLHA_saida_ponte.jpg", ["CAM_VM_V2_RuaSaida", "CAM_VM_V2_Portao", "CAM_VM_V2_Ponte"],
     "rua de saida, portao e ponte da Ilha 1"),
    ("FOLHA_canal.jpg", ["CAM_VM_V2_Canal", "CAM_VM_V2_CanalOeste"], "canal: muros e pontezinhas"),
]


def v2_sheets(dp, dr, outdir):
    os.makedirs(outdir, exist_ok=True)
    for fn, cams, t in V2_SHEETS:
        rows = []
        for c in cams:
            n = c.replace("CAM_VM_V2_", "")
            rows.append([label(fit(os.path.join(dp, c + ".jpg"), W, 540), "PREVIA  " + n),
                         label(fit(os.path.join(dr, c + ".jpg"), W, 540), "ROBLOX  " + n)])
        compose(rows, os.path.join(outdir, fn), "Lobby Vila Medieval V2b - " + t)
    # praca 360 na altura do jogador (roblox em cima, previa embaixo)
    cams = ["CAM_VM_V2_Praca360_%d" % k for k in range(4)]
    rows = [[label(fit(os.path.join(d, c + ".jpg"), 640, 360), "%s  %s" % (m, ("leste", "sul", "oeste", "norte")[i]), 18)
             for i, c in enumerate(cams)] for d, m in ((dr, "ROBLOX"), (dp, "PREVIA"))]
    compose(rows, os.path.join(outdir, "FOLHA_praca360.jpg"),
            "Lobby Vila Medieval V2b - praca 360 na altura do jogador (do medalhao para leste, sul, oeste, norte)")
    # aerea x planta aprovada
    pl = Image.open(os.path.join(REF, "planta_aprovada_v1.png")).convert("RGB")
    top = Image.open(os.path.join(dr, "CAM_VM_Plan.jpg")).convert("RGB").resize(pl.size, Image.LANCZOS)
    over = Image.blend(top, pl, 0.42)
    s = 0.62
    sz = (round(pl.width * s), round(pl.height * s))
    rows = [[label(pl.resize(sz), "PLANTA APROVADA v1"), label(top.resize(sz), "V2b vista de cima (ROBLOX)"),
             label(over.resize(sz), "SOBREPOSICAO (planta 42%)")],
            [label(fit(os.path.join(dr, "CAM_VM_V2_Air_SE.jpg"), 1110, 624), "ROBLOX  aerea sudeste"),
             label(fit(os.path.join(dr, "CAM_VM_V2_Air_W.jpg"), 1110, 624), "ROBLOX  aerea oeste")]]
    compose(rows, os.path.join(outdir, "FOLHA_aerea.jpg"), "Lobby Vila Medieval V2b - aerea x planta aprovada")
    # ref_01 lado a lado
    h = 540
    rows = [[label(fit(os.path.join(REF, "ref_01_estilo_vila.jpg"), W, h), "REFERENCIA ref_01"),
             label(fit(os.path.join(dr, "CAM_VM_V2_Ref01.jpg"), W, h), "V2b ROBLOX  rua curva de saida")],
            [label(fit(os.path.join(dp, "CAM_VM_V2_Ref01.jpg"), W, h), "V2b PREVIA  rua curva de saida"),
             label(fit(os.path.join(dr, "CAM_VM_V2_Praca360_0.jpg"), W, h), "V2b ROBLOX  praca -> rua da loja")]]
    compose(rows, os.path.join(outdir, "FOLHA_ref01.jpg"), "Lobby Vila Medieval V2b - ref_01 x vila")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "v2vila":                          # <pasta_previa> <pasta_roblox> <pasta_saida>
        v2_sheets(a[1], a[2], a[3])
    elif a[0] == "ref":
        ref_sheet(a[1], a[2], a[3])
    elif a[0] == "plan":
        plan_sheet(a[1], a[2])
    elif a[0] == "jogador":
        pair_sheet(a[1], a[2], a[3], PLAYER, "Lobby Vila Medieval V0 - altura do jogador (boneco R15 5,2 studs)")
    elif a[0] == "aereo":
        pair_sheet(a[1], a[2], a[3], AIR, "Lobby Vila Medieval V0 - vistas aereas")
    elif a[0] == "v1jogador":
        v1_jogador(a[1], a[2], a[3])
    elif a[0] == "v1ref":
        v1_ref(a[1], a[2], a[3])
    elif a[0] == "v1closes":                     # <pasta> <saida> [rotulo]
        v1_grid(a[1], T_CLOSES, a[2], "Lobby Vila Medieval V1 - closes na altura do jogador (%s, boneco 5,2)" % (
            a[3] if len(a) > 3 else "ROBLOX"), prefix=(a[3] if len(a) > 3 else "ROBLOX") + "  ")
    elif a[0] == "v1medal":
        v1_grid(a[1], ["CAM_VM_T_MedalTop", "CAM_VM_T_MedalSpawn"], a[2],
                "Lobby Vila Medieval V1 - medalhao da praca (picareta + bigorna, rebaixado, sem colisao)", w=960, per=2)
    elif a[0] == "v1kit":                         # <pasta_estudio> <saida> [rotulo]
        cams = sorted(f[:-4] for f in os.listdir(a[1]) if f.startswith("CAM_ST_") and f.endswith(".jpg"))
        v1_grid(a[1], cams, a[2], "Lobby Vila Medieval V1 - kit da vila: presets e pecas (%s, boneco 5,2)" % (
            a[3] if len(a) > 3 else "ROBLOX"), prefix=(a[3] if len(a) > 3 else "ROBLOX") + "  ")
