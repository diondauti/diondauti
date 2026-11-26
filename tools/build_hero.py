#!/usr/bin/env python3
"""Generate hero.svg: a neural network with forward passes pulsing through it.

Two waves run per cycle, half a cycle apart, so the network is never at rest.

Layers light up left to right on a loop, signals travel along the edges, and
nodes flare as the wave reaches them. Pure SMIL so it animates inside a GitHub
README; deterministic layout via a fixed seed so re-running gives the same file.

Run:  python3 tools/build_hero.py
"""
import random

W, H = 760, 212
BG, PANEL = "#0d1117", "#11161d"
EDGE_C = "#2b313a"
ACCENT = "#4f9ff2"
ACCENT_2 = "#7ee2c7"
FG, MUTED, DIM = "#e8eef5", "#8b949e", "#6e7681"
MONO = ('ui-monospace, "SFMono-Regular", "SF Mono", Menlo, Consolas, '
        '"Liberation Mono", monospace')

LAYERS = [5, 7, 7, 4]          # nodes per layer
NET_X0, NET_X1 = 452, 724      # horizontal extent of the network
NET_CY, NET_H = H / 2, 162
CYCLE = 3.0                    # seconds per forward pass
STEP = 0.36                    # delay between layers
PARTICLES = 64
LEAD = 0.2                     # quiet lead-in before the wave starts

random.seed(11)


def bump(center, half, base, peak):
    """Two short bumps per cycle, at `center` and half a cycle later.

    Returns (values, keyTimes) for an <animate>.
    """
    times, vals = [0.0], [base]
    for c in (center, center + 0.5):
        for t, v in ((c - half, base), (c, peak), (c + half, base)):
            t = min(1.0, max(times[-1], t))
            times.append(t)
            vals.append(v)
    times.append(1.0)
    vals.append(base)
    return (";".join(str(v) for v in vals), ";".join(f"{t:.4f}" for t in times))


def build():
    # Node positions
    nodes = []
    for li, count in enumerate(LAYERS):
        x = NET_X0 + (NET_X1 - NET_X0) * li / (len(LAYERS) - 1)
        span = NET_H if count > 1 else 0
        col = []
        for ni in range(count):
            t = 0 if count == 1 else ni / (count - 1)
            y = NET_CY - span / 2 + span * t
            y += random.uniform(-4.5, 4.5)
            col.append((x, y))
        nodes.append(col)

    out = []

    # Panel, soft glow behind the network, faint dot field
    out.append(f'<defs>'
               f'<radialGradient id="g" cx=".5" cy=".5" r=".5">'
               f'<stop offset="0" stop-color="{ACCENT}" stop-opacity=".16"/>'
               f'<stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/>'
               f'</radialGradient>'
               f'<pattern id="d" width="20" height="20" patternUnits="userSpaceOnUse">'
               f'<circle cx="1.3" cy="1.3" r="1" fill="{MUTED}" fill-opacity=".09"/>'
               f'</pattern>'
               f'<clipPath id="panel"><rect width="{W}" height="{H}" rx="10"/></clipPath>'
               f'</defs>')
    out.append(f'<g clip-path="url(#panel)">')
    out.append(f'<rect width="{W}" height="{H}" fill="{PANEL}"/>')
    out.append(f'<rect width="{W}" height="{H}" fill="url(#d)"/>')
    out.append(f'<ellipse cx="{(NET_X0 + NET_X1) / 2}" cy="{NET_CY}" rx="210" ry="118" fill="url(#g)"/>')

    # Edges: stroke-opacity bump as the wave crosses each layer
    edges = []
    for li in range(len(LAYERS) - 1):
        centre = (LEAD + (li + 0.5) * STEP) / CYCLE
        ev, ekt = bump(centre, 0.06, 0.09, 0.6)
        for (x1, y1) in nodes[li]:
            for (x2, y2) in nodes[li + 1]:
                edges.append(((x1, y1), (x2, y2), li))
                out.append(
                    f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                    f'stroke="{ACCENT}" stroke-width="0.9" stroke-opacity="0.09">'
                    f'<animate attributeName="stroke-opacity" '
                    f'values="{ev}" keyTimes="{ekt}" '
                    f'dur="{CYCLE}s" repeatCount="indefinite"/></line>')

    # Signals travelling along a sample of edges
    for (p1, p2, li) in random.sample(edges, min(PARTICLES, len(edges))):
        centre = (LEAD + (li + 0.5) * STEP) / CYCLE
        travel = STEP / CYCLE
        a, b = centre - travel / 2, centre + travel / 2
        ov, okt = bump(centre, travel / 2, 0, 1)
        out.append(
            f'<circle r="2.3" fill="{ACCENT_2}" opacity="0">'
            f'<animateMotion path="M{p1[0]:.1f},{p1[1]:.1f} L{p2[0]:.1f},{p2[1]:.1f}" '
            f'keyPoints="0;0;1;0;1;1" '
            f'keyTimes="0;{a:.4f};{b:.4f};{a+0.5:.4f};{b+0.5:.4f};1" calcMode="linear" '
            f'dur="{CYCLE}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="{ov}" keyTimes="{okt}" '
            f'dur="{CYCLE}s" repeatCount="indefinite"/></circle>')

    # Nodes: flare as the wave arrives
    for li, col in enumerate(nodes):
        centre = (LEAD + li * STEP) / CYCLE
        sv, skt = bump(centre, 0.07, 0.4, 1)
        rv, _ = bump(centre, 0.07, 4, 6)
        hv, _ = bump(centre, 0.07, 0, 0.22)
        for (x, y) in col:
            out.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{BG}" '
                f'stroke="{ACCENT}" stroke-width="1.2" stroke-opacity="0.4">'
                f'<animate attributeName="stroke-opacity" values="{sv}" '
                f'keyTimes="{skt}" dur="{CYCLE}s" repeatCount="indefinite"/>'
                f'<animate attributeName="r" values="{rv}" keyTimes="{skt}" '
                f'dur="{CYCLE}s" repeatCount="indefinite"/></circle>')
            out.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="10" fill="{ACCENT}" opacity="0">'
                f'<animate attributeName="opacity" values="{hv}" keyTimes="{skt}" '
                f'dur="{CYCLE}s" repeatCount="indefinite"/></circle>')

    # Left-hand type, settles once and stays put
    out.append(
        f'<g opacity="0"><animate attributeName="opacity" to="1" dur="0.7s" begin="0.15s" fill="freeze"/>'
        f'<text x="40" y="84" font-size="27" font-weight="600" fill="{FG}">dion dauti</text>'
        f'<text x="40" y="112" font-size="13.5" fill="{MUTED}">machine learning and full stack developer</text>'
        f'<text x="40" y="134" font-size="13.5" fill="{MUTED}">tirana, albania</text></g>')
    out.append(
        f'<g opacity="0"><animate attributeName="opacity" to="1" dur="0.7s" begin="0.5s" fill="freeze"/>'
        f'<rect x="40" y="152" width="3" height="13" fill="{ACCENT}"/>'
        f'<text x="52" y="163" font-size="11.5" fill="{DIM}">forward pass</text></g>')

    out.append('</g>')
    out.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="10" '
               f'fill="none" stroke="{EDGE_C}"/>')

    label = ("dion dauti, machine learning and full stack developer, tirana, albania, "
             "beside an animated neural network with a forward pass running through it")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}" role="img" aria-label="{label}">\n'
            f'<title>{label}</title>\n'
            f'<style>text{{font-family:{MONO};}}</style>\n'
            + "\n".join(out) + "\n</svg>\n")


if __name__ == "__main__":
    s = build()
    with open("hero.svg", "w") as f:
        f.write(s)
    print(f"hero.svg written: {W}x{H}, {len(s)} bytes")
