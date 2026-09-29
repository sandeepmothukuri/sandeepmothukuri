from pathlib import Path
import re

DURATION_MS = 20900
GRID_STEP_MS = 100
MAX_GROWTH_SEGMENTS = 96


def add_growth(svg: str) -> str:
    # Platane's generated SVG contains one cN keyframe for each non-zero
    # contribution cell. Its first keyframe percentage is the exact moment
    # that cell is eaten by the original snake.
    events = [
        float(value)
        for value in re.findall(
            r"@keyframes\s+c[0-9a-z]+\{\s*([0-9]+(?:\.[0-9]+)?)%\{fill:var\(--c[1-4]\)\}",
            svg,
        )
    ]
    events = sorted(set(events))[:MAX_GROWTH_SEGMENTS]
    if not events:
        raise RuntimeError("No contribution-eating events found")

    # The original generator uses 12px contribution cells and the snake is
    # rendered on the same native grid. We deliberately do not scale these
    # dimensions. The extra segments are ordinary 12x12 snake cells.
    native = re.search(
        r'<rect\s+class="s(?:\s+s0)?"[^>]*?width="([^"]+)"[^>]*?height="([^"]+)"[^>]*?(?:rx="([^"]+)")?[^>]*?(?:ry="([^"]+)")?[^>]*/?>',
        svg,
    )
    if native:
        width, height, rx, ry = native.groups()
        rx = rx or "0"
        ry = ry or rx
    else:
        width = height = "12"
        rx = ry = "2"

    css = [
        "<style>",
        ".snake-growth{fill:var(--cs);shape-rendering:geometricPrecision;opacity:0;animation-timing-function:linear,linear;animation-iteration-count:infinite,infinite;animation-fill-mode:both,both;}",
    ]
    rects = ['<g aria-label="contribution-driven snake growth">']

    for index, event in enumerate(events, 1):
        # One native grid-step behind the head for each added body segment.
        lag = index * GRID_STEP_MS
        css.append(
            f".snake-growth-{index}{{animation-name:s0,grow{index};"
            f"animation-duration:{DURATION_MS}ms,{DURATION_MS}ms;"
            f"animation-delay:-{lag}ms,0ms;}}"
        )
        css.append(
            f"@keyframes grow{index}{{0%,{event:.2f}%{{opacity:0;}}"
            f"{event:.2f}%,100%{{opacity:1;}}}}"
        )
        rects.append(
            f'<rect class="snake-growth snake-growth-{index}" '
            f'x="0" y="-16" width="{width}" height="{height}" '
            f'rx="{rx}" ry="{ry}" />'
        )

    rects.append("</g>")
    css.append("</style>")

    # Overlay the additional body cells. The original snake is untouched.
    return svg.replace("</svg>", "".join(css) + "".join(rects) + "</svg>", 1)


for svg_path in sorted(Path("dist").glob("github-snake*.svg")):
    original = svg_path.read_text(encoding="utf-8")
    modified = add_growth(original)
    svg_path.write_text(modified, encoding="utf-8")
    print(f"Growth segments added: {svg_path}")
