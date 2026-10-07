# tools_sheet.py - folhas de ANTES/DEPOIS (mesma camera lado a lado) para o relatorio do refinamento.
# uso: python tools_sheet.py <pasta_antes> <pasta_depois> <saida.jpg> CAM_A,CAM_B,... ["rotulo antes" "rotulo depois"]
import os, sys
from PIL import Image, ImageDraw, ImageFont

W = 960                                  # largura de cada quadro na folha
FONT = "C:/Windows/Fonts/arialbd.ttf"
if not os.path.exists(FONT):   # Linux (container da sessao em nuvem)
    FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def label(im, text, size=26):
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, size)
    x0, y0, x1, y1 = d.textbbox((0, 0), text, font=f)
    d.rectangle((0, 0, x1 - x0 + 24, y1 - y0 + 18), fill=(16, 10, 30))
    d.text((12, 8 - y0), text, font=f, fill=(226, 212, 255))


def frame(path, text):
    im = Image.open(path).convert("RGB")
    im = im.resize((W, round(im.height * W / im.width)), Image.LANCZOS)
    label(im, text)
    return im


def sheet(before_dir, after_dir, out, cams, tb="ANTES", ta="DEPOIS"):
    rows = []
    for c in cams:
        a, b = os.path.join(before_dir, c + ".jpg"), os.path.join(after_dir, c + ".jpg")
        if not (os.path.exists(a) and os.path.exists(b)):
            print("pulado (falta imagem):", c)
            continue
        name = c.replace("CAM_SG_", "")
        rows.append((frame(a, "%s  %s" % (tb, name)), frame(b, "%s  %s" % (ta, name))))
    if not rows:
        raise SystemExit("nenhuma camera com as duas imagens")
    gap = 8
    h = sum(max(x.height, y.height) for x, y in rows) + gap * (len(rows) + 1)
    out_im = Image.new("RGB", (W * 2 + gap * 3, h), (10, 8, 18))
    y = gap
    for x_im, y_im in rows:
        out_im.paste(x_im, (gap, y))
        out_im.paste(y_im, (W + gap * 2, y))
        y += max(x_im.height, y_im.height) + gap
    out_im.save(out, quality=88)
    print("folha:", out, len(rows), "cameras")


if __name__ == "__main__":
    a = sys.argv[1:]
    sheet(a[0], a[1], a[2], a[3].split(","), *(a[4:6] if len(a) >= 6 else ()))
