// Print a report URL or a local HTML file to an A4 PDF with the installed Playwright Chromium
// (task M5-T153, scenario S5). The report composes its own A4 pages with an @page rule; this
// script honours that page size (preferCSSPageSize), prints backgrounds, and — because the
// installed Playwright (1.61.1) declares them in its PDFOptions type
// (node_modules/playwright-core/types/types.d.ts) — writes the heading bookmarks (outline) and a
// tagged (accessible) structure. NO package is added; it uses the Chromium that Playwright already
// installs. It starts no server and binds no port: it drives a `file:`/`http(s):` URL directly.
//
//   node scripts/print-report-pdf.mjs <url-or-html-file> <out.pdf>
//
// A missing argument, or an input file that does not exist, fails with a clear message and a
// non-zero exit.

import { chromium } from "playwright";
import { existsSync } from "node:fs";
import { isAbsolute, resolve } from "node:path";
import { pathToFileURL } from "node:url";

const USAGE = "usage: node scripts/print-report-pdf.mjs <url-or-html-file> <out.pdf>";

/**
 * Turn the first argument into a URL Playwright can open: an http(s)/file URL is used as-is; any
 * other string is treated as a local HTML file path and must exist. A missing file is a clear
 * failure (scenario S5).
 */
export function resolveInput(input) {
  if (typeof input !== "string" || input.trim() === "") {
    throw new Error(`${USAGE}\n  missing <url-or-html-file>`);
  }
  if (/^(https?|file):/i.test(input)) return input;
  const abs = isAbsolute(input) ? input : resolve(process.cwd(), input);
  if (!existsSync(abs)) {
    throw new Error(`input not found: ${input}\n  expected a URL or a readable HTML file`);
  }
  return pathToFileURL(abs).href;
}

/**
 * Render `input` (a URL or an HTML file) to `out` as a PDF. `launcher` is injectable so a test can
 * pass the installed chromium (it defaults to it). Throws a clear error on a missing argument.
 */
export async function printToPdf(input, out, { launcher = chromium } = {}) {
  const url = resolveInput(input);
  if (typeof out !== "string" || out.trim() === "") {
    throw new Error(`${USAGE}\n  missing <out.pdf>`);
  }
  const browser = await launcher.launch({ headless: true });
  try {
    const page = await browser.newPage();
    await page.goto(url, { waitUntil: "load" });
    await page.emulateMedia({ media: "print" });
    await page.pdf({
      path: out,
      preferCSSPageSize: true,
      printBackground: true,
      outline: true,
      tagged: true,
    });
  } finally {
    await browser.close();
  }
  return out;
}

const invokedDirectly =
  typeof process.argv[1] === "string" &&
  import.meta.url === pathToFileURL(process.argv[1]).href;

if (invokedDirectly) {
  const [input, out] = process.argv.slice(2);
  printToPdf(input, out).then(
    written => {
      console.log(`wrote ${written}`);
    },
    err => {
      console.error(String(err?.message ?? err));
      process.exit(1);
    },
  );
}
