# Handover — Overnight 14.6.2026 (Tools-Site)

Stand: **19 Tools, 374 Seiten, Sitemap 373.** Alles gebaut, lokal QA-geprüft
(Desktop + Mobile), committet, gepusht, live verifiziert auf
https://tivtools.yannick-748.workers.dev

## Was in dieser Nacht passiert ist

### 1. Illustrationen auf Deutsch / ohne englischen Text
Higgsfield backt bei Motiven mit Beschriftung gern englische Wörter ein
(„ISITVEGAN", „HIDDEN", „HONEY"). Neu generiert mit Prompt-Zusatz
**„Absolutely no text, no letters, no words anywhere"**: ist-das-vegan,
versteckte-zutaten, e-nummern, Veganizer-Honig. Ergebnis: saubere, sprach-
neutrale Doodles. OG-Karten + Veganizer-Karten neu gerendert.

### 2. Tool-Illustrationen auf den Seiten integriert
Jede der 20 Tool-Landingpages hat jetzt ein **rundes Hero-Emblem** mit der
Tool-Illustration. Technisch zentral in `page()` injiziert (nur für Pfade in
`OG_MAP` = genau die Landingpages, Detailseiten bleiben frei). Assets:
`site-illu/<slug>.png` → `dist/illu/`. Responsive (120px Desktop, 96px Mobil).

### 3. Drei neue Tools (recherchegetrieben)
Recherche (WebSearch: Google-Trends-Signale, Suchvolumen): „vegan dress"/Mode
steigt stark, „is wine vegan" ist Evergreen, Anfänger brauchen Orientierung.
- **/vegane-materialien/** — Mode/Textil-Ampel, 30 Stoffe (Leder, Wolle, Seide,
  Daunen … vs. Kork, Piñatex, Apfel-/Kaktus-/Pilzleder), je Detailseite.
- **/getraenke-vegan/** — Wein, Bier, Sekt, Spirituosen, Likör (22), Fokus auf
  versteckte Klärhilfen (Hausenblase, Gelatine, Eiklar, Casein).
- **/vegane-einkaufsliste/** — interaktive Starter-Küche zum Abhaken (49 Items,
  8 Kategorien), localStorage-Persistenz, Kopieren, Drucken, B12-Pflichthinweis.

### 4. Design-Pass (Brand-DNA, weg vom AI-Template-Look)
Body bekam fixed Radial-Gradient-Washes in Markenfarben (teal/green/terra,
low-alpha) → warmer, organischer Look. Plus die Hero-Emblems geben jeder Seite
Charakter. Gabarito (rounded Display) bleibt als unverwechselbare Schrift.

## Code-Struktur (für nächste Tools)
- **Ampel-Tools** (tierisch/kann-tierisch/vegan + Suche + Filter + Detailseiten):
  generischer `build_ampel_hub(cfg, items)` / `build_ampel_detail(cfg, item, items)`
  + `_ampel_js()`. Neues Tool = JSON-Daten + ein `<tool>_cfg(meta)`-Dict +
  3 Zeilen in `main()` + Hub-Card + ItemList + OG_MAP-Eintrag + Illustration.
- **Karten-Generatoren** (lokal, Pillow, committet in `_handover_tmp/`):
  `make_og_cards.py` (1200×630 OG), `make_reise_cards.py` (1080×1920 Handy),
  `make_cards.py` (1080×1080 Veganizer). Logo-Assets: `og-assets/logo-tiv-*.png`.
- **Hero-Emblems**: `site-illu/` (getrimmt+quadratisch weiß). Neue per
  Trim-Skript aus `/tmp/ogill/<slug>.png`.
- Illustration-Quellen liegen in `/tmp/ogill/` (nicht committet, bei Bedarf neu
  via Higgsfield generieren; ~15% Ausfallrate, failed Jobs einzeln neu starten).

## Backlog (recherchiert, noch offen — auf User-Freigabe)
- Vegane Siegel & Logos erklärt (V-Label, Veganblume, PETA-Approved)
- Veganuary / 30-Tage-vegan-Starter (saisonal stark im Januar)
- B12-Guide / Dosierung (medizinisch vorsichtig framen, Orientierung)

## Offen (Infrastruktur, unverändert)
- Custom-Domain `tools.this-is-vegan.com` per DNS ans Worker hängen
  (Canonicals + og:image zeigen schon dorthin), danach `workers_dev:false`.
- GSC-Property + Sitemap einreichen, WP-Menü-Verlinkung von der Hauptdomain.
