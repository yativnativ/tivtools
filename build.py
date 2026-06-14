#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Statischer Site-Generator für die This-Is-Vegan-Tools (Cloudflare Pages).

Liest data/enummern-data.json und baut nach dist/:
  /                       Tool-Übersichtsseite (Hub)
  /e-nummern/             interaktiver E-Nummern-Checker + komplette Liste
  /e-nummern/<code>/      eine SEO-Seite pro Zusatzstoff (FAQ-Schema, Breadcrumbs)
  sitemap.xml, robots.txt, _headers, 404.html, /fonts/*, favicon.svg

Aufruf:  python3 build.py
"""
import html
import json
import shutil
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
DATA_FILE = ROOT / "data" / "enummern-data.json"

# Bei Wechsel auf Subdirectory-Deploy (this-is-vegan.com/tools) nur diese
# beiden Werte anpassen und neu bauen.
BASE_URL = "https://tools.this-is-vegan.com"
PREFIX = ""  # z. B. "/tools" beim Reverse-Proxy-Setup

MAIN_SITE = "https://this-is-vegan.com"

READ_MORE = [
    ("Versteckte tierische Inhaltsstoffe", f"{MAIN_SITE}/versteckte-tierische-inhaltsstoffe/"),
    ("Gelatine erkennen und vegane Alternativen", f"{MAIN_SITE}/gelatine-erkennen-und-vegane-alternativen/"),
    ("Ist Maltodextrin vegan?", f"{MAIN_SITE}/was-ist-eigentlich-maltodextrin-ist-maltodextrin-vegan/"),
    ("Die wichtigsten veganen Logos im Überblick", f"{MAIN_SITE}/die-wichtigsten-veganen-logos-im-ueberblick/"),
]

LABEL = {
    "yes": {"t": "Vegan", "s": "Pflanzlich, mineralisch oder synthetisch", "icon": "✓"},
    "no": {"t": "Nicht vegan", "s": "Tierischen Ursprungs", "icon": "✕"},
    "maybe": {"t": "Kommt drauf an", "s": "Kann tierisch oder pflanzlich sein", "icon": "?"},
}

CLASS_BLURB = {
    "Emulgator": "Emulgatoren verbinden Wasser und Fett, damit sich Zutaten nicht trennen. Typisch in Backwaren, Schokolade, Margarine und Fertigprodukten.",
    "Farbstoff": "Farbstoffe geben Lebensmitteln Farbe oder gleichen Farbverluste bei der Verarbeitung aus.",
    "Verdickungsmittel": "Verdickungsmittel binden Wasser und geben Soßen, Desserts und Drinks eine cremigere Konsistenz.",
    "Geschmacksverstärker": "Geschmacksverstärker intensivieren den Eigengeschmack, vor allem die herzhafte Umami-Note in Chips, Würzmischungen und Fertiggerichten.",
    "Säureregulator": "Säureregulatoren halten den Säuregrad eines Lebensmittels konstant und stabilisieren so Geschmack und Haltbarkeit.",
    "Süßstoff": "Süßstoffe süßen praktisch kalorienfrei und sind ein Vielfaches süßer als Zucker.",
    "Trennmittel": "Trennmittel verhindern, dass Pulver, Tabletten oder geriebene Lebensmittel verklumpen oder aneinander kleben.",
    "Süßungsmittel": "Süßungsmittel wie Zuckeralkohole süßen mit weniger Kalorien als Zucker und stecken oft in zuckerfreien Produkten.",
    "Konservierungsstoff": "Konservierungsstoffe verlängern die Haltbarkeit, indem sie Bakterien, Hefen und Schimmel hemmen.",
    "Säuerungsmittel": "Säuerungsmittel geben einen sauren Geschmack und senken den pH-Wert, was Lebensmittel haltbarer macht.",
    "Geliermittel": "Geliermittel lassen Flüssigkeiten fest werden, etwa in Gummibärchen, Marmelade, Tortenguss oder Desserts.",
    "Antioxidationsmittel": "Antioxidationsmittel schützen Lebensmittel vor Sauerstoff, damit Fette nicht ranzig werden und Farben stabil bleiben.",
    "Überzugsmittel": "Überzugsmittel geben Oberflächen Glanz und Schutz, etwa bei Süßigkeiten, Dragees, Obst oder Kaugummi.",
    "Trägerstoff": "Trägerstoffe lösen oder verdünnen andere Zusatzstoffe und Aromen, damit sie sich gleichmäßig verteilen lassen.",
    "Packgas": "Packgase ersetzen in der Verpackung den Sauerstoff und halten Lebensmittel so länger frisch.",
    "Mehlbehandlungsmittel": "Mehlbehandlungsmittel verbessern die Backeigenschaften von Teigen, vor allem bei industrieller Brötchen- und Brotproduktion.",
    "Backtriebmittel": "Backtriebmittel lockern Teige auf, indem sie beim Backen Gas freisetzen.",
    "Festigungsmittel": "Festigungsmittel halten Obst, Gemüse oder Tofu fest und formstabil.",
    "Feuchthaltemittel": "Feuchthaltemittel verhindern das Austrocknen von Lebensmitteln und halten sie geschmeidig.",
    "Farbstabilisator": "Farbstabilisatoren erhalten die natürliche Farbe eines Lebensmittels während Verarbeitung und Lagerung.",
    "Enzyme": "Enzyme beschleunigen als Hilfsstoffe Prozesse wie Teigreifung oder Saftklärung und sind im Endprodukt oft nicht mehr aktiv.",
    "Farbstoff / Trennmittel": "Wird sowohl als weißer Farbstoff als auch als Trennmittel gegen Verklumpen eingesetzt.",
    "Treibgas": "Treibgase drücken Lebensmittel aus der Verpackung, etwa bei Sprühsahne, oder sorgen für Kohlensäure.",
    "Entschäumer": "Entschäumer verhindern unerwünschte Schaumbildung bei der Herstellung, etwa beim Frittieren.",
}

STATUS_GUIDE = {
    "yes": "Du kannst Produkte mit {code} aus veganer Sicht entspannt kaufen. Der Stoff wird pflanzlich, mineralisch oder synthetisch hergestellt, tierische Quellen spielen in der Praxis keine Rolle.",
    "no": "{code} ist immer tierischen Ursprungs. Ein Produkt, das {code} enthält, ist damit nicht vegan. Die gute Nachricht: Für die meisten Einsatzzwecke gibt es pflanzliche Alternativen, und viele Hersteller steigen um.",
    "maybe": "Bei {code} hilft nur ein Blick aufs Produkt: Steht ein Vegan-Label drauf, ist die Herkunft pflanzlich. Ohne Label bleibt nur die Nachfrage beim Hersteller, denn die Herkunft muss auf der Zutatenliste nicht angegeben werden.",
}

# ---------------------------------------------------------------- helpers

def esc(s):
    return html.escape(str(s), quote=True)


def slug(code):
    return code.lower()


def url(path):
    return PREFIX + path


def german_date(iso):
    months = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli",
              "August", "September", "Oktober", "November", "Dezember"]
    y, m, d = (int(x) for x in iso.split("-"))
    return f"{d}. {months[m - 1]} {y}"


def meta_description(a):
    first = a["info"].split(". ")[0].rstrip(".") + "."
    lead = {
        "yes": f"{a['code']} ist vegan.",
        "no": f"{a['code']} ist nicht vegan.",
        "maybe": f"{a['code']} ist nicht automatisch vegan.",
    }[a["status"]]
    desc = f"{lead} {first} Status, Erklärung und ähnliche Zusatzstoffe im E-Nummern-Checker von This Is Vegan."
    if len(desc) > 155:
        desc = f"{lead} {first}"
        if len(desc) > 155:
            desc = desc[:152].rstrip() + "..."
    return desc


# ---------------------------------------------------------------- CSS

CSS = """
:root{--peach:#f8decd;--teal-bg:#0a4a4a;--teal-deep:#073a3a;--teal-card:#0a6b6c;--teal:#147d77;--green:#29a579;--green-deep:#106050;--terra:#e59875;--terra-light:#f7b79a;--yes:#2a9d6f;--no:#c0392b;--maybe:#d68a3a;--ink:#0a3030;--line:rgba(248,222,205,.16)}
*{box-sizing:border-box;margin:0;padding:0}
@font-face{font-family:'Gabarito';font-style:normal;font-weight:500 900;font-display:swap;src:url(/fonts/gabarito-latin.woff2) format('woff2')}
@font-face{font-family:'Figtree';font-style:normal;font-weight:400 700;font-display:swap;src:url(/fonts/figtree-latin.woff2) format('woff2')}
html{scroll-behavior:smooth}
body{background:var(--teal-bg);color:var(--peach);font-family:'Figtree',system-ui,sans-serif;line-height:1.55;-webkit-font-smoothing:antialiased;min-height:100vh}
.wrap{max-width:920px;margin:0 auto;padding:0 20px}
a{color:inherit}
header.site{padding:22px 0 4px;display:flex;align-items:center;justify-content:space-between;gap:16px}
.brand{display:flex;align-items:center;gap:10px;font-family:'Gabarito';font-weight:800;letter-spacing:-.02em;font-size:18px;text-decoration:none}
.brand .dot{width:11px;height:11px;border-radius:50%;background:var(--green);box-shadow:0 0 0 4px rgba(41,165,121,.22)}
.brand small{display:block;font-family:'Figtree';font-weight:500;font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--terra);opacity:.85;margin-top:-3px}
.free{font-size:12px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:var(--peach);opacity:.7}
.crumbs{padding:18px 0 0;font-size:13px;opacity:.75}
.crumbs a{text-decoration:none}
.crumbs a:hover{text-decoration:underline}
.crumbs span{opacity:.55;margin:0 6px}
.hero{padding:44px 0 14px;text-align:center}
.hero.left{text-align:left;padding-top:30px}
.eyebrow{font-size:12px;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:var(--terra);margin-bottom:18px}
h1{font-family:'Gabarito';font-weight:900;letter-spacing:-.035em;font-size:clamp(40px,8vw,76px);line-height:.95;color:var(--peach)}
h1.detail{font-size:clamp(34px,6.5vw,58px)}
h1 .q{color:var(--green)}
.sub{margin:18px auto 0;max-width:540px;font-size:17px;color:var(--peach);opacity:.82}
.hero.left .sub{margin-left:0}
h2{font-family:'Gabarito';font-weight:800;font-size:26px;letter-spacing:-.02em}
.search-shell{margin:34px auto 0;max-width:620px;position:relative}
.search-box{display:flex;align-items:center;gap:12px;background:var(--peach);border-radius:18px;padding:6px 6px 6px 22px;box-shadow:0 18px 50px -18px rgba(0,0,0,.55);border:2px solid transparent;transition:border-color .15s,box-shadow .15s}
.search-box:focus-within{border-color:var(--green);box-shadow:0 20px 60px -16px rgba(41,165,121,.5)}
.search-box svg{flex:none;color:var(--teal)}
#q{flex:1;min-width:0;border:0;background:transparent;outline:none;font-family:'Gabarito';font-weight:600;font-size:20px;color:var(--ink);padding:14px 0}
#q::placeholder{color:var(--teal);opacity:.55;font-weight:500}
.go{flex:none;border:0;cursor:pointer;background:var(--ink);color:var(--peach);font-family:'Gabarito';font-weight:700;font-size:15px;padding:14px 22px;border-radius:13px;transition:background .15s,transform .1s}
.go:hover{background:var(--green-deep)}
.go:active{transform:scale(.97)}
.chips{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:18px auto 0;max-width:620px}
.chips span{font-size:12px;color:var(--peach);opacity:.6;align-self:center;margin-right:2px}
.chip{border:1px solid var(--line);background:rgba(248,222,205,.04);color:var(--peach);font-family:'Figtree';font-weight:600;font-size:13px;padding:6px 13px;border-radius:999px;cursor:pointer;transition:all .14s}
.chip:hover{background:var(--peach);color:var(--ink);border-color:var(--peach)}
#result{margin:30px auto 0;max-width:620px}
.card{background:var(--peach);color:var(--ink);border-radius:20px;overflow:hidden;box-shadow:0 22px 60px -24px rgba(0,0,0,.6);animation:pop .28s cubic-bezier(.2,.9,.3,1.2);text-align:left}
@keyframes pop{from{opacity:0;transform:translateY(10px) scale(.985)}to{opacity:1;transform:none}}
.verdict{display:flex;align-items:center;gap:14px;padding:18px 24px;color:#fff;font-family:'Gabarito';font-weight:800}
.verdict.yes{background:var(--yes)}
.verdict.no{background:var(--no)}
.verdict.maybe{background:var(--maybe)}
.verdict .mark{width:38px;height:38px;flex:none;border-radius:50%;background:rgba(255,255,255,.22);display:grid;place-items:center;font-size:22px}
.verdict .vtext{font-size:22px;letter-spacing:-.01em;line-height:1.1}
.verdict .vtext small{display:block;font-family:'Figtree';font-weight:500;font-size:12px;letter-spacing:.12em;text-transform:uppercase;opacity:.8}
.card-body{padding:22px 24px 24px}
.enum{font-family:'Gabarito';font-weight:900;font-size:30px;letter-spacing:-.03em;color:var(--ink)}
.ename{font-weight:600;font-size:18px;color:var(--teal);margin-top:-2px}
.klasse{display:inline-block;margin-top:12px;font-size:12px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--green-deep);background:rgba(16,96,80,.1);padding:5px 11px;border-radius:7px}
.info{margin-top:14px;font-size:16px;color:#264a48}
.note{margin-top:14px;padding:13px 15px;border-radius:11px;font-size:14px;background:rgba(214,138,58,.13);border-left:3px solid var(--maybe);color:#6b4419;display:flex;gap:9px}
.note b{font-weight:600}
.detail-link{display:inline-block;margin-top:16px;font-family:'Gabarito';font-weight:700;font-size:14px;color:var(--green-deep)}
.miss{background:var(--peach);color:var(--ink);border-radius:18px;padding:26px 24px;text-align:center;box-shadow:0 18px 50px -24px rgba(0,0,0,.5);animation:pop .28s ease}
.miss h3{font-family:'Gabarito';font-weight:800;font-size:20px}
.miss p{margin-top:6px;color:#3a5856;font-size:15px}
.listsec{margin-top:64px;padding-bottom:30px}
.listhead{display:flex;align-items:flex-end;justify-content:space-between;gap:20px;flex-wrap:wrap;margin-bottom:20px}
.listhead p{font-size:14px;opacity:.7;max-width:340px}
.filters{display:flex;gap:8px;flex-wrap:wrap}
.filt{cursor:pointer;border:1px solid var(--line);background:transparent;color:var(--peach);font-family:'Figtree';font-weight:600;font-size:13px;padding:8px 14px;border-radius:999px;display:flex;align-items:center;gap:7px;transition:all .14s}
.filt .swatch{width:9px;height:9px;border-radius:50%}
.filt.s-yes .swatch{background:var(--yes)}
.filt.s-no .swatch{background:var(--no)}
.filt.s-maybe .swatch{background:var(--maybe)}
.filt.active{background:var(--peach);color:var(--ink);border-color:var(--peach)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:10px}
.item{background:rgba(248,222,205,.05);border:1px solid var(--line);border-radius:13px;padding:13px 15px;cursor:pointer;transition:all .14s;display:flex;gap:11px;align-items:flex-start;text-decoration:none}
.item:hover{background:rgba(248,222,205,.1);transform:translateY(-1px)}
.item .bar{width:4px;align-self:stretch;border-radius:3px;flex:none}
.item.yes .bar{background:var(--yes)}
.item.no .bar{background:var(--no)}
.item.maybe .bar{background:var(--maybe)}
.item .en{font-family:'Gabarito';font-weight:800;font-size:15px;color:var(--peach)}
.item .nm{font-size:13px;opacity:.72;margin-top:1px}
.item.hidden{display:none}
.empty{grid-column:1/-1;text-align:center;opacity:.6;padding:30px;font-size:15px;display:none}
.section{margin-top:54px}
.section h2{margin-bottom:14px}
.section p.lead{font-size:16px;opacity:.85;max-width:640px}
.prose{margin-top:16px;font-size:16px;opacity:.9;max-width:640px}
.prose+.prose{margin-top:12px}
.toolcards{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px;margin-top:26px}
.toolcard{background:var(--peach);color:var(--ink);border-radius:20px;padding:26px;box-shadow:0 22px 60px -28px rgba(0,0,0,.55);display:flex;flex-direction:column;gap:10px;text-decoration:none;transition:transform .14s}
a.toolcard:hover{transform:translateY(-3px)}
.toolcard.soon{background:rgba(248,222,205,.06);color:var(--peach);border:1px dashed var(--line);box-shadow:none}
.toolcard .badge{align-self:flex-start;font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;padding:5px 10px;border-radius:999px;background:var(--green);color:#fff}
.toolcard.soon .badge{background:rgba(248,222,205,.12);color:var(--peach)}
.toolcard h3{font-family:'Gabarito';font-weight:800;font-size:22px;letter-spacing:-.02em}
.toolcard p{font-size:15px;opacity:.85}
.toolcard .meta{margin-top:auto;padding-top:10px;font-size:13px;font-weight:600;color:var(--green-deep)}
.toolcard.soon .meta{color:var(--terra)}
.linklist{margin-top:18px;display:grid;gap:10px;max-width:640px}
.linklist a{display:flex;align-items:center;justify-content:space-between;gap:14px;background:rgba(248,222,205,.05);border:1px solid var(--line);border-radius:13px;padding:14px 18px;text-decoration:none;font-weight:600;font-size:15px;transition:all .14s}
.linklist a:hover{background:rgba(248,222,205,.1)}
.linklist .arrow{color:var(--green);font-family:'Gabarito';font-weight:800}
.related{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:10px;margin-top:18px}
.cta{margin-top:44px;background:var(--teal-card);border-radius:20px;padding:28px;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:18px}
.cta h2{font-size:22px}
.cta p{font-size:14px;opacity:.8;margin-top:4px}
.btn{display:inline-block;background:var(--peach);color:var(--ink);font-family:'Gabarito';font-weight:700;font-size:15px;padding:13px 22px;border-radius:13px;text-decoration:none;transition:transform .1s}
.btn:hover{transform:translateY(-1px)}
footer.site{border-top:1px solid var(--line);padding:30px 0 50px;margin-top:60px}
.disc{font-size:13px;opacity:.62;max-width:640px;line-height:1.6}
.disc b{opacity:.9}
.sources{margin-top:14px;font-size:12px;opacity:.5;max-width:640px}
.fbrand{margin-top:18px;font-family:'Gabarito';font-weight:800;font-size:15px;display:flex;align-items:center;gap:8px}
.fbrand .dot{width:9px;height:9px;border-radius:50%;background:var(--green)}
.flinks{margin-top:10px;font-size:13px;opacity:.7;display:flex;gap:16px;flex-wrap:wrap}
.flinks a{text-decoration:none}
.flinks a:hover{text-decoration:underline}
@media(max-width:560px){.go{padding:14px 16px}#q{font-size:18px}.listhead{align-items:flex-start}}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
""".strip()

# Zusatz-Styles für den Vegan-Ersatz-Finder (Substitut-Listen)
CSS += """
.subs{margin-top:18px;display:flex;flex-direction:column;gap:12px}
.colstack{display:flex;flex-direction:column;gap:12px}
.optcard{background:rgba(255,255,255,.5);border-radius:13px;padding:14px 16px;border:1px solid rgba(10,48,48,.08)}
.optcard .sname{font-family:'Gabarito';font-weight:800;font-size:17px;color:var(--ink);display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}
.optcard .bf{font-family:'Figtree';font-weight:600;font-size:11px;letter-spacing:.04em;text-transform:uppercase;color:var(--green-deep);background:rgba(41,165,121,.14);padding:3px 9px;border-radius:999px}
.optcard .ratio{margin-top:5px;font-size:14px;color:var(--teal);font-weight:600}
.optcard .nt{margin-top:5px;font-size:14px;color:#3a5856}
.usecards{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-top:18px}
.usecard{background:rgba(248,222,205,.05);border:1px solid var(--line);border-radius:13px;padding:14px 16px}
.usecard b{font-family:'Gabarito';font-weight:800;color:var(--peach);font-size:15px}
.usecard span{display:block;margin-top:3px;font-size:13px;opacity:.75}
"""

# Zusatz-Styles für den Nährstoff-Rechner
CSS += """
.calc{background:var(--peach);color:var(--ink);border-radius:20px;padding:24px;box-shadow:0 22px 60px -28px rgba(0,0,0,.55);max-width:640px;margin:30px auto 0}
.calc-grid{display:grid;grid-template-columns:1fr;gap:18px}
@media(min-width:620px){.calc-grid{grid-template-columns:1fr 1fr}}
.field{display:grid;gap:8px}
.field label{font-family:'Gabarito';font-weight:700;font-size:14px;color:var(--ink)}
.field input[type=number]{font-family:'Gabarito';font-weight:700;font-size:20px;border:2px solid rgba(10,48,48,.15);border-radius:12px;padding:12px 14px;background:#fff;color:var(--ink);width:100%}
.field input[type=number]:focus{outline:none;border-color:var(--green)}
.seg{display:flex;gap:8px;flex-wrap:wrap}
.seg button{cursor:pointer;border:2px solid rgba(10,48,48,.15);background:#fff;color:var(--ink);font-family:'Figtree';font-weight:600;font-size:14px;padding:10px 15px;border-radius:999px;transition:all .14s}
.seg button.on{background:var(--green-deep);border-color:var(--green-deep);color:#fff}
.nresults{display:grid;grid-template-columns:repeat(auto-fit,minmax(225px,1fr));gap:12px;margin:24px auto 0;max-width:920px}
.ncard{background:var(--peach);color:var(--ink);border-radius:16px;padding:18px 20px;text-align:left;display:flex;flex-direction:column}
.ncard .nlabel{font-family:'Figtree';font-weight:600;font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--teal)}
.ncard .nval{font-family:'Gabarito';font-weight:900;font-size:28px;letter-spacing:-.02em;color:var(--ink);line-height:1.05;margin-top:2px}
.ncard .nunit{font-size:13px;color:#3a5856;font-weight:600;margin-top:1px}
.ncard .nsrc{margin-top:11px;font-size:13px;color:#3a5856;flex:1}
.ncard .b2{align-self:flex-start;margin-top:11px;font-size:11px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;padding:3px 9px;border-radius:999px}
.b-ess{background:rgba(192,57,43,.14);color:#a02d20}
.b-opt{background:rgba(41,165,121,.14);color:var(--green-deep)}
.ncard .more{margin-top:11px;font-family:'Gabarito';font-weight:700;font-size:13px;color:var(--green-deep);text-decoration:none}
.infobox{margin-top:24px;background:rgba(248,222,205,.06);border:1px solid var(--line);border-left:3px solid var(--terra);border-radius:12px;padding:16px 18px;font-size:14px;opacity:.9;max-width:920px}
.infobox b{opacity:1}
"""

# Zusatz-Styles für den Impact-Rechner
CSS += """
.iunit{display:flex;gap:10px;align-items:center;justify-content:center;flex-wrap:wrap;margin:24px auto 0;max-width:560px}
.iunit input{font-family:'Gabarito';font-weight:800;font-size:24px;width:120px;text-align:center;border:2px solid rgba(248,222,205,.22);border-radius:13px;padding:12px;background:rgba(248,222,205,.07);color:var(--peach)}
.iunit input:focus{outline:none;border-color:var(--green)}
.stats{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin:30px auto 0;max-width:760px}
@media(min-width:760px){.stats{grid-template-columns:repeat(4,1fr)}}
.stat{background:var(--peach);color:var(--ink);border-radius:18px;padding:22px 16px;text-align:center;box-shadow:0 18px 50px -28px rgba(0,0,0,.5)}
.stat .snum{font-family:'Gabarito';font-weight:900;font-size:clamp(26px,5vw,40px);letter-spacing:-.03em;line-height:1;color:var(--green-deep)}
.stat .slabel{font-family:'Gabarito';font-weight:700;font-size:14px;margin-top:9px;color:var(--ink)}
.stat .seq{font-size:12px;color:#3a5856;margin-top:6px;line-height:1.4}
"""

# Zusatz-Styles für den Saisonkalender
CSS += """
.months{display:flex;gap:6px;flex-wrap:wrap;justify-content:center;margin:24px auto 0;max-width:640px}
.months button{cursor:pointer;border:1px solid var(--line);background:rgba(248,222,205,.05);color:var(--peach);font-family:'Figtree';font-weight:600;font-size:13px;padding:8px 13px;border-radius:999px;transition:all .14s}
.months button:hover{background:rgba(248,222,205,.12)}
.months button.on{background:var(--peach);color:var(--ink);border-color:var(--peach)}
.subhead{font-family:'Gabarito';font-weight:800;font-size:18px;margin:30px 0 12px;color:var(--peach);display:flex;align-items:center;gap:9px}
.subhead .swatch{width:10px;height:10px;border-radius:50%;background:var(--yes)}
.subhead.lager .swatch{background:var(--maybe)}
"""

# Zusatz-Styles für die Protein-Tabelle
CSS += """
.psort{display:flex;gap:8px;flex-wrap:wrap;justify-content:center;margin:16px auto 0}
.ptable{margin-top:10px;display:flex;flex-direction:column;max-width:720px;margin-left:auto;margin-right:auto}
.prow{display:flex;align-items:center;justify-content:space-between;gap:14px;padding:13px 4px;border-bottom:1px solid var(--line)}
.prow .pname{font-family:'Gabarito';font-weight:700;font-size:16px;color:var(--peach)}
.prow .pcat{font-size:12px;opacity:.6;margin-top:1px}
.prow .pval{font-family:'Gabarito';font-weight:900;font-size:22px;letter-spacing:-.02em;color:var(--green);white-space:nowrap}
.prow .pval small{font-size:11px;font-weight:600;opacity:.6;color:var(--peach)}
.prow.top .pval{color:var(--terra-light)}
.prow.tier .pval{color:#e8845f}
.prow.pflanz .pval{color:var(--green)}
.field select{font-family:'Gabarito';font-weight:700;font-size:17px;border:2px solid rgba(10,48,48,.15);border-radius:12px;padding:12px 14px;background:#fff;color:var(--ink);width:100%}
.field select:focus{outline:none;border-color:var(--green)}
.addbtn{margin-top:4px;border:0;cursor:pointer;background:var(--green-deep);color:var(--peach);font-family:'Gabarito';font-weight:700;font-size:15px;padding:13px 22px;border-radius:13px;width:100%;transition:transform .1s}
.addbtn:active{transform:scale(.98)}
.rm{flex:none;width:30px;height:30px;border-radius:50%;border:0;background:rgba(192,57,43,.12);color:#a02d20;font-size:18px;cursor:pointer;line-height:1}
.mealsum{background:var(--peach);color:var(--ink);border-radius:16px;padding:22px;text-align:center;margin:16px auto 0;max-width:720px}
.mealsum .big{font-family:'Gabarito';font-weight:900;font-size:38px;color:var(--green-deep);letter-spacing:-.02em;line-height:1}
.mealsum .pct{font-size:14px;color:#3a5856;margin-top:5px}
"""

# Zusatz-Styles für den Schriftarten-Generator (Creator)
CSS += """
.fontinput{width:100%;max-width:640px;margin:30px auto 0;display:block;font-family:'Figtree';font-size:18px;border:2px solid rgba(248,222,205,.22);border-radius:16px;padding:16px;background:rgba(248,222,205,.07);color:var(--peach);resize:vertical;min-height:84px}
.fontinput:focus{outline:none;border-color:var(--green)}
.fontlist{margin:20px auto 0;display:flex;flex-direction:column;gap:10px;max-width:720px}
.fontrow{display:flex;align-items:center;justify-content:space-between;gap:14px;background:var(--peach);color:var(--ink);border-radius:14px;padding:12px 16px}
.fontrow .flabel{display:block;font-size:11px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--teal);margin-bottom:3px}
.fontrow .fout{font-size:18px;word-break:break-word;line-height:1.45;color:var(--ink)}
.copybtn{flex:none;border:0;cursor:pointer;background:var(--ink);color:var(--peach);font-family:'Gabarito';font-weight:700;font-size:13px;padding:9px 14px;border-radius:10px;transition:background .15s}
.copybtn:hover{background:var(--green-deep)}
.copybtn.done{background:var(--green)}
.decogrid{display:flex;flex-wrap:wrap;gap:8px;max-width:720px;margin:14px auto 0;justify-content:center}
.decobtn{cursor:pointer;border:1px solid var(--line);background:rgba(248,222,205,.05);color:var(--peach);font-size:18px;padding:8px 13px;border-radius:11px;transition:all .14s}
.decobtn:hover{background:var(--peach);color:var(--ink);border-color:var(--peach)}
"""

# ---------------------------------------------------------------- JS (Checker)

CHECKER_JS = r"""
const DATA = __DATA__;
const LABEL = {
  yes:{t:"Vegan", s:"Pflanzlich, mineralisch oder synthetisch", icon:"✓"},
  no:{t:"Nicht vegan", s:"Tierischen Ursprungs", icon:"✕"},
  maybe:{t:"Kommt drauf an", s:"Kann tierisch oder pflanzlich sein", icon:"?"}
};
const norm = str => str.toLowerCase().replace(/\s+/g,"").replace(/[^a-z0-9äöüß]/g,"");
const normNum = str => str.toLowerCase().replace(/\s+/g,"").replace(/^e/,"");
function find(query){
  const q = norm(query);
  if(!q) return null;
  const qn = normNum(query);
  let hit = DATA.find(d => normNum(d.n) === qn && /^[e]?\d/.test(norm(query)));
  if(hit) return hit;
  // exakter Name vor Teilstring, sonst gewinnt "Milchsäureester" gegen "Milchsäure"
  hit = DATA.find(d => norm(d.name) === q)
     || DATA.find(d => norm(d.name).split("(")[0] === q)
     || DATA.find(d => norm(d.name).startsWith(q))
     || DATA.find(d => norm(d.name).includes(q) || norm(d.n).includes(q));
  return hit || null;
}
function render(item){
  const r = document.getElementById("result");
  if(!item){
    r.innerHTML = '<div class="miss"><h3>Dazu habe ich keinen Eintrag</h3>'+
      '<p>Tippfehler? Versuch die reine Nummer (z. B. 471) oder den Namen. Diese Liste deckt die gängigsten Zusatzstoffe ab, nicht jeden seltenen Stoff.</p></div>';
    return;
  }
  const L = LABEL[item.s];
  r.innerHTML =
    '<div class="card">'+
      '<div class="verdict '+item.s+'"><div class="mark">'+L.icon+'</div>'+
      '<div class="vtext">'+L.t+'<small>'+L.s+'</small></div></div>'+
      '<div class="card-body">'+
        '<div class="enum">'+item.n+'</div>'+
        '<div class="ename">'+item.name+'</div>'+
        '<span class="klasse">'+item.k+'</span>'+
        '<p class="info">'+item.info+'</p>'+
        (item.note ? '<div class="note"><span>!</span><span><b>Gut zu wissen:</b> '+item.note+'</span></div>' : '')+
        '<a class="detail-link" href="'+item.u+'">Alle Details zu '+item.n+' →</a>'+
      '</div></div>';
}
function search(){
  const v = document.getElementById("q").value;
  if(!v.trim()){ document.getElementById("result").innerHTML=""; return; }
  render(find(v));
}
document.getElementById("go").addEventListener("click", search);
document.getElementById("q").addEventListener("keydown", e => { if(e.key==="Enter") search(); });
document.getElementById("q").addEventListener("input", e => {
  if(e.target.value.trim().length >= 2) search();
  else document.getElementById("result").innerHTML="";
});
document.querySelectorAll(".chip").forEach(c => c.addEventListener("click", () => {
  document.getElementById("q").value = c.dataset.c;
  search();
  document.getElementById("result").scrollIntoView({behavior:"smooth", block:"center"});
}));
document.querySelectorAll(".filt").forEach(f => f.addEventListener("click", () => {
  document.querySelectorAll(".filt").forEach(x=>x.classList.remove("active"));
  f.classList.add("active");
  const flt = f.dataset.f;
  let shown = 0;
  document.querySelectorAll("#grid .item").forEach(el => {
    const show = flt==="all" || el.classList.contains(flt);
    el.classList.toggle("hidden", !show);
    if(show) shown++;
  });
  document.querySelector("#grid .empty").style.display = shown ? "none" : "block";
}));
""".strip()

# ---------------------------------------------------------------- JS (Ersatz-Finder)

ERSATZ_JS = r"""
const DATA = __DATA__;
const norm = s => s.toLowerCase().replace(/\s+/g,"").replace(/[^a-z0-9äöüß]/g,"");
function find(query){
  const q = norm(query);
  if(!q) return null;
  let hit = DATA.find(d => norm(d.name) === q);
  if(hit) return hit;
  hit = DATA.find(d => d.aka.some(a => norm(a) === q));
  if(hit) return hit;
  hit = DATA.find(d => norm(d.name).startsWith(q));
  if(hit) return hit;
  return DATA.find(d => norm(d.name).includes(q) || d.aka.some(a => norm(a).includes(q))) || null;
}
function render(item){
  const r = document.getElementById("result");
  if(!item){
    r.innerHTML = '<div class="miss"><h3>Dazu habe ich noch keinen Eintrag</h3>'+
      '<p>Versuch die Grundzutat (z. B. Ei, Butter, Milch, Käse). Wir bauen die Liste laufend aus.</p></div>';
    return;
  }
  const subs = item.subs.map(s =>
    '<div class="optcard"><div class="sname">'+s.name+(s.bf?'<span class="bf">'+s.bf+'</span>':'')+'</div>'+
    '<div class="ratio">'+s.ratio+'</div>'+(s.nt?'<div class="nt">'+s.nt+'</div>':'')+'</div>').join("");
  r.innerHTML =
    '<div class="card"><div class="card-body">'+
      '<div class="enum">'+item.name+' vegan ersetzen</div>'+
      (item.intro?'<p class="info">'+item.intro+'</p>':'')+
      '<div class="subs">'+subs+'</div>'+
      '<a class="detail-link" href="'+item.u+'">Alle Details und Tipps zu '+item.name+' →</a>'+
    '</div></div>';
}
function search(){
  const v = document.getElementById("q").value;
  if(!v.trim()){ document.getElementById("result").innerHTML=""; return; }
  render(find(v));
}
document.getElementById("go").addEventListener("click", search);
document.getElementById("q").addEventListener("keydown", e => { if(e.key==="Enter") search(); });
document.getElementById("q").addEventListener("input", e => {
  if(e.target.value.trim().length >= 2) search();
  else document.getElementById("result").innerHTML="";
});
document.querySelectorAll(".chip").forEach(c => c.addEventListener("click", () => {
  document.getElementById("q").value = c.dataset.c;
  search();
  document.getElementById("result").scrollIntoView({behavior:"smooth", block:"center"});
}));
""".strip()

# ---------------------------------------------------------------- JS (Nährstoff-Rechner)

NAEHR_JS = r"""
const N = __DATA__;
let weight = 70, sex = 'f', act = 'active';
function proteinRange(){
  const f = {low:[0.8,1.0], active:[1.2,1.4], sport:[1.4,1.6]}[act];
  return Math.round(weight*f[0]) + ' bis ' + Math.round(weight*f[1]);
}
function targetFor(n){
  if(n.type==='protein') return proteinRange();
  if(n.type==='sex') return String(sex==='f' ? n.tf : n.tm);
  return String(n.target);
}
function badge(n){
  if(n.sup==='essenziell') return '<span class="b2 b-ess">Supplement Pflicht</span>';
  if(n.sup==='sinnvoll') return '<span class="b2 b-opt">Supplement sinnvoll</span>';
  return '';
}
function render(){
  document.getElementById('nresults').innerHTML = N.map(n =>
    '<div class="ncard"><div class="nlabel">'+n.name+'</div>'+
    '<div class="nval">'+targetFor(n)+'</div><div class="nunit">'+n.unit+'</div>'+
    '<div class="nsrc">'+n.cover+'</div>'+badge(n)+
    '<a class="more" href="'+n.u+'">So deckst du es →</a></div>').join('');
}
const w = document.getElementById('w');
if(w){ w.addEventListener('input', () => { const v = parseFloat(w.value); if(v>0 && v<400){ weight = v; render(); } }); }
document.querySelectorAll('[data-sex]').forEach(b => b.addEventListener('click', () => {
  sex = b.dataset.sex; document.querySelectorAll('[data-sex]').forEach(x=>x.classList.toggle('on', x===b)); render();
}));
document.querySelectorAll('[data-act]').forEach(b => b.addEventListener('click', () => {
  act = b.dataset.act; document.querySelectorAll('[data-act]').forEach(x=>x.classList.toggle('on', x===b)); render();
}));
render();
""".strip()

# ---------------------------------------------------------------- JS (Impact-Rechner)

IMPACT_JS = r"""
const P = __DATA__;
let amount = 1, unit = 'year';
function days(){ return amount * (unit==='day'?1:(unit==='month'?30.44:365)); }
function fmt(x){ return Math.round(x).toLocaleString('de-DE'); }
function card(n,l,e){ return '<div class="stat"><div class="snum">'+n+'</div><div class="slabel">'+l+'</div><div class="seq">'+e+'</div></div>'; }
function render(){
  const d = days();
  const animals = P.animals*d, co2 = P.co2_kg*d, water = P.water_l*d, land = P.land_m2*d;
  const co2str = co2>=1000 ? fmt(co2/1000)+' t' : fmt(co2)+' kg';
  document.getElementById('stats').innerHTML =
    card(fmt(animals), 'Tiere gerettet', 'die meisten davon Fische') +
    card(co2str, 'CO2 gespart', 'wie rund '+fmt(co2/0.12)+' km im Auto') +
    card(fmt(water)+' L', 'Wasser gespart', 'rund '+fmt(water/150)+' volle Badewannen') +
    card(fmt(land)+' m²', 'Ackerland gespart', 'das sonst für Tierfutter draufginge');
}
const inp = document.getElementById('amt');
if(inp){ inp.addEventListener('input', ()=>{ const v=parseFloat(inp.value); if(v>0 && v<100000){ amount=v; render(); } }); }
document.querySelectorAll('[data-unit]').forEach(b=>b.addEventListener('click',()=>{
  unit=b.dataset.unit; document.querySelectorAll('[data-unit]').forEach(x=>x.classList.toggle('on',x===b)); render();
}));
render();
""".strip()

# ---------------------------------------------------------------- JS (Lebensmittel-Checker)

FOOD_JS = r"""
const DATA = __DATA__;
const L = {
  yes:{t:"In der Regel vegan", s:"meist ohne Tierisches", i:"✓"},
  maybe:{t:"Kommt drauf an", s:"oft versteckt tierisch", i:"?"},
  no:{t:"Meist nicht vegan", s:"enthält in der Regel Tierisches", i:"✕"}
};
const norm = s => s.toLowerCase().replace(/\s+/g,"").replace(/[^a-z0-9äöüß]/g,"");
function find(query){
  const q = norm(query);
  if(!q) return null;
  return DATA.find(d => norm(d.name) === q)
    || DATA.find(d => d.aka.some(a => norm(a) === q))
    || DATA.find(d => norm(d.name).startsWith(q))
    || DATA.find(d => norm(d.name).includes(q) || d.aka.some(a => norm(a).includes(q)))
    || null;
}
function render(item){
  const r = document.getElementById("result");
  if(!item){
    r.innerHTML = '<div class="miss"><h3>Dazu habe ich noch keinen Eintrag</h3>'+
      '<p>Versuch ein anderes Lebensmittel oder die Grundzutat. Die Liste wächst laufend.</p></div>';
    return;
  }
  const x = L[item.s];
  r.innerHTML =
    '<div class="card"><div class="verdict '+item.s+'"><div class="mark">'+x.i+'</div>'+
    '<div class="vtext">'+x.t+'<small>'+x.s+'</small></div></div>'+
    '<div class="card-body"><div class="enum">'+item.name+'</div>'+
    '<span class="klasse">'+item.cat+'</span><p class="info">'+item.info+'</p>'+
    (item.note ? '<div class="note"><span>!</span><span><b>Achte drauf:</b> '+item.note+'</span></div>' : '')+
    '<a class="detail-link" href="'+item.u+'">Ist '+item.name+' vegan? Alle Details →</a></div></div>';
}
function search(){
  const v = document.getElementById("q").value;
  if(!v.trim()){ document.getElementById("result").innerHTML=""; return; }
  render(find(v));
}
document.getElementById("go").addEventListener("click", search);
document.getElementById("q").addEventListener("keydown", e => { if(e.key==="Enter") search(); });
document.getElementById("q").addEventListener("input", e => {
  if(e.target.value.trim().length >= 2) search();
  else document.getElementById("result").innerHTML="";
});
document.querySelectorAll(".chip").forEach(c => c.addEventListener("click", () => {
  document.getElementById("q").value = c.dataset.c;
  search();
  document.getElementById("result").scrollIntoView({behavior:"smooth", block:"center"});
}));
document.querySelectorAll(".filt").forEach(f => f.addEventListener("click", () => {
  document.querySelectorAll(".filt").forEach(x=>x.classList.remove("active"));
  f.classList.add("active");
  const flt = f.dataset.f;
  let shown = 0;
  document.querySelectorAll("#grid .item").forEach(el => {
    const show = flt==="all" || el.classList.contains(flt);
    el.classList.toggle("hidden", !show);
    if(show) shown++;
  });
  document.querySelector("#grid .empty").style.display = shown ? "none" : "block";
}));
""".strip()

# ---------------------------------------------------------------- JS (Saisonkalender)

SAISON_JS = r"""
const D = __DATA__;
const MO = ["Januar","Februar","März","April","Mai","Juni","Juli","August","September","Oktober","November","Dezember"];
let m = (new Date()).getMonth() + 1;
function cards(arr){
  if(!arr.length) return '<div class="empty" style="display:block">In diesem Monat ist regional nichts dabei.</div>';
  return arr.map(d => {
    const lager = !d.f.includes(m) && d.l.includes(m);
    return '<div class="item '+(lager?'maybe':'yes')+'"><span class="bar"></span><div>'+
      '<div class="en">'+d.name+'</div><div class="nm">'+(lager?'aus dem Lager':'Freiland')+'</div></div></div>';
  }).join('');
}
function render(){
  document.querySelectorAll('[data-m]').forEach(b => b.classList.toggle('on', (+b.dataset.m)===m));
  document.getElementById('motitle').textContent = 'Saison im ' + MO[m-1];
  const inS = D.filter(d => d.f.includes(m) || d.l.includes(m));
  document.getElementById('gem').innerHTML = cards(inS.filter(d => d.type==='gemuese'));
  document.getElementById('obs').innerHTML = cards(inS.filter(d => d.type==='obst'));
}
document.querySelectorAll('[data-m]').forEach(b => b.addEventListener('click', () => { m = +b.dataset.m; render(); }));
render();
""".strip()

# ---------------------------------------------------------------- JS (Pflanzendrink-Vergleich)

PFLANZ_JS = r"""
const D = __DATA__, U = __UC__;
let uc = "kaffee";
function statline(d){ return d.protein+' g Protein · '+d.kcal+' kcal pro 100 ml'+(d.barista?' · Barista-tauglich':''); }
function render(){
  document.querySelectorAll('[data-uc]').forEach(b => b.classList.toggle('on', b.dataset.uc===uc));
  const u = U.find(x => x.key===uc);
  document.getElementById('uchint').textContent = u.hint;
  const sorted = [...D].sort((a,b) => b.r[uc]-a.r[uc] || a.name.localeCompare(b.name,'de'));
  const max = sorted[0].r[uc];
  document.getElementById('drinkout').innerHTML = sorted.map(d => {
    const top = d.r[uc]===max;
    const lvl = d.r[uc]===3?'top geeignet':(d.r[uc]===2?'gut geeignet':'weniger geeignet');
    const badge = top ? '<span class="bf">Top-Wahl</span>'
      : '<span class="bf" style="background:rgba(20,125,119,.12);color:var(--teal)">'+lvl+'</span>';
    return '<div class="optcard"><div class="sname">'+d.name+badge+'</div>'+
      '<div class="ratio">'+statline(d)+'</div><div class="nt">'+d.reason+'</div>'+
      '<a class="more" href="'+d.u+'" style="display:inline-block;margin-top:9px;font-family:Gabarito;font-weight:700;font-size:13px;color:var(--green-deep);text-decoration:none">Mehr zu '+d.name+' →</a></div>';
  }).join('');
}
document.querySelectorAll('[data-uc]').forEach(b => b.addEventListener('click', () => { uc = b.dataset.uc; render(); }));
render();
""".strip()

# ---------------------------------------------------------------- JS (Protein-Tabelle)

PROT_JS = r"""
const F = __DATA__;
let q = "", cat = "all", sort = "protein";
function rowsHtml(){
  let list = F.filter(f => (cat==="all" || f.c===cat) && (!q || f.n.toLowerCase().includes(q)));
  list.sort((a,b) => sort==="protein" ? b.p-a.p : a.n.localeCompare(b.n,'de'));
  if(!list.length) return '<div class="empty" style="display:block">Dazu finde ich nichts.</div>';
  const top = new Set(list.slice(0,3).map(f => f.n));
  return list.map(f => '<div class="prow'+(sort==="protein" && top.has(f.n)?' top':'')+'">'+
    '<div><div class="pname">'+f.n+'</div><div class="pcat">'+f.c+'</div></div>'+
    '<div class="pval">'+f.p+'<small> g/100g</small></div></div>').join('');
}
function render(){ document.getElementById('ptable').innerHTML = rowsHtml(); }
const qi = document.getElementById('pq');
qi.addEventListener('input', () => { q = qi.value.trim().toLowerCase(); render(); });
document.querySelectorAll('[data-cat]').forEach(b => b.addEventListener('click', () => {
  cat = b.dataset.cat; document.querySelectorAll('[data-cat]').forEach(x => x.classList.toggle('active', x===b)); render();
}));
document.querySelectorAll('[data-sort]').forEach(b => b.addEventListener('click', () => {
  sort = b.dataset.sort; document.querySelectorAll('[data-sort]').forEach(x => x.classList.toggle('on', x===b)); render();
}));
render();
""".strip()

# ---------------------------------------------------------------- JS (CO2-Vergleich)

CO2_JS = r"""
const F = __DATA__;
let q = "", cat = "all", sort = "desc";
function rowsHtml(){
  let list = F.filter(f => (cat==="all" || f.t===cat) && (!q || f.n.toLowerCase().includes(q)));
  list.sort((a,b) => sort==="desc" ? b.co2-a.co2 : a.co2-b.co2);
  if(!list.length) return '<div class="empty" style="display:block">Dazu finde ich nichts.</div>';
  return list.map(f => '<div class="prow '+(f.t==="Tierisch"?"tier":"pflanz")+'">'+
    '<div><div class="pname">'+f.n+'</div><div class="pcat">'+f.t+'</div></div>'+
    '<div class="pval">'+f.co2+'<small> kg CO2</small></div></div>').join('');
}
function render(){ document.getElementById('ptable').innerHTML = rowsHtml(); }
const qi = document.getElementById('pq');
qi.addEventListener('input', () => { q = qi.value.trim().toLowerCase(); render(); });
document.querySelectorAll('[data-cat]').forEach(b => b.addEventListener('click', () => {
  cat = b.dataset.cat; document.querySelectorAll('[data-cat]').forEach(x => x.classList.toggle('active', x===b)); render();
}));
document.querySelectorAll('[data-sort]').forEach(b => b.addEventListener('click', () => {
  sort = b.dataset.sort; document.querySelectorAll('[data-sort]').forEach(x => x.classList.toggle('on', x===b)); render();
}));
render();
""".strip()

# ---------------------------------------------------------------- JS (Protein-pro-Mahlzeit)

MEAL_JS = r"""
const FOODS = __DATA__;
let items = [], target = 60;
function round1(x){ return Math.round(x*10)/10; }
function render(){
  const list = document.getElementById('mealitems');
  if(!items.length){
    list.innerHTML = '<div class="empty" style="display:block">Noch nichts drin. Wähl oben ein Lebensmittel und gib die Menge an.</div>';
  } else {
    list.innerHTML = items.map((it,i) =>
      '<div class="prow"><div><div class="pname">'+it.n+'</div><div class="pcat">'+it.g+' g</div></div>'+
      '<div style="display:flex;align-items:center;gap:14px"><div class="pval">'+round1(it.p*it.g/100)+'<small> g</small></div>'+
      '<button class="rm" data-i="'+i+'" aria-label="Entfernen">×</button></div></div>').join('');
  }
  const tot = items.reduce((s,it) => s + it.p*it.g/100, 0);
  document.getElementById('mealbig').textContent = round1(tot) + ' g Protein';
  document.getElementById('mealpct').textContent = items.length ? ('deckt rund '+Math.round(tot/target*100)+' % von '+target+' g Tagesziel') : 'Tagesziel '+target+' g';
  document.querySelectorAll('.rm').forEach(b => b.addEventListener('click', () => { items.splice(+b.dataset.i,1); render(); }));
}
document.getElementById('addbtn').addEventListener('click', () => {
  const sel = document.getElementById('foodsel');
  const g = parseFloat(document.getElementById('grams').value);
  if(!g || g <= 0) return;
  const f = FOODS.find(x => x.n === sel.value);
  if(f){ items.push({n: f.n, p: f.p, g: g}); render(); }
});
const ti = document.getElementById('target');
ti.addEventListener('input', () => { const v = parseFloat(ti.value); if(v > 0){ target = v; render(); } });
render();
""".strip()

# ---------------------------------------------------------------- JS (Schriftarten-Generator)

FONT_JS = r"""
const SCRIPT_EX={B:'ℬ',E:'ℰ',F:'ℱ',H:'ℋ',I:'ℐ',L:'ℒ',M:'ℳ',R:'ℛ',e:'ℯ',g:'ℊ',o:'ℴ'};
const FRAK_EX={C:'ℭ',H:'ℌ',I:'ℑ',R:'ℜ',Z:'ℨ'};
const DS_EX={C:'ℂ',H:'ℍ',N:'ℕ',P:'ℙ',Q:'ℚ',R:'ℝ',Z:'ℤ'};
const SMALLCAPS={a:'ᴀ',b:'ʙ',c:'ᴄ',d:'ᴅ',e:'ᴇ',f:'ꜰ',g:'ɢ',h:'ʜ',i:'ɪ',j:'ᴊ',k:'ᴋ',l:'ʟ',m:'ᴍ',n:'ɴ',o:'ᴏ',p:'ᴘ',q:'ǫ',r:'ʀ',s:'s',t:'ᴛ',u:'ᴜ',v:'ᴠ',w:'ᴡ',x:'x',y:'ʏ',z:'ᴢ'};
const FLIP={a:'ɐ',b:'q',c:'ɔ',d:'p',e:'ǝ',f:'ɟ',g:'ƃ',h:'ɥ',i:'ᴉ',j:'ɾ',k:'ʞ',l:'l',m:'ɯ',n:'u',o:'o',p:'d',q:'b',r:'ɹ',s:'s',t:'ʇ',u:'n',v:'ʌ',w:'ʍ',x:'x',y:'ʎ',z:'z',A:'∀',B:'B',C:'Ɔ',D:'D',E:'Ǝ',F:'Ⅎ',G:'פ',H:'H',I:'I',J:'ſ',K:'K',L:'˥',M:'W',N:'N',O:'O',P:'Ԁ',Q:'Q',R:'R',S:'S',T:'⊥',U:'∩',V:'Λ',W:'M',X:'X',Y:'⅄',Z:'Z','1':'Ɩ','2':'ᄅ','3':'Ɛ','4':'ㄣ','5':'ϛ','6':'9','7':'ㄥ','8':'8','9':'6','0':'0','.':'˙','?':'¿','!':'¡'};
function mapc(str,up,low,dig,ex){
  ex=ex||{}; let o='';
  for(const ch of str){
    if(ex[ch]){o+=ex[ch];continue;}
    const c=ch.codePointAt(0);
    if(c>=65&&c<=90)o+=String.fromCodePoint(up+(c-65));
    else if(c>=97&&c<=122)o+=String.fromCodePoint(low+(c-97));
    else if(dig&&c>=48&&c<=57)o+=String.fromCodePoint(dig+(c-48));
    else o+=ch;
  }
  return o;
}
function circled(str){let o='';for(const ch of str){const c=ch.codePointAt(0);
  if(c>=65&&c<=90)o+=String.fromCodePoint(0x24B6+(c-65));
  else if(c>=97&&c<=122)o+=String.fromCodePoint(0x24D0+(c-97));
  else if(c===48)o+='⓪';
  else if(c>=49&&c<=57)o+=String.fromCodePoint(0x2460+(c-49));
  else o+=ch;}return o;}
function fullwidth(str){let o='';for(const ch of str){const c=ch.codePointAt(0);
  if(c>=33&&c<=126)o+=String.fromCodePoint(0xFF01+(c-33));
  else if(c===32)o+='　';else o+=ch;}return o;}
function combine(str,mark){return [...str].map(c=>c+mark).join('');}
function smallcaps(str){return [...str].map(c=>SMALLCAPS[c.toLowerCase()]||c).join('');}
function flip(str){return [...str].map(c=>FLIP[c]||FLIP[c.toLowerCase()]||c).reverse().join('');}
const STYLES=[
  ['Fett', s=>mapc(s,0x1D5D4,0x1D5EE,0x1D7EC)],
  ['Kursiv', s=>mapc(s,0x1D608,0x1D622,null)],
  ['Fett kursiv', s=>mapc(s,0x1D63C,0x1D656,null)],
  ['Schreibschrift', s=>mapc(s,0x1D49C,0x1D4B6,null,SCRIPT_EX)],
  ['Schreibschrift fett', s=>mapc(s,0x1D4D0,0x1D4EA,null)],
  ['Serif fett', s=>mapc(s,0x1D400,0x1D41A,0x1D7CE)],
  ['Gotisch', s=>mapc(s,0x1D504,0x1D51E,null,FRAK_EX)],
  ['Gotisch fett', s=>mapc(s,0x1D56C,0x1D586,null)],
  ['Outline', s=>mapc(s,0x1D538,0x1D552,0x1D7D8,DS_EX)],
  ['Monospace', s=>mapc(s,0x1D670,0x1D68A,0x1D7F6)],
  ['Eingekreist', circled],
  ['Fullwidth', fullwidth],
  ['Kapitälchen', smallcaps],
  ['Durchgestrichen', s=>combine(s,'̶')],
  ['Unterstrichen', s=>combine(s,'̲')],
  ['Kopfüber', flip],
  ['Rückwärts', s=>[...s].reverse().join('')],
  ['Gesperrt', s=>[...s].join(' ')]
];
const DECO=['🌱','🌿','🥑','🍃','☘️','🍀','💚','♻️','🐮','🐷','🐔','🐝','✿','❀','✦','✧','⋆','♡','·','˖'];
const DIVIDERS=['˚₊‧ꓰ᠁ 🌱 ᠂ꓱ ‧₊˚','⋆｡˚ 🌿 ˚｡⋆','·｡°✦ 🌱 ✦°｡·','╰┈➤ 🌱','⊚ ˚˖ 🌿 ˖˚ ⊚','･:＊¨ 🌱 ¨＊:･'];
function escH(t){return t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
function copy(text){
  if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(text);}
  else{const ta=document.createElement('textarea');ta.value=text;document.body.appendChild(ta);ta.select();try{document.execCommand('copy');}catch(e){}ta.remove();}
}
function flash(b){const o=b.textContent;b.textContent='Kopiert!';b.classList.add('done');setTimeout(()=>{b.textContent=o;b.classList.remove('done');},1200);}
function wireCopy(scope){
  scope.querySelectorAll('.copybtn[data-text]').forEach(b=>{b.onclick=()=>{copy(decodeURIComponent(b.dataset.text));flash(b);};});
}
function render(){
  const t=document.getElementById('ftext').value || 'vegan';
  document.getElementById('fontlist').innerHTML=STYLES.map(([name,fn])=>{
    const out=fn(t);
    return '<div class="fontrow"><div style="flex:1;min-width:0"><span class="flabel">'+name+'</span>'+
      '<div class="fout">'+escH(out)+'</div></div>'+
      '<button class="copybtn" data-text="'+encodeURIComponent(out)+'">Kopieren</button></div>';
  }).join('');
  wireCopy(document.getElementById('fontlist'));
}
document.getElementById('ftext').addEventListener('input',render);
document.getElementById('decogrid').innerHTML=DECO.map(d=>'<button class="decobtn" data-d="'+encodeURIComponent(d)+'">'+d+'</button>').join('');
document.querySelectorAll('.decobtn').forEach(b=>{b.onclick=()=>{const ta=document.getElementById('ftext');ta.value+=decodeURIComponent(b.dataset.d);render();ta.focus();};});
document.getElementById('divlist').innerHTML=DIVIDERS.map(d=>'<div class="fontrow"><div class="fout" style="flex:1;min-width:0">'+escH(d)+'</div><button class="copybtn" data-text="'+encodeURIComponent(d)+'">Kopieren</button></div>').join('');
wireCopy(document.getElementById('divlist'));
render();
""".strip()

# ---------------------------------------------------------------- page shell


def page(title, desc, path, body, jsonld=None, og_type="website"):
    canonical = BASE_URL + url(path)
    ld = ""
    if jsonld:
        for block in jsonld:
            ld += '<script type="application/ld+json">' + json.dumps(block, ensure_ascii=False) + "</script>\n"
    fonts = (
        f'<link rel="preload" href="{url("/fonts/gabarito-latin.woff2")}" as="font" type="font/woff2" crossorigin>\n'
        f'<link rel="preload" href="{url("/fonts/figtree-latin.woff2")}" as="font" type="font/woff2" crossorigin>'
    )
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canonical}">
<meta name="theme-color" content="#0a4a4a">
<link rel="icon" href="{url('/favicon.svg')}" type="image/svg+xml">
<meta property="og:site_name" content="This Is Vegan Tools">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="{og_type}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{BASE_URL}{url('/og-image.png')}">
<meta property="og:locale" content="de_DE">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{BASE_URL}{url('/og-image.png')}">
{fonts}
<style>{CSS}</style>
{ld}</head>
<body>
<div class="wrap">
{body}
</div>
</body>
</html>"""


def site_header(subtitle, tagline="Gratis · ohne Anmeldung"):
    return f"""<header class="site">
  <a class="brand" href="{url('/')}">
    <span class="dot"></span>
    <div>This Is Vegan<small>{esc(subtitle)}</small></div>
  </a>
  <div class="free">{esc(tagline)}</div>
</header>"""


def site_footer(meta, full_disclaimer=True):
    stand = german_date(meta["lastUpdated"])
    disc = ""
    if full_disclaimer:
        disc = """<p class="disc">
  <b>Angaben ohne Gewähr.</b> Diese Einordnung dient der Orientierung. Bei vielen Zusatzstoffen (besonders Fettsäuren, Emulgatoren und Geschmacksverstärkern) hängt die Herkunft vom jeweiligen Hersteller ab und ist auf der Verpackung nicht erkennbar. Im Zweifel hilft nur eins: beim Hersteller nachfragen oder auf ein Vegan-Siegel achten. Zusatzstoffe, die im Endprodukt nicht mehr enthalten sind (technische Hilfsmittel wie Gelatine zur Weinklärung), müssen nicht deklariert werden.
</p>"""
    else:
        disc = f'<p class="disc">Alle Tools sind kostenlos, laufen direkt im Browser und speichern nichts. Stand: {esc(stand)}.</p>'
    return f"""<footer class="site">
{disc}
<div class="fbrand"><span class="dot"></span>This Is Vegan</div>
<div class="flinks">
  <a href="{MAIN_SITE}/">Zum Magazin</a>
  <a href="{MAIN_SITE}/impressum/">Impressum</a>
  <a href="{MAIN_SITE}/datenschutzerklaerung/">Datenschutz</a>
</div>
</footer>"""


# ---------------------------------------------------------------- pages


def build_hub(meta, adds, ings, nutrients):
    counts = {s: sum(1 for a in adds if a["status"] == s) for s in ("yes", "no", "maybe")}
    body = site_header("Tools", "Gratis · ohne Anmeldung") + f"""
<section class="hero left">
  <div class="eyebrow">Kleine Helfer für den veganen Alltag</div>
  <h1>Vegane <span class="q">Tools.</span></h1>
  <p class="sub">Schnelle Antworten auf die Fragen, die im Supermarkt oder in der Küche auftauchen. Alles kostenlos, ohne Anmeldung, direkt im Browser.</p>
</section>

<section class="section">
  <div class="toolcards">
    <a class="toolcard" href="{url('/e-nummern/')}">
      <span class="badge">Live</span>
      <h3>E-Nummern-Checker</h3>
      <p>E-Nummer oder Zutat eingeben und sofort sehen, ob der Zusatzstoff vegan ist. {len(adds)} Zusatzstoffe: {counts['yes']} vegan, {counts['maybe']} herkunftsabhängig, {counts['no']} immer tierisch.</p>
      <span class="meta">Jetzt prüfen →</span>
    </a>
    <a class="toolcard" href="{url(ERSATZ_BASE)}">
      <span class="badge">Live</span>
      <h3>Vegan-Ersatz-Finder</h3>
      <p>Zutat eingeben und die besten veganen Alternativen sehen, mit Menge und Einsatzzweck. {len(ings)} Zutaten von Ei und Butter bis Käse und Gelatine.</p>
      <span class="meta">Ersatz finden →</span>
    </a>
    <a class="toolcard" href="{url(NAEHR_BASE)}">
      <span class="badge">Live</span>
      <h3>Nährstoff-Rechner</h3>
      <p>Gewicht und Aktivität eingeben und sofort sehen, wie viel Protein, B12, Eisen, Omega-3 und Calcium du brauchst, plus die besten pflanzlichen Quellen.</p>
      <span class="meta">Bedarf berechnen →</span>
    </a>
    <a class="toolcard" href="{url(IMPACT_BASE)}">
      <span class="badge">Live</span>
      <h3>Impact-Rechner</h3>
      <p>Sieh, was deine vegane Ernährung bewegt: gerettete Tiere, gespartes CO2, Wasser und Ackerland. Zeitraum eingeben, Ergebnis teilen.</p>
      <span class="meta">Wirkung sehen →</span>
    </a>
    <a class="toolcard" href="{url(FOOD_BASE)}">
      <span class="badge">Live</span>
      <h3>Ist das vegan?</h3>
      <p>Lebensmittel eingeben und sofort sehen, ob es vegan ist und wo die versteckten tierischen Zutaten lauern, von Wein bis Gummibärchen.</p>
      <span class="meta">Lebensmittel prüfen →</span>
    </a>
    <a class="toolcard" href="{url(SAISON_BASE)}">
      <span class="badge">Live</span>
      <h3>Saisonkalender</h3>
      <p>Monat wählen und sehen, welches Obst und Gemüse regional gerade Saison hat, frisch vom Feld oder aus dem Lager. Für jeden Monat eine eigene Übersicht.</p>
      <span class="meta">Saison checken →</span>
    </a>
    <a class="toolcard" href="{url(PFLANZ_BASE)}">
      <span class="badge">Live</span>
      <h3>Pflanzendrink-Vergleich</h3>
      <p>Hafer, Soja, Mandel und Co. im Vergleich: welcher Drink für Kaffee, Backen, Protein oder Klima am besten passt, mit Nährwerten.</p>
      <span class="meta">Drink finden →</span>
    </a>
    <a class="toolcard" href="{url(PROT_BASE)}">
      <span class="badge">Live</span>
      <h3>Protein-Tabelle</h3>
      <p>Die proteinreichsten pflanzlichen Lebensmittel, durchsuchbar und sortierbar, mit Eiweiß pro 100 Gramm. Von Tofu über Linsen bis Hanfsamen.</p>
      <span class="meta">Protein finden →</span>
    </a>
    <a class="toolcard" href="{url(CO2_BASE)}">
      <span class="badge">Live</span>
      <h3>CO2-Fußabdruck</h3>
      <p>Der Klima-Fußabdruck von Lebensmitteln im Vergleich, tierisch gegen pflanzlich, in kg CO2 pro Kilo. Auf Basis großer Ökobilanz-Daten.</p>
      <span class="meta">Klimabilanz sehen →</span>
    </a>
    <a class="toolcard" href="{url(MEAL_BASE)}">
      <span class="badge">Live</span>
      <h3>Protein pro Mahlzeit</h3>
      <p>Stell deine Mahlzeit aus pflanzlichen Lebensmitteln zusammen und sieh sofort, wie viel Protein zusammenkommt und wie viel vom Tagesziel.</p>
      <span class="meta">Mahlzeit rechnen →</span>
    </a>
    <div class="toolcard soon">
      <span class="badge">In Arbeit</span>
      <h3>Mehr Tools kommen</h3>
      <p>Wir bauen die Tool-Sammlung Stück für Stück aus. Wenn dir ein Tool fehlt, das dir den veganen Alltag leichter machen würde, sag uns Bescheid.</p>
      <span class="meta">Bald verfügbar</span>
    </div>
  </div>
</section>

<section class="section">
  <h2>Für Content Creator</h2>
  <p class="lead">Eigener Bereich für vegane, Tierschutz- und Food-Accounts auf Instagram, TikTok und Co.</p>
  <div class="toolcards">
    <a class="toolcard" href="{url(FONT_BASE)}">
      <span class="badge">Live</span>
      <h3>Schriftarten-Generator</h3>
      <p>Text in 18 Stilen kopieren: fett, kursiv, Schreibschrift, durchgestrichen, kopfüber und mehr, plus vegane Deko und Trenner für Bio und Caption.</p>
      <span class="meta">Schrift stylen →</span>
    </a>
    <a class="toolcard" href="{url(CREATOR_BASE)}">
      <span class="badge">Neu</span>
      <h3>Creator-Bereich</h3>
      <p>Alle Tools für deinen veganen Account an einem Ort. Wir bauen den Bereich Stück für Stück aus.</p>
      <span class="meta">Bereich ansehen →</span>
    </a>
  </div>
</section>

<section class="section">
  <h2>Mehr von This Is Vegan</h2>
  <p class="lead">Die Tools gehören zum This-Is-Vegan-Magazin. Dort findest du Tests, Guides und Rezepte rund um den veganen Alltag.</p>
  <div class="linklist">
""" + "\n".join(
        f'    <a href="{href}">{esc(t)}<span class="arrow">→</span></a>' for t, href in READ_MORE
    ) + f"""
  </div>
</section>
""" + site_footer(meta, full_disclaimer=False)

    jsonld = [
        {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": "Vegane Tools von This Is Vegan",
            "description": "Kostenlose Web-Tools für den veganen Alltag, vom E-Nummern-Checker bis zu weiteren Helfern.",
            "url": BASE_URL + url("/"),
            "isPartOf": {"@type": "WebSite", "name": "This Is Vegan", "url": MAIN_SITE},
            "mainEntity": {
                "@type": "ItemList",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": 1,
                        "name": "E-Nummern-Checker: Ist das vegan?",
                        "url": BASE_URL + url("/e-nummern/"),
                    },
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": "Vegan-Ersatz-Finder",
                        "url": BASE_URL + url(ERSATZ_BASE),
                    },
                    {
                        "@type": "ListItem",
                        "position": 3,
                        "name": "Veganer Nährstoff-Rechner",
                        "url": BASE_URL + url(NAEHR_BASE),
                    },
                    {
                        "@type": "ListItem",
                        "position": 4,
                        "name": "Veganer Impact-Rechner",
                        "url": BASE_URL + url(IMPACT_BASE),
                    },
                    {
                        "@type": "ListItem",
                        "position": 5,
                        "name": "Ist das vegan? Lebensmittel-Checker",
                        "url": BASE_URL + url(FOOD_BASE),
                    },
                    {
                        "@type": "ListItem",
                        "position": 6,
                        "name": "Vegan-Saisonkalender",
                        "url": BASE_URL + url(SAISON_BASE),
                    },
                    {
                        "@type": "ListItem",
                        "position": 7,
                        "name": "Pflanzendrink-Vergleich",
                        "url": BASE_URL + url(PFLANZ_BASE),
                    },
                    {
                        "@type": "ListItem",
                        "position": 8,
                        "name": "Vegane Protein-Tabelle",
                        "url": BASE_URL + url(PROT_BASE),
                    },
                    {
                        "@type": "ListItem",
                        "position": 9,
                        "name": "CO2-Fußabdruck von Lebensmitteln",
                        "url": BASE_URL + url(CO2_BASE),
                    },
                    {
                        "@type": "ListItem",
                        "position": 10,
                        "name": "Protein-pro-Mahlzeit-Rechner",
                        "url": BASE_URL + url(MEAL_BASE),
                    },
                    {
                        "@type": "ListItem",
                        "position": 11,
                        "name": "Schriftarten-Generator für Creator",
                        "url": BASE_URL + url(FONT_BASE),
                    },
                ],
            },
        }
    ]
    return page(
        "Vegane Tools: kostenlose Helfer für den Alltag | This Is Vegan",
        f"Kostenlose vegane Tools von This Is Vegan: E-Nummern-Checker mit {len(adds)} Zusatzstoffen und mehr. Ohne Anmeldung, direkt im Browser.",
        "/",
        body,
        jsonld,
    )


def build_checker(meta, adds):
    order = {"no": 0, "maybe": 1, "yes": 2}
    sorted_adds = sorted(adds, key=lambda a: (order[a["status"]], _numkey(a["code"])))
    items = "\n".join(
        f'    <a class="item {a["status"]}" href="{url("/e-nummern/" + slug(a["code"]) + "/")}">'
        f'<span class="bar"></span><div><div class="en">{esc(a["code"])}</div>'
        f'<div class="nm">{esc(a["name"])}</div></div></a>'
        for a in sorted_adds
    )
    compact = [
        {
            "n": a["code"], "name": a["name"], "k": a["class"], "s": a["status"],
            "info": a["info"], **({"note": a["note"]} if a.get("note") else {}),
            "u": url("/e-nummern/" + slug(a["code"]) + "/"),
        }
        for a in adds
    ]
    js = CHECKER_JS.replace("__DATA__", json.dumps(compact, ensure_ascii=False, separators=(",", ":")))
    counts = {s: sum(1 for a in adds if a["status"] == s) for s in ("yes", "no", "maybe")}

    body = site_header("E-Nummern-Checker") + f"""
<nav class="crumbs" aria-label="Breadcrumb"><a href="{url('/')}">Tools</a><span>›</span>E-Nummern-Checker</nav>
<section class="hero">
  <div class="eyebrow">Steh nicht mehr ratlos im Supermarkt</div>
  <h1>Ist das <span class="q">vegan?</span></h1>
  <p class="sub">E-Nummer oder Zutat eingeben und sofort sehen, ob der Zusatzstoff vegan, nicht vegan oder grenzwertig ist.</p>

  <div class="search-shell">
    <div class="search-box">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"></circle><path d="M21 21l-4.3-4.3"></path></svg>
      <input id="q" type="text" autocomplete="off" placeholder="z. B. E471, Gelatine oder Karmin" aria-label="E-Nummer oder Zutat suchen">
      <button class="go" id="go">Prüfen</button>
    </div>
  </div>

  <div class="chips">
    <span>Häufig gesucht:</span>
    <button class="chip" data-c="E120">E120 Karmin</button>
    <button class="chip" data-c="E471">E471</button>
    <button class="chip" data-c="E441">Gelatine</button>
    <button class="chip" data-c="E270">Milchsäure</button>
    <button class="chip" data-c="E621">Glutamat</button>
    <button class="chip" data-c="E920">L-Cystein</button>
  </div>

  <div id="result" aria-live="polite"></div>
</section>

<section class="listsec">
  <div class="listhead">
    <div>
      <h2>Alle Zusatzstoffe</h2>
      <p>{len(adds)} Einträge: {counts['yes']} vegan, {counts['maybe']} herkunftsabhängig, {counts['no']} immer tierisch. Tippe einen Eintrag an für die Details.</p>
    </div>
    <div class="filters" id="filters">
      <button class="filt active" data-f="all">Alle</button>
      <button class="filt s-yes" data-f="yes"><span class="swatch"></span>Vegan</button>
      <button class="filt s-maybe" data-f="maybe"><span class="swatch"></span>Kommt drauf an</button>
      <button class="filt s-no" data-f="no"><span class="swatch"></span>Nicht vegan</button>
    </div>
  </div>
  <div class="grid" id="grid">
{items}
    <div class="empty">Keine Einträge in diesem Filter.</div>
  </div>
</section>

<section class="section">
  <h2>Die häufigsten Verwechslungen</h2>
  <p class="prose"><b>Milchsäure (E270) ist vegan.</b> Sie klingt tierisch, entsteht aber durch Fermentation von Zucker und steckt auch in Sauerkraut. Mit Milch hat sie nichts zu tun.</p>
  <p class="prose"><b>Glutamat (E621) ist vegan.</b> Trotz schlechtem Ruf wird MSG durch Fermentation von pflanzlicher Stärke oder Melasse hergestellt.</p>
  <p class="prose"><b>E471 ist die häufigste Falle.</b> Die Mono- und Diglyceride können aus tierischen oder pflanzlichen Fetten stammen, und auf der Verpackung steht es nicht. Ohne Vegan-Label hilft nur die Nachfrage beim Hersteller.</p>
  <p class="prose"><b>L-Cystein (E920) steckt oft in Brötchen.</b> Es wird häufig aus Schweineborsten oder Federn gewonnen, zunehmend aber auch mikrobiell. Als technisches Hilfsmittel muss es oft nicht mal deklariert werden.</p>
</section>
""" + site_footer(meta) + f"\n<script>{js}</script>"

    jsonld = [
        {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": "E-Nummern-Checker: Ist das vegan?",
            "url": BASE_URL + url("/e-nummern/"),
            "applicationCategory": "UtilityApplication",
            "operatingSystem": "Web",
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
            "description": f"Kostenloser Checker für {len(adds)} Lebensmittelzusatzstoffe: E-Nummer eingeben und sofort sehen, ob der Stoff vegan ist.",
            "publisher": {"@type": "Organization", "name": "This Is Vegan", "url": MAIN_SITE},
        },
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": "Ist Milchsäure (E270) vegan?",
                    "acceptedAnswer": {"@type": "Answer", "text": "Ja. Milchsäure klingt tierisch, entsteht aber durch Fermentation von Zucker und steckt auch in Sauerkraut. Mit Milch hat sie nichts zu tun."},
                },
                {
                    "@type": "Question",
                    "name": "Ist Glutamat (E621) vegan?",
                    "acceptedAnswer": {"@type": "Answer", "text": "Ja. Mononatriumglutamat wird durch Fermentation von pflanzlicher Stärke oder Melasse hergestellt und ist trotz schlechtem Ruf nicht tierisch."},
                },
                {
                    "@type": "Question",
                    "name": "Ist E471 vegan?",
                    "acceptedAnswer": {"@type": "Answer", "text": "Nicht automatisch. Die Mono- und Diglyceride von Speisefettsäuren können aus tierischen oder pflanzlichen Fetten stammen. Ohne Vegan-Label hilft nur die Nachfrage beim Hersteller."},
                },
                {
                    "@type": "Question",
                    "name": "Welche E-Nummern sind nie vegan?",
                    "acceptedAnswer": {"@type": "Answer", "text": "Immer tierischen Ursprungs sind E120 (Karmin), E441 (Gelatine), E542 (Knochenphosphat), E901 (Bienenwachs), E904 (Schellack), E913 (Lanolin), E966 (Lactit) und E1105 (Lysozym)."},
                },
            ],
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Tools", "item": BASE_URL + url("/")},
                {"@type": "ListItem", "position": 2, "name": "E-Nummern-Checker", "item": BASE_URL + url("/e-nummern/")},
            ],
        },
    ]
    return page(
        "E-Nummern-Checker: Ist das vegan? | This Is Vegan",
        f"E-Nummer oder Zutat eingeben und in Sekunden sehen, ob ein Zusatzstoff vegan ist. {len(adds)} E-Nummern mit Erklärung. Kostenlos, ohne Anmeldung.",
        "/e-nummern/",
        body,
        jsonld,
    )


def _numkey(code):
    num = "".join(c for c in code[1:] if c.isdigit())
    suffix = "".join(c for c in code[1:] if not c.isdigit())
    return (int(num), suffix)


def related_additives(a, adds, n=6):
    others = [x for x in adds if x["code"] != a["code"]]
    same_class = [x for x in others if x["class"] == a["class"]]
    same_status = [x for x in others if x["status"] == a["status"] and x["class"] != a["class"]]
    rel = same_class[:n]
    for x in same_status:
        if len(rel) >= n:
            break
        rel.append(x)
    return rel[:n]


def build_detail(a, meta, adds):
    code, name, status = a["code"], a["name"], a["status"]
    L = LABEL[status]
    s = slug(code)
    path = f"/e-nummern/{s}/"
    title = f"{code} vegan? – {name} | This Is Vegan"
    desc = meta_description(a)
    note_html = ""
    if a.get("note"):
        note_html = f'<div class="note"><span>!</span><span><b>Gut zu wissen:</b> {esc(a["note"])}</span></div>'
    guide = STATUS_GUIDE[status].format(code=code)
    blurb = CLASS_BLURB.get(a["class"], "")
    rel = related_additives(a, adds)
    rel_html = "\n".join(
        f'    <a class="item {x["status"]}" href="{url("/e-nummern/" + slug(x["code"]) + "/")}">'
        f'<span class="bar"></span><div><div class="en">{esc(x["code"])}</div>'
        f'<div class="nm">{esc(x["name"])}</div></div></a>'
        for x in rel
    )
    # pro Seite zwei wechselnde Magazin-Links, damit nicht jede Seite identisch verlinkt
    idx = sum(ord(c) for c in code)
    picks = [READ_MORE[idx % 4], READ_MORE[(idx + 1) % 4]]
    read_html = "\n".join(
        f'    <a href="{href}">{esc(t)}<span class="arrow">→</span></a>' for t, href in picks
    )

    answer_text = f"{L['t']}: {a['info']}"
    if a.get("note"):
        answer_text += f" {a['note']}"

    body = site_header("E-Nummern-Checker") + f"""
<nav class="crumbs" aria-label="Breadcrumb"><a href="{url('/')}">Tools</a><span>›</span><a href="{url('/e-nummern/')}">E-Nummern-Checker</a><span>›</span>{esc(code)}</nav>
<section class="hero left">
  <div class="eyebrow">{esc(a["class"])} · E-Nummern-Check</div>
  <h1 class="detail">Ist {esc(code)} <span class="q">vegan?</span></h1>
</section>

<div id="result" style="margin:26px 0 0;max-width:620px">
  <div class="card" style="animation:none">
    <div class="verdict {status}">
      <div class="mark">{L["icon"]}</div>
      <div class="vtext">{L["t"]}<small>{L["s"]}</small></div>
    </div>
    <div class="card-body">
      <div class="enum">{esc(code)}</div>
      <div class="ename">{esc(name)}</div>
      <span class="klasse">{esc(a["class"])}</span>
      <p class="info">{esc(a["info"])}</p>
      {note_html}
    </div>
  </div>
</div>

<section class="section">
  <h2>Was heißt das für dich?</h2>
  <p class="prose">{esc(guide)}</p>
</section>

<section class="section">
  <h2>Wofür wird {esc(code)} eingesetzt?</h2>
  <p class="prose">{esc(name)} gehört zur Gruppe der Zusatzstoffe mit der Funktion {esc(a["class"])}. {esc(blurb)}</p>
</section>

<section class="section">
  <h2>Ähnliche Zusatzstoffe</h2>
  <div class="related">
{rel_html}
  </div>
</section>

<div class="cta">
  <div>
    <h2>Anderen Zusatzstoff prüfen?</h2>
    <p>Der E-Nummern-Checker kennt {len(adds)} Zusatzstoffe und zeigt dir sofort die Einordnung.</p>
  </div>
  <a class="btn" href="{url('/e-nummern/')}">Zum Checker →</a>
</div>

<section class="section">
  <h2>Weiterlesen im Magazin</h2>
  <div class="linklist">
{read_html}
  </div>
</section>
""" + site_footer(meta)

    jsonld = [
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": f"Ist {code} vegan?",
                    "acceptedAnswer": {"@type": "Answer", "text": answer_text},
                }
            ],
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Tools", "item": BASE_URL + url("/")},
                {"@type": "ListItem", "position": 2, "name": "E-Nummern-Checker", "item": BASE_URL + url("/e-nummern/")},
                {"@type": "ListItem", "position": 3, "name": code, "item": BASE_URL + url(path)},
            ],
        },
    ]
    return page(title, desc, path, body, jsonld, og_type="article")


ERSATZ_BASE = "/vegan-ersetzen/"

ERSATZ_POPULAR = ["Ei", "Butter", "Milch", "Schlagsahne", "Käse", "Gelatine"]


def build_ersatz_hub(meta, ings):
    sorted_ings = sorted(ings, key=lambda x: x["name"].lower())
    items = "\n".join(
        f'    <a class="item yes" href="{url(ERSATZ_BASE + i["slug"] + "/")}">'
        f'<span class="bar"></span><div><div class="en">{esc(i["name"])}</div>'
        f'<div class="nm">{esc(i["category"])}</div></div></a>'
        for i in sorted_ings
    )
    compact = [
        {
            "name": i["name"], "aka": i.get("aka", []), "intro": i.get("intro", ""),
            "subs": [
                {"name": s["name"], "ratio": s["ratio"], "bf": s.get("best_for", ""), "nt": s.get("note", "")}
                for s in i["substitutes"]
            ],
            "u": url(ERSATZ_BASE + i["slug"] + "/"),
        }
        for i in ings
    ]
    js = ERSATZ_JS.replace("__DATA__", json.dumps(compact, ensure_ascii=False, separators=(",", ":")))
    chips = "\n".join(f'    <button class="chip" data-c="{esc(c)}">{esc(c)}</button>' for c in ERSATZ_POPULAR)

    body = site_header("Vegan-Ersatz-Finder") + f"""
<nav class="crumbs" aria-label="Breadcrumb"><a href="{url('/')}">Tools</a><span>›</span>Vegan-Ersatz-Finder</nav>
<section class="hero">
  <div class="eyebrow">Kochen und Backen ohne Tierisches</div>
  <h1>Womit <span class="q">ersetzen?</span></h1>
  <p class="sub">Zutat eingeben und sofort die besten veganen Alternativen sehen, mit Menge und wofür sie sich am besten eignen.</p>

  <div class="search-shell">
    <div class="search-box">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"></circle><path d="M21 21l-4.3-4.3"></path></svg>
      <input id="q" type="text" autocomplete="off" placeholder="z. B. Ei, Butter, Sahne oder Gelatine" aria-label="Zutat suchen, die du vegan ersetzen willst">
      <button class="go" id="go">Finden</button>
    </div>
  </div>

  <div class="chips">
    <span>Beliebt:</span>
{chips}
  </div>

  <div id="result" aria-live="polite"></div>
</section>

<section class="listsec">
  <div class="listhead">
    <div>
      <h2>Alle Zutaten</h2>
      <p>{len(ings)} Zutaten mit veganen Alternativen. Tipp antippen für alle Details.</p>
    </div>
  </div>
  <div class="grid" id="grid">
{items}
  </div>
</section>
""" + site_footer(meta, full_disclaimer=False) + f"\n<script>{js}</script>"

    jsonld = [
        {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": "Vegan-Ersatz-Finder",
            "url": BASE_URL + url(ERSATZ_BASE),
            "applicationCategory": "LifestyleApplication",
            "operatingSystem": "Web",
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
            "description": f"Kostenloser Finder für vegane Alternativen zu {len(ings)} Zutaten wie Ei, Butter, Milch und Käse, mit Mengenangaben.",
            "publisher": {"@type": "Organization", "name": "This Is Vegan", "url": MAIN_SITE},
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Tools", "item": BASE_URL + url("/")},
                {"@type": "ListItem", "position": 2, "name": "Vegan-Ersatz-Finder", "item": BASE_URL + url(ERSATZ_BASE)},
            ],
        },
    ]
    return page(
        "Vegan ersetzen: der Ersatz-Finder für Ei, Butter, Milch und mehr | This Is Vegan",
        f"Zutat eingeben und die besten veganen Alternativen sehen, mit Menge und Einsatzzweck. {len(ings)} Zutaten von Ei bis Gelatine. Kostenlos, ohne Anmeldung.",
        ERSATZ_BASE,
        body,
        jsonld,
    )


def build_ersatz_detail(ing, meta, ings):
    name = ing["name"]
    s = ing["slug"]
    path = ERSATZ_BASE + s + "/"
    subs = ing["substitutes"]
    top = subs[0]

    subs_html = "\n".join(
        f'    <div class="optcard"><div class="sname">{esc(x["name"])}'
        + (f'<span class="bf">{esc(x["best_for"])}</span>' if x.get("best_for") else "")
        + f'</div><div class="ratio">{esc(x["ratio"])}</div>'
        + (f'<div class="nt">{esc(x["note"])}</div>' if x.get("note") else "")
        + "</div>"
        for x in subs
    )

    related = [x for x in ings if x["category"] == ing["category"] and x["slug"] != s][:6]
    if len(related) < 4:
        related += [x for x in ings if x["slug"] != s and x not in related][: 4 - len(related)]
    rel_html = "\n".join(
        f'    <a class="item yes" href="{url(ERSATZ_BASE + r["slug"] + "/")}">'
        f'<span class="bar"></span><div><div class="en">{esc(r["name"])}</div>'
        f'<div class="nm">{esc(r["category"])}</div></div></a>'
        for r in related
    )

    read_links = ing.get("readmore", [])
    read_html = ""
    if read_links:
        read_html = (
            '<section class="section"><h2>Weiterlesen im Magazin</h2><div class="linklist">'
            + "".join(
                f'<a href="{MAIN_SITE}{href}">{esc(t)}<span class="arrow">→</span></a>'
                for t, href in read_links
            )
            + "</div></section>"
        )

    intro = ing.get("intro", "")
    answer = f"Am vielseitigsten ist {top['name']} ({top['ratio']}). Insgesamt gibt es {len(subs)} gute vegane Alternativen, je nachdem, was {name} im Rezept tun soll."

    body = site_header("Vegan-Ersatz-Finder") + f"""
<nav class="crumbs" aria-label="Breadcrumb"><a href="{url('/')}">Tools</a><span>›</span><a href="{url(ERSATZ_BASE)}">Vegan ersetzen</a><span>›</span>{esc(name)}</nav>
<section class="hero left">
  <div class="eyebrow">{esc(ing["category"])} · vegan ersetzen</div>
  <h1 class="detail">{esc(name)} vegan <span class="q">ersetzen</span></h1>
  <p class="sub" style="margin-left:0">{esc(intro)}</p>
</section>

<div id="result" style="margin:20px 0 0;max-width:640px">
  <div class="card" style="animation:none"><div class="card-body">
    <div class="enum" style="font-size:22px">Die besten Alternativen</div>
    <div class="subs">
{subs_html}
    </div>
  </div></div>
</div>

<section class="section">
  <h2>Was eignet sich wofür?</h2>
  <div class="usecards">
""" + "\n".join(
        f'    <div class="usecard"><b>{esc(x["name"])}</b><span>{esc(x.get("best_for", "Allrounder"))}</span></div>'
        for x in subs
    ) + f"""
  </div>
</section>

<section class="section">
  <h2>Ähnliche Zutaten ersetzen</h2>
  <div class="related">
{rel_html}
  </div>
</section>

<div class="cta">
  <div>
    <h2>Noch eine Zutat ersetzen?</h2>
    <p>Der Vegan-Ersatz-Finder kennt {len(ings)} Zutaten und zeigt dir sofort die passende Alternative.</p>
  </div>
  <a class="btn" href="{url(ERSATZ_BASE)}">Zum Finder →</a>
</div>

{read_html}
""" + site_footer(meta, full_disclaimer=False)

    jsonld = [
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": f"Wie kann ich {name} vegan ersetzen?",
                    "acceptedAnswer": {"@type": "Answer", "text": answer},
                }
            ],
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Tools", "item": BASE_URL + url("/")},
                {"@type": "ListItem", "position": 2, "name": "Vegan ersetzen", "item": BASE_URL + url(ERSATZ_BASE)},
                {"@type": "ListItem", "position": 3, "name": name, "item": BASE_URL + url(path)},
            ],
        },
    ]
    desc = f"{name} vegan ersetzen: {len(subs)} Alternativen mit Menge und Einsatzzweck. Bester Allrounder: {top['name']}. Kostenlos im Ersatz-Finder von This Is Vegan."
    if len(desc) > 155:
        desc = f"{name} vegan ersetzen: {len(subs)} Alternativen mit Menge und Einsatzzweck, vom This-Is-Vegan-Ersatz-Finder."
    return page(
        f"{name} vegan ersetzen: die besten Alternativen | This Is Vegan",
        desc,
        path,
        body,
        jsonld,
        og_type="article",
    )


NAEHR_BASE = "/naehrstoffrechner/"


def _cover(n):
    return "z. B. " + ", ".join(s["food"] for s in n["sources"][:3])


def build_naehrstoff_hub(meta, nutrients):
    compact = [
        {
            "name": n["name"], "unit": n["unit"], "type": n["target_type"],
            "target": n.get("target"), "tf": n.get("target_female"), "tm": n.get("target_male"),
            "cover": _cover(n), "sup": n["supplement"]["level"],
            "u": url(NAEHR_BASE + n["slug"] + "/"),
        }
        for n in nutrients
    ]
    js = NAEHR_JS.replace("__DATA__", json.dumps(compact, ensure_ascii=False, separators=(",", ":")))

    blurbs = "\n".join(
        f'  <p class="prose"><b>{esc(n["name"])}.</b> {esc(n["intro"])} '
        f'<a href="{url(NAEHR_BASE + n["slug"] + "/")}" style="color:var(--green);font-weight:700;text-decoration:none">Mehr →</a></p>'
        for n in nutrients
    )

    body = site_header("Nährstoff-Rechner") + f"""
<nav class="crumbs" aria-label="Breadcrumb"><a href="{url('/')}">Tools</a><span>›</span>Nährstoff-Rechner</nav>
<section class="hero">
  <div class="eyebrow">Dein veganer Nährstoff-Check</div>
  <h1>Deckst du deinen <span class="q">Bedarf?</span></h1>
  <p class="sub">Gewicht und Aktivität eingeben, sofort deine Richtwerte für die fünf wichtigsten Nährstoffe sehen, mit den besten pflanzlichen Quellen.</p>

  <div class="calc">
    <div class="calc-grid">
      <div class="field">
        <label for="w">Dein Gewicht in kg</label>
        <input id="w" type="number" value="70" min="30" max="250" inputmode="numeric" aria-label="Gewicht in Kilogramm">
      </div>
      <div class="field">
        <label>Geschlecht</label>
        <div class="seg">
          <button type="button" data-sex="f" class="on">weiblich</button>
          <button type="button" data-sex="m">männlich</button>
        </div>
      </div>
    </div>
    <div class="field">
      <label>Wie aktiv bist du?</label>
      <div class="seg">
        <button type="button" data-act="low">wenig aktiv</button>
        <button type="button" data-act="active" class="on">aktiv</button>
        <button type="button" data-act="sport">Sport oder Kraft</button>
      </div>
    </div>
  </div>

  <div class="nresults" id="nresults"></div>
  <div class="infobox">{esc(meta["disclaimer"])}</div>
</section>

<section class="section">
  <h2>Die fünf, auf die es ankommt</h2>
  <p class="lead">Bei veganer Ernährung lohnt der Blick auf diese fünf Nährstoffe. Vier davon deckst du leicht über Essen, einen musst du supplementieren.</p>
  <div style="margin-top:16px;max-width:640px">
{blurbs}
  </div>
</section>
""" + site_footer(meta, full_disclaimer=False) + f"\n<script>{js}</script>"

    jsonld = [
        {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": "Veganer Nährstoff-Rechner",
            "url": BASE_URL + url(NAEHR_BASE),
            "applicationCategory": "HealthApplication",
            "operatingSystem": "Web",
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
            "description": "Berechnet Richtwerte für Protein, B12, Eisen, Omega-3 und Calcium bei veganer Ernährung, mit den besten pflanzlichen Quellen.",
            "publisher": {"@type": "Organization", "name": "This Is Vegan", "url": MAIN_SITE},
        },
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": "Wie viel Protein brauche ich vegan?",
                 "acceptedAnswer": {"@type": "Answer", "text": "Je nach Aktivität rund 0,8 bis 1,6 g pro Kilo Körpergewicht. Wenig aktiv 0,8 bis 1,0, aktiv 1,2 bis 1,4, bei Kraft- oder Ausdauersport 1,4 bis 1,6 g pro kg."}},
                {"@type": "Question", "name": "Muss ich B12 supplementieren?",
                 "acceptedAnswer": {"@type": "Answer", "text": "Ja. B12 ist der einzige Nährstoff, den du bei veganer Ernährung zwingend über ein Supplement zuführen musst, da Pflanzen es nicht in verlässlicher Form liefern."}},
                {"@type": "Question", "name": "Welche Nährstoffe sind bei veganer Ernährung kritisch?",
                 "acceptedAnswer": {"@type": "Answer", "text": "Vor allem B12 (Supplement nötig), außerdem lohnt der Blick auf Protein, Eisen, Omega-3 und Calcium. Diese vier lassen sich gut über die Ernährung decken."}},
            ],
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Tools", "item": BASE_URL + url("/")},
                {"@type": "ListItem", "position": 2, "name": "Nährstoff-Rechner", "item": BASE_URL + url(NAEHR_BASE)},
            ],
        },
    ]
    return page(
        "Veganer Nährstoff-Rechner: dein Bedarf in 10 Sekunden | This Is Vegan",
        "Gewicht und Aktivität eingeben und sehen, wie viel Protein, B12, Eisen, Omega-3 und Calcium du als Veganer brauchst, mit den besten pflanzlichen Quellen. Kostenlos.",
        NAEHR_BASE,
        body,
        jsonld,
    )


def build_naehrstoff_detail(n, meta, nutrients):
    name = n["name"]
    s = n["slug"]
    path = NAEHR_BASE + s + "/"
    sup = n["supplement"]
    sup_class = "b-ess" if sup["level"] == "essenziell" else "b-opt"

    sources_html = "\n".join(
        f'    <div class="usecard"><b>{esc(src["food"])}</b><span>{esc(src["amount"])}</span></div>'
        for src in n["sources"]
    )
    related = [x for x in nutrients if x["slug"] != s]
    rel_html = "\n".join(
        f'    <a class="item yes" href="{url(NAEHR_BASE + r["slug"] + "/")}">'
        f'<span class="bar"></span><div><div class="en">{esc(r["name"])}</div>'
        f'<div class="nm">{esc(r["unit"])}</div></div></a>'
        for r in related
    )
    read_links = n.get("readmore", [])
    read_html = ""
    if read_links:
        read_html = (
            '<section class="section"><h2>Weiterlesen im Magazin</h2><div class="linklist">'
            + "".join(f'<a href="{MAIN_SITE}{href}">{esc(t)}<span class="arrow">→</span></a>' for t, href in read_links)
            + "</div></section>"
        )

    body = site_header("Nährstoff-Rechner") + f"""
<nav class="crumbs" aria-label="Breadcrumb"><a href="{url('/')}">Tools</a><span>›</span><a href="{url(NAEHR_BASE)}">Nährstoff-Rechner</a><span>›</span>{esc(name)}</nav>
<section class="hero left">
  <div class="eyebrow">Vegan versorgt</div>
  <h1 class="detail">{esc(name)} <span class="q">vegan</span> decken</h1>
  <p class="sub" style="margin-left:0">{esc(n["intro"])}</p>
</section>

<section class="section">
  <h2>Wie viel brauchst du?</h2>
  <p class="prose">{esc(n["targets"])}</p>
  <div class="infobox"><b>{esc(sup["level"].capitalize())}:</b> {esc(sup["text"])}</div>
</section>

<section class="section">
  <h2>Warum es zählt</h2>
  <p class="prose">{esc(n["why"])}</p>
</section>

<section class="section">
  <h2>Die besten pflanzlichen Quellen</h2>
  <div class="usecards">
{sources_html}
  </div>
  <div class="infobox"><b>Tipp:</b> {esc(n["tip"])}</div>
</section>

<section class="section">
  <h2>Weitere Nährstoffe</h2>
  <div class="related">
{rel_html}
  </div>
</section>

<div class="cta">
  <div>
    <h2>Deinen Bedarf berechnen?</h2>
    <p>Der Nährstoff-Rechner zeigt dir deine persönlichen Richtwerte in zehn Sekunden.</p>
  </div>
  <a class="btn" href="{url(NAEHR_BASE)}">Zum Rechner →</a>
</div>

{read_html}
""" + site_footer(meta, full_disclaimer=False)

    answer = n["targets"]
    jsonld = [
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": f"Wie viel {name} brauchen Veganer?",
                 "acceptedAnswer": {"@type": "Answer", "text": answer}},
            ],
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Tools", "item": BASE_URL + url("/")},
                {"@type": "ListItem", "position": 2, "name": "Nährstoff-Rechner", "item": BASE_URL + url(NAEHR_BASE)},
                {"@type": "ListItem", "position": 3, "name": name, "item": BASE_URL + url(path)},
            ],
        },
    ]
    first = n["intro"].split(". ")[0].rstrip(".") + "."
    desc = f"{name} vegan decken: Bedarf, beste pflanzliche Quellen und Tipps. {first}"
    if len(desc) > 155:
        desc = f"{name} vegan: Bedarf, beste pflanzliche Quellen und Tipps zur Versorgung. Vom This-Is-Vegan-Nährstoff-Rechner."
    titles = {
        "protein": "Veganer Proteinbedarf: wie viel brauchst du wirklich? | This Is Vegan",
        "b12": "Vitamin B12 vegan: Bedarf, Quellen und Supplement | This Is Vegan",
        "eisen": "Eisen vegan: Bedarf und die besten Quellen | This Is Vegan",
        "omega-3": "Omega-3 vegan: ALA, EPA, DHA und Algenöl | This Is Vegan",
        "calcium": "Calcium vegan: Bedarf ohne Milch decken | This Is Vegan",
    }
    return page(titles.get(s, f"{name} vegan: Bedarf und Quellen | This Is Vegan"), desc, path, body, jsonld, og_type="article")


FOOD_BASE = "/ist-das-vegan/"

FOOD_LABEL = {
    "yes": {"t": "In der Regel vegan", "s": "meist ohne Tierisches", "icon": "✓"},
    "maybe": {"t": "Kommt drauf an", "s": "oft versteckt tierisch", "icon": "?"},
    "no": {"t": "Meist nicht vegan", "s": "enthält in der Regel Tierisches", "icon": "✕"},
}

FOOD_POPULAR = ["Wein", "Pommes frites", "Brot", "Gummibärchen", "Dunkle Schokolade", "Honig"]


def build_food_hub(meta, foods):
    order = {"no": 0, "maybe": 1, "yes": 2}
    sorted_foods = sorted(foods, key=lambda x: (order[x["status"]], x["name"].lower()))
    items = "\n".join(
        f'    <a class="item {f["status"]}" href="{url(FOOD_BASE + f["slug"] + "/")}">'
        f'<span class="bar"></span><div><div class="en">{esc(f["name"])}</div>'
        f'<div class="nm">{esc(f["category"])}</div></div></a>'
        for f in sorted_foods
    )
    compact = [
        {"name": f["name"], "aka": f.get("aka", []), "cat": f["category"], "s": f["status"],
         "info": f["info"], **({"note": f["note"]} if f.get("note") else {}),
         "u": url(FOOD_BASE + f["slug"] + "/")}
        for f in foods
    ]
    js = FOOD_JS.replace("__DATA__", json.dumps(compact, ensure_ascii=False, separators=(",", ":")))
    chips = "\n".join(f'    <button class="chip" data-c="{esc(c)}">{esc(c)}</button>' for c in FOOD_POPULAR)
    counts = {s: sum(1 for f in foods if f["status"] == s) for s in ("yes", "no", "maybe")}

    body = site_header("Ist das vegan?") + f"""
<nav class="crumbs" aria-label="Breadcrumb"><a href="{url('/')}">Tools</a><span>›</span>Ist das vegan?</nav>
<section class="hero">
  <div class="eyebrow">Der schnelle Check fürs Regal</div>
  <h1>Ist das <span class="q">vegan?</span></h1>
  <p class="sub">Lebensmittel eingeben und sofort sehen, ob es in der Regel vegan ist, wo die versteckten Fallen liegen und worauf du achten musst.</p>

  <div class="search-shell">
    <div class="search-box">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"></circle><path d="M21 21l-4.3-4.3"></path></svg>
      <input id="q" type="text" autocomplete="off" placeholder="z. B. Wein, Brot oder Gummibärchen" aria-label="Lebensmittel suchen">
      <button class="go" id="go">Prüfen</button>
    </div>
  </div>

  <div class="chips">
    <span>Häufig gesucht:</span>
{chips}
  </div>

  <div id="result" aria-live="polite"></div>
</section>

<section class="listsec">
  <div class="listhead">
    <div>
      <h2>Alle Lebensmittel</h2>
      <p>{len(foods)} Einträge: {counts['yes']} meist vegan, {counts['maybe']} kommt drauf an, {counts['no']} meist nicht vegan.</p>
    </div>
    <div class="filters" id="filters">
      <button class="filt active" data-f="all">Alle</button>
      <button class="filt s-yes" data-f="yes"><span class="swatch"></span>Vegan</button>
      <button class="filt s-maybe" data-f="maybe"><span class="swatch"></span>Kommt drauf an</button>
      <button class="filt s-no" data-f="no"><span class="swatch"></span>Nicht vegan</button>
    </div>
  </div>
  <div class="grid" id="grid">
{items}
    <div class="empty">Keine Einträge in diesem Filter.</div>
  </div>
</section>
""" + site_footer(meta) + f"\n<script>{js}</script>"

    jsonld = [
        {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": "Ist das vegan? Lebensmittel-Checker",
            "url": BASE_URL + url(FOOD_BASE),
            "applicationCategory": "UtilityApplication",
            "operatingSystem": "Web",
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
            "description": f"Checker für {len(foods)} Lebensmittel: sofort sehen, ob ein Produkt vegan ist und wo die versteckten tierischen Zutaten liegen.",
            "publisher": {"@type": "Organization", "name": "This Is Vegan", "url": MAIN_SITE},
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Tools", "item": BASE_URL + url("/")},
                {"@type": "ListItem", "position": 2, "name": "Ist das vegan?", "item": BASE_URL + url(FOOD_BASE)},
            ],
        },
    ]
    return page(
        "Ist das vegan? Der Lebensmittel-Checker | This Is Vegan",
        f"Lebensmittel eingeben und sofort sehen, ob es vegan ist, von Wein über Brot bis Gummibärchen. {len(foods)} Produkte mit den versteckten Fallen. Kostenlos.",
        FOOD_BASE,
        body,
        jsonld,
    )


def build_food_detail(f, meta, foods):
    name = f["name"]
    s = f["slug"]
    status = f["status"]
    path = FOOD_BASE + s + "/"
    L = FOOD_LABEL[status]
    note_html = ""
    if f.get("note"):
        note_html = f'<div class="note"><span>!</span><span><b>Achte drauf:</b> {esc(f["note"])}</span></div>'

    related = [x for x in foods if x["category"] == f["category"] and x["slug"] != s][:6]
    if len(related) < 4:
        related += [x for x in foods if x["slug"] != s and x not in related][: 4 - len(related)]
    rel_html = "\n".join(
        f'    <a class="item {r["status"]}" href="{url(FOOD_BASE + r["slug"] + "/")}">'
        f'<span class="bar"></span><div><div class="en">{esc(r["name"])}</div>'
        f'<div class="nm">{esc(r["category"])}</div></div></a>'
        for r in related
    )

    verdict_long = {
        "yes": f"{name} ist in der Regel vegan. Du kannst meist ohne langes Prüfen zugreifen, ein kurzer Blick auf die Zutatenliste schadet bei verarbeiteten Produkten trotzdem nie.",
        "maybe": f"Ob {name} vegan ist, hängt vom Produkt ab. Es gibt vegane und nicht vegane Varianten, und die Herkunft steht nicht immer offensichtlich auf der Packung. Im Zweifel hilft das Vegan-Siegel.",
        "no": f"{name} ist in der klassischen Form nicht vegan. Die gute Nachricht: Für fast alles gibt es heute eine pflanzliche Alternative, oft direkt daneben im Regal.",
    }[status]

    body = site_header("Ist das vegan?") + f"""
<nav class="crumbs" aria-label="Breadcrumb"><a href="{url('/')}">Tools</a><span>›</span><a href="{url(FOOD_BASE)}">Ist das vegan?</a><span>›</span>{esc(name)}</nav>
<section class="hero left">
  <div class="eyebrow">{esc(f["category"])} · Vegan-Check</div>
  <h1 class="detail">Ist {esc(name)} <span class="q">vegan?</span></h1>
</section>

<div id="result" style="margin:24px 0 0;max-width:620px">
  <div class="card" style="animation:none">
    <div class="verdict {status}">
      <div class="mark">{L["icon"]}</div>
      <div class="vtext">{L["t"]}<small>{L["s"]}</small></div>
    </div>
    <div class="card-body">
      <div class="enum">{esc(name)}</div>
      <span class="klasse">{esc(f["category"])}</span>
      <p class="info">{esc(f["info"])}</p>
      {note_html}
    </div>
  </div>
</div>

<section class="section">
  <h2>Was heißt das für dich?</h2>
  <p class="prose">{esc(verdict_long)}</p>
</section>

<section class="section">
  <h2>Ähnliche Lebensmittel</h2>
  <div class="related">
{rel_html}
  </div>
</section>

<div class="cta">
  <div>
    <h2>Noch was prüfen?</h2>
    <p>Der Checker kennt {len(foods)} Lebensmittel und zeigt dir sofort, ob etwas vegan ist.</p>
  </div>
  <a class="btn" href="{url(FOOD_BASE)}">Zum Checker →</a>
</div>
""" + site_footer(meta)

    answer = f"{L['t']}. {f['info']}"
    if f.get("note"):
        answer += f" {f['note']}"
    jsonld = [
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": f"Ist {name} vegan?",
                 "acceptedAnswer": {"@type": "Answer", "text": answer}},
            ],
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Tools", "item": BASE_URL + url("/")},
                {"@type": "ListItem", "position": 2, "name": "Ist das vegan?", "item": BASE_URL + url(FOOD_BASE)},
                {"@type": "ListItem", "position": 3, "name": name, "item": BASE_URL + url(path)},
            ],
        },
    ]
    lead = {"yes": f"{name} ist in der Regel vegan.", "maybe": f"{name} ist nicht immer vegan.", "no": f"{name} ist meist nicht vegan."}[status]
    desc = f"{lead} {f['info']} Status, Erklärung und Fallen im Vegan-Checker von This Is Vegan."
    if len(desc) > 155:
        desc = f"{lead} {f['info']}"
        if len(desc) > 155:
            desc = desc[:152].rstrip() + "..."
    return page(f"Ist {name} vegan? | This Is Vegan", desc, path, body, jsonld, og_type="article")


IMPACT_BASE = "/impact-rechner/"


def build_impact(meta):
    js = IMPACT_JS.replace("__DATA__", json.dumps(meta["per_day"], ensure_ascii=False, separators=(",", ":")))
    body = site_header("Impact-Rechner") + f"""
<nav class="crumbs" aria-label="Breadcrumb"><a href="{url('/')}">Tools</a><span>›</span>Impact-Rechner</nav>
<section class="hero">
  <div class="eyebrow">Zahlen, die motivieren</div>
  <h1>Was du wirklich <span class="q">bewegst.</span></h1>
  <p class="sub">Gib ein, wie lange du schon vegan lebst, und sieh, was das für Tiere, Klima, Wasser und Ackerland bedeutet.</p>

  <div class="iunit">
    <input id="amt" type="number" value="1" min="1" max="99999" inputmode="numeric" aria-label="Zeitraum">
    <div class="seg">
      <button type="button" data-unit="day">Tage</button>
      <button type="button" data-unit="month">Monate</button>
      <button type="button" data-unit="year" class="on">Jahre</button>
    </div>
  </div>

  <div class="stats" id="stats"></div>
  <div class="infobox" style="margin-left:auto;margin-right:auto"><b>So rechnen wir:</b> {esc(meta["methodik"])}</div>
</section>

<section class="section">
  <h2>Warum jeder Tag zählt</h2>
  <p class="prose">Diese Zahlen sind keine Abrechnung, sondern eine Erinnerung. Jede Mahlzeit ohne tierische Produkte senkt die Nachfrage, und Nachfrage ist am Ende das Einzige, worauf die Lebensmittelindustrie reagiert. Du musst nicht perfekt sein, damit sich etwas bewegt.</p>
  <p class="prose">Teil dein Ergebnis mit Leuten, die noch zögern. Konkrete Zahlen überzeugen oft mehr als jedes Argument.</p>
</section>

<section class="section">
  <h2>Mehr von This Is Vegan</h2>
  <div class="linklist">
""" + "\n".join(
        f'    <a href="{href}">{esc(t)}<span class="arrow">→</span></a>' for t, href in READ_MORE
    ) + f"""
  </div>
</section>
""" + site_footer(meta, full_disclaimer=False) + f"\n<script>{js}</script>"

    jsonld = [
        {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": "Veganer Impact-Rechner",
            "url": BASE_URL + url(IMPACT_BASE),
            "applicationCategory": "LifestyleApplication",
            "operatingSystem": "Web",
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
            "description": "Zeigt, wie viele Tiere, wie viel CO2, Wasser und Ackerland eine vegane Ernährung über einen Zeitraum spart.",
            "publisher": {"@type": "Organization", "name": "This Is Vegan", "url": MAIN_SITE},
        },
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": "Wie viele Tiere rettet man als Veganer?",
                 "acceptedAnswer": {"@type": "Answer", "text": "Konservativ geschätzt rund 100 Tiere pro Jahr, der größte Teil davon Fische und Meerestiere. Die Zahl beruht auf vermiedener Nachfrage und schwankt je nach Quelle zwischen etwa 30 und über 400."}},
                {"@type": "Question", "name": "Wie viel CO2 spart eine vegane Ernährung?",
                 "acceptedAnswer": {"@type": "Answer", "text": "Im Vergleich zu einer durchschnittlichen Ernährung rund 2,5 kg CO2-Äquivalent pro Tag, also etwa 0,9 Tonnen im Jahr. Studien zur Ernährungs-Ökobilanz nennen je nach Annahmen unterschiedliche Werte."}},
            ],
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Tools", "item": BASE_URL + url("/")},
                {"@type": "ListItem", "position": 2, "name": "Impact-Rechner", "item": BASE_URL + url(IMPACT_BASE)},
            ],
        },
    ]
    return page(
        "Veganer Impact-Rechner: Tiere, CO2 und Wasser, die du sparst | This Is Vegan",
        "Sieh, wie viele Tiere, wie viel CO2, Wasser und Ackerland deine vegane Ernährung spart. Zeitraum eingeben, sofort dein persönliches Ergebnis sehen. Kostenlos.",
        IMPACT_BASE,
        body,
        jsonld,
    )


SAISON_BASE = "/saisonkalender/"
MONTHS = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
MONTH_SLUGS = ["januar", "februar", "maerz", "april", "mai", "juni", "juli", "august", "september", "oktober", "november", "dezember"]
MONTH_ABBR = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]


def _produce_cards(items, m):
    if not items:
        return '<div class="empty" style="display:block">In diesem Monat ist regional nichts dabei.</div>'
    out = []
    for d in items:
        lager = m not in d["f"] and m in d["l"]
        cls = "maybe" if lager else "yes"
        label = "aus dem Lager" if lager else "Freiland"
        out.append(
            f'    <div class="item {cls}"><span class="bar"></span><div>'
            f'<div class="en">{esc(d["name"])}</div><div class="nm">{label}</div></div></div>'
        )
    return "\n".join(out)


def build_saison_hub(meta, produce):
    compact = [{"name": p["name"], "type": p["type"], "f": p["f"], "l": p["l"]} for p in produce]
    js = SAISON_JS.replace("__DATA__", json.dumps(compact, ensure_ascii=False, separators=(",", ":")))
    month_btns = "\n".join(
        f'    <button type="button" data-m="{i+1}">{MONTH_ABBR[i]}</button>' for i in range(12)
    )
    month_links = "\n".join(
        f'    <a href="{url(SAISON_BASE + MONTH_SLUGS[i] + "/")}">{MONTHS[i]}<span class="arrow">→</span></a>'
        for i in range(12)
    )

    body = site_header("Saisonkalender") + f"""
<nav class="crumbs" aria-label="Breadcrumb"><a href="{url('/')}">Tools</a><span>›</span>Saisonkalender</nav>
<section class="hero">
  <div class="eyebrow">Regional und im richtigen Moment</div>
  <h1>Was hat gerade <span class="q">Saison?</span></h1>
  <p class="sub">Monat wählen und sehen, welches Obst und Gemüse regional gerade frisch vom Feld kommt oder aus dem Lager verfügbar ist.</p>
  <div class="months">
{month_btns}
  </div>
</section>

<section class="listsec">
  <h2 id="motitle">Saison</h2>
  <div class="subhead"><span class="swatch"></span>Gemüse</div>
  <div class="grid" id="gem"></div>
  <div class="subhead"><span class="swatch" style="background:var(--terra)"></span>Obst</div>
  <div class="grid" id="obs"></div>
  <div class="infobox">{esc(meta["disclaimer"])}</div>
</section>

<section class="section">
  <h2>Alle Monate</h2>
  <p class="lead">Jeder Monat hat seine eigene Saison-Seite mit allem, was frisch ist.</p>
  <div class="linklist" style="grid-template-columns:repeat(auto-fit,minmax(160px,1fr));display:grid">
{month_links}
  </div>
</section>
""" + site_footer(meta, full_disclaimer=False) + f"\n<script>{js}</script>"

    jsonld = [
        {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": "Vegan-Saisonkalender",
            "url": BASE_URL + url(SAISON_BASE),
            "applicationCategory": "LifestyleApplication",
            "operatingSystem": "Web",
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
            "description": "Saisonkalender für regionales Obst und Gemüse in Deutschland, Monat für Monat, mit Freiland- und Lagerware.",
            "publisher": {"@type": "Organization", "name": "This Is Vegan", "url": MAIN_SITE},
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Tools", "item": BASE_URL + url("/")},
                {"@type": "ListItem", "position": 2, "name": "Saisonkalender", "item": BASE_URL + url(SAISON_BASE)},
            ],
        },
    ]
    return page(
        "Vegan-Saisonkalender: was hat gerade Saison? | This Is Vegan",
        "Monat wählen und sehen, welches Obst und Gemüse regional gerade Saison hat, frisch vom Feld oder aus dem Lager. Kostenloser Saisonkalender für Deutschland.",
        SAISON_BASE,
        body,
        jsonld,
    )


def build_saison_month(idx, meta, produce):
    m = idx + 1
    month = MONTHS[idx]
    path = SAISON_BASE + MONTH_SLUGS[idx] + "/"
    in_season = [p for p in produce if m in p["f"] or m in p["l"]]
    gem = [p for p in in_season if p["type"] == "gemuese"]
    obs = [p for p in in_season if p["type"] == "obst"]

    prev_i, next_i = (idx - 1) % 12, (idx + 1) % 12
    names = ", ".join(p["name"] for p in in_season[:8])

    body = site_header("Saisonkalender") + f"""
<nav class="crumbs" aria-label="Breadcrumb"><a href="{url('/')}">Tools</a><span>›</span><a href="{url(SAISON_BASE)}">Saisonkalender</a><span>›</span>{month}</nav>
<section class="hero left">
  <div class="eyebrow">Saisonkalender</div>
  <h1 class="detail">Saison im <span class="q">{month}</span></h1>
  <p class="sub" style="margin-left:0">Diese {len(in_season)} Obst- und Gemüsesorten haben im {month} in Deutschland regional Saison, frisch vom Feld oder aus heimischer Lagerung.</p>
</section>

<section class="section">
  <div class="subhead"><span class="swatch"></span>Gemüse</div>
  <div class="grid">
{_produce_cards(gem, m)}
  </div>
</section>

<section class="section">
  <div class="subhead"><span class="swatch" style="background:var(--terra)"></span>Obst</div>
  <div class="grid">
{_produce_cards(obs, m)}
  </div>
</section>

<div class="cta">
  <div>
    <h2>Anderer Monat?</h2>
    <p>Im interaktiven Kalender springst du mit einem Klick durch das ganze Jahr.</p>
  </div>
  <a class="btn" href="{url(SAISON_BASE)}">Zum Kalender →</a>
</div>

<section class="section">
  <h2>Weiter im Jahr</h2>
  <div class="linklist">
    <a href="{url(SAISON_BASE + MONTH_SLUGS[prev_i] + "/")}"><span class="arrow" style="transform:rotate(180deg)">→</span>{MONTHS[prev_i]}</a>
    <a href="{url(SAISON_BASE + MONTH_SLUGS[next_i] + "/")}">{MONTHS[next_i]}<span class="arrow">→</span></a>
  </div>
</section>
""" + site_footer(meta, full_disclaimer=False)

    jsonld = [
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": f"Welches Obst und Gemüse hat im {month} Saison?",
                 "acceptedAnswer": {"@type": "Answer", "text": f"Im {month} haben unter anderem {names} regional Saison. Insgesamt sind es {len(in_season)} Sorten, frisch vom Feld oder aus dem Lager."}},
            ],
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Tools", "item": BASE_URL + url("/")},
                {"@type": "ListItem", "position": 2, "name": "Saisonkalender", "item": BASE_URL + url(SAISON_BASE)},
                {"@type": "ListItem", "position": 3, "name": month, "item": BASE_URL + url(path)},
            ],
        },
    ]
    return page(
        f"Saisonkalender {month}: Obst und Gemüse mit Saison | This Is Vegan",
        f"Welches Obst und Gemüse hat im {month} Saison? {len(in_season)} regionale Sorten frisch vom Feld oder aus dem Lager, im veganen Saisonkalender von This Is Vegan.",
        path,
        body,
        jsonld,
        og_type="article",
    )


PFLANZ_BASE = "/pflanzendrink-vergleich/"
RATING_LABEL = {3: "top geeignet", 2: "gut geeignet", 1: "weniger geeignet"}


def build_drink_hub(meta, drinks, usecases):
    compact = [
        {"name": d["name"], "protein": d["protein"], "kcal": d["kcal"], "barista": d["barista"],
         "reason": d["reason"], "r": d["r"], "u": url(PFLANZ_BASE + d["slug"] + "/")}
        for d in drinks
    ]
    js = PFLANZ_JS.replace("__DATA__", json.dumps(compact, ensure_ascii=False, separators=(",", ":")))
    js = js.replace("__UC__", json.dumps(usecases, ensure_ascii=False, separators=(",", ":")))
    uc_btn_list = []
    for u in usecases:
        on = ' class="on"' if u["key"] == "kaffee" else ""
        uc_btn_list.append(f'    <button type="button" data-uc="{u["key"]}"{on}>{esc(u["label"])}</button>')
    uc_btns = "\n".join(uc_btn_list)
    detail_links = "\n".join(
        f'    <a href="{url(PFLANZ_BASE + d["slug"] + "/")}">{esc(d["name"])}<span class="arrow">→</span></a>'
        for d in sorted(drinks, key=lambda x: x["name"].lower())
    )

    body = site_header("Pflanzendrink-Vergleich") + f"""
<nav class="crumbs" aria-label="Breadcrumb"><a href="{url('/')}">Tools</a><span>›</span>Pflanzendrink-Vergleich</nav>
<section class="hero">
  <div class="eyebrow">Hafer, Soja, Mandel und Co.</div>
  <h1>Welcher Drink <span class="q">wofür?</span></h1>
  <p class="sub">Sag, wofür du den Pflanzendrink brauchst, und sieh, welcher am besten passt, mit Nährwerten und Klimabilanz.</p>
  <div class="months" role="group" aria-label="Einsatzzweck wählen">
{uc_btns}
  </div>
  <p class="sub" id="uchint" style="margin-top:14px;font-size:15px;opacity:.7"></p>
</section>

<section class="listsec">
  <div class="subs" id="drinkout" style="max-width:680px;margin:0 auto"></div>
  <div class="infobox" style="margin-left:auto;margin-right:auto">{esc(meta["disclaimer"])}</div>
</section>

<section class="section">
  <h2>Alle Drinks im Einzelporträt</h2>
  <div class="linklist" style="grid-template-columns:repeat(auto-fit,minmax(160px,1fr));display:grid">
{detail_links}
  </div>
</section>
""" + site_footer(meta, full_disclaimer=False) + f"\n<script>{js}</script>"

    jsonld = [
        {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": "Pflanzendrink-Vergleich",
            "url": BASE_URL + url(PFLANZ_BASE),
            "applicationCategory": "LifestyleApplication",
            "operatingSystem": "Web",
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
            "description": "Vergleicht Hafer-, Soja-, Mandel- und weitere Pflanzendrinks nach Einsatzzweck, Nährwerten und Klimabilanz.",
            "publisher": {"@type": "Organization", "name": "This Is Vegan", "url": MAIN_SITE},
        },
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": "Welche Pflanzenmilch eignet sich am besten für Kaffee?",
                 "acceptedAnswer": {"@type": "Answer", "text": "Haferdrink in der Barista-Variante schäumt am besten und gerinnt im Kaffee nicht. Auch Soja- und Erbsendrink mit Barista-Zusatz funktionieren gut."}},
                {"@type": "Question", "name": "Welcher Pflanzendrink hat am meisten Protein?",
                 "acceptedAnswer": {"@type": "Answer", "text": "Sojadrink liegt mit rund 3,3 g pro 100 ml vorn, gefolgt von Erbsendrink mit etwa 2 g. Nuss- und Reisdrinks enthalten dagegen kaum Protein."}},
            ],
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Tools", "item": BASE_URL + url("/")},
                {"@type": "ListItem", "position": 2, "name": "Pflanzendrink-Vergleich", "item": BASE_URL + url(PFLANZ_BASE)},
            ],
        },
    ]
    return page(
        "Pflanzendrink-Vergleich: welche Pflanzenmilch wofür? | This Is Vegan",
        "Hafer, Soja, Mandel und Co. im Vergleich: welcher Pflanzendrink für Kaffee, Backen, Protein oder Klima am besten passt. Mit Nährwerten. Kostenlos.",
        PFLANZ_BASE,
        body,
        jsonld,
    )


def build_drink_detail(d, meta, drinks, usecases):
    name = d["name"]
    s = d["slug"]
    path = PFLANZ_BASE + s + "/"
    rating_html = "\n".join(
        f'    <div class="usecard"><b>{esc(u["label"])}</b><span>{RATING_LABEL[d["r"][u["key"]]]}</span></div>'
        for u in usecases
    )
    related = [x for x in drinks if x["slug"] != s][:6]
    rel_html = "\n".join(
        f'    <a class="item yes" href="{url(PFLANZ_BASE + r["slug"] + "/")}">'
        f'<span class="bar"></span><div><div class="en">{esc(r["name"])}</div>'
        f'<div class="nm">{r["protein"]} g Protein · {r["kcal"]} kcal</div></div></a>'
        for r in related
    )
    barista = "Ja, in der Barista-Variante" if d["barista"] else "Eher nicht, schäumt schwach"

    body = site_header("Pflanzendrink-Vergleich") + f"""
<nav class="crumbs" aria-label="Breadcrumb"><a href="{url('/')}">Tools</a><span>›</span><a href="{url(PFLANZ_BASE)}">Pflanzendrink-Vergleich</a><span>›</span>{esc(name)}</nav>
<section class="hero left">
  <div class="eyebrow">Im Pflanzendrink-Check</div>
  <h1 class="detail">{esc(name)} <span class="q">im Check</span></h1>
  <p class="sub" style="margin-left:0">{esc(d["reason"])}</p>
</section>

<section class="section">
  <h2>Nährwerte pro 100 ml</h2>
  <div class="usecards">
    <div class="usecard"><b>{d["protein"]} g</b><span>Protein</span></div>
    <div class="usecard"><b>{d["kcal"]} kcal</b><span>Energie</span></div>
    <div class="usecard"><b>Kaffee</b><span>{esc(barista)}</span></div>
  </div>
</section>

<section class="section">
  <h2>Wofür eignet sich {esc(name)}?</h2>
  <div class="usecards">
{rating_html}
  </div>
</section>

<section class="section">
  <h2>Klima und Anbau</h2>
  <p class="prose">{esc(d["eco"])}</p>
</section>

<section class="section">
  <h2>Andere Drinks</h2>
  <div class="related">
{rel_html}
  </div>
</section>

<div class="cta">
  <div>
    <h2>Den passenden Drink finden?</h2>
    <p>Im Vergleich siehst du je nach Einsatzzweck die beste Wahl.</p>
  </div>
  <a class="btn" href="{url(PFLANZ_BASE)}">Zum Vergleich →</a>
</div>
""" + site_footer(meta, full_disclaimer=False)

    best = max(usecases, key=lambda u: d["r"][u["key"]])
    answer = f"{d['reason']} Besonders gut eignet sich {name} {best['label'].lower()}. Pro 100 ml stecken rund {d['protein']} g Protein und {d['kcal']} kcal drin."
    jsonld = [
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": f"Wofür eignet sich {name}?",
                 "acceptedAnswer": {"@type": "Answer", "text": answer}},
            ],
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Tools", "item": BASE_URL + url("/")},
                {"@type": "ListItem", "position": 2, "name": "Pflanzendrink-Vergleich", "item": BASE_URL + url(PFLANZ_BASE)},
                {"@type": "ListItem", "position": 3, "name": name, "item": BASE_URL + url(path)},
            ],
        },
    ]
    return page(
        f"{name} im Check: Nährwerte, Eignung, Klima | This Is Vegan",
        f"{name} im Vergleich: Nährwerte, wofür er sich eignet und wie die Klimabilanz ist. {d['protein']} g Protein und {d['kcal']} kcal pro 100 ml.",
        path,
        body,
        jsonld,
        og_type="article",
    )


PROT_BASE = "/protein-tabelle/"


def _prot_num(p):
    return str(int(p)) if float(p) == int(p) else str(p)


def build_protein(meta, foods, categories):
    compact = [{"n": f["name"], "c": f["category"], "p": f["protein"]} for f in foods]
    js = PROT_JS.replace("__DATA__", json.dumps(compact, ensure_ascii=False, separators=(",", ":")))

    ranked = sorted(foods, key=lambda f: -f["protein"])
    top_names = {f["name"] for f in ranked[:3]}
    rows = "\n".join(
        f'    <div class="prow{" top" if f["name"] in top_names else ""}">'
        f'<div><div class="pname">{esc(f["name"])}</div><div class="pcat">{esc(f["category"])}</div></div>'
        f'<div class="pval">{_prot_num(f["protein"])}<small> g/100g</small></div></div>'
        for f in ranked
    )
    cat_chips = '    <button class="filt active" data-cat="all">Alle</button>\n' + "\n".join(
        f'    <button class="filt" data-cat="{esc(c)}">{esc(c)}</button>' for c in categories
    )

    body = site_header("Protein-Tabelle") + f"""
<nav class="crumbs" aria-label="Breadcrumb"><a href="{url('/')}">Tools</a><span>›</span>Protein-Tabelle</nav>
<section class="hero">
  <div class="eyebrow">Eiweiß ohne Tier</div>
  <h1>Wo steckt das <span class="q">Protein?</span></h1>
  <p class="sub">Die proteinreichsten pflanzlichen Lebensmittel auf einen Blick, durchsuchbar und sortierbar, mit Eiweiß pro 100 Gramm.</p>

  <div class="search-shell">
    <div class="search-box">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"></circle><path d="M21 21l-4.3-4.3"></path></svg>
      <input id="pq" type="text" autocomplete="off" placeholder="z. B. Tofu, Linsen oder Haferflocken" aria-label="Lebensmittel suchen">
    </div>
  </div>

  <div class="psort">
    <div class="seg">
      <button type="button" data-sort="protein" class="on">Nach Protein</button>
      <button type="button" data-sort="name">A bis Z</button>
    </div>
  </div>
</section>

<section class="listsec">
  <div class="filters" id="filters" style="justify-content:center;margin-bottom:8px">
{cat_chips}
  </div>
  <div class="ptable" id="ptable">
{rows}
  </div>
  <div class="infobox" style="margin-left:auto;margin-right:auto">{esc(meta["disclaimer"])}</div>
</section>

<section class="section">
  <h2>Wie viel Protein brauchst du?</h2>
  <p class="prose">Je nach Aktivität rund 0,8 bis 1,6 g pro Kilo Körpergewicht. Wie viel genau für dich, rechnet dir der <a href="{url(NAEHR_BASE + "protein/")}" style="color:var(--green);font-weight:700;text-decoration:none">Nährstoff-Rechner</a> aus. Tipp: Kombiniere über den Tag verschiedene Quellen, dann passt auch das Aminosäureprofil.</p>
</section>
""" + site_footer(meta, full_disclaimer=False) + f"\n<script>{js}</script>"

    jsonld = [
        {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": "Vegane Protein-Tabelle",
            "url": BASE_URL + url(PROT_BASE),
            "applicationCategory": "HealthApplication",
            "operatingSystem": "Web",
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
            "description": f"Durchsuchbare Tabelle der {len(foods)} proteinreichsten pflanzlichen Lebensmittel mit Eiweiß pro 100 Gramm.",
            "publisher": {"@type": "Organization", "name": "This Is Vegan", "url": MAIN_SITE},
        },
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": "Welche veganen Lebensmittel haben am meisten Protein?",
                 "acceptedAnswer": {"@type": "Answer", "text": f"Ganz vorn liegen {ranked[0]['name']}, {ranked[1]['name']} und {ranked[2]['name']}. Unter den Grundnahrungsmitteln sind Tofu, Tempeh, Hülsenfrüchte und Haferflocken die stärksten Proteinquellen."}},
                {"@type": "Question", "name": "Wie viel Protein hat Tofu?",
                 "acceptedAnswer": {"@type": "Answer", "text": "Tofu natur liefert rund 12 g Protein pro 100 g, Räuchertofu etwa 16 g und Tempeh sogar rund 19 g."}},
            ],
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Tools", "item": BASE_URL + url("/")},
                {"@type": "ListItem", "position": 2, "name": "Protein-Tabelle", "item": BASE_URL + url(PROT_BASE)},
            ],
        },
    ]
    return page(
        "Vegane Protein-Tabelle: die eiweißreichsten Lebensmittel | This Is Vegan",
        f"Die {len(foods)} proteinreichsten pflanzlichen Lebensmittel, durchsuchbar und sortierbar, mit Eiweiß pro 100 g. Von Tofu über Linsen bis Hanfsamen. Kostenlos.",
        PROT_BASE,
        body,
        jsonld,
    )


CO2_BASE = "/co2-fussabdruck/"


def build_co2(meta, foods):
    compact = [{"n": f["name"], "t": f["category"], "co2": f["co2"]} for f in foods]
    js = CO2_JS.replace("__DATA__", json.dumps(compact, ensure_ascii=False, separators=(",", ":")))
    ranked = sorted(foods, key=lambda f: -f["co2"])
    rows = "\n".join(
        f'    <div class="prow {"tier" if f["category"] == "Tierisch" else "pflanz"}">'
        f'<div><div class="pname">{esc(f["name"])}</div><div class="pcat">{esc(f["category"])}</div></div>'
        f'<div class="pval">{_prot_num(f["co2"])}<small> kg CO2</small></div></div>'
        for f in ranked
    )
    cat_chips = (
        '    <button class="filt active" data-cat="all">Alle</button>\n'
        '    <button class="filt" data-cat="Tierisch">Tierisch</button>\n'
        '    <button class="filt" data-cat="Pflanzlich">Pflanzlich</button>'
    )

    body = site_header("CO2-Fußabdruck") + f"""
<nav class="crumbs" aria-label="Breadcrumb"><a href="{url('/')}">Tools</a><span>›</span>CO2-Fußabdruck</nav>
<section class="hero">
  <div class="eyebrow">Klimabilanz auf dem Teller</div>
  <h1>Wie viel CO2 steckt im <span class="q">Essen?</span></h1>
  <p class="sub">Der CO2-Fußabdruck von Lebensmitteln im direkten Vergleich. 1 kg Rindfleisch verursacht rund 99 kg CO2, so viel wie etwa 800 km mit dem Auto. 1 kg Linsen: unter 1 kg.</p>

  <div class="search-shell">
    <div class="search-box">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"></circle><path d="M21 21l-4.3-4.3"></path></svg>
      <input id="pq" type="text" autocomplete="off" placeholder="z. B. Rindfleisch, Käse oder Tofu" aria-label="Lebensmittel suchen">
    </div>
  </div>

  <div class="psort">
    <div class="seg">
      <button type="button" data-sort="desc" class="on">Größter Fußabdruck</button>
      <button type="button" data-sort="asc">Kleinster Fußabdruck</button>
    </div>
  </div>
</section>

<section class="listsec">
  <div class="filters" id="filters" style="justify-content:center;margin-bottom:8px">
{cat_chips}
  </div>
  <div class="ptable" id="ptable">
{rows}
  </div>
  <div class="infobox" style="margin-left:auto;margin-right:auto"><b>So rechnen wir:</b> {esc(meta["methodik"])}</div>
</section>

<section class="section">
  <h2>Warum die Unterschiede so groß sind</h2>
  <p class="prose">Tierische Lebensmittel verursachen pro Kilo fast immer ein Vielfaches der Emissionen pflanzlicher. Der Grund: Tiere müssen erst mit Pflanzen gefüttert werden, dabei geht ein Großteil der Energie verloren, dazu kommen Methan aus der Verdauung und Flächen, die für Weide und Futteranbau gerodet werden. Pflanzen direkt zu essen spart diesen Umweg.</p>
  <p class="prose">Sieh dir auch den <a href="{url(IMPACT_BASE)}" style="color:var(--green);font-weight:700;text-decoration:none">Impact-Rechner</a> an, der hochrechnet, was deine Ernährung übers Jahr spart.</p>
</section>
""" + site_footer(meta, full_disclaimer=False) + f"\n<script>{js}</script>"

    jsonld = [
        {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": "CO2-Fußabdruck von Lebensmitteln",
            "url": BASE_URL + url(CO2_BASE),
            "applicationCategory": "LifestyleApplication",
            "operatingSystem": "Web",
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
            "description": f"Vergleicht den CO2-Fußabdruck von {len(foods)} Lebensmitteln, tierisch und pflanzlich, in kg CO2 pro kg.",
            "publisher": {"@type": "Organization", "name": "This Is Vegan", "url": MAIN_SITE},
        },
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": "Welches Lebensmittel hat den größten CO2-Fußabdruck?",
                 "acceptedAnswer": {"@type": "Answer", "text": "Rindfleisch liegt mit rund 99 kg CO2 pro kg klar an der Spitze, gefolgt von Lammfleisch und Käse. Pflanzliche Lebensmittel liegen fast alle unter 5 kg pro kg."}},
                {"@type": "Question", "name": "Wie viel CO2 spart eine pflanzliche Ernährung?",
                 "acceptedAnswer": {"@type": "Answer", "text": "Pflanzliche Lebensmittel verursachen pro Kilo meist ein Vielfaches weniger als tierische. Studien zeigen für pflanzliche Alternativen zu Rindfleisch rund 77 Prozent weniger Klimalast."}},
            ],
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Tools", "item": BASE_URL + url("/")},
                {"@type": "ListItem", "position": 2, "name": "CO2-Fußabdruck", "item": BASE_URL + url(CO2_BASE)},
            ],
        },
    ]
    return page(
        "CO2-Fußabdruck von Lebensmitteln: die Klima-Tabelle | This Is Vegan",
        "Der CO2-Fußabdruck von Lebensmitteln im Vergleich, tierisch gegen pflanzlich, in kg CO2 pro kg. Durchsuchbar und sortierbar, auf Basis großer Ökobilanz-Daten.",
        CO2_BASE,
        body,
        jsonld,
    )


MEAL_BASE = "/protein-pro-mahlzeit/"


def build_meal(meta, foods):
    sorted_foods = sorted(foods, key=lambda f: f["name"].lower())
    compact = [{"n": f["name"], "p": f["protein"]} for f in sorted_foods]
    js = MEAL_JS.replace("__DATA__", json.dumps(compact, ensure_ascii=False, separators=(",", ":")))
    options = "\n".join(
        f'          <option value="{esc(f["name"])}">{esc(f["name"])} ({_prot_num(f["protein"])} g/100g)</option>'
        for f in sorted_foods
    )

    body = site_header("Protein pro Mahlzeit") + f"""
<nav class="crumbs" aria-label="Breadcrumb"><a href="{url('/')}">Tools</a><span>›</span>Protein pro Mahlzeit</nav>
<section class="hero">
  <div class="eyebrow">Eiweiß zusammenrechnen</div>
  <h1>Wie viel Protein hat deine <span class="q">Mahlzeit?</span></h1>
  <p class="sub">Stell deine Mahlzeit aus pflanzlichen Lebensmitteln zusammen und sieh sofort, wie viel Protein zusammenkommt.</p>

  <div class="calc">
    <div class="calc-grid">
      <div class="field">
        <label for="foodsel">Lebensmittel</label>
        <select id="foodsel" aria-label="Lebensmittel wählen">
{options}
        </select>
      </div>
      <div class="field">
        <label for="grams">Menge in Gramm</label>
        <input id="grams" type="number" value="100" min="1" max="2000" inputmode="numeric" aria-label="Menge in Gramm">
      </div>
    </div>
    <button type="button" class="addbtn" id="addbtn">Zur Mahlzeit hinzufügen</button>
    <div class="field" style="margin-top:4px">
      <label for="target">Dein Tagesziel in Gramm</label>
      <input id="target" type="number" value="60" min="20" max="300" inputmode="numeric" aria-label="Tagesziel in Gramm Protein">
    </div>
  </div>

  <div class="mealsum">
    <div class="big" id="mealbig">0 g Protein</div>
    <div class="pct" id="mealpct"></div>
  </div>
  <div class="ptable" id="mealitems" style="margin-top:14px"></div>
</section>

<section class="section">
  <h2>So holst du genug Protein raus</h2>
  <p class="prose">Kombiniere zu jeder Mahlzeit eine kräftige Eiweißquelle wie Tofu, Tempeh, Hülsenfrüchte oder Seitan mit Getreide. Wie viel du am Tag brauchst, rechnet dir der <a href="{url(NAEHR_BASE + "protein/")}" style="color:var(--green);font-weight:700;text-decoration:none">Nährstoff-Rechner</a> aus, welche Lebensmittel am meisten liefern, zeigt die <a href="{url(PROT_BASE)}" style="color:var(--green);font-weight:700;text-decoration:none">Protein-Tabelle</a>.</p>
</section>
""" + site_footer(meta, full_disclaimer=False) + f"\n<script>{js}</script>"

    jsonld = [
        {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": "Protein-pro-Mahlzeit-Rechner",
            "url": BASE_URL + url(MEAL_BASE),
            "applicationCategory": "HealthApplication",
            "operatingSystem": "Web",
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
            "description": "Stellt eine Mahlzeit aus pflanzlichen Lebensmitteln zusammen und berechnet den Proteingehalt pro Portion.",
            "publisher": {"@type": "Organization", "name": "This Is Vegan", "url": MAIN_SITE},
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Tools", "item": BASE_URL + url("/")},
                {"@type": "ListItem", "position": 2, "name": "Protein pro Mahlzeit", "item": BASE_URL + url(MEAL_BASE)},
            ],
        },
    ]
    return page(
        "Protein-Rechner: wie viel Eiweiß hat deine Mahlzeit? | This Is Vegan",
        "Stell deine vegane Mahlzeit zusammen und berechne den Proteingehalt pro Portion, mit Gramm-genauen Werten. Kostenlos, ohne Anmeldung.",
        MEAL_BASE,
        body,
        jsonld,
    )


CREATOR_BASE = "/creator/"
FONT_BASE = "/creator/schriftarten/"
CREATOR_META = {"lastUpdated": "2026-06-13"}


def build_creator_hub(meta):
    body = site_header("Für Creator", "Gratis · ohne Anmeldung") + f"""
<nav class="crumbs" aria-label="Breadcrumb"><a href="{url('/')}">Tools</a><span>›</span>Für Content Creator</nav>
<section class="hero left">
  <div class="eyebrow">Tools für vegane Accounts</div>
  <h1>Mehr Reichweite, <span class="q">weniger Reibung.</span></h1>
  <p class="sub">Kleine Helfer für vegane, Tierschutz- und Food-Accounts auf Instagram, TikTok und Co. Mehr Kreativität in Bio, Caption und Story, in Sekunden.</p>
</section>

<section class="section">
  <div class="toolcards">
    <a class="toolcard" href="{url(FONT_BASE)}">
      <span class="badge">Live</span>
      <h3>Schriftarten-Generator</h3>
      <p>Text eingeben und in 18 Stilen kopieren: fett, kursiv, Schreibschrift, durchgestrichen, kopfüber und mehr, plus vegane Deko und Trenner für Bio und Caption.</p>
      <span class="meta">Schrift stylen →</span>
    </a>
    <div class="toolcard soon">
      <span class="badge">In Arbeit</span>
      <h3>Mehr Creator-Tools</h3>
      <p>Hashtag-Helfer, Caption-Ideen, Best-Time-Planer und mehr. Sag uns, was dir den Account-Alltag leichter machen würde.</p>
      <span class="meta">Bald verfügbar</span>
    </div>
  </div>
</section>
""" + site_footer(meta, full_disclaimer=False)

    jsonld = [
        {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": "Tools für vegane Content Creator",
            "description": "Kostenlose Tools für vegane, Tierschutz- und Food-Accounts auf Social Media.",
            "url": BASE_URL + url(CREATOR_BASE),
            "isPartOf": {"@type": "WebSite", "name": "This Is Vegan", "url": MAIN_SITE},
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Tools", "item": BASE_URL + url("/")},
                {"@type": "ListItem", "position": 2, "name": "Für Content Creator", "item": BASE_URL + url(CREATOR_BASE)},
            ],
        },
    ]
    return page(
        "Tools für vegane Content Creator | This Is Vegan",
        "Kostenlose Tools für vegane, Tierschutz- und Food-Accounts auf Instagram und TikTok. Schriftarten, Deko und mehr Kreativität für Bio und Caption.",
        CREATOR_BASE,
        body,
        jsonld,
    )


def build_font_tool(meta):
    js = FONT_JS
    body = site_header("Schriftarten") + f"""
<nav class="crumbs" aria-label="Breadcrumb"><a href="{url('/')}">Tools</a><span>›</span><a href="{url(CREATOR_BASE)}">Für Creator</a><span>›</span>Schriftarten</nav>
<section class="hero">
  <div class="eyebrow">Für Bio, Caption und Story</div>
  <h1>Schriftarten zum <span class="q">Kopieren.</span></h1>
  <p class="sub">Tipp deinen Text ein und kopier ihn in fett, kursiv, Schreibschrift, durchgestrichen, kopfüber und mehr. Funktioniert in Instagram, TikTok, WhatsApp und überall sonst.</p>
  <textarea id="ftext" class="fontinput" aria-label="Dein Text">vegan 🌱</textarea>
  <div class="fontlist" id="fontlist"></div>
</section>

<section class="section">
  <h2>Vegane Deko zum Einsetzen</h2>
  <p class="lead">Tipp ein Symbol an, es landet direkt in deinem Text. Ideal für die Bio.</p>
  <div class="decogrid" id="decogrid"></div>
</section>

<section class="section">
  <h2>Fertige Trenner</h2>
  <p class="lead">Hübsche Trennlinien für die Bio oder zwischen Caption-Absätzen.</p>
  <div class="fontlist" id="divlist"></div>
</section>

<section class="section">
  <h2>So nutzt du die Schriften richtig</h2>
  <p class="prose">Die Stile sind besondere Unicode-Zeichen, keine echten Schriftarten. Deshalb kannst du sie überall einfügen, wo du normal tippst, also in deine Instagram-Bio, in Captions, Stories, TikTok, WhatsApp oder die Twitch-Bio. Ein Hinweis aus der Praxis: Setz sie sparsam ein. Screenreader lesen verzierte Schrift oft nicht sauber vor, deshalb lieber nur einzelne Wörter hervorheben als ganze Sätze. Der durchgestrichene Stil ist übrigens perfekt, um pflanzliche Statements zu setzen.</p>
</section>
""" + site_footer(meta, full_disclaimer=False) + f"\n<script>{js}</script>"

    jsonld = [
        {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": "Schriftarten-Generator",
            "url": BASE_URL + url(FONT_BASE),
            "applicationCategory": "DesignApplication",
            "operatingSystem": "Web",
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
            "description": "Wandelt Text in 18 kopierbare Schriftstile für Instagram, TikTok und Co., inklusive durchgestrichen, kursiv und kopfüber.",
            "publisher": {"@type": "Organization", "name": "This Is Vegan", "url": MAIN_SITE},
        },
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": "Wie bekomme ich andere Schriftarten in meine Instagram-Bio?",
                 "acceptedAnswer": {"@type": "Answer", "text": "Tipp deinen Text in den Generator, kopier den gewünschten Stil und füg ihn in deine Bio oder Caption ein. Die Stile sind Unicode-Zeichen und funktionieren ohne App direkt in Instagram."}},
                {"@type": "Question", "name": "Funktionieren die Schriftarten auch bei TikTok und WhatsApp?",
                 "acceptedAnswer": {"@type": "Answer", "text": "Ja. Da es sich um Unicode-Zeichen handelt, lassen sie sich überall einfügen, wo du Text eingeben kannst, also auch bei TikTok, WhatsApp, Threads oder Discord."}},
            ],
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Tools", "item": BASE_URL + url("/")},
                {"@type": "ListItem", "position": 2, "name": "Für Creator", "item": BASE_URL + url(CREATOR_BASE)},
                {"@type": "ListItem", "position": 3, "name": "Schriftarten", "item": BASE_URL + url(FONT_BASE)},
            ],
        },
    ]
    return page(
        "Schriftarten-Generator für Instagram: Fonts zum Kopieren | This Is Vegan",
        "Text in coole Schriftarten umwandeln und kopieren, für Instagram, TikTok und Co. Fett, kursiv, Schreibschrift, durchgestrichen, kopfüber, plus vegane Deko. Kostenlos.",
        FONT_BASE,
        body,
        jsonld,
    )


def build_404(meta):
    body = site_header("Tools") + f"""
<section class="hero">
  <div class="eyebrow">404</div>
  <h1>Hier wächst <span class="q">nichts.</span></h1>
  <p class="sub">Die Seite gibt es nicht (mehr). Vielleicht hilft dir der E-Nummern-Checker weiter, oder du startest auf der Tool-Übersicht.</p>
  <div style="margin-top:28px;display:flex;gap:12px;justify-content:center;flex-wrap:wrap">
    <a class="btn" href="{url('/e-nummern/')}">Zum E-Nummern-Checker</a>
    <a class="btn" href="{url('/')}">Alle Tools</a>
  </div>
</section>
""" + site_footer(meta, full_disclaimer=False)
    return page("Seite nicht gefunden | This Is Vegan Tools", "Diese Seite gibt es nicht. Zurück zur Tool-Übersicht von This Is Vegan.", "/404.html", body)


# ---------------------------------------------------------------- build


def main():
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    meta, adds = data["meta"], data["additives"]

    ersatz_data = json.loads((ROOT / "data" / "ersatz-data.json").read_text(encoding="utf-8"))
    ersatz_meta, ings = ersatz_data["meta"], ersatz_data["ingredients"]

    naehr_data = json.loads((ROOT / "data" / "naehrstoffe-data.json").read_text(encoding="utf-8"))
    naehr_meta, nutrients = naehr_data["meta"], naehr_data["nutrients"]

    impact_full = json.loads((ROOT / "data" / "impact-data.json").read_text(encoding="utf-8"))
    impact_cfg = {
        "lastUpdated": impact_full["meta"]["lastUpdated"],
        "per_day": impact_full["per_day"],
        "methodik": impact_full["methodik"],
    }

    food_data = json.loads((ROOT / "data" / "lebensmittel-data.json").read_text(encoding="utf-8"))
    food_meta, foods = food_data["meta"], food_data["foods"]

    saison_data = json.loads((ROOT / "data" / "saison-data.json").read_text(encoding="utf-8"))
    saison_meta, produce = saison_data["meta"], saison_data["produce"]

    drink_data = json.loads((ROOT / "data" / "pflanzendrinks-data.json").read_text(encoding="utf-8"))
    drink_meta, drinks, usecases = drink_data["meta"], drink_data["drinks"], drink_data["usecases"]

    protein_data = json.loads((ROOT / "data" / "protein-data.json").read_text(encoding="utf-8"))
    protein_meta, protein_foods, protein_cats = protein_data["meta"], protein_data["foods"], protein_data["categories"]

    co2_data = json.loads((ROOT / "data" / "co2-data.json").read_text(encoding="utf-8"))
    co2_meta, co2_foods = co2_data["meta"], co2_data["foods"]

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    # static assets
    shutil.copytree(ROOT / "assets" / "fonts", DIST / "fonts")
    for f in (ROOT / "static").glob("*"):
        shutil.copy(f, DIST / f.name)

    pages = {}  # path -> html
    pages["/"] = build_hub(meta, adds, ings, nutrients)
    pages["/e-nummern/"] = build_checker(meta, adds)
    for a in adds:
        pages[f"/e-nummern/{slug(a['code'])}/"] = build_detail(a, meta, adds)

    # Vegan-Ersatz-Finder
    pages[ERSATZ_BASE] = build_ersatz_hub(ersatz_meta, ings)
    for i in ings:
        pages[ERSATZ_BASE + i["slug"] + "/"] = build_ersatz_detail(i, ersatz_meta, ings)

    # Nährstoff-Rechner
    pages[NAEHR_BASE] = build_naehrstoff_hub(naehr_meta, nutrients)
    for nt in nutrients:
        pages[NAEHR_BASE + nt["slug"] + "/"] = build_naehrstoff_detail(nt, naehr_meta, nutrients)

    # Impact-Rechner
    pages[IMPACT_BASE] = build_impact(impact_cfg)

    # Ist das vegan? Lebensmittel-Checker
    pages[FOOD_BASE] = build_food_hub(food_meta, foods)
    for f in foods:
        pages[FOOD_BASE + f["slug"] + "/"] = build_food_detail(f, food_meta, foods)

    # Saisonkalender
    pages[SAISON_BASE] = build_saison_hub(saison_meta, produce)
    for i in range(12):
        pages[SAISON_BASE + MONTH_SLUGS[i] + "/"] = build_saison_month(i, saison_meta, produce)

    # Pflanzendrink-Vergleich
    pages[PFLANZ_BASE] = build_drink_hub(drink_meta, drinks, usecases)
    for d in drinks:
        pages[PFLANZ_BASE + d["slug"] + "/"] = build_drink_detail(d, drink_meta, drinks, usecases)

    # Protein-Tabelle
    pages[PROT_BASE] = build_protein(protein_meta, protein_foods, protein_cats)

    # CO2-Fußabdruck
    pages[CO2_BASE] = build_co2(co2_meta, co2_foods)

    # Protein-pro-Mahlzeit-Rechner
    pages[MEAL_BASE] = build_meal(protein_meta, protein_foods)

    # Creator-Bereich
    pages[CREATOR_BASE] = build_creator_hub(CREATOR_META)
    pages[FONT_BASE] = build_font_tool(CREATOR_META)

    for path, content in pages.items():
        out = DIST / path.lstrip("/") / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content, encoding="utf-8")

    (DIST / "404.html").write_text(build_404(meta), encoding="utf-8")

    # sitemap
    today = date.today().isoformat()
    urls = "\n".join(
        f"  <url><loc>{BASE_URL}{url(p)}</loc><lastmod>{today}</lastmod></url>" for p in pages
    )
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n</urlset>\n",
        encoding="utf-8",
    )

    (DIST / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {BASE_URL}{url('/sitemap.xml')}\n", encoding="utf-8"
    )

    (DIST / "_headers").write_text(
        "/fonts/*\n"
        "  Cache-Control: public, max-age=31536000, immutable\n"
        "/favicon.svg\n"
        "  Cache-Control: public, max-age=604800\n"
        "/og-image.png\n"
        "  Cache-Control: public, max-age=604800\n"
        "/*\n"
        "  X-Content-Type-Options: nosniff\n"
        "  X-Frame-Options: DENY\n"
        "  Referrer-Policy: strict-origin-when-cross-origin\n",
        encoding="utf-8",
    )

    n = len(pages) + 1
    print(f"OK: {n} Seiten nach {DIST} gebaut ({len(adds)} Zusatzstoffe, {len(ings)} Ersatz-Zutaten, {len(nutrients)} Nährstoffe, {len(foods)} Lebensmittel, Saisonkalender).")


if __name__ == "__main__":
    main()
