# portal_sheet.py - monta a prancha de avaliacao de um portal a partir dos PNGs do portal_studio (python normal)
# uso: python portal_sheet.py <pasta> <Key|ALL> <saida.jpg> [titulo]
import sys, os, glob
from PIL import Image, ImageDraw, ImageFont

src, key, out = sys.argv[1], sys.argv[2], sys.argv[3]
title = sys.argv[4] if len(sys.argv) > 4 else key
fs = sorted(glob.glob(os.path.join(src, key + "_*.png")))
if not fs:
    raise SystemExit("nenhum PNG para " + key)
hero = [f for f in fs if "_A_Hero" in f or "ALL_Ledge" in f]
rest = [f for f in fs if f not in hero]
W = 1920
try:
    font = ImageFont.truetype("arial.ttf", 30)
    small = ImageFont.truetype("arial.ttf", 20)
except Exception:
    font = small = ImageFont.load_default()
tiles = []
if hero:
    im = Image.open(hero[0]).convert("RGB")
    tiles.append(("full", im.resize((W, int(W * im.height / im.width))), os.path.basename(hero[0])[:-4]))
cols = 3
tw = W // cols
th = int(tw * 9 / 16)
rows = (len(rest) + cols - 1) // cols
H = 60 + (tiles[0][1].height if tiles else 0) + rows * (th + 30) + 10
sheet = Image.new("RGB", (W, H), (22, 22, 26))
d = ImageDraw.Draw(sheet)
d.text((20, 14), title, fill=(255, 214, 120), font=font)
y = 60
if tiles:
    sheet.paste(tiles[0][1], (0, y))
    y += tiles[0][1].height
for i, f in enumerate(rest):
    im = Image.open(f).convert("RGB").resize((tw, th))
    x = (i % cols) * tw
    yy = y + (i // cols) * (th + 30)
    d.text((x + 10, yy + 4), os.path.basename(f)[:-4].split("_", 1)[1], fill=(210, 210, 210), font=small)
    sheet.paste(im, (x, yy + 28))
sheet.save(out, quality=90)
print("sheet", out, len(fs))
