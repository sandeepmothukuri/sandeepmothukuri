"use strict";
exports.id = 642;
exports.ids = [642];
exports.modules = {

/***/ 642:
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {


// EXPORTS
__webpack_require__.d(__webpack_exports__, {
  createGif: () => (/* binding */ createGif)
});

// UNUSED EXPORTS: withTmpDir

// EXTERNAL MODULE: external "node:child_process"
var external_node_child_process_ = __webpack_require__(421);
// EXTERNAL MODULE: external "node:fs"
var external_node_fs_ = __webpack_require__(24);
var external_node_fs_default = /*#__PURE__*/__webpack_require__.n(external_node_fs_);
// EXTERNAL MODULE: external "node:os"
var external_node_os_ = __webpack_require__(161);
// EXTERNAL MODULE: external "node:path"
var external_node_path_ = __webpack_require__(760);
var external_node_path_default = /*#__PURE__*/__webpack_require__.n(external_node_path_);
// EXTERNAL MODULE: ../types/grid.ts
var types_grid = __webpack_require__(105);
;// CONCATENATED MODULE: ../draw/pathRoundedRect.ts
const pathRoundedRect_pathRoundedRect = (ctx, width, height, borderRadius) => {
    ctx.moveTo(borderRadius, 0);
    ctx.arcTo(width, 0, width, height, borderRadius);
    ctx.arcTo(width, height, 0, height, borderRadius);
    ctx.arcTo(0, height, 0, 0, borderRadius);
    ctx.arcTo(0, 0, width, 0, borderRadius);
};

;// CONCATENATED MODULE: ../draw/drawGrid.ts


const drawGrid_drawGrid = (ctx, grid, cells, o) => {
    for (let x = grid.width; x--;)
        for (let y = grid.height; y--;) {
            if (!cells || cells.some((c) => c.x === x && c.y === y)) {
                const c = (0,types_grid/* getColor */.oU)(grid, x, y);
                // @ts-ignore
                const color = !c ? o.colorEmpty : o.colorDots[c];
                ctx.save();
                ctx.translate(x * o.sizeCell + (o.sizeCell - o.sizeDot) / 2, y * o.sizeCell + (o.sizeCell - o.sizeDot) / 2);
                ctx.fillStyle = color;
                ctx.strokeStyle = o.colorDotBorder;
                ctx.lineWidth = 1;
                ctx.beginPath();
                pathRoundedRect_pathRoundedRect(ctx, o.sizeDot, o.sizeDot, o.sizeDotBorderRadius);
                ctx.fill();
                ctx.stroke();
                ctx.closePath();
                ctx.restore();
            }
        }
};

;// CONCATENATED MODULE: ../draw/drawSnake.ts


const drawSnake_drawSnake = (ctx, snake, o) => {
    const cells = snakeToCells(snake);
    for (let i = 0; i < cells.length; i++) {
        const u = (i + 1) * 0.6;
        ctx.save();
        ctx.fillStyle = o.colorSnake;
        ctx.translate(cells[i].x * o.sizeCell + u, cells[i].y * o.sizeCell + u);
        ctx.beginPath();
        pathRoundedRect(ctx, o.sizeCell - u * 2, o.sizeCell - u * 2, (o.sizeCell - u * 2) * 0.25);
        ctx.fill();
        ctx.restore();
    }
};
const lerp = (k, a, b) => (1 - k) * a + k * b;
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
const drawSnakeLerp = (ctx, snake0, snake1, k, o) => {
    const m = 0.8;
    const n = snake0.length / 2;
    for (let i = 0; i < n; i++) {
        const u = (i + 1) * 0.6 * (o.sizeCell / 16);
        const a = (1 - m) * (i / Math.max(n - 1, 1));
        const ki = clamp((k - a) / m, 0, 1);
        const x = lerp(ki, snake0[i * 2 + 0], snake1[i * 2 + 0]) - 2;
        const y = lerp(ki, snake0[i * 2 + 1], snake1[i * 2 + 1]) - 2;
        ctx.save();
        ctx.fillStyle = o.colorSnake;
        ctx.translate(x * o.sizeCell + u, y * o.sizeCell + u);
        ctx.beginPath();
        pathRoundedRect_pathRoundedRect(ctx, o.sizeCell - u * 2, o.sizeCell - u * 2, (o.sizeCell - u * 2) * 0.25);
        ctx.fill();
        ctx.restore();
    }
};

;// CONCATENATED MODULE: ../draw/drawWorld.ts


const drawStack = (ctx, stack, max, width, o) => {
    ctx.save();
    const m = width / max;
    for (let i = 0; i < stack.length; i++) {
        // @ts-ignore
        ctx.fillStyle = o.colorDots[stack[i]];
        ctx.fillRect(i * m, 0, m + width * 0.005, 10);
    }
    ctx.restore();
};
const drawWorld = (ctx, grid, cells, snake, stack, o) => {
    ctx.save();
    if (o.colorBackground) {
        ctx.fillStyle = o.colorBackground;
        ctx.fillRect(0, 0, 99999, 99999);
    }
    ctx.translate(1 * o.sizeCell, 2 * o.sizeCell);
    drawGrid(ctx, grid, cells, o);
    drawSnake(ctx, snake, o);
    ctx.restore();
    ctx.save();
    ctx.translate(o.sizeCell, (grid.height + 4) * o.sizeCell);
    const max = grid.data.reduce((sum, x) => sum + +!!x, stack.length);
    drawStack(ctx, stack, max, grid.width * o.sizeCell, o);
    ctx.restore();
    // ctx.save();
    // ctx.translate(o.sizeCell + 100, (grid.height + 4) * o.sizeCell + 100);
    // ctx.scale(0.6, 0.6);
    // drawCircleStack(ctx, stack, o);
    // ctx.restore();
};
const drawLerpWorld = (ctx, grid, cells, snake0, snake1, stack, k, o) => {
    ctx.save();
    if (o.colorBackground) {
        ctx.fillStyle = o.colorBackground;
        ctx.fillRect(0, 0, 99999, 99999);
    }
    ctx.translate(1 * o.sizeCell, 2 * o.sizeCell);
    drawGrid_drawGrid(ctx, grid, cells, o);
    drawSnakeLerp(ctx, snake0, snake1, k, o);
    ctx.translate(0, (grid.height + 2) * o.sizeCell);
    const max = grid.data.reduce((sum, x) => sum + +!!x, stack.length);
    drawStack(ctx, stack, max, grid.width * o.sizeCell, o);
    ctx.restore();
};
const getCanvasWorldSize = (grid, o) => {
    const width = o.sizeCell * (grid.width + 2);
    const height = o.sizeCell * (grid.height + 4) + 30;
    return { width, height };
};

// EXTERNAL MODULE: ../types/snake.ts
var types_snake = __webpack_require__(777);
;// CONCATENATED MODULE: ../solver/step.ts


const step = (grid, stack, snake) => {
    const x = (0,types_snake/* getHeadX */.tN)(snake);
    const y = (0,types_snake/* getHeadY */.Ap)(snake);
    const color = (0,types_grid/* getColor */.oU)(grid, x, y);
    if ((0,types_grid/* isInside */.FK)(grid, x, y) && !(0,types_grid/* isEmpty */.Im)(color)) {
        stack.push(color);
        (0,types_grid/* setColorEmpty */.l$)(grid, x, y);
    }
};

;// CONCATENATED MODULE: ../gif-creator/index.ts







const createGif = async (grid0, cells, chain, drawOptions, animationOptions) => withTmpDir(async (dir) => {
    // import dependencies that are optionnals for svg
    //
    const { createCanvas } = await Promise.resolve(/* import() */).then(__webpack_require__.t.bind(__webpack_require__, 919, 23));
    const { default: gifsicle } = await Promise.resolve(/* import() */).then(__webpack_require__.t.bind(__webpack_require__, 667, 23));
    // @ts-ignore
    const { default: GIFEncoder } = await __webpack_require__.e(/* import() */ 680).then(__webpack_require__.t.bind(__webpack_require__, 680, 23));
    const { width, height } = getCanvasWorldSize(grid0, drawOptions);
    const canvas = createCanvas(width, height);
    const ctx = canvas.getContext("2d", {
        alpha: true,
    });
    const grid = (0,types_grid/* copyGrid */.mi)(grid0);
    const stack = [];
    const encoder = new GIFEncoder(width, height, "neuquant", true, chain.length * animationOptions.frameByStep);
    encoder.setRepeat(0);
    encoder.setDelay(animationOptions.stepDurationMs / animationOptions.frameByStep);
    // transparency does not look good, let's not
    // encoder.setTransparent("0x000000");
    encoder.start();
    for (let i = 0; i < chain.length; i += 1) {
        const snake0 = chain[i];
        const snake1 = chain[Math.min(chain.length - 1, i + 1)];
        step(grid, stack, snake0);
        for (let k = 0; k < animationOptions.frameByStep; k++) {
            ctx.clearRect(0, 0, width, height);
            drawLerpWorld(ctx, grid, cells, snake0, snake1, stack, k / animationOptions.frameByStep, drawOptions);
            encoder.addFrame(ctx);
        }
    }
    const outFileName = external_node_path_default().join(dir, "out.gif");
    const optimizedFileName = external_node_path_default().join(dir, "out.optimized.gif");
    // generate palette file
    const paletteFileName = external_node_path_default().join(dir, "palette.txt");
    {
        const colors = [
            drawOptions.colorBackground,
            drawOptions.colorEmpty,
            drawOptions.colorSnake,
            drawOptions.colorDotBorder,
            ...Object.values(drawOptions.colorDots),
        ].filter(Boolean);
        const canvas = createCanvas(colors.length, 1);
        const ctx = canvas.getContext("2d");
        for (let i = colors.length; i--;) {
            ctx.fillStyle = colors[i];
            ctx.fillRect(i, 0, 1, 1);
        }
        const imgData = ctx.getImageData(0, 0, colors.length, 1);
        external_node_fs_default().writeFileSync(paletteFileName, Array.from({ length: colors.length }, (_, i) => [
            imgData.data[i * 4 + 0],
            imgData.data[i * 4 + 1],
            imgData.data[i * 4 + 2],
        ].join(" ")).join("\n"));
    }
    encoder.finish();
    external_node_fs_default().writeFileSync(outFileName, encoder.out.getData());
    (0,external_node_child_process_.execFileSync)(gifsicle, [
        //
        "--optimize=3",
        "--color-method=diversity",
        `--use-colormap=${paletteFileName}`,
        // "--colors=16",
        outFileName,
        ["--output", optimizedFileName],
    ].flat());
    return new Uint8Array(external_node_fs_default().readFileSync(optimizedFileName));
});
const withTmpDir = async (handler) => {
    const dir = external_node_path_default().join((0,external_node_os_.tmpdir)(), Math.random().toString(16).slice(2));
    external_node_fs_default().mkdirSync(dir, { recursive: true });
    try {
        return await handler(dir);
    }
    finally {
        external_node_fs_default().rmdirSync(dir, { recursive: true });
    }
};


/***/ })

};
;