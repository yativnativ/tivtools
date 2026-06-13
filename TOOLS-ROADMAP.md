# Tools-Roadmap This Is Vegan

Strategische Auswahl: Welche Tools bringen Traffic und zahlen aufs Ziel ein.
Bewertungslogik: Suchvolumen/SEO-Potenzial × Eigenständigkeit (eigene URL-Cluster) ×
Conversion/Goal × Bau-Aufwand. Alles statisch, ein Datensatz wird zu vielen
indexierbaren Seiten, deploybar per `git push`.

## Live

1. **E-Nummern-Checker** (`/e-nummern/`) — 113 Zusatzstoffe, je eine SEO-Seite.
   Long-tail "E… vegan", "ist … vegan". Traffic-Anker.
2. **Vegan-Ersatz-Finder** (`/vegan-ersetzen/`) — 17 Zutaten (Ei, Butter, Milch,
   Käse, Gelatine …). Riesiges evergreen Volumen ("X vegan ersetzen", "X-Ersatz").
   Hohe Praxis-Intention, verlinkt natürlich zu Rezepten und Produkten.

## Tier 1 — als Nächstes bauen (höchster Hebel)

3. **Veganer Nährstoff-Bedarf-Rechner** (Protein, B12, Eisen, Omega-3, Calcium)
   - Eingabe Gewicht/Aktivität → Tagesbedarf + beste pflanzliche Quellen je Nährstoff.
   - Warum: hohe Intention ("veganer Proteinbedarf", "B12 Bedarf vegan"), Rechner
     ziehen Backlinks, und es ist der natürliche Ort für die Supplement- und
     Proteinpulver-Empfehlungen (Nutri+ zuerst). **Goal: Umsatz + Autorität.**
   - Achtung: keine Heilversprechen, konservative Werte, Quellen-Disclaimer
     (Bedarf höher als DGE, 1,2–1,6 g/kg Protein). Werte als Orientierung framen.

4. **Impact-Rechner "Was deine Ernährung bewirkt"**
   - Eingabe Tage/Jahre vegan → gerettete Tiere, CO2, Wasser, Land gespart.
   - Warum: emotional, extrem teilbar → Social-Traffic + Backlinks, zahlt direkt
     auf die Tierschutz-Mission ein. **Goal: Reichweite + Marke.**
   - Achtung: nur belegbare, klar zitierte Zahlen (Mittelwerte aus Studien),
     transparente Methodik-Box, eher konservativ rechnen.

## Tier 2 — danach

5. **"Ist das vegan?" Lebensmittel- und Marken-Checker** — breiter als E-Nummern
   (Wein, Gnocchi, Pesto, Süßigkeiten, Marken). Deckt die Masse an "ist X vegan"-Suchen.
6. **Vegan-Saisonkalender** — welches Gemüse/Obst hat gerade Saison, mit Rezept-Links.
   Wiederkehrender Saison-Traffic, starke interne Verlinkung.
7. **Rezept-Nährwert-/Protein-pro-Portion-Rechner** — ergänzt Tool 3, Foodie-Intention.

## Tier 3 — nice to have

8. Vegan-auf-Reisen-Sätze (Übersetzungs-Spickzettel), Einkaufslisten-Generator,
   Etiketten-Scanner (braucht Backend, später).

## Bauprinzip für jedes Tool

- Ein JSON-Datensatz in `data/`, eine `build_<tool>()`-Funktion, Hub-Card ergänzen,
  ItemList-Schema im Hub erweitern. Pro Eintrag eine indexierbare Seite mit
  FAQ- + Breadcrumb-Schema, Canonical, OG, interne Links zu Magazin/Rezepten.
- Voice: locker, direkt, keine Floskeln, keine Em-Dashes, sentence case.
- Bei allem mit Gesundheitsbezug: Orientierung statt Beratung, Disclaimer, Quellen.
