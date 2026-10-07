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

## Veröffentlichen (GitHub Pages + Domain bei Strato)

Bei jedem Push auf `main` veröffentlicht `.github/workflows/pages.yml` die Seite automatisch. `_source/`, `README.md` und die Konfiguration werden dabei nicht mit ausgeliefert.

### 1. Repository auf GitHub anlegen
1. Auf https://github.com/new ein neues, leeres Repository anlegen, z. B. `paulper.com` (öffentlich, ohne README).
2. Im Projektordner:
   ```bash
   git remote add origin https://github.com/<DEIN-GITHUB-NAME>/paulper.com.git
   git push -u origin main
   ```
3. Im Repo unter **Settings → Pages → Build and deployment → Source** die Option **GitHub Actions** wählen.
4. Unter **Settings → Pages → Custom domain** `paulper.com` eintragen (steht auch schon in der Datei `CNAME`).

### 2. DNS bei Strato umstellen
Strato-Kundenlogin → **Domains → Domainverwaltung → paulper.com → Zahnrad / DNS**:

| Eintrag | Typ | Wert |
|---|---|---|
| `paulper.com` | A-Record | `185.199.108.153` |
|  |  | `185.199.109.153` |
|  |  | `185.199.110.153` |
|  |  | `185.199.111.153` |
| `paulper.com` | AAAA-Record | `2606:50c0:8000::153`, `2606:50c0:8001::153`, `2606:50c0:8002::153`, `2606:50c0:8003::153` |
| `www` | CNAME | `<DEIN-GITHUB-NAME>.github.io` |

- Bei Strato heißt das „A-Record / AAAA-Record: **andere IP-Adresse**“ statt „Strato-Server“.
- Die bisherigen Gamma-Einträge (A-Record `3.137.108.170`, CNAME `www` → `sites.gamma.app…`) dabei ersetzen.
- **Die MX-Einträge (E-Mail) nicht anfassen.**

### 3. HTTPS aktivieren
Nach der DNS-Umstellung (dauert meist wenige Minuten bis einige Stunden) unter **Settings → Pages** prüfen, ob der Domain-Check grün ist, und dann **Enforce HTTPS** anhaken.

### 4. Gamma abschalten
Erst wenn die neue Seite unter https://paulper.com läuft: in Gamma die Custom Domain entfernen bzw. die Seite depublizieren.
