// Acceptance pack for the presentation-token source (task M5-T148 part A,
// the presentation contract's section 5). Node built-in runner; no install.
//
//   S1 parity  : the globals.css block and the Python module equal a fresh
//                render of docs/design/presentation-tokens.json, and a changed
//                JSON colour that was not regenerated is caught.
//   S2 values  : the tokens carry the contract's section-5 values, and the
//                font token equals the application font stack (ruling V4).
//   S3 contrast: every declared text/background pair is computed; text >= 4.5:1,
//                a control boundary >= 3:1; the quiet divider is never an edge.

import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";

import {
  loadTokens,
  renderCssBlock,
  renderGlobalsCss,
  renderPython,
  contrastRatio,
  GLOBALS_CSS_PATH,
  PY_PATH,
} from "../presentation-tokens.mjs";

const CSS_BEGIN_FIND = "  /* BEGIN GENERATED presentation tokens";
const CSS_END_FIND = "  /* END GENERATED presentation tokens */";

function onDiskCssBlock() {
  const css = readFileSync(GLOBALS_CSS_PATH, "utf8");
  const begin = css.indexOf(CSS_BEGIN_FIND);
  const endStart = css.indexOf(CSS_END_FIND, begin);
  assert.ok(begin !== -1 && endStart !== -1, "globals.css must carry the marked token block");
  return css.slice(begin, endStart + CSS_END_FIND.length);
}

// --- S1: parity -----------------------------------------------------------

test("S1 the globals.css block equals a fresh render of the JSON", () => {
  const tokens = loadTokens();
  assert.equal(onDiskCssBlock(), renderCssBlock(tokens));
  // Re-rendering the whole file is a no-op (only the marked block changes).
  const css = readFileSync(GLOBALS_CSS_PATH, "utf8");
  assert.equal(renderGlobalsCss(tokens, css), css);
});

test("S1 the Python module equals a fresh render of the JSON", () => {
  const tokens = loadTokens();
  assert.equal(readFileSync(PY_PATH, "utf8"), renderPython(tokens));
});

test("S1 a changed JSON colour that is not regenerated fails parity for both outputs", () => {
  const tokens = loadTokens();
  const drifted = JSON.parse(JSON.stringify(tokens));
  drifted.color.ink = "#000000"; // changed source, outputs NOT regenerated
  assert.notEqual(renderCssBlock(drifted), onDiskCssBlock());
  assert.notEqual(renderPython(drifted), readFileSync(PY_PATH, "utf8"));
});

// --- S2: the contract's section-5 values ----------------------------------

test("S2 spacing scale is 4, 8, 12, 16, 24, 32, 48 px", () => {
  const { spacing } = loadTokens();
  assert.deepEqual(
    Object.entries(spacing).map(([k, v]) => [k, v]),
    [
      ["4", 4],
      ["8", 8],
      ["12", 12],
      ["16", 16],
      ["24", 24],
      ["32", 32],
      ["48", 48],
    ],
  );
});

test("S2 the nine palette colours match the contract table", () => {
  const { color } = loadTokens();
  assert.deepEqual(color, {
    ink: "#182B3A",
    supporting: "#52616C",
    action: "#18577A",
    page: "#F2F5F6",
    surface: "#FFFFFF",
    divider: "#D8E0E5",
    selected: "#EEF4F7",
    "caution-ink": "#795318",
    "caution-surface": "#FBF4E7",
  });
});

test("S2 control height 44 px, control radius 6 px, panel radius 8 px", () => {
  const tokens = loadTokens();
  assert.equal(tokens.control.height, 44);
  assert.equal(tokens.control.radius, 6);
  assert.equal(tokens.radius.panel, 8);
});

test("S2 each type role sits inside its contract screen and print range", () => {
  const { type } = loadTokens();
  const within = (v, lo, hi) => v >= lo && v <= hi;
  assert.ok(within(type["property-title"].screen_px, 28, 30));
  assert.equal(type["property-title"].line_height, 1.2);
  assert.equal(type["property-title"].weight, 700);
  assert.ok(within(type["property-title"].print_pt, 22, 23));
  assert.ok(within(type["headline-value"].screen_px, 36, 44));
  assert.equal(type["headline-value"].line_height, 1.1);
  assert.ok(within(type["headline-value"].print_pt, 28, 32));
  assert.ok(within(type["section-title"].screen_px, 18, 20));
  assert.equal(type["section-title"].line_height, 1.3);
  assert.ok([600, 700].includes(type["section-title"].weight));
  assert.ok(within(type["section-title"].print_pt, 12, 14));
  assert.equal(type.body.screen_px, 16);
  assert.ok(within(type.body.line_height, 1.45, 1.55));
  assert.ok(within(type.body.print_pt, 10.5, 11));
  assert.ok(within(type.body.print_line_height, 1.35, 1.45));
  assert.ok(within(type.compact.screen_px, 14, 15));
  assert.ok(type.compact.line_height >= 1.35);
  assert.ok(within(type.compact.print_pt, 9.5, 10));
  assert.ok(within(type["source-note"].screen_px, 13, 14));
  assert.ok(within(type["source-note"].print_pt, 8.5, 9));
  // Drawing-label minimum: at least 14 px / 8.5 pt, 9.5 pt preferred.
  assert.ok(type["drawing-label"].screen_px >= 14);
  assert.ok(type["drawing-label"].print_pt >= 8.5);
  assert.equal(type["drawing-label"].print_pt_preferred, 9.5);
});

test("S2 the font token equals the application font stack in layout.tsx (ruling V4)", () => {
  const layoutPath = join(dirname(GLOBALS_CSS_PATH), "layout.tsx");
  const layout = readFileSync(layoutPath, "utf8");
  const match = layout.match(/fontFamily:\s*"([^"]+)"/);
  assert.ok(match, "layout.tsx must declare a fontFamily string");
  assert.equal(loadTokens().font.family, match[1]);
});

test("S2 the screen statuses are settled (no marker), conditional, not-known; colour secondary", () => {
  const { status } = loadTokens();
  assert.equal(status.settled.marker, false);
  assert.equal(status.conditional.marker, true);
  assert.equal(status.conditional.color_role, "secondary");
  assert.equal(status["not-known"].marker, true);
  assert.equal(status["not-known"].color_role, "secondary");
  assert.ok(!("verified" in status), "no Verified status token (ruling V3)");
});

// --- S3: contrast ---------------------------------------------------------

test("S3 every declared pair meets its WCAG 2.2 minimum; the divider is never an edge", () => {
  const tokens = loadTokens();
  const color = tokens.color;
  const report = [];
  let dividerPairs = 0;
  for (const pair of tokens.contrastPairs) {
    const ratio = contrastRatio(color[pair.fg], color[pair.bg]);
    report.push(`${pair.name}: ${ratio.toFixed(2)}:1 (${pair.role})`);
    if (pair.role === "text") {
      assert.ok(ratio >= 4.5, `${pair.name} is ${ratio.toFixed(2)}:1, below 4.5:1 for text`);
    } else if (pair.role === "control") {
      assert.ok(ratio >= 3, `${pair.name} is ${ratio.toFixed(2)}:1, below 3:1 for a control edge`);
    } else {
      assert.equal(pair.role, "divider");
      assert.equal(pair.controlEdge, false, `${pair.name} must be marked never a control edge`);
      dividerPairs += 1;
    }
  }
  assert.ok(dividerPairs >= 1, "the quiet divider must be declared and marked non-edge");
  // No pair uses the quiet divider as a control boundary.
  for (const pair of tokens.contrastPairs) {
    assert.ok(
      !(pair.fg === "divider" && pair.role === "control"),
      "the quiet divider must never be a control edge",
    );
  }
  console.log("S3 contrast ratios:\n  " + report.join("\n  "));
});
