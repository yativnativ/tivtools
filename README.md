# This Is Vegan – Tools (tools.this-is-vegan.com)

Statische Tool-Sammlung für Cloudflare Pages. Kein Framework, kein Node:
`build.py` (Python 3, nur Standardbibliothek) generiert aus `data/` fertige
HTML-Seiten nach `dist/`.

## Bauen

```bash
python3 build.py
```

Ergebnis: 116 Seiten in `dist/` (Hub, Checker, 113 Detailseiten, 404)
plus `sitemap.xml`, `robots.txt`, `_headers`, Fonts, Favicon, OG-Image.

## Deploy: GitHub + Cloudflare Pages (empfohlen, einmalig einrichten)

Quelle der Wahrheit ist dieses Git-Repo. `dist/` wird NICHT eingecheckt
(steht in `.gitignore`), Cloudflare baut es bei jedem Push neu.

Einmalige Einrichtung:
1. Repo zu GitHub pushen (privat reicht).
2. https://dash.cloudflare.com → **Workers & Pages** → **Create** → Tab **Pages**
   → **Connect to Git** → dieses Repo wählen.
3. Build-Einstellungen:
   - **Framework preset:** None
   - **Build command:** `python3 build.py`
   - **Build output directory:** `dist`
   (Das Build-Image hat `python3` ab Werk. `build.py` nutzt nur die
   Standardbibliothek, keine Dependencies, kein `requirements.txt` nötig.)
4. Deploy. Läuft unter `tiv-tools.pages.dev`.
5. Custom Domain: Pages-Projekt → **Custom domains** → `tools.this-is-vegan.com`.

Danach ist **jeder Deploy nur noch `git push`** — Cloudflare baut und
veröffentlicht automatisch. Jeder Branch bekommt zusätzlich eine Preview-URL,
zum Testen bevor es live geht.

## Deploy: Direct Upload (Fallback ohne Git, ~3 Minuten)

1. https://dash.cloudflare.com → **Workers & Pages** → **Create** → Tab **Pages**
2. **Upload assets** → Projektname `tiv-tools` → Inhalt von `dist/` reinziehen
   (vorher `python3 build.py` laufen lassen)
3. Deploy → `tiv-tools.pages.dev`, dann Custom Domain wie oben.

## Wichtig nach dem ersten Deploy

- In der Google Search Console `tools.this-is-vegan.com` als Property anlegen
  und `https://tools.this-is-vegan.com/sitemap.xml` einreichen.
- Von der Hauptseite (WordPress) auf die Tools verlinken, z. B. Menüpunkt
  "Tools" + ein kurzer Magazin-Beitrag. Ohne interne Links von der starken
  Domain dauert das Ranking deutlich länger.

## Neues Tool hinzufügen (das Muster)

1. Datenquelle als JSON nach `data/` legen.
2. In `build.py` eine `build_<tool>()`-Funktion ergänzen (Seitenshell via
   `page()` + `site_header()` + `site_footer()`, CI-Styles sind schon da).
3. Auf der Hub-Seite (`build_hub`) eine neue `toolcard` ergänzen und den
   Eintrag in der `ItemList` im JSON-LD ergänzen.
4. `python3 build.py` → neu deployen. Sitemap und interne Links entstehen
   automatisch, solange die Seiten über `pages[...]` registriert werden.

## Architektur-Entscheidungen

- **Subdomain statt Subdirectory** (Option 2 aus HANDOFF.md): 80 % des
  SEO-Nutzens, kein Reverse-Proxy nötig. Wechsel auf
  `this-is-vegan.com/tools/...` später möglich: in `build.py` nur
  `BASE_URL` und `PREFIX` ändern und neu bauen.
- **Fonts self-hosted** (`assets/fonts/`, variable woff2, Latin-Subset,
  54 KB gesamt): keine Google-Fonts-Requests, keine Consent-Frage, schnellerer LCP.
- **CSS inline pro Seite**: spart den Render-blocking Request. Seitengröße
  bleibt unter 20 KB (Checker 56 KB wegen eingebetteter Suchdaten).
- **JS nur auf der Checker-Seite**, Detailseiten und Hub sind komplett statisch.
- **SEO pro Detailseite**: FAQPage- + BreadcrumbList-Schema, Canonical,
  OG/Twitter-Tags, interne Verlinkung (ähnliche Zusatzstoffe + 2 rotierende
  Magazin-Links), Meta-Description mit Verdict im ersten Satz.
- **Faktenqualität**: `data/enummern-data.json` ist die Single Source of
  Truth. Regeln und Quellen stehen in `HANDOFF.md`. Bei Erweiterungen immer
  2 unabhängige Quellen gegenchecken, Disclaimer bleibt auf jeder Seite.
