# Progressive Snake Growth Generator

This generator adapts the official Platane/snk engine to add progressive growth behavior while preserving 100% fidelity with the original contribution grid, colors, timing, and native segment sizing.

## Implementation Details

1. **Origin & Baseline:**
   Adapted directly from Platane's `snk/svg-only` runtime bundle.
   - Contribution fetching uses the exact GitHub GraphQL query.
   - Solver uses Platane's BFS routing algorithm to clear non-empty contribution cells.
   - Grid layout, viewBox (`-16 -32 880 192`), palettes (`github` and `github-dark`), cell dimensions (12px on 16px grid), and timing (100ms per step) are completely preserved.

2. **Growth Mechanics:**
   - The snake starts at its native length: 4 segments (`s0`, `s1`, `s2`, `s3`).
   - As the snake head moves across the grid and reaches an occupied contribution cell at timestamp `t_appear`, that cell is eaten (turns from contribution color to empty `--ce`).
   - For each contribution cell eaten, exactly ONE additional body segment (`s4`, `s5`, ...) is added.
   - The new segment appears at the exact position where the tail was at the previous step, following the identical snake trajectory lagged by its segment index:
     `position(k, step) = headPosition(step - k)`.
   - Before `t_appear`, the growth segment is invisible (`opacity: 0`). At `t_appear`, it transitions cleanly to `opacity: 1` and remains part of the snake body for the rest of the run.
   - When the animation completes and loops back to `0%`, all growth segments reset to `opacity: 0`, returning the snake to its original length.

3. **Segment Sizing (No Scaling):**
   - Head (`s0`): native `14.4px x 14.4px` (margin 0.8px, rx 4.5px).
   - Taper segments (`s1`, `s2`): native `12.3px` and `10.8px`.
   - Body segment (`s3`): native `9.9px x 9.9px` (margin 3.0px, rx 3.3px).
   - All added growth segments (`s4`, `s5`, ...): use the exact native body segment dimensions (`9.9px x 9.9px`, margin 3.0px, rx 3.3px).
   - No `transform: scale(...)` or size inflation is used anywhere.

4. **Identical Dual-Palette Generation:**
   Both `github-snake.svg` and `github-snake-dark.svg` are generated from the exact same computed route and growth event schedule, differing only in their color tokens (`--ce`, `--c0`..`--c4`).
