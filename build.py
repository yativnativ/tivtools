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
</p>
<p class="sources">Quellen: PETA Deutschland, Verbraucherzentrale, vegpool.de, This Is Vegan. Stand: """ + esc(stand) + ".</p>"
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


def build_hub(meta, adds):
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
      <p>E-Nummer oder Zutat eingeben und sofort sehen, ob der Zusatzstoff vegan ist. {len(adds)} Zusatzstoffe in der Datenbank: {counts['yes']} vegan, {counts['maybe']} herkunftsabhängig, {counts['no']} immer tierisch.</p>
      <span class="meta">Jetzt prüfen →</span>
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
                    }
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

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    # static assets
    shutil.copytree(ROOT / "assets" / "fonts", DIST / "fonts")
    for f in (ROOT / "static").glob("*"):
        shutil.copy(f, DIST / f.name)

    pages = {}  # path -> html
    pages["/"] = build_hub(meta, adds)
    pages["/e-nummern/"] = build_checker(meta, adds)
    for a in adds:
        pages[f"/e-nummern/{slug(a['code'])}/"] = build_detail(a, meta, adds)

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
    print(f"OK: {n} Seiten nach {DIST} gebaut ({len(adds)} Zusatzstoffe).")


if __name__ == "__main__":
    main()
