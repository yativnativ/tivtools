# Übergabe: E-Nummern-Checker ("Ist das vegan?")

Handoff für Claude Code. Hier steht alles drin, um das Tool von Prototyp zu einem SEO-starken, deploybaren Projekt auszubauen. Lies das einmal komplett, bevor du loslegst.

---

## Was das ist

Ein kostenloses Web-Tool für This Is Vegan: Nutzer tippt eine E-Nummer oder Zutat ein (z. B. "E471", "Gelatine", "Karmin") und sieht sofort per Ampel, ob der Zusatzstoff vegan, nicht vegan oder grenzwertig ist. Läuft komplett clientseitig, kein Backend nötig.

**Strategisches Ziel:** SEO-Traffic. Leute googeln massenhaft "E120 vegan", "ist E471 vegan", "Gelatine vegan" usw. Jede E-Nummer soll eine eigene URL bekommen, die einzeln ranken kann. Aus einer Datenquelle entstehen so 100+ indexierbare Seiten plus das interaktive Such-Tool.

---

## Dateien in diesem Ordner

- `tool-prototype.html` — funktionierender Single-File-Prototyp (HTML/CSS/JS, alles inline). So sieht das Tool aktuell aus und so soll es sich anfühlen. Dient als Referenz fürs Design und als lauffähige Such-UI.
- `enummern-data.json` — die komplette Datenbank als saubere JSON (113 Einträge). **Das ist die Single Source of Truth.** Der Seiten-Generator soll daraus bauen, nicht aus dem HTML.

### Datenschema (`enummern-data.json`)

```json
{
  "meta": { "version", "lastUpdated", "statusValues", "sources", "disclaimer" },
  "additives": [
    {
      "code": "E471",
      "name": "Mono- und Diglyceride von Speisefettsäuren",
      "class": "Emulgator",
      "status": "maybe",          // "yes" | "no" | "maybe"
      "info": "Erklärtext (1-2 Sätze).",
      "note": "Optional: Zusatzhinweis / Falle / Kontext."
    }
  ]
}
```

Aktueller Stand: 72 vegan, 8 nicht vegan, 33 kommt drauf an.

---

## WICHTIG: Faktenqualität

Bei diesem Tool steht und fällt alles mit korrekten Daten. Falsche Angaben = Vertrauensverlust + potenziell Leute, die unbeabsichtigt Tierisches essen.

Regeln:
- **Nichts erfinden.** Wenn ein Zusatzstoff unklar ist, Status `maybe` und ehrlich erklären, warum.
- **Bei jeder Erweiterung der Datenbank: Quellen gegenchecken** (mind. 2 unabhängige). Genutzte Quellen stehen in `meta.sources`.
- Die kniffligen Fälle, die schon korrekt drin sind und nicht "vereinfacht" werden dürfen:
  - **E270 Milchsäure → vegan.** Klingt tierisch, kommt aber aus Fermentation (auch in Sauerkraut). Häufigste Verwechslung.
  - **E621 Glutamat/MSG → vegan.** Fermentation, trotz schlechtem Ruf nicht tierisch.
  - **E920/E921 L-Cystein → maybe.** Oft aus Schweineborsten/Federn, zunehmend mikrobiell. Nicht pauschal als "nicht vegan" labeln.
  - **E171 Titandioxid → in EU seit 2022 als Lebensmittelzusatz verboten.** Hinweis muss bleiben.
  - **E631 / E635 → maybe.** Oft aus Fisch/Fleisch, kann aber pflanzlich sein.
- Disclaimer ("Angaben ohne Gewähr", im Zweifel Hersteller fragen) muss auf jeder Seite sichtbar bleiben. Das ist bei dem Thema Pflicht, nicht Deko.

Optional-Ausbau-Idee: Datenbank gegen [OpenFoodFacts](https://de.openfoodfacts.org) abgleichen, die haben eine offene Zusatzstoff-DB.

---

## Empfohlener Tech-Stack

**Astro** ist hier ideal:
- Generiert statische Seiten zur Build-Zeit (perfekte Core Web Vitals, top für SEO)
- Eine dynamische Route `[code].astro` rendert aus der JSON automatisch eine Seite pro E-Nummer
- Deployt 1:1 auf Cloudflare Pages
- Das interaktive Such-Tool aus dem Prototyp läuft als Insel (oder einfach als eingebettetes Script auf der Startseite)

Grobe Struktur:
```
src/
  data/enummern-data.json        // die DB hier rein
  pages/
    index.astro                  // Startseite mit Live-Such-Tool (UI aus Prototyp übernehmen)
    e-nummern/[code].astro       // 1 Seite pro Zusatzstoff, generiert via getStaticPaths()
  components/
    Verdict.astro                // Ampel-Karte
    SearchTool.astro             // Such-Insel
  layouts/Base.astro             // Meta-Tags, Schema.org, Footer-Disclaimer
```

Wenn du lieber ohne Framework willst: ein simples Node-Script, das durch die JSON loopt und pro Eintrag eine HTML-Datei aus einem Template schreibt, tut es auch. Astro ist nur wartungsfreundlicher.

---

## SEO-Anforderungen pro Seite

Jede `/e-nummern/eXXX`-Seite braucht:
- `<title>` im Muster: `E471 vegan? – Mono- und Diglyceride | This Is Vegan`
- `<meta name="description">` mit dem Status-Verdict im ersten Satz
- **Schema.org**: `FAQPage` mit der Frage "Ist E471 vegan?" + Antwort, oder `Article`. Das holt Rich Results in Google.
- Open Graph Tags (für Insta/Social-Shares)
- Saubere H1: "Ist E471 vegan?"
- Interne Verlinkung: "Ähnliche Zusatzstoffe" (gleiche Klasse oder gleicher Status) unten verlinken → hält Crawler und Nutzer im Loop
- Klarer Slug. Empfehlung: `/e-nummern/e471` (plus optional `/e-nummern/e471-mono-diglyceride` mit Canonical). Konsistent bleiben.
- `sitemap.xml` automatisch generieren (Astro-Integration `@astrojs/sitemap`)
- Eine Übersichts-/Hub-Seite, die alle Einträge nach Status gruppiert verlinkt

---

## Design / CI (This Is Vegan)

Übernimm die Optik aus `tool-prototype.html`. Die Werte:

**Farben (CI):**
```
--peach:     #f8decd
--teal-bg:   #0a4a4a   (Haupthintergrund)
--teal-card: #0a6b6c
--teal:      #147d77
--green:     #29a579   (Akzent / "ja")
--green-deep:#106050
--terra:     #e59875
--terra-light:#f7b79a
Ampel: ja #2a9d6f, nein #c0392b, maybe #d68a3a
```
Weitere CI-Farben, falls gebraucht: `0a4a4a`, `0a6b6c`.

**Fonts:** Gabarito (Display/Headlines, 700-900) + Figtree (Body). Beide Google Fonts.

**Voice/Copy-Regeln (gelten projektweit):**
- Keine Em-Dashes (—). Niemals. Stattdessen Komma, Doppelpunkt oder Punkt.
- Kein Press-Release-Sprech, keine KI-Floskeln ("In der heutigen schnelllebigen Welt...").
- Klar, direkt, wie an einen schlauen Freund geschrieben. Locker, aber sachlich korrekt.
- Sentence case, aktive Verben.

---

## Deployment-Entscheidung (noch offen)

Das Tool soll auf this-is-vegan.com hängen, weil die Domain schon Autorität hat. Drei Optionen, in Reihenfolge der SEO-Stärke:

1. **Subdirectory** `this-is-vegan.com/tools/e-nummern/...` via Cloudflare-Reverse-Proxy (Worker-Regel: `/tools/*` → Astro-Build, Rest → WordPress). **SEO-Königsweg**, technisch aufwändigster. Setzt voraus, dass DNS bei Cloudflare liegt (Umzug von Porkbun war eh angedacht).
2. **Subdomain** `tools.this-is-vegan.com` → Cloudflare Pages. 80 % des Nutzens, viel weniger Aufwand. Guter Startpunkt.
3. ~~Custom-HTML-Block in WordPress~~ — nicht empfohlen, killt Performance und URL-Struktur.

**OFFENE FRAGE, die Yannick noch klären muss:** Läuft this-is-vegan.com auf WordPress.com (gehostet) oder selbst gehostetem WordPress? Das entscheidet, ob der Reverse-Proxy-Weg (Option 1) überhaupt geht. Bei WordPress.com hat man weniger DNS/Routing-Kontrolle → dann eher Option 2.

Fürs erste Deployment/Testen: einfach den Astro-Build auf Cloudflare Pages werfen, eigene Subdomain, läuft. Domain-Anbindung später, mit sauberen Redirects.

---

## Konkrete Task-Liste für Claude Code

1. Astro-Projekt aufsetzen, `enummern-data.json` nach `src/data/` legen.
2. Base-Layout mit Meta-Tags, Schema.org, CI-Styles, Footer-Disclaimer.
3. `getStaticPaths()` über die JSON → eine Seite pro Zusatzstoff generieren.
4. Startseite mit Live-Such-Tool (UI/Logik aus `tool-prototype.html` übernehmen, die Such-Funktion `find()` ist dort schon gebaut).
5. Hub-/Übersichtsseite (alle Einträge nach Status gefiltert).
6. Interne Verlinkung "ähnliche Zusatzstoffe".
7. Sitemap + robots.txt.
8. Cloudflare Pages Deploy testen.
9. **Datenbank erweitern** auf 150+ Einträge (meistgesuchte zuerst), jeweils mit Quellencheck.

---

## Quick Reference: aktuelle Datenlage

Quellen (alle gegengecheckt am 2026-06-12): PETA Deutschland, Verbraucherzentrale-Liste (via CareElite), vegpool.de, this-is-vegan.com eigener Artikel, VeganBlatt/veganivore für L-Cystein.

Status-Werte: `yes` = vegan · `no` = nicht vegan (immer tierisch) · `maybe` = herkunftsabhängig.

Die 8 "immer tierisch": E120, E441, E542, E901, E904, E913, E966, E1105.
