# tools_sheet.py - folhas lado a lado da Ilha 4 (copia do tools_sheet da Ilha 3, com o modo de referencia).
# uso:
#   python tools_sheet.py <pasta_A> <pasta_B> <saida.jpg> CAM_A,CAM_B,... ["rotulo A" "rotulo B"]
#       a MESMA camera nas duas pastas (antes/depois, previa/roblox)
#   python tools_sheet.py --ref <pasta_ref> <pasta_previa> <pasta_roblox> <saida.jpg> CAM_DS_Ref_01,... ["estado"]
#       cada camera de referencia ao lado da imagem aprovada (ref_0n.jpg) - previa e roblox. "estado" vai no rotulo
#       (ex.: "BLOCKOUT", "ONDA 4"); sem ele o rotulo e so PREVIA/ROBLOX (ONDA 4: antes era sempre "BLOCKOUT")
import os, sys
from PIL import Image, ImageDraw, ImageFont

W = 960                                  # largura de cada quadro na folha
FONT = "C:/Windows/Fonts/arialbd.ttf"


def label(im, text, size=24):
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, size)
    x0, y0, x1, y1 = d.textbbox((0, 0), text, font=f)
    d.rectangle((0, 0, x1 - x0 + 24, y1 - y0 + 18), fill=(12, 16, 34))
    d.text((12, 8 - y0), text, font=f, fill=(226, 232, 255))


def frame(path, text, h=None):
    im = Image.open(path).convert("RGB")
    if h:                                 # mesma altura (as referencias nao sao 16:9 exato)
        im = im.resize((W, h), Image.LANCZOS) if abs(im.width / im.height - W / h) < 0.08 else \
            im.resize((round(im.width * h / im.height), h), Image.LANCZOS).crop((0, 0, W, h))
    else:
        im = im.resize((W, round(im.height * W / im.width)), Image.LANCZOS)
    label(im, text)
    return im


def compose(rows, out):
    gap = 8
    ncol = max(len(r) for r in rows)
    h = sum(max(x.height for x in r) for r in rows) + gap * (len(rows) + 1)
    im = Image.new("RGB", (W * ncol + gap * (ncol + 1), h), (8, 10, 22))
    y = gap
    for r in rows:
        for k, x in enumerate(r):
            im.paste(x, (gap + k * (W + gap), y))
        y += max(x.height for x in r) + gap
    im.save(out, quality=88)
    print("folha:", out, len(rows), "linhas")


def sheet(dir_a, dir_b, out, cams, ta="PREVIA", tb="ROBLOX"):
    rows = []
    for c in cams:
        a, b = os.path.join(dir_a, c + ".jpg"), os.path.join(dir_b, c + ".jpg")
        if not (os.path.exists(a) and os.path.exists(b)):
            print("pulado (falta imagem):", c)
            continue
        n = c.replace("CAM_DS_", "")
        rows.append([frame(a, "%s  %s" % (ta, n)), frame(b, "%s  %s" % (tb, n))])
    if not rows:
        raise SystemExit("nenhuma camera com as duas imagens")
    compose(rows, out)


def ref_sheet(dir_ref, dir_prev, dir_rbx, out, cams, tag=""):
    pre = (tag.strip() + " ") if tag and tag.strip() else ""
    rows = []
    for c in cams:
        k = c[-2:]
        r = os.path.join(dir_ref, "ref_%s.jpg" % k)
        p, b = os.path.join(dir_prev, c + ".jpg"), os.path.join(dir_rbx, c + ".jpg")
        if not (os.path.exists(r) and os.path.exists(p)):
            print("pulado (falta imagem):", c)
            continue
        h = round(W * 9 / 16)
        row = [frame(r, "REFERENCIA ref_%s" % k, h), frame(p, "%sPREVIA  %s" % (pre, c.replace("CAM_DS_", "")), h)]
        if os.path.exists(b):
            row.append(frame(b, "%sROBLOX  %s" % (pre, c.replace("CAM_DS_", "")), h))
        rows.append(row)
    compose(rows, out)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "--ref":
        ref_sheet(a[1], a[2], a[3], a[4], a[5].split(","), a[6] if len(a) > 6 else "")
    else:
        sheet(a[0], a[1], a[2], a[3].split(","), *(a[4:6] if len(a) >= 6 else ()))
