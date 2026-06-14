#!/usr/bin/env python3
"""Build downloadable iPhone-size (1080x1920) phrase cards per language for the
Vegan-auf-Reisen tool. Flag on top, the most important phrases in the middle,
This Is Vegan logo + source at the bottom. Run locally (Pillow).
Flags in /tmp/flags/<cc>.png, output committed to ../reise-cards/<slug>.png."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FLAGS = Path("/tmp/flags")
OUT = ROOT / "reise-cards"
OUT.mkdir(exist_ok=True)
GAB = "/tmp/Gabarito.ttf"
UNI = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"

TEAL = (10, 74, 74)
PEACH = (248, 222, 205)
GREEN = (41, 165, 121)
TERRA = (229, 152, 117)
CREAM = (246, 236, 225)
WHITE = (255, 255, 255)
W, H = 1080, 1920

# the 6 phrases that go on the saveable card (incl. the friendly ordering one)
CARD_KEYS = ["bin_vegan", "no_animal", "contains", "no_cheese", "recommend_polite", "thanks"]


def gab(size, weight=700):
    f = ImageFont.truetype(GAB, size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def uni(size):
    return ImageFont.truetype(UNI, size)


def wrap(draw, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [""]


def rounded(size, radius, fill):
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=fill)
    return im


def make(lang, phrases):
    img = Image.new("RGB", (W, H), TEAL)
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([-200, -260, 240, 180], fill=(255, 255, 255, 9))
    d.ellipse([W - 320, H - 360, W + 200, H + 160], fill=(229, 152, 117, 16))

    pad = 80
    cx = W // 2

    # flag (fit into 300x200 box, rounded, subtle border)
    flag = Image.open(FLAGS / f"{lang['cc']}.png").convert("RGB")
    fb_w, fb_h = 300, 200
    scale = min(fb_w / flag.width, fb_h / flag.height)
    fw, fh = int(flag.width * scale), int(flag.height * scale)
    flag = flag.resize((fw, fh), Image.LANCZOS)
    fmask = Image.new("L", (fw, fh), 0)
    ImageDraw.Draw(fmask).rounded_rectangle([0, 0, fw - 1, fh - 1], radius=22, fill=255)
    fy = 96
    img.paste(flag, (cx - fw // 2, fy), fmask)
    d.rounded_rectangle([cx - fw // 2, fy, cx - fw // 2 + fw - 1, fy + fh - 1], radius=22, outline=(248, 222, 205, 120), width=2)

    # eyebrow + language title + native
    y = fy + fh + 40
    eb = gab(24, 700)
    ebt = "V E G A N   A U F   R E I S E N"
    d.text((cx - d.textlength(ebt, font=eb) / 2, y), ebt, font=eb, fill=TERRA)
    y += 44
    tf = gab(62, 800)
    tt = lang["name"]
    d.text((cx - d.textlength(tt, font=tf) / 2, y), tt, font=tf, fill=CREAM)
    y += 76
    nf = uni(28)
    nt = lang["native"]
    d.text((cx - d.textlength(nt, font=nf) / 2, y), nt, font=nf, fill=PEACH)
    y += 60

    # phrase blocks (dynamic height, light rounded panels)
    pmap = {p["key"]: p for p in phrases}
    label_f = uni(25)
    # Gabarito is Latin-only; non-Latin scripts need the Unicode font for the translation.
    needs_uni = lang["slug"] in ("japanisch", "griechisch")
    x_f = uni(37) if needs_uni else gab(37, 700)
    rom_f = uni(23)
    inner = W - 2 * pad - 48
    for key in CARD_KEYS:
        p = pmap[key]
        t = lang["t"][key]
        de = p["de"]
        xt = t["x"]
        rom = t.get("r")
        xlines = wrap(d, xt, x_f, inner)
        # block height
        bh = 26 + 30 + len(xlines) * 46 + (30 if rom else 0) + 26
        panel = rounded((W - 2 * pad, bh), 26, (248, 222, 205, 12))
        img.paste(panel, (pad, y), panel)
        d2 = ImageDraw.Draw(img, "RGBA")
        iy = y + 24
        d2.text((pad + 24, iy), de, font=label_f, fill=(248, 222, 205, 180))
        iy += 36
        for ln in xlines:
            d2.text((pad + 24, iy), ln, font=x_f, fill=CREAM)
            iy += 46
        if rom:
            d2.text((pad + 24, iy + 2), rom, font=rom_f, fill=(248, 222, 205, 150))
        y += bh + 16

    # footer
    fy2 = H - 150
    d.ellipse([cx - 112, fy2, cx - 112 + 22, fy2 + 22], fill=GREEN)
    bf = gab(34, 800)
    d.text((cx - 70, fy2 - 6), "This Is Vegan", font=bf, fill=PEACH)
    sf = uni(24)
    s1 = "von www.this-is-vegan.com"
    s2 = "IG: thisisvegan.magazin"
    d.text((cx - d.textlength(s1, font=sf) / 2, fy2 + 42), s1, font=sf, fill=(248, 222, 205, 200))
    d.text((cx - d.textlength(s2, font=sf) / 2, fy2 + 76), s2, font=sf, fill=(248, 222, 205, 200))

    sl = lang["slug"]
    out_path = OUT / f"{sl}.png"
    img.save(out_path, optimize=True)
    return f"{sl}.png ({out_path.stat().st_size // 1024} KB)"


if __name__ == "__main__":
    data = json.loads((ROOT / "data" / "reise-data.json").read_text(encoding="utf-8"))
    for lang in data["languages"]:
        print(make(lang, data["phrases"]))
