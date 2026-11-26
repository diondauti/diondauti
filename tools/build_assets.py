#!/usr/bin/env python3
"""Generate the profile README's animated SVG assets.

Everything is SMIL (<animate>), self-hosted, and uses the same tokens as
header.svg, so the page reads as one design rather than assembled parts.
GitHub strips <script> from READMEs, which is why none of this uses JS.

Run:  python3 tools/build_assets.py
"""
import os

BG      = "#0d1117"
PANEL   = "#11161d"
EDGE    = "#2b313a"
ACCENT  = "#4f9ff2"
FG      = "#e8eef5"
MUTED   = "#8b949e"
DIM     = "#6e7681"
MONO    = ('ui-monospace, "SFMono-Regular", "SF Mono", Menlo, Consolas, '
           '"Liberation Mono", monospace')
W = 760

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def svg(w, h, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">\n'
            f'<title>{esc(label)}</title>\n'
            f'<style>text{{font-family:{MONO};}}</style>\n{body}\n</svg>\n')

def write(path, content):
    full = os.path.join("assets", path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)
    return f"{full}  {len(content)}B"


# ---------------------------------------------------------------- section rule
def section(label):
    """A label with a hairline that draws itself to the right edge."""
    h = 38
    y = 24
    tx = 16 + 7 * len(label) * 0.6 + 14   # label advance + gap
    body = f'''<rect x="0" y="{y-7}" width="4" height="13" fill="{ACCENT}" opacity="0">
  <animate attributeName="opacity" to="1" dur="0.3s" begin="0s" fill="freeze"/></rect>
<text x="14" y="{y+4}" font-size="13.5" font-weight="600" fill="{FG}" opacity="0">
  <animate attributeName="opacity" to="1" dur="0.45s" begin="0.1s" fill="freeze"/>{esc(label)}</text>
<rect x="{round(tx,1)}" y="{y-1}" width="0" height="1" fill="{EDGE}">
  <animate attributeName="width" from="0" to="{round(W-tx,1)}" dur="0.8s" begin="0.25s"
    fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1" keyTimes="0;1"/></rect>'''
    return svg(W, h, body, f"Section: {label}")


# --------------------------------------------------------------- project cards
CARDS = [
    ("tirana-house-price-prediction", "Python", "#3572A5",
     ["Apartment price regression on 24 listings I", "collected by hand from Albanian marketplaces."],
     "no public dataset existed"),
    ("rental-pricing-rl", "Python", "#3572A5",
     ["A Q-learning agent pricing a rental night by", "night across 84 states, beating fixed pricing."],
     "+26.8%, p < 0.0001"),
    ("tirana-price-static", "HTML", "#e34c26",
     ["The same model ported to pure JavaScript and", "verified against scikit-learn, row by row."],
     "0.000000 divergence"),
    ("booking-system", "JavaScript", "#f1e05a",
     ["Appointment booking with a calendar slot", "picker, Express API and SQLite storage."],
     "full stack"),
    ("forest-fire-risk-prediction", "Python", "#3572A5",
     ["Risk classifier served over FastAPI, with a", "rule override for unambiguously unsafe input."],
     "model + rules"),
    ("F1", "Jupyter Notebook", "#DA5B0B",
     ["Every Formula 1 race result since 1950, joined", "from an API and Wikipedia into tidy CSVs."],
     "two sources, one schema"),
]

def card(name, lang, langcolor, desc, metric):
    w, h = 372, 124
    parts = [f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="8" '
             f'fill="{PANEL}" stroke="{EDGE}"/>']
    parts.append(
        f'<g opacity="0"><animate attributeName="opacity" to="1" dur="0.5s" begin="0.1s" fill="freeze"/>'
        f'<text x="18" y="31" font-size="13" font-weight="600" fill="{ACCENT}">{esc(name)}</text></g>')
    parts.append(f'<rect x="18" y="40" width="0" height="1" fill="{EDGE}">'
                 f'<animate attributeName="width" from="0" to="{w-36}" dur="0.7s" begin="0.2s" fill="freeze"/></rect>')
    for i, line in enumerate(desc):
        parts.append(
            f'<text x="18" y="{62 + i*17}" font-size="11.5" fill="{MUTED}" opacity="0">'
            f'<animate attributeName="opacity" to="1" dur="0.5s" begin="{0.3 + i*0.1}s" fill="freeze"/>'
            f'{esc(line)}</text>')
    parts.append(
        f'<g opacity="0"><animate attributeName="opacity" to="1" dur="0.5s" begin="0.55s" fill="freeze"/>'
        f'<circle cx="24" cy="{h-22}" r="5" fill="{langcolor}"/>'
        f'<text x="36" y="{h-18}" font-size="11" fill="{MUTED}">{esc(lang)}</text>'
        f'<text x="{w-18}" y="{h-18}" font-size="10.5" fill="{DIM}" text-anchor="end">{esc(metric)}</text>'
        f'</g>')
    return svg(w, h, "\n".join(parts), f"{name}: {' '.join(desc)} ({lang}, {metric})")


if __name__ == "__main__":
    out = []
    for slug, label in [("about", "about"),
                        ("work", "selected work")]:
        out.append(write(f"rules/{slug}.svg", section(label)))
    for c in CARDS:
        out.append(write(f"cards/{c[0]}.svg", card(*c)))
    print("\n".join(out))
