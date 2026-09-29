"use strict";
exports.id = 578;
exports.ids = [578];
exports.modules = {

/***/ 578:
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {


// EXPORTS
__webpack_require__.d(__webpack_exports__, {
  createSvg: () => (/* binding */ createSvg)
});

// EXTERNAL MODULE: ../types/grid.ts
var types_grid = __webpack_require__(105);
// EXTERNAL MODULE: ../types/snake.ts
var types_snake = __webpack_require__(777);
;// CONCATENATED MODULE: ../svg-creator/xml-utils.ts
const h = (element, attributes) => `<${element} ${toAttribute(attributes)}/>`;
const toAttribute = (o) => Object.entries(o)
    .filter(([, value]) => value !== null)
    .map(([name, value]) => `${name}="${value}"`)
    .join(" ");

;// CONCATENATED MODULE: ../svg-creator/css-utils.ts
const percent = (x) => parseFloat((x * 100).toFixed(2)).toString() + "%";
const mergeKeyFrames = (keyframes) => {
    const s = new Map();
    for (const { t, style } of keyframes) {
        s.set(style, [...(s.get(style) ?? []), t]);
    }
    return Array.from(s.entries())
        .map(([style, ts]) => ({ style, ts }))
        .sort((a, b) => a.ts[0] - b.ts[0]);
};
/**
 * generate the keyframe animation from a list of keyframe
 */
const createAnimation = (name, keyframes) => `@keyframes ${name}{` +
    mergeKeyFrames(keyframes)
        .map(({ style, ts }) => ts.map(percent).join(",") + `{${style}}`)
        .join("") +
    "}";
/**
 * remove white spaces
 */
const minifyCss = (css) => css
    .replace(/\s+/g, " ")
    .replace(/.\s+[,;:{}()]/g, (a) => a.replace(/\s+/g, ""))
    .replace(/[,;:{}()]\s+./g, (a) => a.replace(/\s+/g, ""))
    .replace(/.\s+[,;:{}()]/g, (a) => a.replace(/\s+/g, ""))
    .replace(/[,;:{}()]\s+./g, (a) => a.replace(/\s+/g, ""))
    .replace(/\;\s*\}/g, "}")
    .trim();

;// CONCATENATED MODULE: ../svg-creator/snake.ts



const lerp = (k, a, b) => (1 - k) * a + k * b;
const createSnake = (chain, { sizeCell, sizeDot }, duration, livingCells) => {
    const eatenCells = (livingCells || [])
        .filter((c) => c.t !== null)
        .sort((a, b) => a.t - b.t);
    const initialLength = chain[0] ? (0,types_snake/* getSnakeLength */.T$)(chain[0]) : 0;
    const totalSegments = initialLength + eatenCells.length;

    const getHeadPos = (s) => {
        if (s >= 0 && s < chain.length) {
            return (0,types_snake/* snakeToCells */.HU)(chain[s])[0];
        }
        if (s < 0) {
            return { x: -s, y: -1 };
        }
        return (0,types_snake/* snakeToCells */.HU)(chain[chain.length - 1])[0];
    };

    const getSegmentPos = (k, s) => getHeadPos(s - k);

    const snakeParts = [];
    for (let k = 0; k < totalSegments; k++) {
        if (k < initialLength) {
            const part = [];
            for (const snake of chain) {
                const cells = (0,types_snake/* snakeToCells */.HU)(snake);
                part.push(cells[k]);
            }
            snakeParts.push(part);
        } else {
            const part = [];
            for (let s = 0; s < chain.length; s++) {
                part.push(getSegmentPos(k, s));
            }
            snakeParts.push(part);
        }
    }

    const svgElements = snakeParts.map((_, i) => {
        let s, m, r;
        if (i < initialLength) {
            const dMin = sizeDot * 0.8;
            const dMax = sizeCell * 0.9;
            const iMax = Math.min(4, initialLength);
            const u = (1 - Math.min(i, iMax) / iMax) ** 2;
            s = lerp(u, dMin, dMax);
            m = (sizeCell - s) / 2;
            r = Math.min(4.5, (4 * s) / sizeDot);
        } else {
            s = 9.9;
            m = (sizeCell - s) / 2;
            r = 3.3;
        }
        return h("rect", {
            class: `s s${i}`,
            x: m.toFixed(1),
            y: m.toFixed(1),
            width: s.toFixed(1),
            height: s.toFixed(1),
            rx: r.toFixed(1),
            ry: r.toFixed(1),
        });
    });

    const transform = ({ x, y }) => `transform:translate(${x * sizeCell}px,${y * sizeCell}px)`;

    const styles = [
        `.s{ 
      shape-rendering: geometricPrecision;
      fill: var(--cs);
      animation: none linear ${duration}ms infinite
    }`,
        ...snakeParts.map((positions, i) => {
            const id = `s${i}`;
            const animationName = id;
            const keyframes = removeInterpolatedPositions(
                positions.map((tr, idx, { length }) => ({ ...tr, t: idx / length }))
            ).map(({ t, ...p }) => ({ t, style: transform(p) }));

            if (i < initialLength) {
                return [
                    createAnimation(animationName, keyframes),
                    `.s.${id}{
          ${transform(positions[0])};
          animation-name: ${animationName}
        }`,
                ];
            } else {
                const growthIdx = i - initialLength;
                const tAppear = eatenCells[growthIdx].t;
                const opacityAnimName = `o${i}`;
                const opacityKeyframes = [
                    { t: 0, style: "opacity:0" },
                    { t: Math.max(0, tAppear - 0.0001), style: "opacity:0" },
                    { t: Math.min(1, tAppear + 0.0001), style: "opacity:1" },
                    { t: 1, style: "opacity:1" }
                ];
                return [
                    createAnimation(animationName, keyframes),
                    createAnimation(opacityAnimName, opacityKeyframes),
                    `.s.${id}{
          ${transform(positions[0])};
          opacity: 0;
          animation-name: ${animationName}, ${opacityAnimName}
        }`,
                ];
            }
        }),
    ].flat();

    return { svgElements, styles };
};
const removeInterpolatedPositions = (arr) => arr.filter((u, i, arr) => {
    if (i - 1 < 0 || i + 1 >= arr.length)
        return true;
    const a = arr[i - 1];
    const b = arr[i + 1];
    const ex = (a.x + b.x) / 2;
    const ey = (a.y + b.y) / 2;
    // return true;
    return !(Math.abs(ex - u.x) < 0.01 && Math.abs(ey - u.y) < 0.01);
});

;// CONCATENATED MODULE: ../svg-creator/grid.ts


const createGrid = (cells, { sizeDotBorderRadius, sizeDot, sizeCell }, duration) => {
    const svgElements = [];
    const styles = [
        `.c{
      shape-rendering: geometricPrecision;
      fill: var(--ce);
      stroke-width: 1px;
      stroke: var(--cb);
      animation: none ${duration}ms linear infinite;
      width: ${sizeDot}px;
      height: ${sizeDot}px;
    }`,
    ];
    let i = 0;
    for (const { x, y, color, t } of cells) {
        const id = t && "c" + (i++).toString(36);
        const m = (sizeCell - sizeDot) / 2;
        if (t !== null && id) {
            const animationName = id;
            styles.push(createAnimation(animationName, [
                { t: t - 0.0001, style: `fill:var(--c${color})` },
                { t: t + 0.0001, style: `fill:var(--ce)` },
                { t: 1, style: `fill:var(--ce)` },
            ]), `.c.${id}{
          fill: var(--c${color});
          animation-name: ${animationName}
        }`);
        }
        svgElements.push(h("rect", {
            class: ["c", id].filter(Boolean).join(" "),
            x: x * sizeCell + m,
            y: y * sizeCell + m,
            rx: sizeDotBorderRadius,
            ry: sizeDotBorderRadius,
        }));
    }
    return { svgElements, styles };
};

;// CONCATENATED MODULE: ../svg-creator/stack.ts


const createStack = (cells, { sizeDot }, width, y, duration) => {
    const svgElements = [];
    const styles = [
        `.u{ 
      transform-origin: 0 0;
      transform: scale(0,1);
      animation: none linear ${duration}ms infinite;
    }`,
    ];
    const stack = cells
        .slice()
        .filter((a) => a.t !== null)
        .sort((a, b) => a.t - b.t);
    const blocks = [];
    stack.forEach(({ color, t }) => {
        const latest = blocks[blocks.length - 1];
        if (latest?.color === color)
            latest.ts.push(t);
        else
            blocks.push({ color, ts: [t] });
    });
    const m = width / stack.length;
    let i = 0;
    let nx = 0;
    for (const { color, ts } of blocks) {
        const id = "u" + (i++).toString(36);
        const animationName = id;
        const x = (nx * m).toFixed(1);
        nx += ts.length;
        svgElements.push(h("rect", {
            class: `u ${id}`,
            height: sizeDot,
            width: (ts.length * m + 0.6).toFixed(1),
            x,
            y,
        }));
        styles.push(createAnimation(animationName, [
            ...ts
                .map((t, i, { length }) => [
                { scale: i / length, t: t - 0.0001 },
                { scale: (i + 1) / length, t: t + 0.0001 },
            ])
                .flat(),
            { scale: 1, t: 1 },
        ].map(({ scale, t }) => ({
            t,
            style: `transform:scale(${scale.toFixed(3)},1)`,
        }))), `.u.${id} {
        fill: var(--c${color});
        animation-name: ${animationName};
        transform-origin: ${x}px 0
      }
      `);
    }
    return { svgElements, styles };
};

;// CONCATENATED MODULE: ../svg-creator/index.ts







const getCellsFromGrid = ({ width, height }) => Array.from({ length: width }, (_, x) => Array.from({ length: height }, (_, y) => ({ x, y }))).flat();
const createLivingCells = (grid0, chain, cells) => {
    const livingCells = (cells ?? getCellsFromGrid(grid0)).map(({ x, y }) => ({
        x,
        y,
        t: null,
        color: (0,types_grid/* getColor */.oU)(grid0, x, y),
    }));
    const grid = (0,types_grid/* copyGrid */.mi)(grid0);
    for (let i = 0; i < chain.length; i++) {
        const snake = chain[i];
        const x = (0,types_snake/* getHeadX */.tN)(snake);
        const y = (0,types_snake/* getHeadY */.Ap)(snake);
        if ((0,types_grid/* isInside */.FK)(grid, x, y) && !(0,types_grid/* isEmpty */.Im)((0,types_grid/* getColor */.oU)(grid, x, y))) {
            (0,types_grid/* setColorEmpty */.l$)(grid, x, y);
            const cell = livingCells.find((c) => c.x === x && c.y === y);
            cell.t = i / chain.length;
        }
    }
    return livingCells;
};
const createSvg = (grid, cells, chain, drawOptions, animationOptions) => {
    const width = (grid.width + 2) * drawOptions.sizeCell;
    const height = (grid.height + 5) * drawOptions.sizeCell;
    const duration = animationOptions.stepDurationMs * chain.length;
    const livingCells = createLivingCells(grid, chain, cells);
    const elements = [
        createGrid(livingCells, drawOptions, duration),
        createStack(livingCells, drawOptions, grid.width * drawOptions.sizeCell, (grid.height + 2) * drawOptions.sizeCell, duration),
        createSnake(chain, drawOptions, duration, livingCells),
    ];
    const viewBox = [
        -drawOptions.sizeCell,
        -drawOptions.sizeCell * 2,
        width,
        height,
    ].join(" ");
    const style = generateColorVar(drawOptions) +
        elements
            .map((e) => e.styles)
            .flat()
            .join("\n");
    const svg = [
        h("svg", {
            viewBox,
            width,
            height,
            xmlns: "http://www.w3.org/2000/svg",
        }).replace("/>", ">"),
        "<desc>",
        "Generated with https://github.com/Platane/snk",
        "</desc>",
        "<style>",
        optimizeCss(style),
        "</style>",
        ...elements.map((e) => e.svgElements).flat(),
        "</svg>",
    ].join("");
    return optimizeSvg(svg);
};
const optimizeCss = (css) => minifyCss(css);
const optimizeSvg = (svg) => svg;
const generateColorVar = (drawOptions) => `
    :root {
    --cb: ${drawOptions.colorDotBorder};
    --cs: ${drawOptions.colorSnake};
    --ce: ${drawOptions.colorEmpty};
    ${Object.entries(drawOptions.colorDots)
    .map(([i, color]) => `--c${i}:${color};`)
    .join("")}
    }
    ` +
    (drawOptions.dark
        ? `
    @media (prefers-color-scheme: dark) {
      :root {
        --cb: ${drawOptions.dark.colorDotBorder || drawOptions.colorDotBorder};
        --cs: ${drawOptions.dark.colorSnake || drawOptions.colorSnake};
        --ce: ${drawOptions.dark.colorEmpty};
        ${Object.entries(drawOptions.dark.colorDots)
            .map(([i, color]) => `--c${i}:${color};`)
            .join("")}
      }
    }
`
        : "");


/***/ })

};
;