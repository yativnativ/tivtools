# Tools-Roadmap This Is Vegan

Strategische Auswahl: Welche Tools bringen Traffic und zahlen aufs Ziel ein.
Bewertungslogik: Suchvolumen/SEO-Potenzial × Eigenständigkeit (eigene URL-Cluster) ×
Conversion/Goal × Bau-Aufwand. Alles statisch, ein Datensatz wird zu vielen
indexierbaren Seiten, deploybar per `git push`.

## Live (Stand 13.6.2026)

1. **E-Nummern-Checker** (`/e-nummern/`) — 113 Zusatzstoffe, je eine SEO-Seite.
   Long-tail "E… vegan", "ist … vegan". Traffic-Anker.
2. **Vegan-Ersatz-Finder** (`/vegan-ersetzen/`) — 17 Zutaten (Ei, Butter, Milch,
   Käse, Gelatine …). Evergreen "X vegan ersetzen". Praxis-Intention, Rezept-Bezug.
3. **Nährstoff-Rechner** (`/naehrstoffrechner/`) — Protein, B12, Eisen, Omega-3,
   Calcium, personalisiert. 5 Detailseiten. Ziel: Umsatz (Supplement/Protein).
4. **Impact-Rechner** (`/impact-rechner/`) — gerettete Tiere, CO2, Wasser, Fläche.
   Share-/Backlink-stark, Tierschutz-Mission. Transparente Methodik.
5. **Ist das vegan?** (`/ist-das-vegan/`) — 40 Lebensmittel (Wein, Brot, Pommes …).
   Greift die Masse der "ist X vegan"-Suchen ab. Ergänzt E-Nummern.
6. **Saisonkalender** (`/saisonkalender/`) — 45 Sorten, 12 Monatsseiten.
   Wiederkehrender Saison-Traffic, Freiland/Lager, starke interne Verlinkung.
7. **Pflanzendrink-Vergleich** (`/pflanzendrink-vergleich/`) — 8 Drinks, Use-Case-Ranking
   (Kaffee, Backen, Protein, Klima), Nährwerte, 8 Detailseiten. Kauf-Intention.
8. **Protein-Tabelle** (`/protein-tabelle/`) — 42 Lebensmittel, durchsuchbar/sortierbar,
   Eiweiß pro 100 g. Targets "veganes protein tabelle", verlinkt zum Nährstoff-Rechner.
9. **CO2-Fußabdruck** (`/co2-fussabdruck/`) — 23 Lebensmittel, kg CO2 pro kg, tierisch
   vs pflanzlich farbcodiert. Werte gegen Science-2018-Metaanalyse/OWID gecheckt.
10. **Protein pro Mahlzeit** (`/protein-pro-mahlzeit/`) — Meal-Builder, Protein
    summieren, Prozent vom Tagesziel. Nutzt die gecheckten Protein-Werte.

Gesamt: rund 209 Seiten, alle mit FAQ- + Breadcrumb-Schema, Canonical, OG.

## Bereich: Für Content Creator (`/creator/`)

Eigener Bereich für vegane, Tierschutz- und Food-Accounts auf Social Media.

C1. **Schriftarten-Generator** (`/creator/schriftarten/`) — 18 Unicode-Stile (fett,
    kursiv, Schreibschrift, gotisch, durchgestrichen, kopfüber u.a.), vegane Deko
    und Trenner, Copy-Buttons. Targets "instagram schriftarten", "schrift kopieren".
C2. **Bild freistellen** (`/creator/bild-freistellen/`) — Hintergrund-Entferner, der
    ein KI-Modell komplett im Browser lädt (@imgly/background-removal via CDN). Kein
    Upload, kein Server-Load, dauerhaft kostenlos. Transparentes PNG + Farb-Swatches.
    Targets "bild freistellen kostenlos", "hintergrund entfernen".

Creator-Backlog: Hashtag-Helfer (vegane/Food-Hashtag-Sets), Caption-Ideen-Generator,
Emoji- und Symbol-Bibliothek, Best-Time-to-Post-Übersicht, Bio-Link-Vorlagen.

## Nächste Ideen (priorisiert)

11. **"Ist das vegan?" ausbauen** auf 100+ Lebensmittel und echte Marken
    (Markenname + Produkt). Marken-Suchen sind riesig und kaum bedient. Achtung:
    Markenrezepturen ändern sich, defensiv formulieren und datieren.
12. **Vegane-Reise-Spickzettel** — "Ich bin vegan"-Sätze + versteckt-tierisch-Begriffe
    pro Sprache. Nische, teilbar, ohne Konkurrenz.
12. **Saisonkalender erweitern**: pro Sorte eine Seite ("Erdbeeren Saison") mit
    Rezept-Links, plus Kräuter und Salate.
13. **Zucker-/Kalorien-Vergleich pflanzlicher Süßungsmittel** oder **CO2-Vergleich
    Lebensmittel** als weitere Datentools.

## Bauprinzip für jedes Tool

- Ein JSON-Datensatz in `data/`, eine `build_<tool>()`-Funktion, Hub-Card ergänzen,
  ItemList-Schema im Hub erweitern, in `main()` registrieren. Pro Eintrag eine
  indexierbare Seite mit FAQ- + Breadcrumb-Schema, Canonical, OG, interne Links.
- Voice: locker, direkt, keine Floskeln, kein KI-Wording, keine Em-Dashes, sentence case.
- Responsive ist durch die bestehenden CSS-Muster abgedeckt (Grids auto-fit,
  Rechner stapeln unter 620px). Neue Tools die Muster wiederverwenden.
- Bei allem mit Gesundheits- oder Umweltbezug: Orientierung statt Beratung,
  Disclaimer, konservative Werte, transparente Methodik.

## Offen (Infrastruktur)

- Subdomain `tools.this-is-vegan.com` ans Worker hängen (Subdomain-Delegation zu
  Cloudflare, Kinsta bleibt Host). Danach `workers_dev: false` setzen.
- Später optional Subdirectory `this-is-vegan.com/tools/` plus WP-Menü/Ads-Nachbau.
