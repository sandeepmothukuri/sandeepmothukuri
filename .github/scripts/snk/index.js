/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ({

/***/ 105:
/***/ ((__unused_webpack_module, __webpack_exports__, __nccwpck_require__) => {

/* harmony export */ __nccwpck_require__.d(__webpack_exports__, {
/* harmony export */   FK: () => (/* binding */ isInside),
/* harmony export */   Im: () => (/* binding */ isEmpty),
/* harmony export */   Kb: () => (/* binding */ createEmptyGrid),
/* harmony export */   Yd: () => (/* binding */ isInsideLarge),
/* harmony export */   l$: () => (/* binding */ setColorEmpty),
/* harmony export */   mi: () => (/* binding */ copyGrid),
/* harmony export */   oU: () => (/* binding */ getColor),
/* harmony export */   wW: () => (/* binding */ setColor)
/* harmony export */ });
/* unused harmony exports isGrid, isGridEmpty, gridEquals */
const isGrid = (x) => !!x &&
    typeof x?.width === "number" &&
    typeof x?.height === "number" &&
    x.data?.length <= x.width * x.height;
const isInside = (grid, x, y) => x >= 0 && y >= 0 && x < grid.width && y < grid.height;
const isInsideLarge = (grid, m, x, y) => x >= -m && y >= -m && x < grid.width + m && y < grid.height + m;
const copyGrid = ({ width, height, data }) => ({
    width,
    height,
    data: Uint8Array.from(data),
});
const getIndex = (grid, x, y) => x * grid.height + y;
const getColor = (grid, x, y) => grid.data[getIndex(grid, x, y)];
const isEmpty = (color) => color === 0;
const setColor = (grid, x, y, color) => {
    grid.data[getIndex(grid, x, y)] = color || 0;
};
const setColorEmpty = (grid, x, y) => {
    setColor(grid, x, y, 0);
};
/**
 * return true if the grid is empty
 */
const isGridEmpty = (grid) => grid.data.every((x) => x === 0);
const gridEquals = (a, b) => a.data.every((_, i) => a.data[i] === b.data[i]);
const createEmptyGrid = (width, height) => ({
    width,
    height,
    data: new Uint8Array(width * height),
});


/***/ }),

/***/ 777:
/***/ ((__unused_webpack_module, __webpack_exports__, __nccwpck_require__) => {

/* harmony export */ __nccwpck_require__.d(__webpack_exports__, {
/* harmony export */   Ap: () => (/* binding */ getHeadY),
/* harmony export */   HU: () => (/* binding */ snakeToCells),
/* harmony export */   J: () => (/* binding */ snakeWillSelfCollide),
/* harmony export */   Sc: () => (/* binding */ nextSnake),
/* harmony export */   T$: () => (/* binding */ getSnakeLength),
/* harmony export */   sW: () => (/* binding */ snakeEquals),
/* harmony export */   tN: () => (/* binding */ getHeadX),
/* harmony export */   yS: () => (/* binding */ createSnakeFromCells)
/* harmony export */ });
/* unused harmony export copySnake */
const getHeadX = (snake) => snake[0] - 2;
const getHeadY = (snake) => snake[1] - 2;
const getSnakeLength = (snake) => snake.length / 2;
const copySnake = (snake) => snake.slice();
const snakeEquals = (a, b) => {
    for (let i = 0; i < a.length; i++)
        if (a[i] !== b[i])
            return false;
    return true;
};
/**
 * return a copy of the next snake, considering that dx, dy is the direction
 */
const nextSnake = (snake, dx, dy) => {
    const copy = new Uint8Array(snake.length);
    for (let i = 2; i < snake.length; i++)
        copy[i] = snake[i - 2];
    copy[0] = snake[0] + dx;
    copy[1] = snake[1] + dy;
    return copy;
};
/**
 * return true if the next snake will collide with itself
 */
const snakeWillSelfCollide = (snake, dx, dy) => {
    const nx = snake[0] + dx;
    const ny = snake[1] + dy;
    for (let i = 2; i < snake.length - 2; i += 2)
        if (snake[i + 0] === nx && snake[i + 1] === ny)
            return true;
    return false;
};
const snakeToCells = (snake) => Array.from({ length: snake.length / 2 }, (_, i) => ({
    x: snake[i * 2 + 0] - 2,
    y: snake[i * 2 + 1] - 2,
}));
const createSnakeFromCells = (points) => {
    const snake = new Uint8Array(points.length * 2);
    for (let i = points.length; i--;) {
        snake[i * 2 + 0] = points[i].x + 2;
        snake[i * 2 + 1] = points[i].y + 2;
    }
    return snake;
};


/***/ }),

/***/ 919:
/***/ ((module) => {

module.exports = require("canvas");

/***/ }),

/***/ 434:
/***/ ((module) => {

module.exports = require("events");

/***/ }),

/***/ 667:
/***/ ((module) => {

module.exports = require("gifsicle");

/***/ }),

/***/ 421:
/***/ ((module) => {

module.exports = require("node:child_process");

/***/ }),

/***/ 24:
/***/ ((module) => {

module.exports = require("node:fs");

/***/ }),

/***/ 161:
/***/ ((module) => {

module.exports = require("node:os");

/***/ }),

/***/ 760:
/***/ ((module) => {

module.exports = require("node:path");

/***/ }),

/***/ 203:
/***/ ((module) => {

module.exports = require("stream");

/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __nccwpck_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		var threw = true;
/******/ 		try {
/******/ 			__webpack_modules__[moduleId](module, module.exports, __nccwpck_require__);
/******/ 			threw = false;
/******/ 		} finally {
/******/ 			if(threw) delete __webpack_module_cache__[moduleId];
/******/ 		}
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__nccwpck_require__.m = __webpack_modules__;
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/compat get default export */
/******/ 	(() => {
/******/ 		// getDefaultExport function for compatibility with non-harmony modules
/******/ 		__nccwpck_require__.n = (module) => {
/******/ 			var getter = module && module.__esModule ?
/******/ 				() => (module['default']) :
/******/ 				() => (module);
/******/ 			__nccwpck_require__.d(getter, { a: getter });
/******/ 			return getter;
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/create fake namespace object */
/******/ 	(() => {
/******/ 		var getProto = Object.getPrototypeOf ? (obj) => (Object.getPrototypeOf(obj)) : (obj) => (obj.__proto__);
/******/ 		var leafPrototypes;
/******/ 		// create a fake namespace object
/******/ 		// mode & 1: value is a module id, require it
/******/ 		// mode & 2: merge all properties of value into the ns
/******/ 		// mode & 4: return value when already ns object
/******/ 		// mode & 16: return value when it's Promise-like
/******/ 		// mode & 8|1: behave like require
/******/ 		__nccwpck_require__.t = function(value, mode) {
/******/ 			if(mode & 1) value = this(value);
/******/ 			if(mode & 8) return value;
/******/ 			if(typeof value === 'object' && value) {
/******/ 				if((mode & 4) && value.__esModule) return value;
/******/ 				if((mode & 16) && typeof value.then === 'function') return value;
/******/ 			}
/******/ 			var ns = Object.create(null);
/******/ 			__nccwpck_require__.r(ns);
/******/ 			var def = {};
/******/ 			leafPrototypes = leafPrototypes || [null, getProto({}), getProto([]), getProto(getProto)];
/******/ 			for(var current = mode & 2 && value; typeof current == 'object' && !~leafPrototypes.indexOf(current); current = getProto(current)) {
/******/ 				Object.getOwnPropertyNames(current).forEach((key) => (def[key] = () => (value[key])));
/******/ 			}
/******/ 			def['default'] = () => (value);
/******/ 			__nccwpck_require__.d(ns, def);
/******/ 			return ns;
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/define property getters */
/******/ 	(() => {
/******/ 		// define getter functions for harmony exports
/******/ 		__nccwpck_require__.d = (exports, definition) => {
/******/ 			for(var key in definition) {
/******/ 				if(__nccwpck_require__.o(definition, key) && !__nccwpck_require__.o(exports, key)) {
/******/ 					Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
/******/ 				}
/******/ 			}
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/ensure chunk */
/******/ 	(() => {
/******/ 		__nccwpck_require__.f = {};
/******/ 		// This file contains only the entry chunk.
/******/ 		// The chunk loading function for additional chunks
/******/ 		__nccwpck_require__.e = (chunkId) => {
/******/ 			return Promise.all(Object.keys(__nccwpck_require__.f).reduce((promises, key) => {
/******/ 				__nccwpck_require__.f[key](chunkId, promises);
/******/ 				return promises;
/******/ 			}, []));
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/get javascript chunk filename */
/******/ 	(() => {
/******/ 		// This function allow to reference async chunks
/******/ 		__nccwpck_require__.u = (chunkId) => {
/******/ 			// return url for filenames based on template
/******/ 			return "" + chunkId + ".index.js";
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/hasOwnProperty shorthand */
/******/ 	(() => {
/******/ 		__nccwpck_require__.o = (obj, prop) => (Object.prototype.hasOwnProperty.call(obj, prop))
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/make namespace object */
/******/ 	(() => {
/******/ 		// define __esModule on exports
/******/ 		__nccwpck_require__.r = (exports) => {
/******/ 			if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 				Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 			}
/******/ 			Object.defineProperty(exports, '__esModule', { value: true });
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/compat */
/******/ 	
/******/ 	if (typeof __nccwpck_require__ !== 'undefined') __nccwpck_require__.ab = __dirname + "/";
/******/ 	
/******/ 	/* webpack/runtime/require chunk loading */
/******/ 	(() => {
/******/ 		// no baseURI
/******/ 		
/******/ 		// object to store loaded chunks
/******/ 		// "1" means "loaded", otherwise not loaded yet
/******/ 		var installedChunks = {
/******/ 			792: 1
/******/ 		};
/******/ 		
/******/ 		// no on chunks loaded
/******/ 		
/******/ 		var installChunk = (chunk) => {
/******/ 			var moreModules = chunk.modules, chunkIds = chunk.ids, runtime = chunk.runtime;
/******/ 			for(var moduleId in moreModules) {
/******/ 				if(__nccwpck_require__.o(moreModules, moduleId)) {
/******/ 					__nccwpck_require__.m[moduleId] = moreModules[moduleId];
/******/ 				}
/******/ 			}
/******/ 			if(runtime) runtime(__nccwpck_require__);
/******/ 			for(var i = 0; i < chunkIds.length; i++)
/******/ 				installedChunks[chunkIds[i]] = 1;
/******/ 		
/******/ 		};
/******/ 		
/******/ 		// require() chunk loading for javascript
/******/ 		__nccwpck_require__.f.require = (chunkId, promises) => {
/******/ 			// "1" is the signal for "already loaded"
/******/ 			if(!installedChunks[chunkId]) {
/******/ 				if(true) { // all chunks have JS
/******/ 					installChunk(require("./" + __nccwpck_require__.u(chunkId)));
/******/ 				} else installedChunks[chunkId] = 1;
/******/ 			}
/******/ 		};
/******/ 		
/******/ 		// no external install chunk
/******/ 		
/******/ 		// no HMR
/******/ 		
/******/ 		// no HMR manifest
/******/ 	})();
/******/ 	
/************************************************************************/
var __webpack_exports__ = {};

// EXTERNAL MODULE: external "node:fs"
var external_node_fs_ = __nccwpck_require__(24);
// EXTERNAL MODULE: external "node:path"
var external_node_path_ = __nccwpck_require__(760);
;// CONCATENATED MODULE: ../forgejo-user-contribution/index.ts
/**
 * Get the contribution grid from a Forgejo/Codeberg user heatmap API.
 *
 * The heatmap endpoint returns raw Unix timestamps (15-minute UTC buckets).
 * Date bucketing uses the caller's local timezone (set TZ env var to control it).
 *
 * Works with any Forgejo instance via the `baseUrl` option.
 * Defaults to Codeberg: https://codeberg.org
 *
 * @example
 *   getForgejoUserContribution("username")
 *   getForgejoUserContribution("username", { baseUrl: "https://codeberg.org" })
 */
const getForgejoUserContribution = async (userName, o = {}) => {
    const baseUrl = o.baseUrl ?? "https://codeberg.org";
    const res = await fetch(`${baseUrl}/api/v1/users/${userName}/heatmap`, {
        headers: { "Content-Type": "application/json" },
    });
    if (!res.ok)
        throw new Error(await res.text().catch(() => res.statusText));
    const heatmapData = (await res.json());
    // Aggregate contributions per local date (YYYY-MM-DD).
    // Timestamps are 15-min UTC buckets; en-CA locale gives consistent YYYY-MM-DD format.
    // The timezone is determined by the process TZ env var.
    const countsByDate = new Map();
    for (const { timestamp, contributions } of heatmapData) {
        const date = new Date(timestamp * 1000).toLocaleDateString("en-CA");
        countsByDate.set(date, (countsByDate.get(date) ?? 0) + contributions);
    }
    // Match the color index formula used by Forgejo's vue3-calendar-heatmap:
    // ceil(count / max * 3) + 1, capped at 4 (we use a 0-4 scale vs their 1-5).
    const max = Math.max(0, ...countsByDate.values());
    const levelForCount = (count) => count <= 0 || max === 0
        ? 0
        : count >= max
            ? 4
            : Math.ceil((count / max) * 3);
    // Build the cell grid covering the last ~365 days, starting on a Sunday.
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    // Find the Sunday at or before (today - 365 days)
    const start = new Date(today);
    start.setDate(start.getDate() - 365);
    start.setDate(start.getDate() - start.getDay()); // rewind to Sunday
    const cells = [];
    const cursor = new Date(start);
    let x = 0;
    while (cursor <= today) {
        const y = cursor.getDay(); // 0 = Sunday
        const date = cursor.toLocaleDateString("en-CA");
        const count = countsByDate.get(date) ?? 0;
        cells.push({ x, y, date, count, level: levelForCount(count) });
        cursor.setDate(cursor.getDate() + 1);
        if (y === 6)
            x++; // advance week after Saturday
    }
    return cells;
};

;// CONCATENATED MODULE: ../github-user-contribution/index.ts
/**
 * get the contribution grid from a github user page
 *
 * use options.from=YYYY-MM-DD options.to=YYYY-MM-DD to get the contribution grid for a specific time range
 * or year=2019 as an alias for from=2019-01-01 to=2019-12-31
 *
 * otherwise return use the time range from today minus one year to today ( as seen in github profile page )
 *
 * @param userName github user name
 * @param options
 *
 * @example
 *  getGithubUserContribution("platane", { from: "2019-01-01", to: "2019-12-31" })
 *  getGithubUserContribution("platane", { year: 2019 })
 *
 */
const getGithubUserContribution = async (userName, o) => {
    const query = /* GraphQL */ `
    query ($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            weeks {
              contributionDays {
                contributionCount
                contributionLevel
                weekday
                date
              }
            }
          }
        }
      }
    }
  `;
    const variables = { login: userName };
    const apiUrl = o.baseUrl
        ? `${o.baseUrl}/api/graphql`
        : "https://api.github.com/graphql";
    const res = await fetch(apiUrl, {
        headers: {
            Authorization: `bearer ${o.githubToken}`,
            "Content-Type": "application/json",
            "User-Agent": "me@platane.me",
        },
        method: "POST",
        body: JSON.stringify({ variables, query }),
    });
    if (!res.ok)
        throw new Error(await res.text().catch(() => res.statusText));
    const { data, errors } = (await res.json());
    if (errors?.[0])
        throw errors[0];
    return data.user.contributionsCollection.contributionCalendar.weeks.flatMap(({ contributionDays }, x) => contributionDays.map((d) => ({
        x,
        y: d.weekday,
        date: d.date,
        count: d.contributionCount,
        level: (d.contributionLevel === "FOURTH_QUARTILE" && 4) ||
            (d.contributionLevel === "THIRD_QUARTILE" && 3) ||
            (d.contributionLevel === "SECOND_QUARTILE" && 2) ||
            (d.contributionLevel === "FIRST_QUARTILE" && 1) ||
            0,
    })));
};

;// CONCATENATED MODULE: ../gitlab-user-contribution/index.ts
/**
 * Get the contribution grid from a GitLab user calendar.
 *
 * Uses the public /users/{username}/calendar.json endpoint, no auth required.
 * Works with any GitLab instance via the `baseUrl` option.
 * Defaults to https://gitlab.com
 *
 * @example
 *   getGitlabUserContribution("username")
 *   getGitlabUserContribution("username", { baseUrl: "https://gitlab.example.com" })
 */
const getGitlabUserContribution = async (userName, o = {}) => {
    const baseUrl = o.baseUrl ?? "https://gitlab.com";
    const res = await fetch(`${baseUrl}/users/${userName}/calendar.json`, {
        headers: { "Content-Type": "application/json" },
    });
    if (!res.ok)
        throw new Error(await res.text().catch(() => res.statusText));
    // Response is already bucketed by day: { "YYYY-MM-DD": count }
    const countsByDate = (await res.json());
    const max = Math.max(0, ...Object.values(countsByDate));
    const levelForCount = (count) => count <= 0 || max === 0
        ? 0
        : count >= max
            ? 4
            : Math.ceil((count / max) * 3);
    // Build the cell grid covering the last ~365 days, starting on a Sunday.
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    // Find the Sunday at or before (today - 365 days)
    const start = new Date(today);
    start.setDate(start.getDate() - 365);
    start.setDate(start.getDate() - start.getDay()); // rewind to Sunday
    const cells = [];
    const cursor = new Date(start);
    let x = 0;
    while (cursor <= today) {
        const y = cursor.getDay(); // 0 = Sunday
        const date = cursor.toLocaleDateString("en-CA");
        const count = countsByDate[date] ?? 0;
        cells.push({ x, y, date, count, level: levelForCount(count) });
        cursor.setDate(cursor.getDate() + 1);
        if (y === 6)
            x++;
    }
    return cells;
};

// EXTERNAL MODULE: ../types/grid.ts
var types_grid = __nccwpck_require__(105);
;// CONCATENATED MODULE: ../types/point.ts
const around4 = [
    { x: 1, y: 0 },
    { x: 0, y: -1 },
    { x: -1, y: 0 },
    { x: 0, y: 1 },
];
const pointEquals = (a, b) => a.x === b.x && a.y === b.y;

;// CONCATENATED MODULE: ../solver/outside.ts


const createOutside = (grid, color = 0) => {
    const outside = (0,types_grid/* createEmptyGrid */.Kb)(grid.width, grid.height);
    for (let x = outside.width; x--;)
        for (let y = outside.height; y--;)
            (0,types_grid/* setColor */.wW)(outside, x, y, 1);
    fillOutside(outside, grid, color);
    return outside;
};
const fillOutside = (outside, grid, color = 0) => {
    let changed = true;
    while (changed) {
        changed = false;
        for (let x = outside.width; x--;)
            for (let y = outside.height; y--;)
                if ((0,types_grid/* getColor */.oU)(grid, x, y) <= color &&
                    !isOutside(outside, x, y) &&
                    around4.some((a) => isOutside(outside, x + a.x, y + a.y))) {
                    changed = true;
                    (0,types_grid/* setColorEmpty */.l$)(outside, x, y);
                }
    }
    return outside;
};
const isOutside = (outside, x, y) => !(0,types_grid/* isInside */.FK)(outside, x, y) || (0,types_grid/* isEmpty */.Im)((0,types_grid/* getColor */.oU)(outside, x, y));

// EXTERNAL MODULE: ../types/snake.ts
var types_snake = __nccwpck_require__(777);
;// CONCATENATED MODULE: ../solver/utils/sortPush.ts
const sortPush = (arr, x, sortFn) => {
    let a = 0;
    let b = arr.length;
    if (arr.length === 0 || sortFn(x, arr[a]) <= 0) {
        arr.unshift(x);
        return;
    }
    while (b - a > 1) {
        const e = Math.ceil((a + b) / 2);
        const s = sortFn(x, arr[e]);
        if (s === 0)
            a = b = e;
        else if (s > 0)
            a = e;
        else
            b = e;
    }
    const e = Math.ceil((a + b) / 2);
    arr.splice(e, 0, x);
};

;// CONCATENATED MODULE: ../solver/tunnel.ts


/**
 * get the sequence of snake to cross the tunnel
 */
const getTunnelPath = (snake0, tunnel) => {
    const chain = [];
    let snake = snake0;
    for (let i = 1; i < tunnel.length; i++) {
        const dx = tunnel[i].x - (0,types_snake/* getHeadX */.tN)(snake);
        const dy = tunnel[i].y - (0,types_snake/* getHeadY */.Ap)(snake);
        snake = (0,types_snake/* nextSnake */.Sc)(snake, dx, dy);
        chain.unshift(snake);
    }
    return chain;
};
/**
 * assuming the grid change and the colors got deleted, update the tunnel
 */
const updateTunnel = (grid, tunnel, toDelete) => {
    while (tunnel.length) {
        const { x, y } = tunnel[0];
        if (isEmptySafe(grid, x, y) ||
            toDelete.some((p) => p.x === x && p.y === y)) {
            tunnel.shift();
        }
        else
            break;
    }
    while (tunnel.length) {
        const { x, y } = tunnel[tunnel.length - 1];
        if (isEmptySafe(grid, x, y) ||
            toDelete.some((p) => p.x === x && p.y === y)) {
            tunnel.pop();
        }
        else
            break;
    }
};
const isEmptySafe = (grid, x, y) => !(0,types_grid/* isInside */.FK)(grid, x, y) || (0,types_grid/* isEmpty */.Im)((0,types_grid/* getColor */.oU)(grid, x, y));
/**
 * remove empty cell from start
 */
const trimTunnelStart = (grid, tunnel) => {
    while (tunnel.length) {
        const { x, y } = tunnel[0];
        if (isEmptySafe(grid, x, y))
            tunnel.shift();
        else
            break;
    }
};
/**
 * remove empty cell from end
 */
const trimTunnelEnd = (grid, tunnel) => {
    while (tunnel.length) {
        const i = tunnel.length - 1;
        const { x, y } = tunnel[i];
        if (isEmptySafe(grid, x, y) ||
            tunnel.findIndex((p) => p.x === x && p.y === y) < i)
            tunnel.pop();
        else
            break;
    }
};

;// CONCATENATED MODULE: ../solver/getBestTunnel.ts






const getColorSafe = (grid, x, y) => (0,types_grid/* isInside */.FK)(grid, x, y) ? (0,types_grid/* getColor */.oU)(grid, x, y) : 0;
const setEmptySafe = (grid, x, y) => {
    if ((0,types_grid/* isInside */.FK)(grid, x, y))
        (0,types_grid/* setColorEmpty */.l$)(grid, x, y);
};
const unwrap = (m) => !m
    ? []
    : [...unwrap(m.parent), { x: (0,types_snake/* getHeadX */.tN)(m.snake), y: (0,types_snake/* getHeadY */.Ap)(m.snake) }];
/**
 * returns the path to reach the outside which contains the least color cell
 */
const getSnakeEscapePath = (grid, outside, snake0, color) => {
    const openList = [{ snake: snake0, w: 0 }];
    const closeList = [];
    while (openList[0]) {
        const o = openList.shift();
        const x = (0,types_snake/* getHeadX */.tN)(o.snake);
        const y = (0,types_snake/* getHeadY */.Ap)(o.snake);
        if (isOutside(outside, x, y))
            return unwrap(o);
        for (const a of around4) {
            const c = getColorSafe(grid, x + a.x, y + a.y);
            if (c <= color && !(0,types_snake/* snakeWillSelfCollide */.J)(o.snake, a.x, a.y)) {
                const snake = (0,types_snake/* nextSnake */.Sc)(o.snake, a.x, a.y);
                if (!closeList.some((s0) => (0,types_snake/* snakeEquals */.sW)(s0, snake))) {
                    const w = o.w + 1 + +(c === color) * 1000;
                    sortPush(openList, { snake, w, parent: o }, (a, b) => a.w - b.w);
                    closeList.push(snake);
                }
            }
        }
    }
    return null;
};
/**
 * compute the best tunnel to get to the cell and back to the outside ( best = less usage of <color> )
 *
 * notice that it's one of the best tunnels, more with the same score could exist
 */
const getBestTunnel = (grid, outside, x, y, color, snakeN) => {
    const c = { x, y };
    const snake0 = (0,types_snake/* createSnakeFromCells */.yS)(Array.from({ length: snakeN }, () => c));
    const one = getSnakeEscapePath(grid, outside, snake0, color);
    if (!one)
        return null;
    // get the position of the snake if it was going to leave the x,y cell
    const snakeICells = one.slice(0, snakeN);
    while (snakeICells.length < snakeN)
        snakeICells.push(snakeICells[snakeICells.length - 1]);
    const snakeI = (0,types_snake/* createSnakeFromCells */.yS)(snakeICells);
    // remove from the grid the colors that one eat
    const gridI = (0,types_grid/* copyGrid */.mi)(grid);
    for (const { x, y } of one)
        setEmptySafe(gridI, x, y);
    const two = getSnakeEscapePath(gridI, outside, snakeI, color);
    if (!two)
        return null;
    one.shift();
    one.reverse();
    one.push(...two);
    trimTunnelStart(grid, one);
    trimTunnelEnd(grid, one);
    return one;
};

;// CONCATENATED MODULE: ../solver/getPathTo.ts




/**
 * starting from snake0, get to the cell x,y
 * return the snake chain (reversed)
 */
const getPathTo = (grid, snake0, x, y) => {
    const openList = [{ snake: snake0, w: 0 }];
    const closeList = [];
    while (openList.length) {
        const c = openList.shift();
        const cx = (0,types_snake/* getHeadX */.tN)(c.snake);
        const cy = (0,types_snake/* getHeadY */.Ap)(c.snake);
        for (let i = 0; i < around4.length; i++) {
            const { x: dx, y: dy } = around4[i];
            const nx = cx + dx;
            const ny = cy + dy;
            if (nx === x && ny === y) {
                // unwrap
                const path = [(0,types_snake/* nextSnake */.Sc)(c.snake, dx, dy)];
                let e = c;
                while (e.parent) {
                    path.push(e.snake);
                    e = e.parent;
                }
                return path;
            }
            if ((0,types_grid/* isInsideLarge */.Yd)(grid, 2, nx, ny) &&
                !(0,types_snake/* snakeWillSelfCollide */.J)(c.snake, dx, dy) &&
                (!(0,types_grid/* isInside */.FK)(grid, nx, ny) || (0,types_grid/* isEmpty */.Im)((0,types_grid/* getColor */.oU)(grid, nx, ny)))) {
                const nsnake = (0,types_snake/* nextSnake */.Sc)(c.snake, dx, dy);
                if (!closeList.some((s) => (0,types_snake/* snakeEquals */.sW)(nsnake, s))) {
                    const w = c.w + 1;
                    const h = Math.abs(nx - x) + Math.abs(ny - y);
                    const f = w + h;
                    const o = { snake: nsnake, parent: c, w, h, f };
                    sortPush(openList, o, (a, b) => a.f - b.f);
                    closeList.push(nsnake);
                }
            }
        }
    }
};

;// CONCATENATED MODULE: ../solver/clearResidualColoredLayer.ts






const clearResidualColoredLayer = (grid, outside, snake0, color) => {
    const snakeN = (0,types_snake/* getSnakeLength */.T$)(snake0);
    const tunnels = getTunnellablePoints(grid, outside, snakeN, color);
    // sort
    tunnels.sort((a, b) => b.priority - a.priority);
    const chain = [snake0];
    while (tunnels.length) {
        // get the best next tunnel
        let t = getNextTunnel(tunnels, chain[0]);
        // goes to the start of the tunnel
        chain.unshift(...getPathTo(grid, chain[0], t[0].x, t[0].y));
        // goes to the end of the tunnel
        chain.unshift(...getTunnelPath(chain[0], t));
        // update grid
        for (const { x, y } of t)
            clearResidualColoredLayer_setEmptySafe(grid, x, y);
        // update outside
        fillOutside(outside, grid);
        // update tunnels
        for (let i = tunnels.length; i--;)
            if ((0,types_grid/* isEmpty */.Im)((0,types_grid/* getColor */.oU)(grid, tunnels[i].x, tunnels[i].y)))
                tunnels.splice(i, 1);
            else {
                const t = tunnels[i];
                const tunnel = getBestTunnel(grid, outside, t.x, t.y, color, snakeN);
                if (!tunnel)
                    tunnels.splice(i, 1);
                else {
                    t.tunnel = tunnel;
                    t.priority = getPriority(grid, color, tunnel);
                }
            }
        // re-sort
        tunnels.sort((a, b) => b.priority - a.priority);
    }
    chain.pop();
    return chain;
};
const getNextTunnel = (ts, snake) => {
    let minDistance = Infinity;
    let closestTunnel = null;
    const x = (0,types_snake/* getHeadX */.tN)(snake);
    const y = (0,types_snake/* getHeadY */.Ap)(snake);
    const priority = ts[0].priority;
    for (let i = 0; ts[i] && ts[i].priority === priority; i++) {
        const t = ts[i].tunnel;
        const d = distanceSq(t[0].x, t[0].y, x, y);
        if (d < minDistance) {
            minDistance = d;
            closestTunnel = t;
        }
    }
    return closestTunnel;
};
/**
 * get all the tunnels for all the cells accessible
 */
const getTunnellablePoints = (grid, outside, snakeN, color) => {
    const points = [];
    for (let x = grid.width; x--;)
        for (let y = grid.height; y--;) {
            const c = (0,types_grid/* getColor */.oU)(grid, x, y);
            if (!(0,types_grid/* isEmpty */.Im)(c) && c < color) {
                const tunnel = getBestTunnel(grid, outside, x, y, color, snakeN);
                if (tunnel) {
                    const priority = getPriority(grid, color, tunnel);
                    points.push({ x, y, priority, tunnel });
                }
            }
        }
    return points;
};
/**
 * get the score of the tunnel
 * prioritize tunnel with maximum color smaller than <color> and with minimum <color>
 * with some tweaks
 */
const getPriority = (grid, color, tunnel) => {
    let nColor = 0;
    let nLess = 0;
    for (let i = 0; i < tunnel.length; i++) {
        const { x, y } = tunnel[i];
        const c = clearResidualColoredLayer_getColorSafe(grid, x, y);
        if (!(0,types_grid/* isEmpty */.Im)(c) && i === tunnel.findIndex((p) => p.x === x && p.y === y)) {
            if (c === color)
                nColor += 1;
            else
                nLess += color - c;
        }
    }
    if (nColor === 0)
        return 99999;
    return nLess / nColor;
};
const distanceSq = (ax, ay, bx, by) => (ax - bx) ** 2 + (ay - by) ** 2;
const clearResidualColoredLayer_getColorSafe = (grid, x, y) => (0,types_grid/* isInside */.FK)(grid, x, y) ? (0,types_grid/* getColor */.oU)(grid, x, y) : 0;
const clearResidualColoredLayer_setEmptySafe = (grid, x, y) => {
    if ((0,types_grid/* isInside */.FK)(grid, x, y))
        (0,types_grid/* setColorEmpty */.l$)(grid, x, y);
};

;// CONCATENATED MODULE: ../solver/clearCleanColoredLayer.ts





const clearCleanColoredLayer = (grid, outside, snake0, color) => {
    const snakeN = (0,types_snake/* getSnakeLength */.T$)(snake0);
    const points = clearCleanColoredLayer_getTunnellablePoints(grid, outside, snakeN, color);
    const chain = [snake0];
    while (points.length) {
        const path = getPathToNextPoint(grid, chain[0], color, points);
        path.pop();
        for (const snake of path)
            clearCleanColoredLayer_setEmptySafe(grid, (0,types_snake/* getHeadX */.tN)(snake), (0,types_snake/* getHeadY */.Ap)(snake));
        chain.unshift(...path);
    }
    fillOutside(outside, grid);
    chain.pop();
    return chain;
};
const clearCleanColoredLayer_unwrap = (m) => !m ? [] : [m.snake, ...clearCleanColoredLayer_unwrap(m.parent)];
const getPathToNextPoint = (grid, snake0, color, points) => {
    const closeList = [];
    const openList = [{ snake: snake0 }];
    while (openList.length) {
        const o = openList.shift();
        const x = (0,types_snake/* getHeadX */.tN)(o.snake);
        const y = (0,types_snake/* getHeadY */.Ap)(o.snake);
        const i = points.findIndex((p) => p.x === x && p.y === y);
        if (i >= 0) {
            points.splice(i, 1);
            return clearCleanColoredLayer_unwrap(o);
        }
        for (const { x: dx, y: dy } of around4) {
            if ((0,types_grid/* isInsideLarge */.Yd)(grid, 2, x + dx, y + dy) &&
                !(0,types_snake/* snakeWillSelfCollide */.J)(o.snake, dx, dy) &&
                clearCleanColoredLayer_getColorSafe(grid, x + dx, y + dy) <= color) {
                const snake = (0,types_snake/* nextSnake */.Sc)(o.snake, dx, dy);
                if (!closeList.some((s0) => (0,types_snake/* snakeEquals */.sW)(s0, snake))) {
                    closeList.push(snake);
                    openList.push({ snake, parent: o });
                }
            }
        }
    }
};
/**
 * get all cells that are tunnellable
 */
const clearCleanColoredLayer_getTunnellablePoints = (grid, outside, snakeN, color) => {
    const points = [];
    for (let x = grid.width; x--;)
        for (let y = grid.height; y--;) {
            const c = (0,types_grid/* getColor */.oU)(grid, x, y);
            if (!(0,types_grid/* isEmpty */.Im)(c) &&
                c <= color &&
                !points.some((p) => p.x === x && p.y === y)) {
                const tunnel = getBestTunnel(grid, outside, x, y, color, snakeN);
                if (tunnel)
                    for (const p of tunnel)
                        if (!clearCleanColoredLayer_isEmptySafe(grid, p.x, p.y))
                            points.push(p);
            }
        }
    return points;
};
const clearCleanColoredLayer_getColorSafe = (grid, x, y) => (0,types_grid/* isInside */.FK)(grid, x, y) ? (0,types_grid/* getColor */.oU)(grid, x, y) : 0;
const clearCleanColoredLayer_setEmptySafe = (grid, x, y) => {
    if ((0,types_grid/* isInside */.FK)(grid, x, y))
        (0,types_grid/* setColorEmpty */.l$)(grid, x, y);
};
const clearCleanColoredLayer_isEmptySafe = (grid, x, y) => !(0,types_grid/* isInside */.FK)(grid, x, y) && (0,types_grid/* isEmpty */.Im)((0,types_grid/* getColor */.oU)(grid, x, y));

;// CONCATENATED MODULE: ../solver/getBestRoute.ts




const getBestRoute = (grid0, snake0) => {
    const grid = (0,types_grid/* copyGrid */.mi)(grid0);
    const outside = createOutside(grid);
    const chain = [snake0];
    for (const color of extractColors(grid)) {
        if (color > 1)
            chain.unshift(...clearResidualColoredLayer(grid, outside, chain[0], color));
        chain.unshift(...clearCleanColoredLayer(grid, outside, chain[0], color));
    }
    return chain.reverse();
};
const extractColors = (grid) => {
    // @ts-ignore
    let maxColor = Math.max(...grid.data);
    return Array.from({ length: maxColor }, (_, i) => (i + 1));
};

;// CONCATENATED MODULE: ../solver/getPathToPose.ts





const getPathToPose_isEmptySafe = (grid, x, y) => !(0,types_grid/* isInside */.FK)(grid, x, y) || (0,types_grid/* isEmpty */.Im)((0,types_grid/* getColor */.oU)(grid, x, y));
const getPathToPose = (snake0, target, grid) => {
    if ((0,types_snake/* snakeEquals */.sW)(snake0, target))
        return [];
    const targetCells = (0,types_snake/* snakeToCells */.HU)(target).reverse();
    const snakeN = (0,types_snake/* getSnakeLength */.T$)(snake0);
    const box = {
        min: {
            x: Math.min((0,types_snake/* getHeadX */.tN)(snake0), (0,types_snake/* getHeadX */.tN)(target)) - snakeN - 1,
            y: Math.min((0,types_snake/* getHeadY */.Ap)(snake0), (0,types_snake/* getHeadY */.Ap)(target)) - snakeN - 1,
        },
        max: {
            x: Math.max((0,types_snake/* getHeadX */.tN)(snake0), (0,types_snake/* getHeadX */.tN)(target)) + snakeN + 1,
            y: Math.max((0,types_snake/* getHeadY */.Ap)(snake0), (0,types_snake/* getHeadY */.Ap)(target)) + snakeN + 1,
        },
    };
    const [t0, ...forbidden] = targetCells;
    forbidden.slice(0, 3);
    const openList = [{ snake: snake0, w: 0 }];
    const closeList = [];
    while (openList.length) {
        const o = openList.shift();
        const x = (0,types_snake/* getHeadX */.tN)(o.snake);
        const y = (0,types_snake/* getHeadY */.Ap)(o.snake);
        if (x === t0.x && y === t0.y) {
            const path = [];
            let e = o;
            while (e) {
                path.push(e.snake);
                e = e.parent;
            }
            path.unshift(...getTunnelPath(path[0], targetCells));
            path.pop();
            path.reverse();
            return path;
        }
        for (let i = 0; i < around4.length; i++) {
            const { x: dx, y: dy } = around4[i];
            const nx = x + dx;
            const ny = y + dy;
            if (!(0,types_snake/* snakeWillSelfCollide */.J)(o.snake, dx, dy) &&
                (!grid || getPathToPose_isEmptySafe(grid, nx, ny)) &&
                (grid
                    ? (0,types_grid/* isInsideLarge */.Yd)(grid, 2, nx, ny)
                    : box.min.x <= nx &&
                        nx <= box.max.x &&
                        box.min.y <= ny &&
                        ny <= box.max.y) &&
                !forbidden.some((p) => p.x === nx && p.y === ny)) {
                const snake = (0,types_snake/* nextSnake */.Sc)(o.snake, dx, dy);
                if (!closeList.some((s) => (0,types_snake/* snakeEquals */.sW)(snake, s))) {
                    const w = o.w + 1;
                    const h = Math.abs(nx - x) + Math.abs(ny - y);
                    const f = w + h;
                    sortPush(openList, { f, w, snake, parent: o }, (a, b) => a.f - b.f);
                    closeList.push(snake);
                }
            }
        }
    }
};

;// CONCATENATED MODULE: ../types/__fixtures__/snake.ts

const create = (length) => (0,types_snake/* createSnakeFromCells */.yS)(Array.from({ length }, (_, i) => ({ x: i, y: -1 })));
const snake1 = create(1);
const snake3 = create(3);
const snake4 = create(4);
const snake5 = create(5);
const snake9 = create(9);

;// CONCATENATED MODULE: ../generate-snake-animation/cellsToGrid.ts

const cellsToGrid = (cells) => {
    const width = Math.max(0, ...cells.map((c) => c.x)) + 1;
    const height = Math.max(0, ...cells.map((c) => c.y)) + 1;
    const grid = (0,types_grid/* createEmptyGrid */.Kb)(width, height);
    for (const c of cells) {
        if (c.level > 0)
            (0,types_grid/* setColor */.wW)(grid, c.x, c.y, c.level);
        else
            (0,types_grid/* setColorEmpty */.l$)(grid, c.x, c.y);
    }
    return grid;
};

;// CONCATENATED MODULE: ../generate-snake-animation/generateSnakeAnimation.ts







const getUserContribution = async (source) => {
    switch (source.platform) {
        case "github":
            return getGithubUserContribution(source.username, {
                githubToken: source.githubToken,
                baseUrl: source.baseUrl,
            });
        case "gitlab":
            return getGitlabUserContribution(source.username, {
                baseUrl: source.baseUrl,
            });
        case "forgejo":
            return getForgejoUserContribution(source.username, {
                baseUrl: source.baseUrl,
            });
    }
};
const generateSnakeAnimation = async (source, outputs) => {
    console.log(`🎣 fetching user contribution from ${source.platform}`);
    const cells = await getUserContribution(source);
    const grid = cellsToGrid(cells);
    const snake = snake4;
    console.log("📡 computing best route");
    const chain = getBestRoute(grid, snake);
    chain.push(...getPathToPose(chain.slice(-1)[0], snake));
    return Promise.all(outputs.map(async (out, i) => {
        if (!out)
            return;
        const { format, drawOptions, animationOptions } = out;
        switch (format) {
            case "svg": {
                console.log(`🖌 creating svg (outputs[${i}])`);
                const { createSvg } = await __nccwpck_require__.e(/* import() */ 578).then(__nccwpck_require__.bind(__nccwpck_require__, 578));
                return createSvg(grid, cells, chain, drawOptions, animationOptions);
            }
            case "gif": {
                console.log(`📹 creating gif (outputs[${i}])`);
                const { createGif } = await __nccwpck_require__.e(/* import() */ 642).then(__nccwpck_require__.bind(__nccwpck_require__, 642));
                return createGif(grid, cells, chain, drawOptions, animationOptions);
            }
        }
    }));
};

;// CONCATENATED MODULE: ../generate-snake-animation/palettes.ts
const basePalettes = {
    "github-light": {
        colorBackground: "#ffffff",
        colorDotBorder: "#1b1f230a",
        colorDots: ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"],
        colorEmpty: "#ebedf0",
        colorSnake: "purple",
    },
    "github-dark": {
        colorBackground: "#0c1116",
        colorDotBorder: "#1b1f230a",
        colorEmpty: "#161b22",
        colorDots: ["#161b22", "#01311f", "#034525", "#0f6d31", "#00c647"],
        colorSnake: "purple",
    },
    "forgejo-light": {
        colorBackground: "#ffffff",
        colorDotBorder: "#00000010",
        colorEmpty: "#d4d4d8",
        colorDots: ["#d4d4d8", "#fdba74", "#f97316", "#c2410c", "#7c2d12"],
        colorSnake: "#7c2d12",
    },
    "forgejo-dark": {
        colorBackground: "#1f2937",
        colorDotBorder: "#ffffff10",
        colorEmpty: "#2b3642",
        colorDots: ["#2b3642", "#9a3412", "#ea580c", "#fb923c", "#fed7aa"],
        colorSnake: "#fed7aa",
    },
    "codeberg-light": {
        colorBackground: "#ffffff",
        colorDotBorder: "#00000010",
        colorEmpty: "#d0d7de",
        colorDots: ["#d0d7de", "#8db5dc", "#679cd0", "#4183c4", "#254f77"],
        colorSnake: "#254f77",
    },
    "codeberg-dark": {
        colorBackground: "#161b22",
        colorDotBorder: "#ffffff10",
        colorEmpty: "#3b444a",
        colorDots: ["#3b444a", "#254f77", "#31699f", "#4183c4", "#8db5dc"],
        colorSnake: "#8db5dc",
    },
    "gitlab-light": {
        colorBackground: "#ffffff",
        colorDotBorder: "#00000010",
        colorEmpty: "#edebe6",
        colorDots: ["#edebe6", "#9dc7f1", "#428fdc", "#2f68b4", "#284779"],
        colorSnake: "#284779",
    },
    "gitlab-dark": {
        colorBackground: "#1f1e24",
        colorDotBorder: "#ffffff10",
        colorEmpty: "#2a2a36",
        colorDots: ["#2a2a36", "#284779", "#2f68b4", "#428fdc", "#9dc7f1"],
        colorSnake: "#9dc7f1",
    },
};
// aliases
const palettes = {
    ...basePalettes,
    // aliases
    github: basePalettes["github-light"],
    forgejo: basePalettes["forgejo-light"],
    codeberg: basePalettes["codeberg-light"],
    gitlab: basePalettes["gitlab-light"],
    default: basePalettes["github-light"],
};

;// CONCATENATED MODULE: ../generate-snake-animation/outputsOptions.ts

const parseOutputsOption = (lines) => lines.map(parseEntry);
const parseEntry = (entry) => {
    const m = entry.trim().match(/^(.+\.(svg|gif))(\?(.*)|\s*({.*}))?$/);
    if (!m)
        return null;
    const [, filename, format, _, q1, q2] = m;
    const query = q1 ?? q2;
    let sp = new URLSearchParams(query || "");
    try {
        const o = JSON.parse(query);
        if (Array.isArray(o.color_dots))
            o.color_dots = o.color_dots.join(",");
        sp = new URLSearchParams(o);
    }
    catch (err) {
        if (!(err instanceof SyntaxError))
            throw err;
    }
    const drawOptions = {
        sizeDotBorderRadius: 2,
        sizeCell: 16,
        sizeDot: 12,
        ...palettes["default"],
    };
    const animationOptions = {
        frameByStep: 1,
        stepDurationMs: 100,
    };
    {
        const palette = palettes[sp.get("palette")];
        if (palette) {
            Object.assign(drawOptions, palette);
        }
    }
    if (sp.has("color_dots")) {
        const colors = sp.get("color_dots").split(/[,;]/);
        drawOptions.colorDots = colors;
        drawOptions.colorEmpty = colors[0];
    }
    if (sp.has("color_snake"))
        drawOptions.colorSnake = sp.get("color_snake");
    if (sp.has("color_background"))
        drawOptions.colorBackground = sp.get("color_background");
    if (sp.has("color_dot_border"))
        drawOptions.colorDotBorder = sp.get("color_dot_border");
    return {
        filename,
        format: format,
        drawOptions,
        animationOptions,
    };
};

// EXTERNAL MODULE: external "node:os"
var external_node_os_ = __nccwpck_require__(161);
;// CONCATENATED MODULE: ./github-action.ts

/**
 * re-export getInput from "@actions/core" without the bloat
 */
const getInput = (name) => process.env[`INPUT_${name.replace(/ /g, "_").toUpperCase()}`] || "";
/**
 * re-export setFailed from "@actions/core" without the bloat
 */
const setFailed = (message) => {
    process.exitCode = 1;
    process.stdout.write(`::error::${escapeData(message)}::${external_node_os_.EOL}`);
};
function escapeData(s) {
    return s.replace(/%/g, "%25").replace(/\r/g, "%0D").replace(/\n/g, "%0A");
}

;// CONCATENATED MODULE: ./index.ts





(async () => {
    try {
        const userName = getInput("github_user_name");
        const githubToken = process.env.GITHUB_TOKEN ?? getInput("github_token");
        const outputsRaw = [
            ...getInput("outputs").split("\n"),
            //
            // legacy
            getInput("gif_out_path"),
            getInput("svg_out_path"),
        ]
            .map((x) => x.trim())
            .filter(Boolean);
        const outputs = parseOutputsOption(outputsRaw);
        const results = await generateSnakeAnimation({ platform: "github", username: userName, githubToken }, outputs);
        outputs.forEach((out, i) => {
            const result = results[i];
            if (out?.filename && result) {
                console.log(`💾 writing to ${out?.filename}`);
                external_node_fs_.mkdirSync(external_node_path_.dirname(out?.filename), { recursive: true });
                external_node_fs_.writeFileSync(out?.filename, result);
            }
        });
    }
    catch (e) {
        setFailed(`Action failed with "${e.message}"`);
    }
})();

module.exports = __webpack_exports__;
/******/ })()
;