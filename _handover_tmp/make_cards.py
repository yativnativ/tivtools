#!/usr/bin/env python3
"""Composite the 8 Higgsfield kritzel illustrations into branded TIV share cards.
Run locally (Pillow). Output committed PNGs -> ../grafik-cards/<slug>.png
The illustration sits on a white rounded 'sticker' panel so its white background
merges seamlessly (no freistell-halo on the teal card)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageFilter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SRC = ROOT / "grafik-src"        # committed source illustrations
OUT = ROOT / "grafik-cards"      # committed final cards
OUT.mkdir(exist_ok=True)
FONT = Path("/tmp/Gabarito.ttf")

# Brand colors
TEAL = (10, 74, 74)
TEAL_DK = (8, 56, 56)
PEACH = (248, 222, 205)
GREEN = (41, 165, 121)
TERRA = (229, 152, 117)
CREAM = (250, 244, 236)
WHITE = (255, 255, 255)

S = 1080

CARDS = [
    ("milch", "warum-trinken-veganer-keine-milch", "Warum trinken Veganer keine Milch?",
     "Eine Kuh gibt nur Milch, wenn sie ein Kalb bekommt. Das Kalb wird kurz nach der Geburt getrennt, ausgediente Kühe werden früh geschlachtet."),
    ("ei", "warum-essen-veganer-keine-eier", "Warum essen Veganer keine Eier?",
     "In der Lege-Industrie werden die männlichen Küken getötet, weil sie keine Eier legen. Legehennen werden nach kurzer Zeit geschlachtet."),
    ("honig", "warum-essen-veganer-keinen-honig", "Warum essen Veganer keinen Honig?",
     "Honig ist der Wintervorrat der Bienen. Er wird entnommen und durch Zuckerwasser ersetzt, das Volk wird wirtschaftlich gemanagt."),
    ("huhn", "warum-essen-veganer-keine-freilandeier", "Warum essen Veganer keine Freilandeier?",
     "Auch bei Freiland und Bio werden die männlichen Küken getötet und die Hennen geschlachtet, sobald die Legeleistung sinkt."),
    ("jacke", "warum-keine-second-hand-leder-pelz", "Warum kein Second-Hand-Leder oder -Pelz?",
     "Second-Hand schafft keine neue Nachfrage, das stimmt. Ob man es trägt, ist eine persönliche Abwägung. Neu kaufen lehnen alle Veganer ab."),
    ("kaese", "warum-essen-veganer-keinen-kaese", "Warum essen Veganer keinen Käse?",
     "Käse basiert auf Milch und damit auf derselben Industrie. Viele Sorten enthalten zudem tierisches Lab aus dem Kälbermagen."),
    ("leder", "warum-tragen-veganer-kein-leder", "Warum tragen Veganer kein Leder?",
     "Leder ist kein bloßer Abfall, sondern ein wertvolles Koppelprodukt der Schlachtindustrie und finanziert sie mit."),
    ("schaf", "warum-tragen-veganer-keine-wolle", "Warum tragen Veganer keine Wolle?",
     "Wollschafe sind auf maximale Wollmenge gezüchtet. Die Akkordschur verletzt oft, ausgediente Tiere werden geschlachtet."),
]


def f(size, weight=600):
    fnt = ImageFont.truetype(str(FONT), size)
    try:
        fnt.set_variation_by_axes([weight])
    except Exception:
        pass
    return fnt


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
    return lines


def trim(im, pad=14):
    """Crop white margins of an RGB illustration, leave small padding."""
    im = im.convert("RGB")
    bg = Image.new("RGB", im.size, (255, 255, 255))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -18)  # ignore near-white noise
    bbox = diff.getbbox()
    if not bbox:
        return im
    l, t, r, b = bbox
    l, t = max(0, l - pad), max(0, t - pad)
    r, b = min(im.width, r + pad), min(im.height, b + pad)
    return im.crop((l, t, r, b))


def rounded_mask(size, radius):
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=255)
    return m


def make_card(motif, slug, headline, fakt):
    img = Image.new("RGB", (S, S), TEAL)
    d = ImageDraw.Draw(img, "RGBA")

    # soft deco circles
    d.ellipse([-160, -200, 240, 200], fill=(255, 255, 255, 12))
    d.ellipse([S - 230, S - 360, S + 220, S + 120], fill=(229, 152, 117, 22))

    # brand row
    bx, by = 70, 74
    d.ellipse([bx, by + 4, bx + 26, by + 30], fill=GREEN)
    d.text((bx + 38, by), "This Is Vegan", font=f(34, 700), fill=PEACH)

    # eyebrow
    eb = f(23, 700)
    d.text((72, 138), "G U T   Z U   W I S S E N", font=eb, fill=TERRA)

    # headline
    hsize = 58 if len(headline) <= 34 else (50 if len(headline) <= 46 else 44)
    hf = f(hsize, 800)
    hlines = wrap(d, headline, hf, S - 150)
    y = 182
    for ln in hlines:
        d.text((72, y), ln, font=hf, fill=WHITE)
        y += int(hsize * 1.12)

    # sticker panel with the illustration
    panel = 432
    px = (S - panel) // 2
    py = y + 26
    # shadow
    sh = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([px, py + 10, px + panel, py + panel + 10],
                                         radius=54, fill=(0, 0, 0, 70))
    img.paste(Image.alpha_composite(Image.new("RGBA", (S, S), (0, 0, 0, 0)), sh).convert("RGB"),
              (0, 0), sh.filter(ImageFilter.GaussianBlur(16)))
    d = ImageDraw.Draw(img, "RGBA")
    # white rounded panel
    mask = rounded_mask((panel, panel), 54)
    white_panel = Image.new("RGB", (panel, panel), WHITE)
    img.paste(white_panel, (px, py), mask)

    # illustration trimmed + scaled to fit inside panel
    ill = trim(Image.open(SRC / f"{motif}.png"))
    inner = panel - 56
    scale = min(inner / ill.width, inner / ill.height)
    nw, nh = int(ill.width * scale), int(ill.height * scale)
    ill = ill.resize((nw, nh), Image.LANCZOS)
    ox = px + (panel - nw) // 2
    oy = py + (panel - nh) // 2
    # clip illustration to the rounded panel so corners stay clean
    cell = Image.new("RGB", (panel, panel), WHITE)
    cell.paste(ill, ((panel - nw) // 2, (panel - nh) // 2))
    img.paste(cell, (px, py), mask)

    # fakt
    ff = f(29, 500)
    flines = wrap(d, fakt, ff, S - 150)
    fy = py + panel + 40
    for ln in flines:
        d.text((72, fy), ln, font=ff, fill=PEACH)
        fy += 40

    # IG line bottom
    igf = f(27, 700)
    igt = "IG: thisisvegan.magazin"
    tw = d.textlength(igt, font=igf)
    lx = (S - tw - 44) // 2
    d.ellipse([lx, S - 66, lx + 24, S - 42], fill=GREEN)
    d.text((lx + 38, S - 70), igt, font=igf, fill=CREAM)

    img.save(OUT / f"{slug}.png", optimize=True)
    return f"{slug}.png  ({(OUT / f'{slug}.png').stat().st_size // 1024} KB)"


if __name__ == "__main__":
    SRC.mkdir(exist_ok=True)
    for motif, slug, headline, fakt in CARDS:
        print(make_card(motif, slug, headline, fakt))
