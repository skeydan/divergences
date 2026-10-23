// divergences chart helpers for Observable JS (```{ojs} cells) in posts.
//
//   import {darkMode, theme, colors, legend} from "/assets/viz.js"
//   dark = darkMode()                    // re-runs the chart when the reader toggles light/dark
//   Plot.plot({...theme(dark), marks: [ ... ]})
//
// The palettes below are validated (lightness band, chroma, colour-blind separation,
// contrast) against this site's light and dark backgrounds. Use the series colours
// in this order; for more than 6 series, use small multiples instead of more colours.

const TOKENS = {
  light: {
    surface: "#e9f3f4", ink: "#0c2a33", ink2: "#3a5860", muted: "#526c75",
    grid: "#d3e3e6", axis: "#b9cbcd",
    // cyan, brown-orange, violet, amber, blue, teal-green
    series: ["#0a8fa8", "#c0662a", "#6a4bc4", "#a87d00", "#2f6fc0", "#0f8a66"],
    // sequential: one hue, low -> high (heatmaps, maps). For a few ordered classes
    // (tiers, buckets) start at the 4th step (#2fa2bd) so every class stays visible.
    // diverging: cool <- neutral -> warm (anomalies, above/below a baseline)
    sequential: ["#d7eef3", "#a9dbe6", "#6fc1d4", "#2fa2bd", "#0b7f98", "#085e71", "#05404d"],
    diverging: { cool: "#0a8fa8", neutral: "#d6e3e5", warm: "#c0662a" },
  },
  dark: {
    surface: "#081a20", ink: "#e1f0f2", ink2: "#a7c3c8", muted: "#86a6ad",
    grid: "#16323a", axis: "#2a4a53",
    series: ["#1aa3bb", "#cf7036", "#8e77e4", "#b88b0c", "#5a8bdc", "#279f78"],
    sequential: ["#0d3a44", "#0f5262", "#127085", "#1690ab", "#3fb0c8", "#7ccbdb", "#b7e4ec"],
    diverging: { cool: "#1aa3bb", neutral: "#24393f", warm: "#cf7036" },
  },
};

export const FONT = "'Bricolage Grotesque', system-ui, sans-serif";

export function isDark() {
  return typeof document !== "undefined" && document.body.classList.contains("quarto-dark");
}

// An OJS-reactive value: true in dark mode, false in light mode; updates on toggle.
export async function* darkMode() {
  let resolve;
  let changed = new Promise((r) => (resolve = r));
  const obs = new MutationObserver(() => resolve());
  obs.observe(document.body, { attributes: true, attributeFilter: ["class"] });
  try {
    let last = null;
    while (true) {
      const now = isDark();
      if (now !== last) { last = now; yield now; }
      await changed;
      changed = new Promise((r) => (resolve = r));
    }
  } finally {
    obs.disconnect();
  }
}

export function colors(dark = isDark()) {
  return TOKENS[dark ? "dark" : "light"];
}

// Base options for Observable Plot: quiet axes and grid, site fonts, series colours.
export function theme(dark = isDark(), { width } = {}) {
  const c = colors(dark);
  return {
    width,
    style: { background: "transparent", color: c.ink2, fontFamily: FONT, fontSize: "12px", overflow: "visible" },
    color: { range: c.series },
    marginLeft: 44,
    marginBottom: 32,
    x: { line: false, tickSize: 0, labelArrow: "none" },
    y: { grid: true, tickSize: 0, labelArrow: "none" },
  };
}

// Tooltip styling for Plot.tip (matches the site's cards).
export function tipStyle(dark = isDark()) {
  const c = colors(dark);
  return { fill: c.surface, stroke: c.axis, textPadding: 8, fontFamily: FONT, fontSize: 12 };
}

// A small HTML legend: legend([["El Niño", "#d9702c", "swatch"], ["La Niña", "#0b8aa6", "swatch"]])
export function legend(entries) {
  const div = document.createElement("div");
  div.className = "dv-viz-legend";
  for (const [label, color, kind] of entries) {
    const s = document.createElement("span");
    if (kind === "swatch") s.className = "swatch";
    s.style.setProperty("--c", color);
    s.textContent = label;
    div.appendChild(s);
  }
  return div;
}
