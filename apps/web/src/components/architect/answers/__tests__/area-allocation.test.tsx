import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import {
  AREA_ILLUSTRATION_CAPTION,
  AREA_ZONE_APARTMENT,
  AREA_ZONE_OTHER,
  PHYSICAL_PLATE_NOT_CHECKED,
} from "@/lib/architect/area-allocation-tokens";
import { AREA_ALLOCATION_CONVERSION_STATEMENT } from "@/lib/results-contract-checks";
import { AreaAllocation } from "../AreaAllocation";

/**
 * M5-T187 — the two-zone area illustration component (S1-S5). The block values are small inline
 * literals mirroring the accepted 1.5.0 fixtures; no figure is copied into the component. The wording
 * is checked byte-for-byte against docs/design/presentation-tokens.json read from disk, so mutating
 * the JSON — or the component's literal — reddens the parity test.
 */

afterEach(cleanup);

const CONVERSION =
  "plate = zoning floor area per storey; no gross-up, exclusions or wall-thickness conversion worked";

function barBlock(share: number, overrides: Record<string, unknown> = {}): Record<string, unknown> {
  const total = 18500;
  const apartment = Math.round(share * total * 100) / 100;
  return {
    label: "Illustrative",
    share,
    measure: "residential_floor_area",
    conversion_statement: CONVERSION,
    apartment_area_sqft: apartment,
    other_area_sqft: total - apartment,
    total_sqft: total,
    fitted: false,
    ...overrides,
  };
}

function fittedBlock(share = 0.7): Record<string, unknown> {
  const total = 19000;
  const apartment = Math.round(share * total * 100) / 100;
  return {
    label: "Illustrative",
    share,
    measure: "residential_floor_area",
    conversion_statement: CONVERSION,
    apartment_area_sqft: apartment,
    other_area_sqft: total - apartment,
    total_sqft: total,
    fitted: true,
  };
}

const PLACED_PLACEMENT = {
  status: "placed",
  outline: [
    [
      [0, 0],
      [82, 0],
      [82, 82],
      [0, 82],
      [0, 0],
    ],
  ],
};

/** The presentation tokens, read from disk (repo root, two levels above the vitest cwd apps/web). */
function presentationTokens(): { wording: Record<string, string> } {
  return JSON.parse(
    readFileSync(resolve(process.cwd(), "../../docs/design/presentation-tokens.json"), "utf8"),
  );
}

// ---- S1: the unfitted proportional bar ----

describe("S1 — the unfitted proportional bar", () => {
  it("shows one bar split by the share, one stated percentage, and no footprint/zones", () => {
    const { container } = render(<AreaAllocation allocation={barBlock(0.65)} />);

    // exactly one stated percentage, read from the block's share.
    expect(screen.getByTestId("area-allocation-percentage").textContent).toBe("65% apartment area");

    // the bar's apartment:other ratio equals the share within 0.5 %.
    const bar = screen.getByTestId("area-allocation-bar");
    const fraction = Number(bar.getAttribute("data-apartment-fraction"));
    expect(Math.abs(fraction - 0.65)).toBeLessThanOrEqual(0.005);

    const apartment = container.querySelector<HTMLElement>('[data-role="area_bar_apartment"]');
    const other = container.querySelector<HTMLElement>('[data-role="area_bar_other"]');
    expect(apartment?.style.width).toBe("65%");
    expect(other?.style.width).toBe("35%");

    // a single proportional bar, NOT zones-in-footprint: no footprint, zone or division is drawn.
    expect(container.querySelectorAll('[data-role="area_footprint"]')).toHaveLength(0);
    expect(container.querySelectorAll('[data-role="area_zone_apartment"]')).toHaveLength(0);
    expect(container.querySelectorAll('[data-role="area_zone_other"]')).toHaveLength(0);
    expect(container.querySelectorAll('[data-role="area_division"]')).toHaveLength(0);
  });
});

// ---- S2: the wording is byte-equal to the presentation tokens (both directions) ----

describe("S2 — the zone labels and caption are byte-equal to presentation-tokens.json", () => {
  it("the component literals equal the JSON wording tokens (mutating the JSON reddens this)", () => {
    const { wording } = presentationTokens();
    expect(AREA_ZONE_APARTMENT).toBe(wording.area_zone_apartment);
    expect(AREA_ZONE_OTHER).toBe(wording.area_zone_other);
    expect(AREA_ILLUSTRATION_CAPTION).toBe(wording.area_illustration_caption);
  });

  it("the rendered labels and caption are exactly those tokens (no trailing full stop)", () => {
    const { wording } = presentationTokens();
    render(<AreaAllocation allocation={barBlock(0.65)} />);
    expect(screen.getByTestId("area-allocation-label-apartment").textContent).toBe(
      wording.area_zone_apartment,
    );
    expect(screen.getByTestId("area-allocation-label-other").textContent).toBe(
      wording.area_zone_other,
    );
    expect(screen.getByTestId("area-allocation-caption").textContent).toBe(
      wording.area_illustration_caption,
    );
    expect(screen.getByTestId("area-allocation-caption").textContent).not.toMatch(/\.$/);
  });
});

// ---- S3: the fitted branch is a marked placeholder in this part ----

describe("S3 — fitted renders a placeholder, not a bar (deferred to Part B)", () => {
  it("fitted:true with a placed placement draws no bar and no second illustration", () => {
    const { container } = render(
      <AreaAllocation allocation={fittedBlock()} placement={PLACED_PLACEMENT} />,
    );
    expect(screen.getByTestId("area-allocation-fitted-deferred")).toBeInTheDocument();
    expect(screen.queryByTestId("area-allocation-bar")).toBeNull();
    expect(screen.queryByTestId("area-allocation-percentage")).toBeNull();
    expect(container.querySelectorAll('[data-role="area_zone_apartment"]')).toHaveLength(0);
  });

  it("table: fitted:false -> bar; fitted:true -> placeholder", () => {
    const { rerender } = render(<AreaAllocation allocation={barBlock(0.65)} />);
    expect(screen.getByTestId("area-allocation-bar")).toBeInTheDocument();
    rerender(<AreaAllocation allocation={fittedBlock()} placement={PLACED_PLACEMENT} />);
    expect(screen.queryByTestId("area-allocation-bar")).toBeNull();
    expect(screen.getByTestId("area-allocation-fitted-deferred")).toBeInTheDocument();
  });
});

// ---- S4: no forbidden marks on any row; never more than one caption ----

describe("S4 — no rooms/unit-walls/apartment-counts/stairs/elevators; one caption at most (R093/R095)", () => {
  const FORBIDDEN = [/\broom\b/i, /unit wall/i, /\bstair/i, /\belevator/i, /\bapartments\b/i, /\bunits\b/i];
  for (const share of [0.6, 0.65, 0.75]) {
    for (const fitted of [false, true]) {
      it(`row {fitted:${fitted}, share:${share}} has no forbidden mark`, () => {
        const allocation = fitted ? fittedBlock(share) : barBlock(share);
        render(
          <AreaAllocation allocation={allocation} placement={fitted ? PLACED_PLACEMENT : undefined} />,
        );
        const text = screen.getByTestId("area-allocation").textContent ?? "";
        for (const pattern of FORBIDDEN) expect(text).not.toMatch(pattern);
        const captions = screen.queryAllByTestId("area-allocation-caption");
        expect(captions.length).toBe(fitted ? 0 : 1);
      });
    }
  }
});

// ---- S5: the conversion statement lives in expandable detail, not the caption ----

describe("S5 — the G-14 conversion statement is in the expandable detail, not the caption", () => {
  it("the methodology carries the exact statement and lists the physical floor plate as not checked", () => {
    render(<AreaAllocation allocation={barBlock(0.65)} />);
    const conversion = screen.getByTestId("area-allocation-conversion").textContent ?? "";
    expect(conversion).toBe(CONVERSION);
    expect(conversion).toBe(AREA_ALLOCATION_CONVERSION_STATEMENT);
    expect(screen.getByTestId("area-allocation-not-checked").textContent).toBe(
      PHYSICAL_PLATE_NOT_CHECKED,
    );
    // the statement is NOT in the one short caption (R095).
    expect(screen.getByTestId("area-allocation-caption").textContent).not.toContain(CONVERSION);
  });
});

// ---- A garbled block fails closed to a plain reason (no default stands for a fact) ----

describe("a garbled or inconsistent block renders an explicit unavailable line, never a guessed bar", () => {
  it("a block with the wrong fixed label shows the plain reason and no bar", () => {
    render(<AreaAllocation allocation={barBlock(0.65, { label: "Verified" })} />);
    expect(screen.getByTestId("area-allocation-unavailable").textContent).toBe(
      "The area allocation is incomplete.",
    );
    expect(screen.queryByTestId("area-allocation-bar")).toBeNull();
  });

  it("a missing block shows the plain reason and no bar", () => {
    render(<AreaAllocation allocation={undefined} />);
    expect(screen.getByTestId("area-allocation-unavailable").textContent).toBe(
      "There is no area allocation to draw.",
    );
    expect(screen.queryByTestId("area-allocation-bar")).toBeNull();
  });
});
