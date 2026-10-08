"""Baut die statische Paulper.com-Seite aus den Gamma-Snapshots in _source/gamma-json.

Aufruf (im Projektordner):  python _source/build.py
Optionen:  --no-download   Bilder nicht herunterladen (nur vorhandene nutzen)
"""
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "_source")
IMG_DIR = os.path.join(ROOT, "assets", "img")
DOWNLOAD = "--no-download" not in sys.argv

# docId -> (Ausgabeordner, json-Datei)
PAGES = {
    "q1vxh31oxywk87c": ("", "index.json"),
    "0bdmzbbw1eqjh2q": ("per-fotografie", "per-fotografie.json"),
    "svy15y2uovglolr": ("per-entdecke-meine-reiseziele", "per-entdecke-meine-reiseziele.json"),
    "x87csbnik4byxsi": ("per-auto-fotografie", "per-auto-fotografie.json"),
    "rjjff09ojainakz": ("per-über-mich", "per-ueber-mich.json"),
    "4br06l673gitil2": ("per-games", "per-games.json"),
    "alamgr9by2aifcg": ("per-impressum", "per-impressum.json"),
    "ci9i2gteu94g9jn": ("per-blog-und-kontakt", "per-blog-und-kontakt.json"),
}
THEME = json.load(open(os.path.join(SRC, "theme.json"), encoding="utf8"))

# Seitenkennung (für Übergangseffekte) und Überzeile je Seite
PAGE_KEYS = {
    "": ("start", "Willkommen"),
    "per-fotografie": ("foto", "Fotografie"),
    "per-entdecke-meine-reiseziele": ("reise", "Reiseziele"),
    "per-auto-fotografie": ("auto", "Auto · Sport · Technik"),
    "per-über-mich": ("ueber", "Über mich"),
    "per-games": ("games", "Games"),
    "per-impressum": ("impressum", "Rechtliches"),
    "per-blog-und-kontakt": ("kontakt", "Blog & Kontakt"),
    "404": ("start", "Fehler 404"),
    "per-fitness-ernaehrung": ("fitness", "Fitness & Ernährung"),
}

PROFILE = "/assets/media/profil.jpg"

# Umbenennungen von Menüpunkten, Buttons und Seitentiteln
RENAME = {"Auto Fotografie": "Auto & Technik", "PER - Auto Fotografie": "PER - Auto & Technik"}
MUSCLE_UP = "/assets/media/muscle-up.mp4"

# Eigene Medien statt Gamma-Bildern: Karten-ID -> Akzent-HTML
ACCENT_OVERRIDES = {
    # Über mich – Kraftsport: Muscle-Up-Video
    "exx5t94m54qu3pl": (f'<div class="accent accent-video reveal"><video src="{MUSCLE_UP}" autoplay loop muted playsinline '
                        f'preload="auto" aria-label="Muscle-Up"></video><span class="accent-tag">Muscle-Up</span></div>'),
}

# Eigene Artikel (HTML in _source/extra), eingefügt nach der n-ten Karte einer Seite
EXTRA_SECTIONS = {
    "per-auto-fotografie": [(1, "zeekr.html"), (1, "traumauto-app.html")],
    "per-entdecke-meine-reiseziele": [(1, "reiseapp.html")],
}

# Eigene Seiten ohne Gamma-Vorlage: Ordner -> (HTML in _source/extra, Seitentitel, Beschreibung)
CUSTOM_PAGES = {
    "per-fitness-ernaehrung": ("fitness.html", "PER - Fitness & Ernährung",
                               "Kraftsport, Muskelaufbau, Körperfett und Ernährung – und meine Web-Apps SuPER Health."),
}
# Zusätzliche Menüpunkte: (nach Menüpunkt, Text, Link)
EXTRA_NAV = [("Über Mich", "Fitness & Ernährung", "/per-fitness-ernaehrung/")]

# Zusätzliche Inhalte am Kartenanfang: Karten-ID -> HTML
CARD_PREPEND = {
    "l42un5a9sk12p84": (f'<div class="hero-portrait reveal"><img src="{PROFILE}" alt="Paul P.E.R." data-lightbox></div>'),
}

# ---------------------------------------------------------------- Bilder
IMAGES = {}  # remote url -> lokaler Dateiname


def img(url, width=1800):
    """Registriert ein Bild zum Download und liefert den lokalen Pfad (relativ zur Seitenwurzel)."""
    if not url:
        return ""
    if url.startswith("/"):
        return url
    if url not in IMAGES:
        ext = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower()
        if ext not in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
            ext = ".jpg"
        name = hashlib.sha1(url.encode()).hexdigest()[:16] + ext
        IMAGES[url] = (name, width)
    return "/assets/img/" + IMAGES[url][0]


def download_all():
    os.makedirs(IMG_DIR, exist_ok=True)

    def get(item):
        url, (name, width) = item
        dest = os.path.join(IMG_DIR, name)
        if os.path.exists(dest) and os.path.getsize(dest) > 0:
            return None
        src = url.replace(" ", "%20")
        if "cdn.gamma.app" in url and not url.endswith(".gif"):
            src = f"https://imgproxy.gamma.app/resize/quality:85/resizing_type:fit/width:{width}/{url}"
        r = subprocess.run(["curl", "-sfL", "--retry", "2", "-o", dest, src])
        if r.returncode != 0:
            r = subprocess.run(["curl", "-sfL", "-o", dest, url.replace(" ", "%20")])
        return None if r.returncode == 0 else url

    with ThreadPoolExecutor(8) as ex:
        failed = [u for u in ex.map(get, IMAGES.items()) if u]
    for u in failed:
        print("  ! Download fehlgeschlagen:", u)


# ---------------------------------------------------------------- Links
def map_href(href):
    if not href:
        return "#"
    m = re.match(r"https?://gamma\.app/docs/(?:[^/#?]*-)?([a-z0-9]{15})(?:[?][^#]*)?(#.*)?$", href)
    if m and m.group(1) in PAGES:
        slug = PAGES[m.group(1)][0]
        anchor = (m.group(2) or "").replace("#card-", "#")
        return ("/" + slug + "/" if slug else "/") + anchor
    return href


def is_external(href):
    return href.startswith("http")


# ---------------------------------------------------------------- Rendering
esc = html.escape
WARN = set()


def marks(text, mks):
    out = esc(text)
    for m in mks or []:
        t, a = m["type"], m.get("attrs") or {}
        if t == "bold":
            out = f"<strong>{out}</strong>"
        elif t == "italic":
            out = f"<em>{out}</em>"
        elif t == "underline":
            out = f"<u>{out}</u>"
        elif t == "strike":
            out = f"<s>{out}</s>"
        elif t == "code":
            out = f"<code>{out}</code>"
        elif t == "link":
            h = map_href(a.get("href"))
            ext = ' target="_blank" rel="noopener"' if is_external(h) else ""
            out = f'<a class="link" href="{esc(h)}"{ext}>{out}</a>'
        else:
            WARN.add("mark:" + t)
    return out


def kids(n):
    return "".join(render(c) for c in n.get("content") or [])


def inline(n):
    return kids(n)


def align_style(a):
    ta = a.get("textAlign") or a.get("horizontalAlign")
    return f' style="text-align:{ta}"' if ta in ("center", "right") else ""


def bg_image_src(bg):
    if not bg or bg.get("type") != "image":
        return None
    return (bg.get("image") or {}).get("src")


def render(n):
    t = n.get("type")
    a = n.get("attrs") or {}
    if t == "text":
        return marks(n.get("text", ""), n.get("marks"))
    if t == "hardBreak":
        return "<br>"
    if t == "paragraph":
        inner = inline(n)
        cls = f' class="{esc(a["class"])}"' if a.get("class") else ""
        return f'<p{cls}{align_style(a)}>{inner}</p>' if inner else '<p class="empty"></p>'
    if t == "heading":
        lvl = a.get("level", 2)
        return f'<h{lvl} class="h{lvl}"{align_style(a)}>{inline(n)}</h{lvl}>'
    if t == "bullet":
        return f'<div class="bullet" style="--indent:{a.get("indent", 0)}"><span class="dot"></span><div>{kids(n)}</div></div>'
    if t == "numbered":
        return f'<div class="bullet numbered" style="--indent:{a.get("indent", 0)}"><span class="num"></span><div>{kids(n)}</div></div>'
    if t == "toggle":
        c = n.get("content") or []
        summary = "".join(render(x) for x in c if x["type"] == "toggleSummary")
        body = "".join(render(x) for x in c if x["type"] != "toggleSummary")
        return f'<details class="toggle reveal"><summary><span class="tri"></span>{summary}</summary><div class="toggle-body">{body}</div></details>'
    if t == "toggleSummary":
        return f'<span class="toggle-title">{inline(n)}</span>'
    if t == "buttonGroup":
        al = a.get("horizontalAlign") or "left"
        return f'<div class="btn-group reveal" style="justify-content:{ {"right": "flex-end", "center": "center"}.get(al, "flex-start")}">{kids(n)}</div>'
    if t == "button":
        return button(n)
    if t == "image":
        src = a.get("src")
        if not src:
            return ""
        alt = esc((a.get("meta") or {}).get("description", "").strip() or a.get("query") or "")
        return f'<figure class="image reveal"><img src="{img(src)}" alt="{alt}" loading="lazy" data-lightbox></figure>'
    if t == "gallery":
        return gallery(n)
    if t == "smartLayout":
        return smart_layout(n)
    if t == "gridLayout":
        cols = a.get("colWidths") or []
        tmpl = " ".join(f"{w}fr" for w in cols) or "1fr"
        return f'<div class="grid-layout reveal" style="--cols:{tmpl}">{kids(n)}</div>'
    if t == "gridCell":
        return f'<div class="grid-cell">{kids(n)}</div>'
    if t == "table":
        return f'<div class="table-wrap reveal"><table>{kids(n)}</table></div>'
    if t == "tableRow":
        return f"<tr>{kids(n)}</tr>"
    if t in ("tableCell", "tableHeader"):
        span = ""
        if a.get("colspan", 1) > 1:
            span += f' colspan="{a["colspan"]}"'
        if a.get("rowspan", 1) > 1:
            span += f' rowspan="{a["rowspan"]}"'
        return f"<td{span}>{kids(n)}</td>"
    if t == "embed":
        return embed(n)
    if t in ("bulletList", "orderedList"):
        return kids(n)
    WARN.add("node:" + str(t))
    return kids(n)


def button(n):
    a = n.get("attrs") or {}
    label = "".join(x.get("text", "") for x in n.get("content") or [])
    if label in RENAME:
        n = dict(n, content=[{"type": "text", "text": RENAME[label]}])
    href = map_href(a.get("href"))
    variant = a.get("variant") or "solid"
    color = a.get("color") or THEME["theme"]["accentColor"]
    ext = ' target="_blank" rel="noopener"' if is_external(href) or href.startswith("/traumauto") else ""
    extra = f' btn-{a["class"]}' if a.get("class") else ""
    return f'<a class="btn btn-{variant}{extra}" style="--btn:{color}" href="{esc(href)}"{ext}>{inline(n)}</a>'


def gallery(n):
    a = n.get("attrs") or {}
    h = float(a.get("thumbHeight") or 12)
    dims = a.get("dimensions") or "square"
    ratio = {"square": "1/1", "portrait": "3/4", "landscape": "4/3"}.get(dims, "1/1")
    layout = a.get("layout") or "grid"
    items = []
    for c in n.get("content") or []:
        ca = c.get("attrs") or {}
        if ca.get("src"):
            items.append(f'<img src="{img(ca["src"])}" alt="" loading="lazy" data-lightbox>')
    return (f'<div class="gallery gallery-{layout} reveal" style="--th:{h};--ratio:{ratio}">'
            + "".join(items) + "</div>")


def smart_layout(n):
    a = n.get("attrs") or {}
    v = a.get("variantKey")
    o = a.get("options") or {}
    cells = n.get("content") or []
    size = o.get("cellSize") or 15
    cls = f"smart smart-{v}"
    style = f"--cell:{size}"
    if v == "timeline":
        if o.get("hasLine"):
            cls += " has-line"
        if o.get("twoSided"):
            cls += " two-sided"
        if o.get("numbered"):
            cls += " numbered"
    if v == "imagesText":
        shape = o.get("imageShape") or "landscape"
        style += f";--ratio:{ {'portrait': '3/4', 'square': '1/1', 'landscape': '16/10', 'circle': '1/1'}.get(shape, '16/10')}"
        if shape == "circle":
            cls += " circle"
    out = []
    for i, c in enumerate(cells, 1):
        ca = c.get("attrs") or {}
        im = ca.get("image") or {}
        # Kachel mit eigenem Foto erst zeigen, wenn die Datei vorhanden ist
        if (im.get("src") or "").startswith("/") and not os.path.exists(os.path.join(ROOT, im["src"].lstrip("/"))):
            print("  Hinweis: Foto fehlt, Kachel ausgeblendet:", im["src"])
            continue
        lead = ""
        if v == "imagesText" and im.get("src"):
            lead = f'<div class="cell-img"><img src="{img(im["src"], 1200)}" alt="" loading="lazy" data-lightbox></div>'
        elif v == "iconsText":
            q = ((im.get("loadImageParams") or {}).get("query")) or "star"
            lead = f'<div class="cell-icon"><i class="fa-solid fa-{esc(q)}"></i></div>'
        elif v == "timeline" and o.get("numbered"):
            lead = f'<div class="cell-num">{i}</div>'
        elif v == "timeline":
            lead = '<div class="cell-num dot"></div>'
        elif v == "bullets":
            lead = f'<div class="cell-num">{i}</div>' if o.get("numbered") else '<div class="cell-dot"></div>'
        elif v == "arrows":
            lead = '<div class="cell-arrow"></div>'
        out.append(f'<div class="cell reveal">{lead}<div class="cell-body">{kids(c)}</div></div>')
    return f'<div class="{cls}" style="{style}">' + "".join(out) + "</div>"


def embed(n):
    a = n.get("attrs") or {}
    url = a.get("url") or (a.get("embed") or {}).get("url") or a.get("sourceUrl")
    meta = a.get("meta") or {}
    thumb = (a.get("thumbnail") or {}).get("src")
    title = esc(meta.get("title") or url)
    desc = esc(meta.get("description") or "")
    host = esc(urllib.parse.urlparse(url).netloc)
    th = f'<div class="embed-thumb"><img src="{img(thumb, 1600)}" alt="{title}" loading="lazy"></div>' if thumb else ""
    return (f'<a class="embed-card reveal" href="{esc(url)}" target="_blank" rel="noopener">{th}'
            f'<div class="embed-meta"><div class="embed-title">{title}</div>'
            + (f'<div class="embed-desc">{desc}</div>' if desc else "")
            + f'<div class="embed-host"><i class="fa-solid fa-arrow-up-right-from-square"></i> {host}</div></div></a>')


def render_card(card):
    a = card["attrs"]
    layout = a.get("layout") or "blank"
    size = a.get("cardSize") or "default"
    body, accent, image_card = "", None, None
    for item in card.get("content") or []:
        if item["type"] == "cardLayoutItem":
            body += kids(item)
        elif item["type"] == "cardAccentLayoutItem":
            accent = bg_image_src((item.get("attrs") or {}).get("background"))
        elif item["type"] == "cardImageItem":
            image_card = ((item.get("attrs") or {}).get("image") or {}).get("src")
        else:
            body += render(item)

    styles = []
    cbg = (a.get("background") or {})
    if cbg.get("type") == "color":
        styles.append(f"--card-bg:{cbg['color']['hex']}")
    contbg = ((a.get("container") or {}).get("background") or {})
    if contbg.get("type") == "color":
        styles.append(f"--section-bg:{contbg['color']['hex']}")
    if (a.get("container") or {}).get("width"):
        styles.append(f"--content-w:var(--w-{a['container']['width']})")
    if contbg.get("type") == "image":
        styles.append(f"--section-img:url('{img(contbg['image']['src'])}')")

    classes = ["card", f"layout-{layout}", f"size-{size}"]
    if contbg:
        classes.append("has-section-bg")
    if image_card:
        return (f'<section id="{a["id"]}" class="card image-card size-{size}" style="{";".join(styles)}">'
                f'<div class="card-inner"><img class="reveal" src="{img(image_card, 2400)}" alt="" data-lightbox></div></section>')

    accent_html = ""
    if a["id"] in ACCENT_OVERRIDES:
        accent_html = ACCENT_OVERRIDES[a["id"]]
    elif accent and layout in ("left", "right", "top"):
        accent_html = f'<div class="accent reveal"><img src="{img(accent, 1600)}" alt="" loading="lazy"></div>'
    elif accent and layout == "behind":
        styles.append(f"--behind:url('{img(accent, 2400)}')")
        classes.append("has-behind")
    return (f'<section id="{a["id"]}" class="{" ".join(classes)}" style="{";".join(styles)}">'
            f'<div class="card-inner">{accent_html if layout in ("left", "top") else ""}'
            f'<div class="card-body">{CARD_PREPEND.get(a["id"], "")}{body}</div>'
            f'{accent_html if layout == "right" else ""}</div></section>')


# Schnellzugriff auf die Apps in den Reitern (und im Startseiten-Menü)
APPS = {
    "reise": ("compass", "Reiseführer-App", "Rom, Berlin, Paris, China, Kraków, Budapest",
              "https://per-g.github.io/Reiseplaner/index.html"),
    "traumauto": ("car-side", "Traumauto-App", "284 Fahrzeuge im persönlichen Ranking", "/traumauto/"),
    "superhealth": ("calculator", "SuPER Health", "Rechner, Ziele und Wissen", "https://su-per-health.vercel.app/"),
    "tracking": ("chart-line", "SuPER Health Tracking", "Kalorien, Makros, Barcode und KI-Foto",
                 "https://su-per-health.vercel.app/tracking"),
    "kueche": ("utensils", "SuPER Küche", "Familien-Wochenplaner und Einkauf",
               "https://su-per-health.vercel.app/wochenplaner/"),
}
NAV_MENUS = {
    "Reiseziele & Fotografie": ["reise"],
    "Auto & Technik": ["traumauto"],
    "Fitness & Ernährung": ["superhealth", "tracking", "kueche"],
    "Games": "games",
}


def game_list():
    """Spiele aus der Games-Seite (Titel, Link, Vorschaubild)."""
    data = json.load(open(os.path.join(SRC, "gamma-json", "per-games.json"), encoding="utf8"))
    out = []

    def walk(n):
        if n.get("type") == "embed":
            a = n["attrs"]
            title = re.sub(r"^[^\w]+", "", (a.get("meta") or {}).get("title") or a["url"]).strip()
            title = {"ALIEN CLONES": "Alien Clones", "Stickman Elite Sniper: Rooftop Rescue": "Stickman Sniper",
                     "HAWO Validation Simulator 3000": "HAWO Validation Simulator",
                     "Hühnerjagd - Wellenmodus": "Hühnerjagd"}.get(title, title)
            if "HTML-Studio" not in a["url"]:  # Werkzeug, kein Spiel
                out.append((title, a["url"], (a.get("thumbnail") or {}).get("src")))
        for c in n.get("content") or []:
            walk(c)
    walk(data)
    return out


def app_target(href):
    return ' target="_blank" rel="noopener"' if href.startswith("http") or href.startswith("/traumauto") else ""


def nav_flyout(text, page_href):
    menu = NAV_MENUS.get(text)
    if not menu:
        return ""
    if menu == "games":
        items = "".join(
            f'<a class="fly-game" href="{esc(u)}" target="_blank" rel="noopener">'
            f'<img src="{img(t, 600) if t else ""}" alt="" loading="lazy"><span>{esc(n)}</span></a>'
            for n, u, t in game_list())
        body = f'<div class="fly-games">{items}</div>'
        label = "Spiele direkt starten"
    else:
        items = "".join(
            f'<a class="fly-app" href="{esc(APPS[k][3])}"{app_target(APPS[k][3])}>'
            f'<i class="fa-solid fa-{APPS[k][0]}"></i><span><b>{esc(APPS[k][1])}</b><small>{esc(APPS[k][2])}</small></span></a>'
            for k in menu)
        body = f'<div class="fly-apps">{items}</div>'
        label = "Apps direkt öffnen"
    return (f'<div class="flyout"><div class="fly-inner"><div class="fly-label">{label}</div>{body}'
            f'<a class="fly-page" href="{esc(page_href)}">Zur Seite {esc(text)} ›</a></div></div>')


def render_nav(current):
    nb = THEME["nav"]["content"][0]
    links, buttons = [], []

    def nav_link(text, href):
        active = ' aria-current="page"' if href == current else ""
        fly = nav_flyout(text, href)
        link = f'<a class="nav-link" href="{esc(href)}"{active}>{esc(text)}</a>'
        if not fly:
            return link
        return f'<div class="nav-item has-menu">{link}{fly}</div>'

    for grp in nb.get("content") or []:
        for b in grp.get("content") or []:
            href = map_href(b["attrs"].get("href"))
            text = "".join(x.get("text", "") for x in b.get("content") or [])
            text = RENAME.get(text, text)
            active = ' aria-current="page"' if href == current else ""
            if grp["type"] == "navbarLinks":
                links.append(nav_link(text, href))
                for after, ntext, nhref in EXTRA_NAV:
                    if after == text:
                        links.append(nav_link(ntext, nhref))
            else:
                buttons.append(f'<a class="nav-btn" href="{esc(href)}"{active}>{esc(text)}</a>')
    # Gamma zeigt die Buttons in umgekehrter Reihenfolge (Kontakt vor Impressum)
    buttons.reverse()
    return ('<header class="nav"><div class="nav-inner">'
            f'<a class="nav-brand" href="/" aria-label="Startseite"><img src="{PROFILE}" alt=""><span>Paul P.E.R.</span></a>'
            '<button class="nav-toggle" aria-label="Menü" aria-expanded="false"><span></span><span></span><span></span></button>'
            f'<nav class="nav-menu"><div class="nav-links">{"".join(links)}</div>'
            f'<div class="nav-buttons">{"".join(buttons)}</div></nav></div></header>')


def page_html(doc_id, slug, data, meta):
    doc = data["content"][0]
    da = doc["attrs"]
    bg = bg_image_src(da.get("background")) or THEME["theme"]["config"]["background"]["image"]["src"]
    key, eyebrow = PAGE_KEYS.get(slug, ("start", ""))
    visible = [c for c in doc.get("content") or [] if not (c.get("attrs") or {}).get("hidden")]
    cards = "".join(render_card(c) for c in visible)
    # Überzeile vor die erste Überschrift der Seite setzen
    cards = cards.replace('<h1 class="h1"', f'<div class="eyebrow">{esc(eyebrow)}</div><h1 class="h1 hero-title"', 1)
    for pos, fname in EXTRA_SECTIONS.get(slug, []):
        extra = open(os.path.join(SRC, "extra", fname), encoding="utf8").read()
        # nach der pos-ten Karte einfügen
        idx = 0
        for _ in range(pos):
            idx = cards.index("</section>", idx) + len("</section>")
        cards = cards[:idx] + extra + cards[idx:]
    current = "/" + slug + "/" if slug else "/"
    title = esc(RENAME.get(meta["title"], meta["title"]))
    desc = esc((meta.get("description") or "").split("\n")[0])
    fmt = da.get("format", "webpage")
    return f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css">
<link rel="stylesheet" href="/assets/style.css">
</head>
<body class="format-{fmt}" data-page="{key}" style="--page-bg:url('{img(bg, 2400)}')">
<div class="page-bg" aria-hidden="true"></div>
{render_nav(current)}
<main>
{cards}
</main>
<div class="lightbox" hidden><button class="lb-close" aria-label="Schließen">&times;</button><button class="lb-prev" aria-label="Zurück">&#8249;</button><img alt=""><button class="lb-next" aria-label="Weiter">&#8250;</button></div>
<script src="/assets/site.js" defer></script>
</body>
</html>
"""


def main():
    metas = {p["id"]: p for p in THEME["pages"]}
    metas.setdefault("q1vxh31oxywk87c", {"title": "PER", "description": "Willkommen in meiner Welt!"})
    out = []
    for doc_id, (slug, fname) in PAGES.items():
        data = json.load(open(os.path.join(SRC, "gamma-json", fname), encoding="utf8"))
        meta = dict(metas.get(doc_id) or {"title": "PER"})
        if doc_id == "q1vxh31oxywk87c":
            meta["title"] = "PER"
        out.append((slug, page_html(doc_id, slug, data, meta)))
    index_doc = json.load(open(os.path.join(SRC, "gamma-json", "index.json"), encoding="utf8"))
    for slug, (fname, title, desc) in CUSTOM_PAGES.items():
        EXTRA_SECTIONS.setdefault(slug, []).insert(0, (0, fname))
        doc = {"type": "doc", "content": [{"type": "document", "attrs": {
            "background": index_doc["content"][0]["attrs"]["background"], "format": "webpage"}, "content": []}]}
        out.append((slug, page_html(slug, slug, doc, {"title": title, "description": desc})))
    for slug, h in out:
        d = os.path.join(ROOT, slug) if slug else ROOT
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w", encoding="utf8") as f:
            f.write(h)
        print("  Seite:", "/" + slug)
    not_found = {"type": "doc", "content": [{"type": "document", "attrs": {}, "content": [{
        "type": "card", "attrs": {"id": "nicht-gefunden", "layout": "blank", "cardSize": "contained",
                                  "background": {"type": "none"}},
        "content": [{"type": "cardLayoutItem", "content": [
            {"type": "heading", "attrs": {"level": 1}, "content": [{"type": "text", "text": "Seite nicht gefunden"}]},
            {"type": "paragraph", "content": [{"type": "text", "text": "Diese Seite gibt es leider nicht (mehr)."}]},
            {"type": "buttonGroup", "content": [{"type": "button", "attrs": {
                "href": "https://gamma.app/docs/q1vxh31oxywk87c", "variant": "solid"},
                "content": [{"type": "text", "text": "Zur Startseite"}]}]}]}]}]}]}
    with open(os.path.join(ROOT, "404.html"), "w", encoding="utf8") as f:
        f.write(page_html("404", "404", not_found, {"title": "PER - Seite nicht gefunden"}))
    print("  Seite: /404.html")
    print(f"  {len(IMAGES)} Bilder referenziert")
    if WARN:
        print("  Nicht unterstützt:", sorted(WARN))
    if DOWNLOAD:
        download_all()
        print("  Bilder heruntergeladen nach assets/img")


if __name__ == "__main__":
    main()
