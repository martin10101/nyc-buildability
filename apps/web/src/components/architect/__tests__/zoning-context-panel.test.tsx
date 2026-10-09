import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen, within } from "@testing-library/react";
import { baseProfile } from "@/test-support/fixtures";
import { ZoningContextPanel } from "../ZoningContextPanel";
import { PropertyOverview } from "../PropertyOverview";
import { ZoningView } from "../ProfileViews";
import { ReportView } from "../ReportView";
import {
  ABSENT_BBL_MAP_LINK_NOTE,
  ZOLA_LOT_LINK_LABEL,
} from "../AddressAutocomplete";

/**
 * M5-T036 acceptance pack — DB-016 zoning-context panel + DB-005 ZoLa
 * unification on the touched surfaces.
 *
 * The panel is LABEL DISPLAY ONLY (owner ruling 2026-09-17): it renders the
 * designations the client-side profile already carries, each with the same
 * per-value provenance and honest absent/Unknown states as the reference
 * components, and ONE validated ZoLa lot link (zolaLotUrl; NO link when the
 * BBL is not canonical). It computes nothing — the development-limits engine
 * stays the differentiator, so the panel carries none of its result testids.
 *
 * The base fixture is the accepted M1-T005 builder output for BBL 1000010010
 * (Governors Island split-zone lot): districts ["R3-2", "C4-1"], no
 * commercial overlay, special district ["GI"], landmark "INDIVIDUAL
 * LANDMARK", historic district "Governors Island Historic District".
 */

// PropertyOverview mounts LotOutlineMap (a fetch/MapLibre seam). Stub it so the
// overview mount test asserts structure without a network/WebGL dependency —
// the same seam the development-limits suite uses.
vi.mock("@/components/address/LotOutlineMap", () => ({
  LotOutlineMap: () => <div>Map presentation seam</div>,
}));

afterEach(cleanup);

const ZOLA_PREFIX = "https://zola.planning.nyc.gov/bbl/";

function renderPanel(profile = baseProfile()) {
  render(<ZoningContextPanel profile={profile} />);
  return screen.getByTestId("zoning-context-panel");
}

describe("AS-1 — every present designation class, with provenance, nothing computed", () => {
  it("renders all districts (split-lot multiples), special districts, and landmark/historic values", () => {
    const panel = renderPanel();
    // Split zoning lot: BOTH districts render, not just the first. Each value
    // ALSO appears inside its own provenance disclosure (the original-value and
    // normalized-value <dd> rows), so the shared list markup carries the value
    // text on more than one element. Assert real presence with getAllByText
    // (which throws when there are zero matches) rather than a single-match
    // getByText that the intended duplication makes ambiguous.
    expect(within(panel).getAllByText("R3-2").length).toBeGreaterThanOrEqual(1);
    expect(within(panel).getAllByText("C4-1").length).toBeGreaterThanOrEqual(1);
    expect(within(panel).getAllByText("GI").length).toBeGreaterThanOrEqual(1);
    // Landmark/historic values are shown verbatim from the profile.
    expect(
      within(panel).getAllByText("INDIVIDUAL LANDMARK").length,
    ).toBeGreaterThanOrEqual(1);
    expect(
      within(panel).getAllByText("Governors Island Historic District").length,
    ).toBeGreaterThanOrEqual(1);
  });

  it("carries per-value provenance disclosures for districts and flags", () => {
    const panel = renderPanel();
    expect(within(panel).getByText("Source for R3-2")).toBeInTheDocument();
    expect(within(panel).getByText("Source for C4-1")).toBeInTheDocument();
    expect(within(panel).getByText("Source for Landmark")).toBeInTheDocument();
    expect(
      within(panel).getByText("Source for Historic district"),
    ).toBeInTheDocument();
  });

  it("renders a populated commercial overlay with its per-value provenance", () => {
    const profile = baseProfile();
    profile.zoning.commercial_overlays = ["C1-4"];
    // Mirror the committed PLUTO overlay column so the SAME D5 fallback join the
    // production path uses (original_field_name in overlay1/overlay2, value
    // match) resolves this overlay's provenance — nothing is invented.
    const zonedist1 = profile.provenance.find(
      (record) => record.original_field_name === "zonedist1",
    )!;
    profile.provenance.push({
      ...structuredClone(zonedist1),
      provenance_id: "pluto-64uk-42ks-26v1-1000010010-overlay1",
      original_field_name: "overlay1",
      original_value: "C1-4",
      normalized_value: "C1-4",
    });
    const panel = renderPanel(profile);
    // The overlay value also renders inside its provenance disclosure rows, so
    // it matches more than one element — assert presence with getAllByText.
    expect(within(panel).getAllByText("C1-4").length).toBeGreaterThanOrEqual(1);
    // The disclosure summary label stays a unique single match.
    expect(within(panel).getByText("Source for C1-4")).toBeInTheDocument();
    // The honest empty-overlay note is gone now that an overlay is present.
    expect(
      within(panel).queryByText(
        "No commercial overlay is present in the official record for this lot.",
      ),
    ).toBeNull();
  });

  it("computes nothing: none of the development-limits result testids appear", () => {
    const panel = renderPanel();
    expect(within(panel).queryByTestId("development-evaluated-far")).toBeNull();
    expect(within(panel).queryByTestId("development-reference-far")).toBeNull();
    expect(within(panel).queryByTestId("architect-cap")).toBeNull();
  });
});

describe("AS-2 — honest absence, mirroring the reference components", () => {
  it("shows the explicit empty text for an empty array (commercial overlays here)", () => {
    const panel = renderPanel();
    expect(
      within(panel).getByText(
        "No commercial overlay is present in the official record for this lot.",
      ),
    ).toBeInTheDocument();
  });

  it("shows explicit empty text for every empty designation array", () => {
    const profile = baseProfile();
    profile.zoning.districts = [];
    profile.zoning.commercial_overlays = [];
    profile.zoning.special_districts = [];
    const panel = renderPanel(profile);
    expect(
      within(panel).getByText(
        "No zoning district is present in the official record for this lot.",
      ),
    ).toBeInTheDocument();
    expect(
      within(panel).getByText(
        "No commercial overlay is present in the official record for this lot.",
      ),
    ).toBeInTheDocument();
    expect(
      within(panel).getByText(
        "No special district is present in the official record for this lot.",
      ),
    ).toBeInTheDocument();
  });

  it("renders 'Unknown — not supplied' rows when mapped_features are absent, hiding nothing", () => {
    const profile = baseProfile();
    profile.zoning.mapped_features = [];
    const panel = renderPanel(profile);
    // Landmark AND historic district each fall back to the honest Unknown row.
    expect(within(panel).getAllByText("Unknown — not supplied")).toHaveLength(2);
    // No provenance disclosure is offered for a value we do not have.
    expect(within(panel).queryByText("Source for Landmark")).toBeNull();
    expect(within(panel).queryByText("Source for Historic district")).toBeNull();
    // The labels themselves remain visible — absence is shown, never hidden.
    expect(within(panel).getByText("Landmark")).toBeInTheDocument();
    expect(within(panel).getByText("Historic district")).toBeInTheDocument();
  });
});

describe("AS-3 — validated ZoLa link (DB-005), honest absence on invalid BBL", () => {
  it("builds exactly the validated /bbl/<canonical> link, opening in a new tab with noopener", () => {
    const panel = renderPanel();
    const link = within(panel).getByTestId("zoning-context-zola-link");
    expect(link.getAttribute("href")).toBe(`${ZOLA_PREFIX}1000010010`);
    expect(link.getAttribute("target")).toBe("_blank");
    expect(link.getAttribute("rel")).toBe("noopener noreferrer");
    expect(within(panel).queryByTestId("zoning-context-zola-absent")).toBeNull();
  });

  it("renders NO ZoLa link for a non-canonical BBL — honest absence, never a raw template URL", () => {
    const profile = baseProfile();
    profile.identity.bbl = "12345"; // wrong length — zolaLotUrl returns null
    const panel = renderPanel(profile);
    expect(within(panel).queryByTestId("zoning-context-zola-link")).toBeNull();
    expect(
      within(panel).getByTestId("zoning-context-zola-absent"),
    ).toBeInTheDocument();
    // No heading anchor points at a guessed ZoLa URL for this lot.
    const headingLink = panel
      .querySelector<HTMLElement>(".architect-panel-heading")!
      .querySelector("a");
    expect(headingLink).toBeNull();
  });
});

describe("AS-4 — mount on the overview surface; excluded from the printed brief", () => {
  it("mounts on the architect overview (PropertyOverview)", () => {
    render(
      <PropertyOverview
        profile={baseProfile()}
        scenario={null}
        evaluation={null}
        onInspect={vi.fn()}
      />,
    );
    expect(screen.getByTestId("zoning-context-panel")).toBeInTheDocument();
  });

  it("does NOT render in the printed brief (ReportView already shows Zoning + Additional flags)", () => {
    render(
      <ReportView
        profile={baseProfile()}
        scenario={null}
        evaluation={null}
        label="Test property"
      />,
    );
    // Decision (stated in the producer report): the panel is an overview
    // affordance; the brief keeps its own ZoningSection + AdditionalZoningFlags,
    // so the panel is deliberately excluded from print.
    expect(screen.queryByTestId("zoning-context-panel")).toBeNull();
  });
});

function renderOverview(profile = baseProfile()) {
  return render(
    <PropertyOverview
      profile={profile}
      scenario={null}
      evaluation={null}
      onInspect={vi.fn()}
    />,
  );
}

describe("AS-5 (DB-019a) — both ZoLa link glyphs are decorative (aria-hidden), names unchanged", () => {
  it("hides the ↗ glyph on the panel's ZoLa link while keeping its accessible name", () => {
    const panel = renderPanel();
    const link = within(panel).getByTestId("zoning-context-zola-link");
    const glyph = link.querySelector<HTMLElement>("span[aria-hidden='true']");
    expect(glyph).not.toBeNull();
    expect(glyph!.textContent).toBe("↗");
    // The decorative arrow is out of the accessible name — the link still
    // resolves by its human name (DB-024(d): the shared ZoLa link label).
    expect(within(panel).getByRole("link", { name: ZOLA_LOT_LINK_LABEL })).toBe(link);
  });

  it("hides the ↗ glyph on the overview Site-context ZoLa link while keeping its name", () => {
    renderOverview();
    const link = screen.getByTestId("site-zola-link");
    const glyph = link.querySelector<HTMLElement>("span[aria-hidden='true']");
    expect(glyph).not.toBeNull();
    expect(glyph!.textContent).toBe("↗");
    // The overview nests ZoningContextPanel, whose ZoLa link now shares the SAME
    // accessible name (DB-024(d)); scope to the map card so this asserts the
    // site-context link specifically.
    const mapCard = document.querySelector<HTMLElement>(".architect-map-card")!;
    expect(within(mapCard).getByRole("link", { name: ZOLA_LOT_LINK_LABEL })).toBe(link);
  });
});

describe("AS-6 (DB-019b) — PropertyOverview honest absent note on a non-canonical or null BBL", () => {
  it("renders NO Site-context link and a panel-matched absent note when the BBL is not canonical", () => {
    const profile = baseProfile();
    profile.identity.bbl = "12345"; // wrong length — zolaLotUrl returns null
    renderOverview(profile);
    expect(screen.queryByTestId("site-zola-link")).toBeNull();
    const siteAbsent = screen.getByTestId("site-zola-absent");
    // PropertyOverview nests ZoningContextPanel, so its own absent note renders
    // in the same tree — assert BOTH honest notes are byte-identical to the
    // shared ABSENT_BBL_MAP_LINK_NOTE constant (single source of truth, DB-024(b)),
    // never independently drifting literals.
    const panelAbsent = screen.getByTestId("zoning-context-zola-absent");
    expect(siteAbsent.textContent).toBe(ABSENT_BBL_MAP_LINK_NOTE);
    expect(panelAbsent.textContent).toBe(ABSENT_BBL_MAP_LINK_NOTE);
  });

  it("renders the honest absent note (no link, no crash) when the BBL is literally null", () => {
    // Explicit null-BBL regression for AS-6 / DB-019b. The generated contract
    // types identity.bbl as a non-null string, but a connector miss can leave
    // it absent; a literal null must take the SAME honest-absence path as a
    // malformed string — never throw (zolaLotUrl's typeof guard and
    // propertyHref's `?? ""` both tolerate it) and never emit a guessed link.
    // Deliberate invalid-shape probe per CODING_RULES: `as unknown as`.
    const profile = baseProfile();
    profile.identity.bbl = null as unknown as string;
    renderOverview(profile);
    expect(screen.queryByTestId("site-zola-link")).toBeNull();
    const siteAbsent = screen.getByTestId("site-zola-absent");
    // Same shared constant on the null-BBL path too: both honest notes are
    // byte-identical to ABSENT_BBL_MAP_LINK_NOTE (DB-024(b)), never drifting.
    const panelAbsent = screen.getByTestId("zoning-context-zola-absent");
    expect(siteAbsent.textContent).toBe(ABSENT_BBL_MAP_LINK_NOTE);
    expect(panelAbsent.textContent).toBe(ABSENT_BBL_MAP_LINK_NOTE);
  });

  it("with a canonical BBL the Site-context link renders and no absent note appears (prior rendering preserved)", () => {
    renderOverview();
    expect(screen.getByTestId("site-zola-link").getAttribute("href")).toBe(
      `${ZOLA_PREFIX}1000010010`,
    );
    expect(screen.queryByTestId("site-zola-absent")).toBeNull();
  });
});

describe("AS-7 (DB-019c) — landmark/historic rows surface the mapped-feature coverage_status", () => {
  it("shows each present designation's coverage status inline, display-only (base fixture: conditional)", () => {
    const panel = renderPanel();
    const designations = within(panel).getByTestId("zoning-context-designations");
    // One badge per PRESENT designation (landmark + historic), read straight
    // from the fixture's coverage_status — nothing computed. Not colour-only:
    // CoverageBadge carries the enum token + a screen-reader gloss.
    const badges = designations.querySelectorAll<HTMLElement>(".status-badge");
    expect(badges).toHaveLength(2);
    for (const badge of Array.from(badges)) {
      expect(badge.className).toContain("status-conditional");
    }
  });

  it("adds NO coverage badge on an Unknown row — nothing is invented when the feature is absent", () => {
    const profile = baseProfile();
    profile.zoning.mapped_features = [];
    const panel = renderPanel(profile);
    const designations = within(panel).getByTestId("zoning-context-designations");
    expect(designations.querySelectorAll(".status-badge")).toHaveLength(0);
    // The honest Unknown rows are still both present.
    expect(within(panel).getAllByText("Unknown — not supplied")).toHaveLength(2);
  });
});

describe("DB-024(c) — the ProfileViews 'Inspect calculation evidence' arrow is decorative", () => {
  it("hides the → glyph (aria-hidden) and keeps the link's accessible name arrow-free", () => {
    // ZoningView carries the primary "Inspect calculation evidence" action; its
    // trailing → must be decorative (out of the accessible name), matching the
    // accepted DB-019a arrow pattern used on the ZoLa links above.
    render(
      <ZoningView
        profile={baseProfile()}
        evaluation={null}
        scenario={null}
        onInspect={vi.fn()}
      />,
    );
    // The link resolves by its arrow-free accessible name — the glyph is excluded.
    const link = screen.getByRole("link", { name: "Inspect calculation evidence" });
    const glyph = link.querySelector<HTMLElement>("span[aria-hidden='true']");
    expect(glyph).not.toBeNull();
    expect(glyph!.textContent).toBe("→");
  });
});
