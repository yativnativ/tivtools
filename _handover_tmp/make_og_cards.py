#!/usr/bin/env python3
"""Composite the per-tool Higgsfield illustrations into 1200x630 branded OG/share
cards. Run locally (Pillow). Sources in /tmp/ogill/<slug>.png, output committed
to ../og-cards/<slug>.png. Landscape layout: text left, illustration on a white
sticker panel right (white illu bg merges with panel, no freistell-halo)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageFilter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SRC = Path("/tmp/ogill")
OUT = ROOT / "og-cards"
OUT.mkdir(exist_ok=True)
FONT = Path("/tmp/Gabarito.ttf")
LOGO = ROOT / "og-assets" / "logo-tiv-cream.png"


def paste_logo(img, x, y, h):
    lg = Image.open(LOGO).convert("RGBA")
    w = round(lg.width * h / lg.height)
    lg = lg.resize((w, h), Image.LANCZOS)
    img.paste(lg, (x, y), lg)

TEAL = (10, 74, 74)
PEACH = (248, 222, 205)
GREEN = (41, 165, 121)
TERRA = (229, 152, 117)
CREAM = (246, 236, 225)
WHITE = (255, 255, 255)

W, H = 1200, 630

# slug -> (eyebrow, headline, subline)
CARDS = {
    "hub": ("VEGANE TOOLS", "Kostenlose vegane Tools", "Schnelle Helfer für Einkauf, Küche und Alltag. Ohne Anmeldung, direkt im Browser."),
    "e-nummern": ("TOOL · ZUSATZSTOFFE", "E-Nummern-Checker", "Ist der Zusatzstoff vegan? 113 E-Nummern mit klarer Einordnung."),
    "vegan-ersetzen": ("TOOL · ERSETZEN", "Vegan-Ersatz-Finder", "Ei, Butter, Käse, Gelatine: die beste pflanzliche Alternative mit Menge."),
    "naehrstoffrechner": ("TOOL · NÄHRSTOFFE", "Nährstoff-Rechner", "Protein, B12, Eisen, Omega-3 und Calcium für deinen Bedarf."),
    "ist-das-vegan": ("TOOL · CHECK", "Ist das vegan?", "Lebensmittel eingeben und die versteckten tierischen Fallen sofort sehen."),
    "impact-rechner": ("TOOL · IMPACT", "Impact-Rechner", "Gerettete Tiere, gespartes CO2, Wasser und Ackerland deiner Ernährung."),
    "saisonkalender": ("TOOL · SAISON", "Saisonkalender", "Welches Obst und Gemüse gerade regional Saison hat, Monat für Monat."),
    "pflanzendrink-vergleich": ("TOOL · VERGLEICH", "Pflanzendrink-Vergleich", "Hafer, Soja, Mandel und Co. für Kaffee, Backen, Protein und Klima."),
    "protein-tabelle": ("TOOL · PROTEIN", "Protein-Tabelle", "Die proteinreichsten pflanzlichen Lebensmittel, durchsuchbar pro 100 g."),
    "co2-fussabdruck": ("TOOL · KLIMA", "CO2-Fußabdruck", "Der Klima-Fußabdruck von Lebensmitteln im Vergleich, tierisch gegen pflanzlich."),
    "protein-pro-mahlzeit": ("TOOL · PROTEIN", "Protein pro Mahlzeit", "Mahlzeit zusammenstellen und das Eiweiß sofort summieren."),
    "veganizer": ("TOOL · ARGUMENTE", "Veganizer", "Schlagfertige, fundierte Antworten auf die häufigsten Anti-Vegan-Sprüche."),
    "creator": ("FÜR CONTENT CREATOR", "Creator-Tools", "Schrift, Hashtags und Bildtools für deinen veganen Account."),
    "schriftarten": ("CREATOR · SCHRIFT", "Schriftarten-Generator", "Text in 18 Stilen kopieren, plus vegane Deko und Trenner."),
    "bild-freistellen": ("CREATOR · BILD", "Bild freistellen", "Hintergrund automatisch entfernen, komplett im Browser. Ohne Upload."),
    "hashtags": ("CREATOR · HASHTAGS", "Hashtag-Helfer", "Kuratierte vegane Hashtag-Sets nach Thema, auf Deutsch und Englisch."),
    "vegan-auf-reisen": ("TOOL · REISEN", "Vegan auf Reisen", "„Ich bin vegan“ und die wichtigsten Sätze in 12 Sprachen, zum Zeigen."),
    "versteckte-zutaten": ("TOOL · CHECK", "Versteckte tierische Zutaten", "Gelatine, Karmin, Molke: was heimlich tierisch ist und wo es sich versteckt."),
    "vegane-materialien": ("TOOL · MODE", "Vegane Materialien", "Leder, Wolle, Seide oder doch Kork und Apfelleder? Was tierfrei ist und was nicht."),
    "getraenke-vegan": ("TOOL · CHECK", "Ist mein Getränk vegan?", "Wein, Bier, Sekt und Likör im Check, samt versteckter tierischer Klärhilfen."),
}


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
    im = im.convert("RGB")
    bg = Image.new("RGB", im.size, (255, 255, 255))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -18)
    bbox = diff.getbbox()
    if not bbox:
        return im
    l, t, r, b = bbox
    l, t = max(0, l - pad), max(0, t - pad)
    r, b = min(im.width, r + pad), min(im.height, b + pad)
    return im.crop((l, t, r, b))


def rounded_mask(size, radius):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=255)
    return m


def make(slug, eyebrow, headline, subline):
    img = Image.new("RGB", (W, H), TEAL)
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([-180, -240, 220, 160], fill=(255, 255, 255, 10))
    d.ellipse([W - 360, H - 200, W + 160, H + 260], fill=(229, 152, 117, 20))

    # sticker panel right
    panel = 450
    px, py = W - panel - 56, (H - panel) // 2
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([px, py + 10, px + panel, py + panel + 10], radius=56, fill=(0, 0, 0, 65))
    img.paste(Image.new("RGB", (W, H), TEAL), (0, 0), sh.filter(ImageFilter.GaussianBlur(16)))
    d = ImageDraw.Draw(img, "RGBA")
    mask = rounded_mask((panel, panel), 56)
    ill = trim(Image.open(SRC / f"{slug}.png"))
    inner = panel - 60
    scale = min(inner / ill.width, inner / ill.height)
    nw, nh = int(ill.width * scale), int(ill.height * scale)
    ill = ill.resize((nw, nh), Image.LANCZOS)
    cell = Image.new("RGB", (panel, panel), WHITE)
    cell.paste(ill, ((panel - nw) // 2, (panel - nh) // 2))
    img.paste(cell, (px, py), mask)

    # text left
    x0 = 72
    textw = px - x0 - 48
    # brand: echtes TIV-Logo (cream)
    paste_logo(img, x0, 62, 50)
    # eyebrow (letterspaced)
    d.text((x0, 140), " ".join(eyebrow), font=f(19, 700), fill=TERRA)
    # headline
    hl = len(headline)
    hsize = 72 if hl <= 17 else (60 if hl <= 26 else 48)
    hf = f(hsize, 800)
    hlines = wrap(d, headline, hf, textw)
    y = 178
    for ln in hlines:
        d.text((x0, y), ln, font=hf, fill=CREAM)
        y += int(hsize * 1.1)
    # subline
    y += 12
    sf = f(25, 500)
    for ln in wrap(d, subline, sf, textw)[:3]:
        d.text((x0, y), ln, font=sf, fill=PEACH)
        y += 34
    # footer url
    d.text((x0, H - 70), "tools.this-is-vegan.com", font=f(23, 700), fill=(248, 222, 205))

    img.save(OUT / f"{slug}.png", optimize=True)
    return f"{slug}.png ({(OUT / f'{slug}.png').stat().st_size // 1024} KB, {len(hlines)} headline lines)"


if __name__ == "__main__":
    for slug, (eb, hl, sl) in CARDS.items():
        src = SRC / f"{slug}.png"
        if not src.exists():
            print(f"MISSING illustration: {slug}")
            continue
        print(make(slug, eb, hl, sl))
