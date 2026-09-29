from pathlib import Path
import re

DURATION_MS = 20900
SEGMENT_LAG_MS = 240
MAX_GROWTH_SEGMENTS = 96


def add_growth(svg: str) -> str:
    # Platane's SVG contains one CSS keyframe per contribution cell.  These
    # keyframes are the authoritative "eaten" timestamps; do not alter the
    # contribution grid or its colors.
    events = []
    pattern = re.compile(
        r"@keyframes\s+c[0-9a-z]+\{\s*([0-9]+(?:\.[0-9]+)?)%\{fill:(var\(--c[1-4]\))\}"
    )
    for match in pattern.finditer(svg):
        events.append(float(match.group(1)))

    events = sorted(set(events))[:MAX_GROWTH_SEGMENTS]
    if not events:
        raise RuntimeError("No non-zero contribution eating events found")

    # Reuse the exact first native snake rectangle dimensions. This guarantees
    # that every growth segment has the original snake-cell size: no scaling.
    head_rect = re.search(
        r'<rect\s+class="s\s+s0"\s+x="([^"]+)"\s+y="([^"]+)"\s+'
        r'width="([^"]+)"\s+height="([^"]+)"\s+rx="([^"]+)"\s+ry="([^"]+)"\s*/?>',
        svg,
    )
    if not head_rect:
        raise RuntimeError("Native snake head rectangle not found")

    x, y, width, height, rx, ry = head_rect.groups()

    css = [
        "<style>",
        ".snake-growth{fill:var(--cs);shape-rendering:geometricPrecision;opacity:0;animation-timing-function:linear,linear;animation-iteration-count:infinite,infinite;animation-fill-mode:both,both;}",
    ]
    rects = ['<g aria-label="contribution-driven snake growth">']

    for index, event in enumerate(events, 1):
        lag = index * SEGMENT_LAG_MS
        before = max(0.0, event - 0.02)
        css.append(
            f".snake-growth-{index}{{"
            f"animation-name:s0,grow{index};"
            f"animation-duration:{DURATION_MS}ms,{DURATION_MS}ms;"
            f"animation-delay:-{lag}ms,0ms;"
            "}"
        )
        css.append(
            f"@keyframes grow{index}{{"
            f"0%,{before:.2f}%{{opacity:0;}}"
            f"{event:.2f}%,100%{{opacity:1;}}"
            "}"
        )
        rects.append(
            f'<rect class="snake-growth snake-growth-{index}" '
            f'x="{x}" y="{y}" width="{width}" height="{height}" '
            f'rx="{rx}" ry="{ry}" />'
        )

    rects.append("</g>")
    css.append("</style>")

    # Insert immediately before the original snake elements. The original
    # snake remains untouched; these are additional normal-size tail segments.
    marker = '<rect class="s s0"'
    position = svg.find(marker)
    if position < 0:
        raise RuntimeError("Native snake element marker not found")

    return svg[:position] + "".join(css) + "".join(rects) + svg[position:]


for svg_path in sorted(Path("dist").glob("github-snake*.svg")):
    original = svg_path.read_text(encoding="utf-8")
    modified = add_growth(original)
    svg_path.write_text(modified, encoding="utf-8")
    print(f"Generated growth animation: {svg_path}")
