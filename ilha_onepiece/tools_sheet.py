# tools_sheet.py - folhas lado a lado da Ilha 5 (copia do tools_sheet da Ilha 4, com as referencias da Wano).
# uso:
#   python tools_sheet.py <pasta_A> <pasta_B> <saida.jpg> CAM_A,CAM_B,... ["rotulo A" "rotulo B"]
#       a MESMA camera nas duas pastas (antes/depois, previa/roblox)
#   python tools_sheet.py --ref <pasta_ref> <pasta_previa> <pasta_roblox> <saida.jpg> CAM_OP_Ref_01,CAM_OP_Ref_02 ["estado"]
#       cada camera de referencia ao lado da imagem aprovada (ref/ref_0n_*.jpg) - previa e roblox
#   python tools_sheet.py --grid <pasta> <saida.jpg> CAM_A,CAM_B,... [colunas] ["rotulo"]
#       mosaico de varias cameras da mesma pasta (vistas gerais)
import os, sys, glob
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
    if h:
        r = im.width / im.height
        if abs(r - W / h) < 0.08:
            im = im.resize((W, h), Image.LANCZOS)
        elif r > W / h:                   # mais larga: ajusta a altura e corta o excesso dos lados (centrado)
            im = im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
            x0 = (im.width - W) // 2
            im = im.crop((x0, 0, x0 + W, h))
        else:                             # mais alta: ajusta a largura e corta em cima/embaixo (centrado)
            im = im.resize((W, round(im.height * W / im.width)), Image.LANCZOS)
            y0 = (im.height - h) // 2
            im = im.crop((0, y0, W, y0 + h))
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
        n = c.replace("CAM_OP_", "")
        rows.append([frame(a, "%s  %s" % (ta, n)), frame(b, "%s  %s" % (tb, n))])
    if not rows:
        raise SystemExit("nenhuma camera com as duas imagens")
    compose(rows, out)


def ref_sheet(dir_ref, dir_prev, dir_rbx, out, cams, tag=""):
    pre = (tag.strip() + " ") if tag and tag.strip() else ""
    rows = []
    for c in cams:
        k = c[-2:]
        refs = sorted(glob.glob(os.path.join(dir_ref, "ref_%s*.jpg" % k)))
        p, b = os.path.join(dir_prev, c + ".jpg"), os.path.join(dir_rbx, c + ".jpg")
        if not (refs and os.path.exists(p)):
            print("pulado (falta imagem):", c)
            continue
        h = round(W * 9 / 16)
        row = [frame(refs[0], "REFERENCIA %s" % os.path.basename(refs[0])[:-4], h),
               frame(p, "%sPREVIA  %s" % (pre, c.replace("CAM_OP_", "")), h)]
        if os.path.exists(b):
            row.append(frame(b, "%sROBLOX  %s" % (pre, c.replace("CAM_OP_", "")), h))
        rows.append(row)
    compose(rows, out)


def grid(dir_a, out, cams, ncol=3, tag=""):
    rows, cur = [], []
    for c in cams:
        a = os.path.join(dir_a, c + ".jpg")
        if not os.path.exists(a):
            print("pulado (falta imagem):", c)
            continue
        cur.append(frame(a, ("%s %s" % (tag, c.replace("CAM_OP_", ""))).strip()))
        if len(cur) == ncol:
            rows.append(cur)
            cur = []
    if cur:
        rows.append(cur)
    compose(rows, out)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "--ref":
        ref_sheet(a[1], a[2], a[3], a[4], a[5].split(","), a[6] if len(a) > 6 else "")
    elif a and a[0] == "--grid":
        grid(a[1], a[2], a[3].split(","), int(a[4]) if len(a) > 4 else 3, a[5] if len(a) > 5 else "")
    else:
        sheet(a[0], a[1], a[2], a[3].split(","), *(a[4:6] if len(a) >= 6 else ()))
