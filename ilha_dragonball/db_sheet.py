# db_sheet.py - pranchas da Ilha 2 (Dragon Ball) de comparacao (Python do sistema + Pillow, fora do Blender)
#   python db_sheet.py compare <pasta_renders> <saida.jpg>     referencia x render lado a lado (recortes da concept aprovada x CAM_DB_*)
#   python db_sheet.py grid <pasta_renders> <saida.jpg> [cols]  todas as cameras num grid (contact sheet)
import os, sys, glob
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
PAIRS = [("ref_main_view.jpg", "CAM_DB_Ref_Main"), ("ref_view_top.jpg", "CAM_DB_Ref_Top"),
         ("ref_view_front.jpg", "CAM_DB_Ref_Front"), ("ref_view_side.jpg", "CAM_DB_Ref_Side"),
         ("ref_view_back.jpg", "CAM_DB_Back"), ("ref_summon.jpg", "CAM_DB_Ref_Summon"),
         ("ref_village.jpg", "CAM_DB_Ref_Village"), ("ref_capsule.jpg", "CAM_DB_Ref_Capsule"),
         ("ref_environment.jpg", "CAM_DB_Ref_Environment"), ("ref_next_gate.jpg", "CAM_DB_Ref_Gate")]


def _font(sz):
    for f in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(f, sz)
        except OSError:
            pass
    return ImageFont.load_default()


def _find(folder, cam):
    for ext in (".png", ".jpg"):
        p = os.path.join(folder, cam + ext)
        if os.path.exists(p):
            return p
    return None


def compare(folder, out, w=760):
    rows = []
    for ref, cam in PAIRS:
        rp = os.path.join(HERE, "refs", ref)
        cp = _find(folder, cam)
        if not cp:
            continue
        a = Image.open(rp).convert("RGB")
        b = Image.open(cp).convert("RGB")
        h = int(w * 9 / 16)
        a = a.resize((w, int(a.height * w / a.width))).crop((0, 0, w, h))
        b = b.resize((w, int(b.height * w / b.width))).crop((0, 0, w, h))
        rows.append((a, b, cam))
    if not rows:
        print("nada para comparar")
        return
    h = rows[0][0].height
    sheet = Image.new("RGB", (w * 2 + 12, (h + 6) * len(rows)), (24, 24, 28))
    d = ImageDraw.Draw(sheet)
    f = _font(18)
    for i, (a, b, cam) in enumerate(rows):
        y = i * (h + 6)
        sheet.paste(a, (0, y))
        sheet.paste(b, (w + 12, y))
        d.text((8, y + 6), "REF", fill=(255, 255, 0), font=f)
        d.text((w + 20, y + 6), cam, fill=(255, 255, 0), font=f)
    sheet.save(out, quality=88)
    print("prancha:", out, sheet.size)


def grid(folder, out, cols=4, w=480):
    files = sorted(glob.glob(os.path.join(folder, "CAM_*.png")) + glob.glob(os.path.join(folder, "CAM_*.jpg")))
    if not files:
        print("sem imagens")
        return
    h = int(w * 9 / 16)
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (w + 6), rows * (h + 26)), (24, 24, 28))
    d = ImageDraw.Draw(sheet)
    f = _font(16)
    for i, p in enumerate(files):
        im = Image.open(p).convert("RGB")
        im = im.resize((w, int(im.height * w / im.width))).crop((0, 0, w, h))
        x, y = (i % cols) * (w + 6), (i // cols) * (h + 26)
        sheet.paste(im, (x, y + 22))
        d.text((x + 4, y + 2), os.path.splitext(os.path.basename(p))[0], fill=(230, 230, 230), font=f)
    sheet.save(out, quality=88)
    print("contact sheet:", out, sheet.size)


if __name__ == "__main__":
    mode, folder, out = sys.argv[1], sys.argv[2], sys.argv[3]
    if mode == "compare":
        compare(folder, out)
    else:
        grid(folder, out, int(sys.argv[4]) if len(sys.argv) > 4 else 4)
