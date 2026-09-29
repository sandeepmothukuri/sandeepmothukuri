from pathlib import Path
import re

MAX_GROWTH_SEGMENTS = 96
GRID_LAG_PCT = 0.48


def parse_keyframes(svg: str, name: str):
    match = re.search(rf"@keyframes\s+{re.escape(name)}\{{(.*?)\}}(?:\.[a-z])", svg)
    if not match:
        raise RuntimeError(f"Snake animation {name} not found")

    body = match.group(1)
    frames = []
    for pct, x, y in re.findall(
        r"([0-9]+(?:\.[0-9]+)?)%\{transform:translate\((-?[0-9]+(?:\.[0-9]+)?)px,(-?[0-9]+(?:\.[0-9]+)?)px)\}",
        body,
    ):
        frames.append((float(pct), float(x), float(y)))
    if not frames:
        raise RuntimeError(f"No keyframes found for {name}")
    return frames


def shifted_keyframes(frames, lag):
    return sorted(((pct + lag) % 100, x, y) for pct, x, y in frames)


def keyframe_css(name, frames):
    parts = [f"@keyframes {name}{{"]
    for pct, x, y in frames:
        parts.append(f"{pct:.2f}%{{transform:translate({x:g}px,{y:g}px)}}")
    parts.append("}")
    return "".join(parts)


def add_growth(svg: str) -> str:
    # Platane emits one cN keyframe for each contribution cell. The first
    # percentage is the moment the snake reaches/eats that contribution.
    events = [
        float(value)
        for value in re.findall(
            r"@keyframes\s+c[0-9a-z]+\{([0-9]+(?:\.[0-9]+)?)%\{fill:var\(--c[1-4]\)\}",
            svg,
        )
    ]
    events = sorted(set(events))[:MAX_GROWTH_SEGMENTS]
    if not events:
        raise RuntimeError("No contribution-eating events found")

    # Reuse the native s3 geometry exactly; no scaling is applied.
    native = re.search(
        r'<rect\s+class="s\s+s3"\s+x="([^"]+)"\s+y="([^"]+)"\s+width="([^"]+)"\s+height="([^"]+)"\s+rx="([^"]+)"\s+ry="([^"]+)"\s*/>',
        svg,
    )
    if not native:
        raise RuntimeError("Native snake body geometry s3 not found")

    x, y, width, height, rx, ry = native.groups()
    head_path = parse_keyframes(svg, "s0")

    css = [
        "<style>",
        ".snake-growth{fill:var(--cs);shape-rendering:geometricPrecision;opacity:0;animation-duration:20900ms;animation-timing-function:linear;animation-iteration-count:infinite;animation-fill-mode:both;}",
    ]
    rects = ['<g aria-label="contribution-driven snake growth">']

    for index, event in enumerate(events, 1):
        lag = (index + 3) * GRID_LAG_PCT
        animation = f"g{index}"
        css.append(keyframe_css(animation, shifted_keyframes(head_path, lag)))
        css.append(
            f"@keyframes grow{index}{{0%,{event:.2f}%{{opacity:0;}}{event:.2f}%,100%{{opacity:1;}}}}"
        )
        css.append(f".snake-growth-{index}{{animation-name:{animation},grow{index};}}")
        rects.append(
            f'<rect class="snake-growth snake-growth-{index}" x="{x}" y="{y}" '
            f'width="{width}" height="{height}" rx="{rx}" ry="{ry}" />'
        )

    rects.append("</g>")
    css.append("</style>")
    return svg.replace("</svg>", "".join(css) + "".join(rects) + "</svg>", 1)


for svg_path in sorted(Path("dist").glob("github-snake*.svg")):
    original = svg_path.read_text(encoding="utf-8")
    modified = add_growth(original)
    svg_path.write_text(modified, encoding="utf-8")
    print(f"Growth segments added: {svg_path}")
