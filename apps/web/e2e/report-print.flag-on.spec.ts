import { expect, test, type Page } from "@playwright/test";
import { spawn } from "node:child_process";
import { existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import profileFixture from "../../../packages/contracts/fixtures/valid/property_profile/builder_output_m1_t005.json";

/**
 * M5-T153 scenario S6 — the printed report, run by the ORCHESTRATOR (ruling X10: builders never
 * start a server). It opens the Results tool on the flag-on :3001 server, presses "Show results",
 * opens the program's report from the Results window, and then checks the report AT ITS PRINT SIZE.
 *
 * The report HTML is produced by the server report route (M5-T151) and the report drawings by
 * M5-T152. Those arrive at integration; this spec therefore asserts the report's SHAPE, not any
 * typed value. Steps that depend on M5-T151's real report output are marked [DEPENDS ON M5-T151].
 *
 * What it checks, in print media:
 *  - the report opens from the Results window in a sandboxed frame that runs no script;
 *  - the six page-type titles appear IN ORDER (page-types.md's reader-question column / the report
 *    headings), matched loosely on the question words;
 *  - no visible text is below 7 pt inside a drawing (SVG), or below 8 pt elsewhere;
 *  - no element is wider than the A4 content box (210 mm - 2 x 14 mm = 182 mm);
 *  - none of the words the owner forbids for a result appears;
 *  - page.pdf({ preferCSSPageSize: true }) yields pages that are all A4 (read from the bytes).
 */

const BBL = "4073340070";
const WINDOW_NAME = "Results";

// A4 portrait: 210 x 297 mm. Content box after 14 mm margins: 182 mm wide. At 96 CSS px / inch,
// 1 mm = 96 / 25.4 px.
const PX_PER_MM = 96 / 25.4;
const A4_CONTENT_WIDTH_PX = Math.round(182 * PX_PER_MM); // ~688 px
// A4 in PostScript points (page.pdf MediaBox): 595.28 x 841.89; Chromium rounds a little.
const A4_WIDTH_PT = 595.28;
const A4_HEIGHT_PT = 841.89;
const PT_TOLERANCE = 4;

// The six page types, matched by their OWN label line (the report's `type-name` line), anchored and
// multiline so a loose word elsewhere never matches first (rework 4: the decision summary's coverage
// block names "H. Option comparisons", which the old loose /option comparison/i matched on page 1).
// The label text is read from the report HTML's `type-name` lines (print-int4/report.html).
const PAGE_TYPE_TITLES: RegExp[] = [
  /^decision summary$/im,
  /^site and context$/im,
  /^option comparison$/im,
  /^scenario sheet\b/im,
  /^assumptions and open items$/im,
  /^calculations and evidence$/im,
];

// The words the owner forbids for a result, anywhere in the report (ruling X5 / X11).
const FORBIDDEN = /\b(achieved|optimal|compliant|feasible|preferred|recommended)\b|no allowance left unused/i;

/** Serve the base profile for the workspace; let the results (POST) and report (POST) reads reach
 * the real harness (the report route arrives with M5-T151). */
async function routeApi(page: Page): Promise<void> {
  await page.route("**/api/v1/properties/**", async (route) => {
    const path = new URL(route.request().url()).pathname;
    if (path.endsWith(`/${BBL}/results`) || path.endsWith(`/${BBL}/report`)) return route.continue();
    const last = path.split("/").at(-1);
    if (last !== BBL) return route.fulfill({ status: 404, json: { detail: "not found" } });
    const profile = structuredClone(profileFixture);
    profile.identity.bbl = BBL;
    await route.fulfill({ json: profile });
  });
}

/** Every `/MediaBox [0 0 w h]` the PDF declares, as [w, h] pairs. */
function mediaBoxes(pdfBytes: Buffer): Array<[number, number]> {
  const text = pdfBytes.toString("latin1");
  const boxes: Array<[number, number]> = [];
  const re = /\/MediaBox\s*\[\s*(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s*\]/g;
  let match: RegExpExecArray | null;
  while ((match = re.exec(text)) !== null) {
    boxes.push([Number(match[3]) - Number(match[1]), Number(match[4]) - Number(match[2])]);
  }
  return boxes;
}

test.describe("M5-T153 — the printed report opens from the Results window and prints as A4", () => {
  test("opens the report, checks print-size legibility and page titles, and prints A4 pages", async ({
    page,
    context,
  }) => {
    await routeApi(page);
    await page.goto(`/property/workspace?ruleeval=on&bbl=${BBL}`);
    await expect(page.getByTestId("connected-dashboard")).toBeVisible({ timeout: 15_000 });

    // Open the Results tool and show results.
    await page.getByRole("button", { name: WINDOW_NAME, exact: true }).click();
    const dialog = page.getByRole("dialog", { name: WINDOW_NAME });
    await expect(dialog).toBeVisible();
    const resultsResponse = page.waitForResponse(
      (r) => r.url().includes(`/${BBL}/results`) && r.request().method() === "POST",
      { timeout: 20_000 },
    );
    await dialog.getByTestId("results-show").click();
    await resultsResponse;
    await expect(dialog.getByTestId("three-answers-panel")).toBeVisible({ timeout: 15_000 });

    // Open the program's report from the Results window. [DEPENDS ON M5-T151: the report route.]
    const reportResponse = page.waitForResponse(
      (r) => r.url().includes(`/${BBL}/report`) && r.request().method() === "POST",
      { timeout: 20_000 },
    );
    await dialog.getByTestId("report-create").click();
    await reportResponse;
    const frame = dialog.getByTestId("report-frame");
    await expect(frame).toBeVisible({ timeout: 15_000 });
    // The frame runs no script: its sandbox grants only what printing from the parent needs.
    const sandbox = await frame.getAttribute("sandbox");
    expect(sandbox).toBe("allow-same-origin allow-modals");
    expect(sandbox).not.toContain("allow-scripts");

    // Read the report HTML the frame holds and render it standalone at the A4 content width in print
    // media, so the print-size checks measure the report as it prints. [DEPENDS ON M5-T151.]
    const reportHtml = await frame.getAttribute("srcdoc");
    expect(reportHtml, "the report frame carries the report HTML").toBeTruthy();

    const printPage = await context.newPage();
    await printPage.setViewportSize({ width: A4_CONTENT_WIDTH_PX, height: 1123 });
    await printPage.emulateMedia({ media: "print" });
    await printPage.setContent(reportHtml as string, { waitUntil: "load" });

    // The six page-type titles appear IN ORDER (loose match on the reader's question words).
    const bodyText = await printPage.innerText("body");
    const positions = PAGE_TYPE_TITLES.map((re) => {
      const match = bodyText.match(re);
      return match ? (match.index ?? -1) : -1;
    });
    for (let i = 0; i < PAGE_TYPE_TITLES.length; i += 1) {
      expect(positions[i], `page-type title ${PAGE_TYPE_TITLES[i]} is present`).toBeGreaterThanOrEqual(0);
    }
    for (let i = 1; i < positions.length; i += 1) {
      expect(positions[i], "page-type titles are in order").toBeGreaterThan(positions[i - 1]);
    }

    // None of the words the owner forbids for a result (ruling X5 / X11).
    expect(bodyText).not.toMatch(FORBIDDEN);

    // C3: the report title is the address the profile carries (the routed profile fixture's recorded
    // address, sent by the website as ?address= — rework 2 C2), not the block-and-lot.
    // [DEPENDS ON M5-T151: the address on the title.]
    const recordedAddress = profileFixture.identity.address?.normalized_address ?? "";
    expect(recordedAddress.length, "the routed profile fixture carries a recorded address").toBeGreaterThan(0);
    const title = (await printPage.locator("h1").first().textContent()) ?? "";
    expect(title, "the report title is the property's address").toContain(recordedAddress);

    // C3: the report holds its drawings — a site plan on the decision summary and the site page, and
    // the floor-stack section on the scenario sheet. A report printed WITHOUT its drawings fails.
    // [DEPENDS ON M5-T152: the report-frame drawings reaching the report.]
    const drawings = await printPage.evaluate(() => {
      const pages = Array.from(document.querySelectorAll(".report-page"));
      const pageWith = (re: RegExp) => pages.find((p) => re.test(p.textContent ?? ""));
      const hasSvg = (p: Element | undefined) => !!(p && p.querySelector("svg"));
      return {
        total: document.querySelectorAll("svg").length,
        decision: hasSvg(pageWith(/decision summary/i)),
        site: hasSvg(pageWith(/site and context/i)),
        scenario: hasSvg(pageWith(/scenario/i)),
      };
    });
    expect(drawings.total, "the report holds its drawings (two site plans and a floor stack)").toBeGreaterThanOrEqual(3);
    expect(drawings.decision, "the decision summary carries a drawing").toBe(true);
    expect(drawings.site, "the site and context page carries a drawing").toBe(true);
    expect(drawings.scenario, "the scenario sheet carries the floor-stack drawing").toBe(true);

    // No visible text below 7 pt inside a drawing (SVG), or below 8 pt elsewhere. SVG text is scaled
    // by its drawing's transform, so the on-screen size is multiplied by the drawing's scale.
    const tooSmall = await printPage.evaluate(() => {
      const PT_PER_PX = 72 / 96;
      const offenders: string[] = [];
      const visible = (el: Element): boolean => {
        const style = getComputedStyle(el);
        if (style.display === "none" || style.visibility === "hidden" || Number(style.opacity) === 0) {
          return false;
        }
        const text = (el.textContent ?? "").trim();
        return text.length > 0;
      };
      // Effective vertical scale from an element's accumulated CTM (SVG) or 1 elsewhere.
      const scaleOf = (el: Element): number => {
        const svgEl = el as SVGGraphicsElement;
        if (typeof svgEl.getCTM === "function") {
          const ctm = svgEl.getCTM();
          if (ctm) return Math.sqrt(Math.abs(ctm.a * ctm.d - ctm.b * ctm.c)) || 1;
        }
        return 1;
      };
      const texts = Array.from(document.querySelectorAll("svg text"));
      for (const el of texts) {
        if (!visible(el)) continue;
        const fontPx = parseFloat(getComputedStyle(el).fontSize);
        const pt = fontPx * PT_PER_PX * scaleOf(el);
        if (pt < 7 - 0.1) offenders.push(`drawing ${pt.toFixed(1)}pt: ${(el.textContent ?? "").trim().slice(0, 24)}`);
      }
      const others = Array.from(
        document.querySelectorAll("p, span, td, th, li, dt, dd, h1, h2, h3, h4, h5, caption, a"),
      );
      for (const el of others) {
        if (el.closest("svg") || !visible(el)) continue;
        const fontPx = parseFloat(getComputedStyle(el).fontSize);
        const pt = fontPx * PT_PER_PX;
        if (pt < 8 - 0.1) offenders.push(`text ${pt.toFixed(1)}pt: ${(el.textContent ?? "").trim().slice(0, 24)}`);
      }
      return offenders;
    });
    expect(tooSmall, "no visible text below its minimum print size").toEqual([]);

    // No element is wider than the A4 content box.
    const tooWide = await printPage.evaluate((contentWidth) => {
      const offenders: string[] = [];
      for (const el of Array.from(document.body.querySelectorAll<HTMLElement>("*"))) {
        const rect = el.getBoundingClientRect();
        if (rect.width > contentWidth + 2) {
          offenders.push(`${el.tagName.toLowerCase()} ${Math.round(rect.width)}px`);
        }
      }
      return offenders;
    }, A4_CONTENT_WIDTH_PX);
    expect(tooWide, "no element wider than the A4 content box").toEqual([]);

    // page.pdf honours the report's own A4 page size; every page is A4. [DEPENDS ON M5-T151.]
    const pdf = await printPage.pdf({ preferCSSPageSize: true });
    const boxes = mediaBoxes(pdf);
    expect(boxes.length, "the PDF has at least one page").toBeGreaterThanOrEqual(1);
    for (const [width, height] of boxes) {
      expect(Math.abs(width - A4_WIDTH_PT)).toBeLessThanOrEqual(PT_TOLERANCE);
      expect(Math.abs(height - A4_HEIGHT_PT)).toBeLessThanOrEqual(PT_TOLERANCE);
    }
    await printPage.close();
  });

  // The print-script check (scenario S5) lives here, NOT in scripts/tests, because it launches
  // Chromium: CI's web-dependency-security job runs `node --test scripts/tests/*.test.mjs` WITHOUT
  // browsers, so a browser-using test there fails. This spec runs under the browser-capable e2e
  // project. It drives scripts/print-report-pdf.mjs as a child process — the real CLI — and keeps
  // every assertion the former node test made: a valid run writes A4 pages; a missing argument fails
  // with a clear message; a non-existent input fails. The orchestrator runs this (ruling X10).
  test("the print script writes A4 pages and fails clearly on a bad argument (S5; CI-safe)", async () => {
    const script = fileURLToPath(new URL("../scripts/print-report-pdf.mjs", import.meta.url));
    const run = (args: string[]): Promise<{ code: number | null; stderr: string }> =>
      new Promise((resolve) => {
        const child = spawn(process.execPath, [script, ...args], { stdio: ["ignore", "ignore", "pipe"] });
        let stderr = "";
        child.stderr.on("data", (d) => {
          stderr += String(d);
        });
        child.on("close", (code) => resolve({ code, stderr }));
      });

    const dir = mkdtempSync(join(tmpdir(), "print-report-"));
    const htmlPath = join(dir, "a4.html");
    const pdfPath = join(dir, "a4.pdf");
    writeFileSync(
      htmlPath,
      `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>tiny</title>` +
        `<style>@page { size: A4; margin: 14mm; } html, body { margin: 0; } h1 { font-size: 24pt; }</style>` +
        `</head><body><h1>A4 print-size probe</h1><p>One short paragraph.</p></body></html>`,
    );
    try {
      // A valid run writes a PDF whose every page is A4 (preferCSSPageSize honoured the @page size).
      const ok = await run([htmlPath, pdfPath]);
      expect(ok.code, ok.stderr).toBe(0);
      expect(existsSync(pdfPath)).toBe(true);
      const bytes = readFileSync(pdfPath);
      expect(bytes.subarray(0, 5).toString("latin1")).toBe("%PDF-");
      const boxes = mediaBoxes(bytes);
      expect(boxes.length).toBeGreaterThanOrEqual(1);
      for (const [width, height] of boxes) {
        expect(Math.abs(width - A4_WIDTH_PT)).toBeLessThanOrEqual(PT_TOLERANCE);
        expect(Math.abs(height - A4_HEIGHT_PT)).toBeLessThanOrEqual(PT_TOLERANCE);
      }
      // A missing output argument, and no arguments at all, fail with a clear message and non-zero exit.
      const missingOut = await run([htmlPath]);
      expect(missingOut.code).not.toBe(0);
      expect(missingOut.stderr).toMatch(/missing <out\.pdf>/);
      const noArgs = await run([]);
      expect(noArgs.code).not.toBe(0);
      expect(noArgs.stderr).toMatch(/missing <url-or-html-file>/);
      // A non-existent input file fails clearly too.
      const noInput = await run([join(dir, "nope.html"), pdfPath]);
      expect(noInput.code).not.toBe(0);
      expect(noInput.stderr).toMatch(/input not found/);
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });
});
