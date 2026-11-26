#!/usr/bin/env python3
"""Generate header.svg: an animated terminal for the GitHub profile README.

Typing is done with SMIL <animate> on clipPath rects using calcMode="discrete",
so each frame reveals exactly one more character. No JavaScript, no web fonts,
no external services, which is what lets it animate inside a GitHub README.

Edit SCRIPT below and re-run:  python3 tools/build_header.py
"""

# (kind, text) - "cmd" lines are typed out, "out" lines appear at once.
SCRIPT = [
    ("cmd", "python3 train_model.py"),
    ("out", "Model trained successfully"),
    ("cmd", "python3 verify_js_matches_sklearn.py"),
    ("out", "max difference: 0.000000"),
    ("cmd", "npm start"),
    ("out", "booking api listening on :3000"),
    ("cmd", "whoami"),
    ("name", "dion dauti"),
    ("out", "machine learning and full stack developer, tirana"),
]

# Geometry
FS = 15.5              # font size
CW = FS * 0.6          # monospace advance width
LH = 29                # line height
PAD_X = 26
BAR_H = 42
TOP = BAR_H + 30
WIDTH = 760
HEIGHT = TOP + LH * len(SCRIPT) + 26

# Timing (seconds)
PER_CHAR = 0.042
AFTER_CMD = 0.34
AFTER_OUT = 0.42
START = 0.45

# Palette: one accent, everything else neutral.
BG = "#0d1117"
BAR = "#161b22"
EDGE = "#2b313a"
PROMPT = "#4f9ff2"
CMD = "#e8eef5"
OUT = "#8b949e"
NAME = "#ffffff"
LABEL = "#6e7681"

PROMPT_STR = "$ "


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    parts = []
    clips = []
    t = START

    for i, (kind, text) in enumerate(SCRIPT):
        y = TOP + i * LH
        baseline = y + FS * 0.78

        if kind == "cmd":
            n = len(text)
            dur = n * PER_CHAR
            x0 = PAD_X + len(PROMPT_STR) * CW
            full = n * CW

            # Per-character reveal: one discrete value per character.
            vals = ";".join(f"{round(k * CW, 2)}" for k in range(n + 1))
            cid = f"c{i}"
            clips.append(
                f'<clipPath id="{cid}"><rect x="{round(x0,2)}" y="{y - 4}" '
                f'height="{LH}" width="0">'
                f'<animate attributeName="width" values="{vals}" '
                f'begin="{round(t,3)}s" dur="{round(dur,3)}s" '
                f'calcMode="discrete" fill="freeze"/></rect></clipPath>'
            )

            # Prompt appears when the line starts.
            parts.append(
                f'<text class="p" x="{PAD_X}" y="{round(baseline,2)}" opacity="0">'
                f'<set attributeName="opacity" to="1" begin="{round(t,3)}s"/>'
                f'{esc(PROMPT_STR.strip())}</text>'
            )
            parts.append(
                f'<g clip-path="url(#{cid})"><text class="c" '
                f'x="{round(x0,2)}" y="{round(baseline,2)}">{esc(text)}</text></g>'
            )

            # Cursor steps along with the typing, then hides.
            cvals = ";".join(f"{round(x0 + k * CW, 2)}" for k in range(n + 1))
            parts.append(
                f'<rect class="cur" x="{round(x0,2)}" y="{y - 1}" width="{round(CW,2)}" '
                f'height="{round(FS,2)}" opacity="0">'
                f'<set attributeName="opacity" to="1" begin="{round(t,3)}s"/>'
                f'<animate attributeName="x" values="{cvals}" begin="{round(t,3)}s" '
                f'dur="{round(dur,3)}s" calcMode="discrete" fill="freeze"/>'
                f'<set attributeName="opacity" to="0" begin="{round(t + dur,3)}s"/>'
                f'</rect>'
            )
            t += dur + AFTER_CMD
        else:
            cls = "n" if kind == "name" else "o"
            parts.append(
                f'<text class="{cls}" x="{PAD_X}" y="{round(baseline,2)}" opacity="0">'
                f'<set attributeName="opacity" to="1" begin="{round(t,3)}s"/>'
                f'{esc(text)}</text>'
            )
            t += AFTER_OUT

    # Resting cursor, blinks from the end of the sequence onwards.
    y = TOP + len(SCRIPT) * LH
    parts.append(
        f'<rect class="cur" x="{PAD_X}" y="{y - 1}" width="{round(CW,2)}" '
        f'height="{round(FS,2)}" opacity="0">'
        f'<set attributeName="opacity" to="1" begin="{round(t,3)}s"/>'
        f'<animate attributeName="opacity" values="1;1;0;0" dur="1.05s" '
        f'begin="{round(t,3)}s" repeatCount="indefinite"/></rect>'
    )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{round(HEIGHT)}" viewBox="0 0 {WIDTH} {round(HEIGHT)}" role="img" aria-label="Terminal running training, verification and server commands, then printing: dion dauti, machine learning and full stack developer, tirana">
<title>dion dauti, machine learning and full stack developer</title>
<defs>
<style>
text {{ font-family: ui-monospace, "SFMono-Regular", "SF Mono", Menlo, Consolas, "Liberation Mono", monospace; font-size: {FS}px; white-space: pre; }}
.p {{ fill: {PROMPT}; }}
.c {{ fill: {CMD}; }}
.o {{ fill: {OUT}; }}
.n {{ fill: {NAME}; font-weight: 600; }}
.l {{ fill: {LABEL}; font-size: 12.5px; }}
.cur {{ fill: {PROMPT}; }}
</style>
{chr(10).join(clips)}
</defs>
<rect x="0.5" y="0.5" width="{WIDTH-1}" height="{round(HEIGHT)-1}" rx="9" fill="{BG}" stroke="{EDGE}"/>
<path d="M0.5 9.5a9 9 0 0 1 9-9h{WIDTH-20}a9 9 0 0 1 9 9v{BAR_H-9}H0.5z" fill="{BAR}"/>
<line x1="0.5" y1="{BAR_H}.5" x2="{WIDTH-0.5}" y2="{BAR_H}.5" stroke="{EDGE}"/>
<text class="l" x="{PAD_X}" y="26">dion@dev ~/projects</text>
{chr(10).join(parts)}
</svg>
'''
    with open("header.svg", "w") as f:
        f.write(svg)
    print(f"header.svg written: {WIDTH}x{round(HEIGHT)}, sequence ends at {t:.1f}s")


if __name__ == "__main__":
    main()
