import { expect, test, type Page } from "@playwright/test";
import { expectProfile, lookup, tabUntil } from "./helpers";

/**
 * S6 (M2-T002, resolving M2-T001 G3 defects D2/D3/D4):
 * - 360/768/1280 viewports render the Property profile and Confirm card
 *   with NO horizontal page overflow (wide tables scroll inside their own
 *   card instead).
 * - The grouped-missing toggle and the failure-state retry button are
 *   operated KEYBOARD-ONLY.
 * - The coverage legend is visible without hover; the shared missing-reason
 *   is stated once with per-field exceptions still shown.
 */

const VIEWPORTS = [
  { width: 360, height: 740, name: "phone-360" },
  { width: 768, height: 1024, name: "tablet-768" },
  { width: 1280, height: 800, name: "desktop-1280" },
] as const;

async function expectNoHorizontalOverflow(page: Page): Promise<void> {
  const overflow = await page.evaluate(() => {
    const doc = document.documentElement;
    return {
      scrollWidth: doc.scrollWidth,
      clientWidth: doc.clientWidth,
    };
  });
  // Allow 1px of sub-pixel rounding.
  expect(
    overflow.scrollWidth,
    `page scrollWidth ${overflow.scrollWidth} must not exceed viewport ${overflow.clientWidth}`,
  ).toBeLessThanOrEqual(overflow.clientWidth + 1);
}

for (const viewport of VIEWPORTS) {
  test(`S6/D2: Property profile renders without horizontal overflow at ${viewport.name}`, async ({
    page,
  }) => {
    await page.setViewportSize({ width: viewport.width, height: viewport.height });
    await lookup(page, "1000010010");
    await expectProfile(page);
    await expectNoHorizontalOverflow(page);
    // The legend (D3) is visible at every supported width.
    await expect(page.getByTestId("coverage-legend")).toBeVisible();
  });

  test(`S6/D2: Confirm card renders without horizontal overflow at ${viewport.name}`, async ({
    page,
  }) => {
    await page.setViewportSize({ width: viewport.width, height: viewport.height });
    await page.goto("/property/confirm?bbl=1000010010");
    await expect(page.getByTestId("confirm-card")).toBeVisible({ timeout: 15_000 });
    await expectNoHorizontalOverflow(page);
    await expect(page.getByTestId("coverage-legend")).toBeVisible();
  });
}

test("S6/D2: the grouped-missing toggle is operated by KEYBOARD only", async ({
  page,
}) => {
  await lookup(page, "1000010101"); // F04 partial-data capture
  await expectProfile(page);

  const toggle = page.getByRole("button", { name: /more missing fields/ });
  await expect(toggle).toHaveAttribute("aria-expanded", "false");

  // Reach the toggle with Tab only and activate it with Enter.
  await tabUntil(page, { textContains: "more missing fields" });
  await page.keyboard.press("Enter");
  await expect(
    page.getByRole("button", { name: /Hide \d+ additional missing fields/ }),
  ).toHaveAttribute("aria-expanded", "true");

  // Collapse again with the keyboard (Space also activates a button).
  await page.keyboard.press("Space");
  await expect(
    page.getByRole("button", { name: /more missing fields/ }),
  ).toHaveAttribute("aria-expanded", "false");
});

test("S6/D2: the failure-state retry button is operated by KEYBOARD only and re-issues the request", async ({
  page,
}) => {
  let apiCalls = 0;
  await page.route("**/api/v1/properties/**", async (route) => {
    apiCalls += 1;
    await route.continue();
  });
  await lookup(page, "3000010001"); // rate_limited (real error mapping)
  await expect(page.getByTestId("state-rate_limited")).toBeVisible();
  expect(apiCalls).toBe(1);

  await tabUntil(page, { textContains: "Retry lookup" });
  await page.keyboard.press("Enter");
  // The retry re-issued a real request (the harness replays rate_limited
  // for this control BBL, so the same typed state returns).
  await expect(page.getByTestId("state-rate_limited")).toBeVisible();
  await expect
    .poll(() => apiCalls, { message: "retry must issue a second API call" })
    .toBe(2);
});

test("S6/D4: the shared missing-reason is stated once; per-field exceptions stay inline", async ({
  page,
}) => {
  await lookup(page, "1000010101"); // F04: numfloors officially "not available"
  await expectProfile(page);

  // The shared boilerplate reason appears exactly once (the section note).
  const sharedNote = page.getByTestId("shared-missing-reason");
  await expect(sharedNote).toBeVisible();
  await expect(sharedNote).toContainText("null-omission semantics");
  await expect(page.getByText(/null-omission semantics/)).toHaveCount(1);

  // The per-field exception (numfloors official-unknown note) is shown
  // inline, distinct from the shared reason.
  const missingSection = page.locator("section", {
    has: page.getByRole("heading", { name: /Missing official inputs/ }),
  });
  await expect(missingSection).toContainText("Number of floors");
  await expect(missingSection).toContainText("numfloors_not_available");
});

test("S6/D3: coverage legend explains every status present WITHOUT hover", async ({
  page,
}) => {
  await lookup(page, "1000010103"); // synthetic borocode conflict variant
  await expectProfile(page);

  const legend = page.getByTestId("coverage-legend");
  await expect(legend).toBeVisible();
  // The conflicting profile carries both conditional and data_conflict
  // badges; each gloss is readable with no interaction at all.
  await expect(legend).toContainText("conditional");
  await expect(legend).toContainText(
    "Official source fact, not yet professionally reviewed.",
  );
  await expect(legend).toContainText("data_conflict");
  await expect(legend).toContainText(
    "Official sources disagree; both values are shown, nothing was resolved.",
  );
});

/* ================================================================ *
 * DB-035 rider a + b (M5-T055): the definitive PIXEL-level CLS proof for the
 * address confirm card's record-note LATE async insert.
 *
 * The record note is rendered OUTSIDE the interactive block — after the Continue
 * CTA and the "Not my property" action, and (rider b) BEFORE the non-interactive
 * <Meta> reference-id footer. This spec proves in a real browser that the primary
 * CTA's document Y-position is byte-stable across the async insert at 360/768/1280,
 * including a LONG record address that wraps across multiple lines; it fails if the
 * CTA's document-top changes by any amount (exact equality, not a sub-pixel tolerance).
 *
 * The record-address channel is intercepted in the browser (page.route) so the
 * spec controls exactly WHEN — and with what long, differing address — the note
 * inserts; the address resolution and lot-outline calls still hit the real fixture
 * harness (e2e/harness/fixture_api.py). The route is held pending so the card first
 * renders in its loading (no-note) shape, the CTA is measured, then the SAME mounted
 * card receives the resolved long record and the CTA is measured again.
 * ================================================================ */

// A long PLUTO address-of-record that DIFFERS from the matched "100 OUTLINE AVENUE"
// frontage and wraps across multiple lines at the narrow 360px width. It is well
// under the client's 600-char reflected-text bound (src/lib/bounded.ts), so it
// renders in full with no truncation marker — the worst realistic wrapping case.
const LONG_RECORD_ADDRESS =
  "1200 EXAMPLE INTERNATIONAL COMMERCE PARKWAY AND MEMORIAL BOULEVARD EXTENSION, SUITE 4400, BROOKLYN NAVY YARD ANNEX BUILDING 292";

function recordAddressBody(): string {
  return JSON.stringify({
    document_kind: "record_address",
    bbl: "1008350041",
    outcome: "address_of_record",
    address: LONG_RECORD_ADDRESS,
    reason: null,
    source: {
      source_id: "nyc-dcp-pluto-soda",
      dataset_id: "64uk-42ks",
      dataset_version: "26v2",
      retrieved_at: "2026-09-19T04:00:03Z",
    },
  });
}

/** Resolve the OUTLINE AVENUE test address to its confirm card (matched frontage
 * "100 OUTLINE AVENUE"), exactly as the lot-outline walkthrough does. */
async function resolveToConfirmCard(page: Page): Promise<void> {
  await page.goto("/property?ruleeval=on");
  await page.getByText("Enter address manually", { exact: true }).click();
  const form = page.getByTestId("address-form");
  await form.getByLabel("House number", { exact: true }).fill("100");
  await form.getByLabel("Street", { exact: true }).fill("OUTLINE AVENUE");
  await form.getByLabel("Borough", { exact: true }).selectOption("Manhattan");
  await form.getByTestId("address-submit").click();
  await expect(page.getByTestId("address-confirm-card")).toBeVisible({
    timeout: 15_000,
  });
}

/** The Continue CTA's document-absolute top (viewport top + scroll offset), in CSS
 * px. An insert strictly BELOW the CTA cannot change this value, so it is a scroll-
 * independent measure of whether the CTA moved. */
async function ctaDocumentTop(page: Page): Promise<number> {
  return page.getByTestId("confirm-continue").evaluate((el) => {
    const rect = el.getBoundingClientRect();
    return rect.top + window.scrollY;
  });
}

for (const viewport of VIEWPORTS) {
  test(`DB-035 rider a (CLS pixel proof): the Continue CTA Y-position is byte-stable across the long record-note insert at ${viewport.name}`, async ({
    page,
  }) => {
    await page.setViewportSize({ width: viewport.width, height: viewport.height });

    // Hold the record-address response pending so the card first renders in its
    // no-note (loading) shape; release it only after the "before" measurement. The
    // fulfilled response carries permissive CORS (the client fetches the API origin
    // with credentials omitted — src/lib/record-address.ts).
    let releaseRecord: () => void = () => undefined;
    const recordGate = new Promise<void>((resolve) => {
      releaseRecord = resolve;
    });
    await page.route("**/record-address**", async (route) => {
      await recordGate;
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        headers: { "access-control-allow-origin": "*" },
        body: recordAddressBody(),
      });
    });

    await resolveToConfirmCard(page);
    const card = page.getByTestId("address-confirm-card");

    // The lot-outline surface (ABOVE the CTA) settles to a terminal state first, so
    // the ONLY layout change between the two CTA measurements is the record note
    // inserting BELOW the CTA — nothing above it moves for any other reason.
    await expect(
      page
        .getByTestId("lot-outline-map")
        .or(page.getByTestId("lot-outline-webgl-unavailable"))
        .or(page.getByTestId("lot-outline-empty"))
        .or(page.getByTestId("lot-outline-review"))
        .or(page.getByTestId("lot-outline-unavailable"))
        .first(),
    ).toBeVisible({ timeout: 15_000 });

    // [ORCH-CORRECTED per G4-1 + CI run 35493851185] The lot-outline surface being
    // VISIBLE is not the same as being HEIGHT-STABLE: the basemap/labels status line
    // (LotOutlineMap `architect-map-status`, ABOVE the CTA) appears once the map
    // context exists and its text changes from "Preparing…/loading" to terminal
    // "loaded/unavailable" as tiles finish. In CI that settle landed BETWEEN the two
    // measurements and moved the CTA 27px at 360/768 (desktop had settled in time) —
    // the exact environmental class the G4 review flagged. Wait for the map region's
    // terminal state before the "before" measurement: either a terminal fallback
    // surface, or the live map with every context layer terminal.
    await expect
      .poll(
        async () => {
          for (const fallbackId of [
            "lot-outline-webgl-unavailable",
            "lot-outline-empty",
            "lot-outline-review",
            "lot-outline-unavailable",
          ]) {
            if ((await page.getByTestId(fallbackId).count()) > 0) return "terminal";
          }
          const mapStatus = page.locator(".architect-map-status");
          if ((await mapStatus.count()) === 0) return "no-status-line-yet";
          const text = await mapStatus.innerText();
          return text.includes("Preparing") || text.includes("loading")
            ? "layers-pending"
            : "terminal";
        },
        { timeout: 15_000 },
      )
      .toBe("terminal");

    // The record channel is still loading: no note yet (the honest as-today shape).
    await expect(card).toHaveAttribute("data-record-address-status", "loading");
    await expect(page.getByTestId("record-address")).toHaveCount(0);

    // Belt-and-braces layout quiescence: two CTA reads 500ms apart must agree before
    // the value counts as the "before" measurement (guards any remaining async
    // above-CTA settle — fonts, late tiles — without weakening the exact-equality
    // assertion that follows).
    let ctaTopBefore = await ctaDocumentTop(page);
    await expect
      .poll(
        async () => {
          const previous = ctaTopBefore;
          await page.waitForTimeout(500);
          ctaTopBefore = await ctaDocumentTop(page);
          return ctaTopBefore === previous;
        },
        { timeout: 10_000 },
      )
      .toBe(true);

    // Release the long, DIFFERING record address → the note inserts below the CTA.
    releaseRecord();
    await expect(card).toHaveAttribute("data-record-address-status", "shown", {
      timeout: 15_000,
    });
    const note = page.getByTestId("record-address");
    await expect(note).toBeVisible();
    await expect(note).toContainText(LONG_RECORD_ADDRESS);

    const ctaTopAfter = await ctaDocumentTop(page);

    // THE pixel proof: the CTA's document-top is byte-identical across the async
    // insert of the long record note — it did not move at all. Exact equality, not
    // a sub-pixel tolerance: the note inserts strictly BELOW the CTA in DOM order,
    // so an unchanged document-absolute top is the honest expectation and the spec
    // fails if the value changes by any amount.
    expect(
      ctaTopAfter,
      `CTA moved from ${ctaTopBefore} to ${ctaTopAfter} at ${viewport.name}`,
    ).toBe(ctaTopBefore);

    // Rider b placement, proven in the browser: the inserted note sits BELOW the
    // Continue CTA (out of the interactive flow) and ABOVE the non-interactive Meta
    // reference-id footer — content-before-footer reading order.
    const ctaBox = await page.getByTestId("confirm-continue").boundingBox();
    const noteBox = await note.boundingBox();
    const metaBox = await page.getByTestId("correlation-id").boundingBox();
    expect(ctaBox && noteBox && metaBox).toBeTruthy();
    if (ctaBox && noteBox && metaBox) {
      // note starts at or below the CTA's bottom edge; the footer at or below the note.
      expect(noteBox.y).toBeGreaterThanOrEqual(ctaBox.y + ctaBox.height - 1);
      expect(metaBox.y).toBeGreaterThanOrEqual(noteBox.y + noteBox.height - 1);
    }
  });
}

/* ================================================================ *
 * D-086 P2 (M5-T115) / DB-083(f): the environment badge + professional-review
 * line stay visible on the SEARCH surface at every width, including the 360px
 * phone width where the shell's own `.architect-environment` disclosure and nav
 * footnote are hidden (architect.css ≤700px). The search-scoped badge/line are
 * carried by PropertySearch so no breakpoint removes the internal-build /
 * no-access-control / do-not-share / "not a legal determination" meaning
 * (LS-P01/A01) or the "professional review required" meaning (A03).
 * ================================================================ */
for (const viewport of VIEWPORTS) {
  test(`D-086 P2 (DB-083 f): the search-surface environment badge + review line are visible at ${viewport.name}`, async ({
    page,
  }) => {
    await page.setViewportSize({ width: viewport.width, height: viewport.height });
    await page.goto("/property?ruleeval=on");

    const env = page.getByTestId("search-environment");
    await expect(env).toBeVisible();
    await expect(env).toContainText("Internal build");
    await expect(env).toContainText("nothing here is a legal determination");
    await expect(page.getByTestId("search-review")).toBeVisible();
    await expect(page.getByTestId("search-review")).toContainText(
      "professional review required",
    );
  });
}

/* ================================================================ *
 * D-086 P3a (M5-T119): the LOADED overview canvas (AS-2) renders with no
 * horizontal overflow at every width, and the shell environment + professional-
 * review disclosure (AS-4 / DB-087 g / DISC-P2-1) is visible at 360px on the
 * loaded workspace — closing the ≤700px gap the M5-T115 slice left open for the
 * loaded surfaces (it fixed only the SEARCH surface).
 * ================================================================ */
async function openOverview(page: Page, bbl = "1000010010"): Promise<void> {
  await page.goto(`/property?ruleeval=on&bbl=${bbl}&view=overview`);
  await expect(page.getByTestId("profile-view")).toBeVisible({ timeout: 15_000 });
  await expect(page.getByRole("region", { name: "Development limits" })).toBeVisible({ timeout: 15_000 });
  await expect(page.getByText("Loading draft scenario…", { exact: true })).toHaveCount(0, { timeout: 15_000 });
}

for (const viewport of VIEWPORTS) {
  test(`D-086 P3a (AS-2): the loaded overview canvas renders with no horizontal overflow at ${viewport.name}`, async ({
    page,
  }) => {
    await page.setViewportSize({ width: viewport.width, height: viewport.height });
    await openOverview(page);
    await expectNoHorizontalOverflow(page);
  });
}

test("D-086 P3a (AS-4 / DB-087 g): the shell environment + review disclosure is visible at 360px on a loaded overview", async ({
  page,
}) => {
  await page.setViewportSize({ width: 360, height: 740 });
  await openOverview(page);
  const env = page.getByTestId("shell-environment");
  await expect(env).toBeVisible();
  await expect(env).toContainText("Internal build");
  // The restriction meaning is visible as text (role=note), not colour alone.
  await expect(env).toContainText("No sign-in or access control yet");
  await expect(env).toContainText("nothing here is a legal determination");
  await expect(env).toContainText("do not share outside the engineering team");
  const review = page.getByTestId("shell-review");
  await expect(review).toBeVisible();
  await expect(review).toContainText("professional review required");
  await expectNoHorizontalOverflow(page);
});

test("D-086 P3a: the shell environment strip is phone-only — hidden at desktop where the topbar carries the meaning", async ({
  page,
}) => {
  await page.setViewportSize({ width: 1280, height: 800 });
  await openOverview(page);
  // In the DOM but display:none ≥701px (the desktop topbar disclosure + nav footnote carry it).
  await expect(page.getByTestId("shell-environment")).toBeHidden();
});
