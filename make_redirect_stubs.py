"""Ersetzt im Subdomain-Build jede HTML-Seite durch eine Umleitung auf
this-is-vegan.com/tools/<pfad>. Assets bleiben liegen (die /tools-Fassung
laedt sie von hier). Ausgenommen: dist/tools, 404.html, linkinbio (Instagram-Bio).

Aufruf im Workflow nach dem Root-Build:  python3 make_redirect_stubs.py dist
"""
import html
import sys
from pathlib import Path

TARGET = "https://this-is-vegan.com/tools"
KEEP_DIRS = {"tools", "linkinbio"}

root = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
n = 0
for f in root.rglob("index.html"):
    rel = f.relative_to(root)
    if rel.parts and rel.parts[0] in KEEP_DIRS:
        continue
    path = "/" + "/".join(rel.parts[:-1])
    path = path if path.endswith("/") else path + "/"
    dest = TARGET + path
    d = html.escape(dest, quote=True)
    f.write_text(
        "<!doctype html>\n<html lang=\"de\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        f"<title>Umgezogen: {d}</title>"
        f"<link rel=\"canonical\" href=\"{d}\">"
        f"<meta http-equiv=\"refresh\" content=\"0; url={d}\">"
        f"<script>location.replace({dest!r}+location.search+location.hash)</script>"
        "</head><body style=\"font-family:system-ui,sans-serif;padding:2rem\">"
        f"<p>Die Tools sind umgezogen: <a href=\"{d}\">{d}</a></p></body></html>\n",
        encoding="utf-8",
    )
    n += 1

(root / "sitemap.xml").unlink(missing_ok=True)
(root / "robots.txt").write_text(
    "User-agent: *\nAllow: /\n\nSitemap: https://this-is-vegan.com/tools/sitemap.xml\n", encoding="utf-8"
)
print(f"Umleitungen: {n} Seiten -> {TARGET}/")
