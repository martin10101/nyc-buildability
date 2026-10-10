// Node built-in test for the report print script (task M5-T153, scenario S5). It prints a tiny
// HTML page whose @page rule sets A4, then reads the written PDF's bytes and checks the page size
// is A4 (so preferCSSPageSize honoured the report's own page size). It also checks that a missing
// argument fails with a clear message. The test launches the installed headless Chromium itself —
// no server, no port.
//
//   node --test scripts/tests/print-report-pdf.test.mjs

import test from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, writeFileSync, readFileSync, rmSync, existsSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { printToPdf, resolveInput } from "../print-report-pdf.mjs";

// A4 portrait in PostScript points: 210 mm x 297 mm = 595.28 x 841.89 pt. Chromium rounds to
// ~595.32 x 841.92; allow a few points of tolerance.
const A4_WIDTH_PT = 595.28;
const A4_HEIGHT_PT = 841.89;
const TOLERANCE_PT = 4;

const A4_PAGE = `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>tiny</title>
<style>@page { size: A4; margin: 14mm; } html, body { margin: 0; }
h1 { font-size: 24pt; }</style></head>
<body><h1>A4 print-size probe</h1><p>One short paragraph.</p></body></html>`;

/** Every `/MediaBox [0 0 w h]` the PDF declares, as [w, h] pairs (the page sizes). */
function mediaBoxes(pdfBytes) {
  const text = Buffer.from(pdfBytes).toString("latin1");
  const boxes = [];
  const re = /\/MediaBox\s*\[\s*(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s*\]/g;
  let match;
  while ((match = re.exec(text)) !== null) {
    boxes.push([Number(match[3]) - Number(match[1]), Number(match[4]) - Number(match[2])]);
  }
  return boxes;
}

test("prints an @page A4 document to a PDF whose page size is A4", async () => {
  const dir = mkdtempSync(join(tmpdir(), "print-report-"));
  const htmlPath = join(dir, "a4.html");
  const pdfPath = join(dir, "a4.pdf");
  writeFileSync(htmlPath, A4_PAGE);
  try {
    const written = await printToPdf(htmlPath, pdfPath);
    assert.equal(written, pdfPath);
    assert.ok(existsSync(pdfPath), "the PDF was written");
    const bytes = readFileSync(pdfPath);
    assert.equal(bytes.subarray(0, 5).toString("latin1"), "%PDF-", "the output is a PDF");

    const boxes = mediaBoxes(bytes);
    assert.ok(boxes.length >= 1, "the PDF declares at least one page MediaBox");
    for (const [width, height] of boxes) {
      assert.ok(
        Math.abs(width - A4_WIDTH_PT) <= TOLERANCE_PT,
        `page width ${width}pt is not A4 (${A4_WIDTH_PT}pt +/- ${TOLERANCE_PT})`,
      );
      assert.ok(
        Math.abs(height - A4_HEIGHT_PT) <= TOLERANCE_PT,
        `page height ${height}pt is not A4 (${A4_HEIGHT_PT}pt +/- ${TOLERANCE_PT})`,
      );
    }
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test("a missing input argument fails with a clear message", async () => {
  await assert.rejects(() => printToPdf(undefined, "/tmp/out.pdf"), /missing <url-or-html-file>/);
  assert.throws(() => resolveInput(""), /missing <url-or-html-file>/);
});

test("a missing output argument fails with a clear message", async () => {
  const dir = mkdtempSync(join(tmpdir(), "print-report-"));
  const htmlPath = join(dir, "a4.html");
  writeFileSync(htmlPath, A4_PAGE);
  try {
    await assert.rejects(() => printToPdf(htmlPath, undefined), /missing <out\.pdf>/);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test("an input file that does not exist fails with a clear message", () => {
  assert.throws(() => resolveInput("/no/such/report.html"), /input not found/);
});
