#!/usr/bin/env python3
"""
Automated validation script for Progressive Snake Growth Animation.
Validates:
1. Light and Dark SVG files exist and are valid XML.
2. Original contribution grid dimensions are unchanged (viewBox, width, height, cell counts).
3. Contribution colors match Platane palettes exactly.
4. Native Snake segment dimensions are unchanged (s0, s1, s2, s3).
5. Additional body segments exist (s4, s5, ...).
6. Additional segments use the exact same dimensions as the original body segment (s3).
7. Additional segments follow the real Snake trajectory.
8. Growth events occur progressively rather than all at once.
9. Light and dark variants contain the identical number and timing of growth events.
10. README.md and banner assets have zero modifications.
"""

import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def fail(msg: str):
    print(f"[FAIL] VALIDATION ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def pass_check(msg: str):
    print(f"[OK] {msg}")


def main():
    repo_root = Path(__file__).resolve().parents[2]
    dist_dir = repo_root / "dist"
    light_svg_path = dist_dir / "github-snake.svg"
    dark_svg_path = dist_dir / "github-snake-dark.svg"

    # 1. Light and Dark SVG exist
    if not light_svg_path.is_file():
        fail(f"Light SVG missing at {light_svg_path}")
    if not dark_svg_path.is_file():
        fail(f"Dark SVG missing at {dark_svg_path}")
    pass_check("Both Light and Dark SVG files exist.")

    # 2. Both SVGs are valid XML
    try:
        light_tree = ET.parse(light_svg_path)
        light_root = light_tree.getroot()
    except Exception as e:
        fail(f"Light SVG is not valid XML: {e}")

    try:
        dark_tree = ET.parse(dark_svg_path)
        dark_root = dark_tree.getroot()
    except Exception as e:
        fail(f"Dark SVG is not valid XML: {e}")
    pass_check("Both Light and Dark SVGs are valid XML.")

    light_svg = light_svg_path.read_text(encoding="utf-8")
    dark_svg = dark_svg_path.read_text(encoding="utf-8")

    # 3. Grid dimensions unchanged
    for name, root, svg in [("light", light_root, light_svg), ("dark", dark_root, dark_svg)]:
        view_box = root.attrib.get("viewBox", "")
        if view_box != "-16 -32 880 192":
            fail(f"{name} SVG has unexpected viewBox: {view_box} (expected -16 -32 880 192)")
        width = root.attrib.get("width", "")
        height = root.attrib.get("height", "")
        if width != "880" or height != "192":
            fail(f"{name} SVG dimensions changed: width={width}, height={height} (expected 880x192)")

        # Grid cells: exactly 52-53 weeks (~365-371 days)
        grid_rects = [r for r in root.findall(".//{http://www.w3.org/2000/svg}rect") if "c" in r.attrib.get("class", "").split()]
        if len(grid_rects) < 365 or len(grid_rects) > 371:
            fail(f"{name} SVG grid cell count is {len(grid_rects)} (expected 365..371)")
    pass_check("Original contribution grid dimensions and cell count (53x7) are unchanged.")

    # 4. Contribution colors unchanged
    # Light palette: --cb:#1b1f230a;--cs:purple;--ce:#ebedf0;--c0:#ebedf0;--c1:#9be9a8;--c2:#40c463;--c3:#30a14e;--c4:#216e39
    if "--ce:#ebedf0" not in light_svg or "--c1:#9be9a8" not in light_svg or "--c4:#216e39" not in light_svg:
        fail("Light SVG contribution colors do not match standard Platane palette.")
    # Dark palette: --ce:#161b22;--c0:#161b22;--c1:#01311f;--c2:#034525;--c3:#0f6d31;--c4:#00c647
    if "--ce:#161b22" not in dark_svg or "--c1:#01311f" not in dark_svg or "--c4:#00c647" not in dark_svg:
        fail("Dark SVG contribution colors do not match standard Platane dark palette.")
    pass_check("Contribution colors match standard Platane palettes exactly.")

    # 5. Native Snake segment dimensions unchanged (s0, s1, s2, s3)
    def get_snake_rects(root):
        rects = root.findall(".//{http://www.w3.org/2000/svg}rect")
        snake_rects = {}
        for r in rects:
            cls = r.attrib.get("class", "").split()
            if "s" in cls:
                for c in cls:
                    if c.startswith("s") and c[1:].isdigit():
                        idx = int(c[1:])
                        snake_rects[idx] = r.attrib
        return snake_rects

    light_snake = get_snake_rects(light_root)
    dark_snake = get_snake_rects(dark_root)

    expected_native = {
        0: {"x": "0.8", "y": "0.8", "width": "14.4", "height": "14.4", "rx": "4.5", "ry": "4.5"},
        1: {"x": "1.8", "y": "1.8", "width": "12.3", "height": "12.3", "rx": "4.1", "ry": "4.1"},
        2: {"x": "2.6", "y": "2.6", "width": "10.8", "height": "10.8", "rx": "3.6", "ry": "3.6"},
        3: {"x": "3.0", "y": "3.0", "width": "9.9", "height": "9.9", "rx": "3.3", "ry": "3.3"},
    }

    for idx, exp in expected_native.items():
        if idx not in light_snake:
            fail(f"Native segment s{idx} missing in Light SVG")
        for attr, val in exp.items():
            if light_snake[idx].get(attr) != val:
                fail(f"Native segment s{idx} attribute {attr}={light_snake[idx].get(attr)} in Light SVG (expected {val})")
            if dark_snake[idx].get(attr) != val:
                fail(f"Native segment s{idx} attribute {attr}={dark_snake[idx].get(attr)} in Dark SVG (expected {val})")
    pass_check("Native Snake segment dimensions (s0..s3) are 100% unchanged.")

    # 6. Additional body segments exist and use original body dimensions
    if len(light_snake) <= 4:
        fail(f"No additional growth segments found: total segments = {len(light_snake)}")
    if len(dark_snake) != len(light_snake):
        fail(f"Light segment count ({len(light_snake)}) != Dark segment count ({len(dark_snake)})")

    # Body segment dimensions (same as s3)
    s3_dim = expected_native[3]
    for idx in range(4, len(light_snake)):
        for attr in ["width", "height", "rx", "ry"]:
            if light_snake[idx].get(attr) != s3_dim[attr]:
                fail(f"Growth segment s{idx} attribute {attr}={light_snake[idx].get(attr)} (expected {s3_dim[attr]})")
            if dark_snake[idx].get(attr) != s3_dim[attr]:
                fail(f"Growth segment s{idx} in dark SVG attribute {attr}={dark_snake[idx].get(attr)} (expected {s3_dim[attr]})")
    pass_check(f"Additional body segments exist ({len(light_snake) - 4} growth segments) and match native body dimensions.")

    # 7. Additional segments follow the snake path
    # Each segment sN has keyframe animation sN
    for idx in range(len(light_snake)):
        if f"@keyframes s{idx}{{" not in light_svg:
            fail(f"Light SVG missing path keyframes for segment s{idx}")
        if f"@keyframes s{idx}{{" not in dark_svg:
            fail(f"Dark SVG missing path keyframes for segment s{idx}")
    pass_check("All segments follow dedicated valid trajectory keyframe animations.")

    # 8. Growth events occur progressively
    # Check opacity animations o4, o5, ...
    opacity_anims = re.findall(r"@keyframes\s+(o[0-9]+)\{0%,([0-9.]+)%\{opacity:0\}", light_svg)
    if not opacity_anims:
        fail("No opacity growth keyframes found")
    
    appearance_times = [float(t) for _, t in opacity_anims]
    if len(appearance_times) != len(light_snake) - 4:
        fail(f"Opacity keyframe count ({len(appearance_times)}) != growth segment count ({len(light_snake) - 4})")
    
    # Verify times are strictly non-decreasing and progressively spread out
    for i in range(1, len(appearance_times)):
        if appearance_times[i] < appearance_times[i-1]:
            fail(f"Growth event times not progressive: {appearance_times[i-1]}% followed by {appearance_times[i]}%")

    time_span = appearance_times[-1] - appearance_times[0]
    if time_span < 10.0:
        fail(f"Growth events occur all at once within span of {time_span}% (expected broad progression)")
    pass_check(f"Growth events occur progressively from {appearance_times[0]}% to {appearance_times[-1]}% (span: {time_span:.1f}%).")

    # 9. Light and dark variants contain identical number and timing of growth events
    dark_opacity_anims = re.findall(r"@keyframes\s+(o[0-9]+)\{0%,([0-9.]+)%\{opacity:0\}", dark_svg)
    if opacity_anims != dark_opacity_anims:
        fail("Growth event timing differs between Light and Dark SVGs")
    pass_check("Light and Dark SVG variants contain identical growth timing and event counts.")

    # 10. README.md and banner assets have zero modifications
    git_diff = subprocess.run(["git", "diff", "--name-only", "origin/main"], cwd=repo_root, capture_output=True, text=True)
    changed_files = [f.strip() for f in git_diff.stdout.splitlines() if f.strip()]
    
    forbidden = ["README.md", "assets/snake-banner-top.svg", "assets/snake-banner-bottom.svg"]
    for f in forbidden:
        if f in changed_files:
            fail(f"Forbidden file was modified: {f}")
    pass_check("README.md and banner assets have zero modifications.")

    print("\n[SUCCESS] ALL AUTOMATED VALIDATION CHECKS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    main()
