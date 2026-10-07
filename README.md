# Paulper.com – statischer Nachbau der Gamma-Seite

Reines HTML/CSS/JS, ohne Gamma und ohne Build-Tools zur Laufzeit. Die Adressen sind dieselben wie bisher (`/per-fotografie/`, `/per-über-mich/` …).

## Struktur
- `index.html`, `per-*/index.html`: die 8 Seiten (werden generiert)
- `assets/style.css`: Design (Theme „Borealis“: Spline Sans / Barlow, Akzentfarbe #16FFBB)
- `assets/site.js`: Navigation, Einblend-Animationen, Bild-Lightbox
- `assets/img/`: alle Bilder lokal (von Gamma heruntergeladen)
- `_source/gamma-json/`: Original-Inhalte aus Gamma (ProseMirror-JSON)
- `_source/build.py`: erzeugt die Seiten aus dem JSON

## Lokal ansehen
```bash
python -m http.server 8765
```
Dann http://localhost:8765 öffnen.

## Neu generieren
```bash
python _source/build.py
```

## Veröffentlichen
Den ganzen Ordner (ohne `_source/` und `.claude/`) auf einen statischen Host laden, z. B. GitHub Pages, Netlify oder Cloudflare Pages. Danach die Domain paulper.com dort hinterlegen und die DNS-Einträge von Gamma auf den neuen Host umstellen.
