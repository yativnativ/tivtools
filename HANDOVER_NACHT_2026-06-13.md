# Nacht-Session 13.6.2026: 4 neue Tools

Über Nacht von 2 auf 6 Live-Tools ausgebaut. Alles getestet, committet, gepusht,
Cloudflare hat jeweils automatisch neu deployt. Live auf der `workers.dev`-URL,
sobald die Subdomain hängt auch dort.

## Neu gebaut

3. **Nährstoff-Rechner** `/naehrstoffrechner/` — Gewicht, Geschlecht, Aktivität rein,
   Live-Ergebnis für Protein, B12, Eisen, Omega-3, Calcium plus 5 Detailseiten.
   Ziel: Umsatz (natürlicher Ort für Supplement-/Protein-Empfehlungen).
4. **Impact-Rechner** `/impact-rechner/` — Zeitraum rein, raus kommen gerettete Tiere,
   CO2, Wasser, Ackerland mit Vergleichen. Transparente Methodik-Box, konservative
   Zahlen. Ziel: Reichweite, Shares, Mission.
5. **Ist das vegan?** `/ist-das-vegan/` — 40 Lebensmittel mit Ampel und versteckten
   Fallen. Greift die "ist X vegan"-Masse ab.
6. **Saisonkalender** `/saisonkalender/` — Monatswähler (springt auf aktuellen Monat)
   plus 12 Monatsseiten, Freiland und Lager getrennt.

## Qualität

- Alle Vorgaben eingehalten: kein KI-Wording, keine Floskeln, keine Em-Dashes,
  redaktioneller This-Is-Vegan-Look, psychologisch und SEO durchdacht.
- Jede Detailseite: FAQ- und Breadcrumb-Schema, Canonical, OG, interne Verlinkung.
- Responsive auf Mobile, iPad und Desktop geprüft, kein horizontaler Überlauf.
- Rund 195 Seiten gesamt, Sitemap 194 URLs, alle JSON-LD-Blöcke valide, keine toten Links.

## Was als Nächstes sinnvoll ist

Siehe `TOOLS-ROADMAP.md`. Kurz: Food-Checker auf 100+ Lebensmittel und echte Marken
ausbauen (riesiges Volumen), Protein-pro-Gericht-Rechner, Pflanzendrink-Vergleich.

## Noch offen (deine Entscheidung)

- Subdomain `tools.this-is-vegan.com` ans Worker hängen (Subdomain-Delegation zu
  Cloudflare, Kinsta bleibt Host, 3 Schritte). Danach `workers_dev: false`.
- Optional später Subdirectory `this-is-vegan.com/tools/` plus WP-Menü- und Ads-Nachbau.
