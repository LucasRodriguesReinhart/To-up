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


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "ref":
        ref_sheet(a[1], a[2], a[3])
    elif a[0] == "plan":
        plan_sheet(a[1], a[2])
    elif a[0] == "jogador":
        pair_sheet(a[1], a[2], a[3], PLAYER, "Lobby Vila Medieval V0 - altura do jogador (boneco R15 5,2 studs)")
    elif a[0] == "aereo":
        pair_sheet(a[1], a[2], a[3], AIR, "Lobby Vila Medieval V0 - vistas aereas")
