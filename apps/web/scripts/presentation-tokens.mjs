#!/usr/bin/env node
// One source of presentation tokens for the architect-facing outputs
// (task M5-T148, the presentation contract's section 5).
//
// docs/design/presentation-tokens.json is the ONLY hand-edited source. This
// generator renders two outputs from it and keeps them in parity:
//   * the marked `--pt-*` block inside :root in apps/web/src/app/globals.css
//     (every existing token is preserved; only the marked block is rewritten),
//   * the Python module services/api/app/drawings/kit/presentation_tokens.py
//     (read by the server drawing kit and the PDF).
//
// Run with no argument to (re)write both outputs. Run with `--check` to exit
// non-zero when either output differs from a fresh render of the JSON — so a
// changed JSON value that was not regenerated fails closed. Node built-ins only;
// this runs with no install and is covered by `node --test scripts/tests/*`.

import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath, pathToFileURL } from "node:url";
import { dirname, join } from "node:path";
import process from "node:process";

const SCRIPT_DIR = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = join(SCRIPT_DIR, "..", "..", "..");

export const JSON_PATH = join(REPO_ROOT, "docs", "design", "presentation-tokens.json");
export const GLOBALS_CSS_PATH = join(REPO_ROOT, "apps", "web", "src", "app", "globals.css");
export const PY_PATH = join(
  REPO_ROOT,
  "services",
  "api",
  "app",
  "drawings",
  "kit",
  "presentation_tokens.py",
);

// The token groups that both outputs mirror, in a fixed render order.
const TOKEN_GROUPS = ["color", "spacing", "control", "radius", "font", "type", "status"];

const CSS_BEGIN =
  "  /* BEGIN GENERATED presentation tokens (M5-T148) — source:" +
  " docs/design/presentation-tokens.json\n" +
  "     generator: apps/web/scripts/presentation-tokens.mjs. Do not edit by hand. */";
const CSS_END = "  /* END GENERATED presentation tokens */";

export function loadTokens(jsonPath = JSON_PATH) {
  return JSON.parse(readFileSync(jsonPath, "utf8"));
}

// A JSON number as its literal text (28 -> "28", 1.35 -> "1.35", 10.5 -> "10.5").
function numText(value) {
  return String(value);
}

function assertPlainString(value) {
  if (value.includes('"') || value.includes("\\")) {
    throw new Error(`token string carries an unsupported character: ${value}`);
  }
  return value;
}

// --- CSS ------------------------------------------------------------------

export function renderCssBlock(tokens) {
  const lines = [CSS_BEGIN];
  const push = (name, value) => lines.push(`  --pt-${name}: ${value};`);

  for (const [key, value] of Object.entries(tokens.spacing)) {
    push(`space-${key}`, `${numText(value)}px`);
  }
  for (const [key, value] of Object.entries(tokens.color)) {
    push(`color-${key}`, assertPlainString(value));
  }
  push("control-height", `${numText(tokens.control.height)}px`);
  push("control-radius", `${numText(tokens.control.radius)}px`);
  push("radius-panel", `${numText(tokens.radius.panel)}px`);
  push("font-family", assertPlainString(tokens.font.family));

  for (const [role, spec] of Object.entries(tokens.type)) {
    push(`type-${role}-size`, `${numText(spec.screen_px)}px`);
    push(`type-${role}-line`, numText(spec.line_height));
    push(`type-${role}-weight`, numText(spec.weight));
  }
  for (const [name, spec] of Object.entries(tokens.status)) {
    if (!spec.marker) {
      continue;
    }
    push(`status-${name}-ink`, assertPlainString(spec.ink));
    push(`status-${name}-surface`, assertPlainString(spec.surface));
  }

  lines.push(CSS_END);
  return lines.join("\n");
}

// Replace the marked block in place, or insert it just before the close of the
// first :root rule. Idempotent: re-running produces byte-identical output.
export function injectCss(originalCss, block) {
  const begin = originalCss.indexOf("  /* BEGIN GENERATED presentation tokens");
  if (begin !== -1) {
    const endStart = originalCss.indexOf(CSS_END, begin);
    if (endStart === -1) {
      throw new Error("globals.css has a BEGIN marker but no matching END marker");
    }
    const endIdx = endStart + CSS_END.length;
    return originalCss.slice(0, begin) + block + originalCss.slice(endIdx);
  }
  const rootOpen = originalCss.indexOf(":root {");
  if (rootOpen === -1) {
    throw new Error("globals.css has no :root rule to receive the generated block");
  }
  const closeIdx = originalCss.indexOf("\n}", rootOpen);
  if (closeIdx === -1) {
    throw new Error("globals.css :root rule is not closed");
  }
  return `${originalCss.slice(0, closeIdx)}\n\n${block}${originalCss.slice(closeIdx)}`;
}

export function renderGlobalsCss(tokens, originalCss) {
  return injectCss(originalCss, renderCssBlock(tokens));
}

// --- Python ---------------------------------------------------------------

function pyLiteral(value, indent) {
  const pad = "    ".repeat(indent);
  const padInner = "    ".repeat(indent + 1);
  if (value === null) {
    return "None";
  }
  if (typeof value === "boolean") {
    return value ? "True" : "False";
  }
  if (typeof value === "number") {
    return numText(value);
  }
  if (typeof value === "string") {
    return `"${assertPlainString(value)}"`;
  }
  const keys = Object.keys(value);
  if (keys.length === 0) {
    return "{}";
  }
  const body = keys
    .map((key) => `${padInner}"${key}": ${pyLiteral(value[key], indent + 1)},`)
    .join("\n");
  return `{\n${body}\n${pad}}`;
}

export function renderPython(tokens) {
  const subset = {};
  for (const group of TOKEN_GROUPS) {
    subset[group] = tokens[group];
  }
  const header =
    '"""Generated presentation tokens (architect presentation contract, section 5).\n' +
    "\n" +
    "Source of truth: docs/design/presentation-tokens.json\n" +
    "Generator: apps/web/scripts/presentation-tokens.mjs (task M5-T148).\n" +
    "Do not edit by hand; regenerate and commit the JSON, this module and the\n" +
    "globals.css block together. The server drawing kit and the PDF read these.\n" +
    '"""\n';
  const tokensText = `TOKENS = ${pyLiteral(subset, 0)}\n`;
  const aliases = [
    'COLOR = TOKENS["color"]',
    'SPACING = TOKENS["spacing"]',
    'CONTROL = TOKENS["control"]',
    'RADIUS = TOKENS["radius"]',
    'FONT = TOKENS["font"]',
    'TYPE = TOKENS["type"]',
    'STATUS = TOKENS["status"]',
  ].join("\n");
  return `${header}\n${tokensText}\n${aliases}\n`;
}

// --- WCAG 2.2 relative-luminance contrast ---------------------------------

function channelToLinear(eight) {
  const c = eight / 255;
  return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
}

function relativeLuminance(hex) {
  const h = hex.replace("#", "");
  const r = parseInt(h.slice(0, 2), 16);
  const g = parseInt(h.slice(2, 4), 16);
  const b = parseInt(h.slice(4, 6), 16);
  return (
    0.2126 * channelToLinear(r) +
    0.7152 * channelToLinear(g) +
    0.0722 * channelToLinear(b)
  );
}

export function contrastRatio(fgHex, bgHex) {
  const a = relativeLuminance(fgHex);
  const b = relativeLuminance(bgHex);
  const hi = Math.max(a, b);
  const lo = Math.min(a, b);
  return (hi + 0.05) / (lo + 0.05);
}

// --- CLI ------------------------------------------------------------------

function main(argv) {
  const check = argv.includes("--check");
  const tokens = loadTokens();
  const expectedCss = renderGlobalsCss(tokens, readFileSync(GLOBALS_CSS_PATH, "utf8"));
  const expectedPy = renderPython(tokens);

  if (check) {
    const actualCss = readFileSync(GLOBALS_CSS_PATH, "utf8");
    const actualPy = readFileSync(PY_PATH, "utf8");
    const problems = [];
    if (actualCss !== expectedCss) {
      problems.push(`${GLOBALS_CSS_PATH} is out of date with the token source`);
    }
    if (actualPy !== expectedPy) {
      problems.push(`${PY_PATH} is out of date with the token source`);
    }
    if (problems.length > 0) {
      for (const problem of problems) {
        console.error(`presentation-tokens --check FAILED: ${problem}`);
      }
      console.error("Run `node scripts/presentation-tokens.mjs` and commit the outputs.");
      process.exit(1);
    }
    console.log("presentation-tokens --check OK: CSS block and Python module match the source.");
    return;
  }

  writeFileSync(GLOBALS_CSS_PATH, expectedCss);
  writeFileSync(PY_PATH, expectedPy);
  console.log("presentation-tokens: wrote the globals.css block and presentation_tokens.py.");
}

if (process.argv[1] && pathToFileURL(process.argv[1]).href === import.meta.url) {
  main(process.argv.slice(2));
}
