"""Publish the built Rentals Archetypes page as this site (docs/, served by GitHub Pages).

    python tools/publish.py --src <the built page, rentals_world.html> [--relief <a sharper relief image>]

The page is built elsewhere as one self-contained document. Here it becomes a site:
  - the heavy parts leave the page and load beside it: the land's relief (assets/relief.webp), each market's water map
    (assets/water-<n>.webp) and the map's data (assets/geo.js, loaded after the page has drawn);
  - the title bar's internal code stamp becomes the data credit, and a Portfolio link is added;
  - every code comment and every internal reference is stripped;
  - a page that carries a local path, an outside address, an email or a phone number is refused.
Where the page was built is never written into the output. Rerun after each data cycle.
"""
import argparse
import base64
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
ASSETS = DOCS / "assets"
PORTFOLIO = "https://plotbot2023.github.io/portfolio/"
CHARSET = re.compile(r'<meta\s+charset=["\']?utf-?8["\']?\s*/?>', re.I)
STAMP = "st.innerHTML='<i>code</i><b>'+code+'</b>';"
LEAKS = {"a local path": re.compile(r"\b[A-Z]:\\\\?(Users|dev)\b"),
         "an outside address": re.compile(r"https?://(?!www\.w3\.org/)[^\s\"'<>)]+"),
         "an email": re.compile(r"[\w.+-]+@[\w-]+\.[a-z]{2,}"),
         "a phone number": re.compile(r"\(?\b\d{3}\)?[ .-]\d{3}[ .-]\d{4}\b")}
GUARD = ("the owner", "fuck", "issue #", "Rules of Claude")
GEO = re.compile(r'<script type="application/json" class="ra-geod">(.*?)</script>', re.S)
RELIEF = re.compile(r'(<image class="ra-grl" href=")data:image/webp;base64,([A-Za-z0-9+/=]+)(")')
# the map's data arrives after the page has drawn (a deferred script runs before the page's own start), and puts
# itself where the page looks for it
GEO_JS = ("(function(){var s=document.createElement('script');s.type='application/json';s.className='ra-geod';"
          "s.textContent=JSON.stringify(%s);var at=document.getElementById('ra-geo-slot');"
          "at.parentNode.replaceChild(s,at);})();")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, type=pathlib.Path)
    ap.add_argument("--relief", type=pathlib.Path, help="a sharper relief image to serve in place of the page's own")
    a = ap.parse_args()
    t = a.src.read_text(encoding="utf-8")
    for what, rx in LEAKS.items():
        m = rx.search(t)
        if m:
            raise SystemExit(f"the page carries {what} ({m.group(0)[:60]!r}): not published")
    t, n = CHARSET.subn('<meta charset="utf-8">', t, count=1)
    if n != 1:
        raise SystemExit("no charset tag found")
    if t.count(STAMP) != 1:
        raise SystemExit("the title bar's stamp script was not found: the credit could not be placed")
    asof = re.search(r'<meta name="gx-asof" content="(\d{4}-\d{2}-\d{2})', t)
    if not asof:
        raise SystemExit("no data date found: the credit could not carry it")
    t = t.replace(STAMP, "st.title='Data: Inside Airbnb (insideairbnb.com), licensed CC BY 4.0. Nights booked are its "
                         "estimates from reviews, not bookings. Every source is listed under Method, Sources and credits.';"
                         f"st.innerHTML='<i>data</i><b>Inside Airbnb {asof.group(1)}, CC BY 4.0</b>';")
    t, n = re.subn(r'(<div class="gx-top-r">)', r'\1<a class="ra-stamp" href="@@PORTFOLIO@@" style="min-height:44px;'
                   r'text-decoration:none" aria-label="Back to the portfolio"><b>Portfolio</b></a>', t, count=1)
    if n != 1:
        raise SystemExit("no title bar found: the Portfolio link could not be placed")
    t = t.replace("</head>", "<style>@media (max-width:1799px){.gx .gx-top-r .gx-asof{display:none}}"
                             "@media (max-width:1499px){.gx-top-r .ra-stamp i{display:none}}</style></head>", 1)

    ASSETS.mkdir(parents=True, exist_ok=True)
    for old in ASSETS.glob("*"):
        old.unlink()
    # the map's data: the water maps become files, then the data itself
    g = GEO.search(t)
    sizes = {}
    if g:
        data = json.loads(g.group(1))
        for i, (market, w) in enumerate(sorted((data.get("water") or {}).items())):
            kind, b64 = re.match(r"data:image/(\w+);base64,(.*)", w["img"], re.S).groups()
            (ASSETS / f"water-{i}.{kind}").write_bytes(base64.b64decode(b64))
            w["img"] = f"assets/water-{i}.{kind}"
        js = GEO_JS % json.dumps(data, separators=(",", ":"))
        (ASSETS / "geo.js").write_text(js, encoding="utf-8", newline="\n")
        sizes["geo.js"] = len(js)
        t = t[:g.start()] + '<span id="ra-geo-slot" hidden></span>' + t[g.end():]
        t = t.replace("</head>", '<script defer src="assets/geo.js"></script></head>', 1)
    r = RELIEF.search(t)
    if r:
        img = a.relief.read_bytes() if a.relief else base64.b64decode(r.group(2))
        (ASSETS / "relief.webp").write_bytes(img)
        sizes["relief.webp"] = len(img)
        t = t[:r.start()] + r.group(1) + "assets/relief.webp" + r.group(3) + t[r.end():]

    # the working comments quote working notes and a private repository's issues: none of it ships
    t, n_css = re.subn(r"/\*.*?\*/", "", t, flags=re.S)
    t, n_html = re.subn(r"<!--(?!\[if).*?-->", "", t, flags=re.S)
    t, n_issue = re.subn(r",? \(?(?:the NFL crests' rule, )?issues? #?\d+\)?", "", t)
    for path in [None, ASSETS / "geo.js"]:
        text = t if path is None else path.read_text(encoding="utf-8")
        # packed coordinates and images are runs of base64: any four letters turn up in them by chance, so the
        # checks read the words around them only
        text = re.sub(r"[A-Za-z0-9+/=]{200,}", "", text)
        for word in GUARD:
            if word in text:
                raise SystemExit(f"{'the page' if path is None else path.name} still carries {word!r}: not published")
        for what, rx in LEAKS.items():
            m = rx.search(text)
            if m:
                raise SystemExit(f"{'the page' if path is None else path.name} carries {what} ({m.group(0)[:60]!r})")
    t = t.replace("@@PORTFOLIO@@", PORTFOLIO)
    (DOCS / "index.html").write_text(t, encoding="utf-8", newline="\n")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    print(f"docs/index.html {len(t):,} characters; {n_css + n_html} comments and {n_issue} internal references dropped; "
          + ", ".join(f"assets/{k} {v:,}" for k, v in sizes.items()))


if __name__ == "__main__":
    main()
