import { afterEach, describe, expect, it, vi } from "vitest";
import { act, cleanup, render, screen, waitFor } from "@testing-library/react";
import { ProposalOutlineMap, drawnOverlayData, finitePointCount } from "../ProposalOutlineMap";

/**
 * Task M5-T066 (D-082-R001). The interaction wrapper composes the accepted
 * LotOutlineMap with its additive click props. Real MapLibre pointer geometry
 * proves in the Playwright e2e; here we pin the PURE overlay builder and the
 * wrapper's click-routing contract (place vs. move vs. select) with LotOutlineMap
 * mocked (no WebGL in jsdom).
 *
 * M5-T071 (DB-047(d)/(e)): the mock renders the leaf's interactive map surface
 * (its semantic aria-label) by default, and a typed-fallback surface when
 * `lotMock.variant` is flipped — so the wrapper's copy-gating (invite a map
 * gesture ONLY when a clickable map actually rendered) and finite-count status
 * are provable without WebGL.
 */

const INTERACTIVE_MAP_LABEL = "Interactive approximate lot outline map";

/**
 * The accepted leaf (LotOutlineMap) renders its interactive, aria-labelled map
 * container ONLY on the drawable single-lot + WebGL + not-render-failed path
 * (LotOutlineMap.tsx L639-647). Every NON-drawable outcome renders a typed
 * fallback that carries NO interactive aria-label. These are those required
 * fallback states, keyed by the leaf's REAL data-testid, so the wrapper's
 * copy-gating is proven against EACH required state, not one generic stand-in:
 *   condo unit / no polygon → lot-outline-empty            (LotOutlineMap.tsx L696)
 *   multiple_features       → lot-outline-review           (LotOutlineMap.tsx L707)
 *   invalid_geometry        → lot-outline-invalid          (LotOutlineMap.tsx L719)
 *   no-WebGL                → lot-outline-webgl-unavailable (LotOutlineMap.tsx L672)
 *   post-construction error → lot-outline-render-error     (LotOutlineMap.tsx L657)
 */
const FALLBACK_STATES = [
  { key: "condo unit / no polygon", testid: "lot-outline-empty" },
  { key: "multiple_features", testid: "lot-outline-review" },
  { key: "invalid_geometry", testid: "lot-outline-invalid" },
  { key: "no-WebGL", testid: "lot-outline-webgl-unavailable" },
  { key: "post-construction render error", testid: "lot-outline-render-error" },
] as const;

// Shared, per-test-controllable mock state (hoisted above the vi.mock factory).
// "interactive" → the aria-labelled drawable container; any other value is a
// leaf fallback data-testid (see FALLBACK_STATES), rendered WITHOUT the aria-label.
const lotMock = vi.hoisted(() => ({ variant: "interactive" as string }));

// Capture the props ProposalOutlineMap passes down so a test can invoke the
// click callbacks exactly as the map runtime would.
interface CapturedMapProps {
  onOutlineMapClick: (lngLat: { lng: number; lat: number }) => void;
  onDrawnVertexClick: (index: number) => void;
  drawnOverlay: unknown;
}
let lastMapProps: CapturedMapProps | null = null;

vi.mock("@/components/address/LotOutlineMap", () => ({
  // "interactive" mirrors the leaf's drawable output (a map container carrying
  // the interactive aria-label the wrapper observes); any other variant mirrors
  // a typed fallback, rendered under the leaf's REAL data-testid and carrying NO
  // interactive aria-label — exactly the signal the wrapper's copy gates on.
  LotOutlineMap: (props: CapturedMapProps) => {
    lastMapProps = props;
    return lotMock.variant === "interactive" ? (
      <div data-testid="mock-lot-map" aria-label={INTERACTIVE_MAP_LABEL} />
    ) : (
      <p data-testid={lotMock.variant}>No interactive map — {lotMock.variant} fallback.</p>
    );
  },
}));

afterEach(() => {
  cleanup();
  lastMapProps = null;
  lotMock.variant = "interactive";
});

describe("drawnOverlayData — pure overlay builder", () => {
  it("returns an empty FeatureCollection for no points", () => {
    expect(drawnOverlayData([], null)).toEqual({ type: "FeatureCollection", features: [] });
  });

  it("emits a Point feature per finite point (keeping its index) and a connecting LineString for 2+ points", () => {
    const overlay = drawnOverlayData(
      [
        { lng: -73.99, lat: 40.7 },
        { lng: -73.98, lat: 40.7 },
      ],
      1,
    );
    // Line first, then the two points.
    expect(overlay.features[0].geometry.type).toBe("LineString");
    const points = overlay.features.filter((f) => f.geometry.type === "Point");
    expect(points).toHaveLength(2);
    expect(points[0].properties).toEqual({ index: 0, selected: false });
    expect(points[1].properties).toEqual({ index: 1, selected: true });
    expect(points[1].geometry).toEqual({ type: "Point", coordinates: [-73.98, 40.7] });
  });

  it("skips non-finite (not-yet-typed) points but preserves the ORIGINAL index of the finite ones", () => {
    const overlay = drawnOverlayData(
      [
        { lng: Number.NaN, lat: Number.NaN }, // index 0 — a fresh keyboard row
        { lng: -73.98, lat: 40.71 }, // index 1
      ],
      null,
    );
    const points = overlay.features.filter((f) => f.geometry.type === "Point");
    expect(points).toHaveLength(1);
    expect(points[0].properties).toEqual({ index: 1, selected: false });
    // Only one finite point, so no LineString is emitted.
    expect(overlay.features.some((f) => f.geometry.type === "LineString")).toBe(false);
  });
});

describe("ProposalOutlineMap — click routing", () => {
  const baseProps = {
    bbl: "1000010010",
    points: [
      { lng: -73.99, lat: 40.7 },
      { lng: -73.98, lat: 40.7 },
    ],
  };

  it("places a new point on a map click when nothing is selected", () => {
    const onPlace = vi.fn();
    const onMoveSelected = vi.fn();
    render(
      <ProposalOutlineMap
        {...baseProps}
        selectedIndex={null}
        onPlace={onPlace}
        onSelect={vi.fn()}
        onMoveSelected={onMoveSelected}
      />,
    );
    act(() => lastMapProps!.onOutlineMapClick({ lng: -73.97, lat: 40.72 }));
    expect(onPlace).toHaveBeenCalledWith({ lng: -73.97, lat: 40.72 });
    expect(onMoveSelected).not.toHaveBeenCalled();
    expect(screen.getByTestId("proposal-outline-map-instructions")).toHaveTextContent("Click the lot map to place");
  });

  it("moves the selected point on a map click when one is selected", () => {
    const onPlace = vi.fn();
    const onMoveSelected = vi.fn();
    render(
      <ProposalOutlineMap
        {...baseProps}
        selectedIndex={1}
        onPlace={onPlace}
        onSelect={vi.fn()}
        onMoveSelected={onMoveSelected}
      />,
    );
    act(() => lastMapProps!.onOutlineMapClick({ lng: -73.97, lat: 40.72 }));
    expect(onMoveSelected).toHaveBeenCalledWith({ lng: -73.97, lat: 40.72 });
    expect(onPlace).not.toHaveBeenCalled();
    expect(screen.getByTestId("proposal-outline-map-instructions")).toHaveTextContent("is selected — click the map to move it");
  });

  it("routes a drawn-vertex click to onSelect", () => {
    const onSelect = vi.fn();
    render(
      <ProposalOutlineMap
        {...baseProps}
        selectedIndex={null}
        onPlace={vi.fn()}
        onSelect={onSelect}
        onMoveSelected={vi.fn()}
      />,
    );
    act(() => lastMapProps!.onDrawnVertexClick(0));
    expect(onSelect).toHaveBeenCalledWith(0);
  });
});

// ---------------------------------------------------------------------------
// Task M5-T071 (DB-047(d)) — the instruction copy describes only interactions
// that EXIST. The click-to-place / click-to-move lead renders ONLY when a real
// interactive map surface is present; every typed-fallback state (condo unit
// lot, multiple_features, invalid_geometry, no-WebGL, render error) leads with
// keyboard-entry copy and never invites a map gesture.
// ---------------------------------------------------------------------------
describe("ProposalOutlineMap — instruction copy gates on a real interactive map (DB-047(d))", () => {
  const gateProps = {
    bbl: "1000010010",
    points: [
      { lng: -73.99, lat: 40.7 },
      { lng: -73.98, lat: 40.7 },
    ],
    onPlace: vi.fn(),
    onSelect: vi.fn(),
    onMoveSelected: vi.fn(),
  };

  it("leads with click-to-place when a drawable interactive map rendered (nothing selected)", async () => {
    render(<ProposalOutlineMap {...gateProps} selectedIndex={null} />);
    await waitFor(() =>
      expect(screen.getByTestId("proposal-outline-map-instructions")).toHaveTextContent(
        "Click the lot map to place",
      ),
    );
  });

  it("leads with click-to-move when a drawable interactive map rendered (a point selected)", async () => {
    render(<ProposalOutlineMap {...gateProps} selectedIndex={1} />);
    await waitFor(() =>
      expect(screen.getByTestId("proposal-outline-map-instructions")).toHaveTextContent(
        "is selected — click the map to move it",
      ),
    );
  });

  // Each REQUIRED typed-fallback state renders its own leaf surface (the leaf's
  // real data-testid) with NO interactive aria-label, so the wrapper must lead
  // keyboard-only for EVERY one — not just a single generic fallback. This binds
  // AS-1's "in EACH typed fallback state … the keyboard-entry copy leads".
  it.each(FALLBACK_STATES)(
    "the $key fallback renders its typed surface with NO interactive map and leads keyboard-only",
    async ({ testid }) => {
      lotMock.variant = testid;
      render(<ProposalOutlineMap {...gateProps} selectedIndex={null} />);
      const copy = await screen.findByTestId("proposal-outline-map-instructions");
      // The leaf's typed fallback for this state rendered …
      expect(screen.getByTestId(testid)).toBeInTheDocument();
      // … and carries NO interactive aria-label, so no map gesture is invited.
      expect(screen.queryByLabelText(INTERACTIVE_MAP_LABEL)).toBeNull();
      // Give any (mistaken) async flip to the interactive copy a chance to appear.
      await Promise.resolve();
      expect(copy).not.toHaveTextContent("Click the lot map to place");
      expect(copy).toHaveTextContent("Add proposed outline points by keyboard");
    },
  );

  it("while the leaf is LOADING the copy claims nothing about the lot — no definite negative, no map gesture (HJ B2)", async () => {
    // [ORCH-CORRECTED per HJ B2] The leaf renders lot-outline-loading during its
    // whole load window (geometry fetch → maplibre import → construction). The
    // old boolean gate asserted "has no interactive drawing surface" — a false
    // definite negative — for that entire window on every drawable lot.
    // Reverting the tri-state to the boolean reddens the negative-claim check.
    lotMock.variant = "lot-outline-loading";
    const { rerender } = render(<ProposalOutlineMap {...gateProps} selectedIndex={null} />);
    const copy = await screen.findByTestId("proposal-outline-map-instructions");
    await Promise.resolve();
    expect(copy).toHaveTextContent("Preparing the reference map");
    expect(copy).not.toHaveTextContent("no interactive drawing surface");
    expect(copy).not.toHaveTextContent("Click the lot map to place");

    // Load resolves into the drawable surface (same bbl → only the observer can
    // re-sync): the click-to-place lead appears.
    lotMock.variant = "interactive";
    rerender(<ProposalOutlineMap {...gateProps} selectedIndex={null} />);
    await waitFor(() => expect(copy).toHaveTextContent("Click the lot map to place"));

    // A load resolving into a typed fallback lands on the definite keyboard-only
    // copy instead (loading → absent), where the negative claim IS the honest one.
    lotMock.variant = "lot-outline-empty";
    rerender(<ProposalOutlineMap {...gateProps} selectedIndex={null} />);
    await waitFor(() => expect(copy).toHaveTextContent("no interactive drawing surface"));
  });

  it("in a typed-fallback state a selected point STILL never invites a map gesture (mutation guard)", async () => {
    lotMock.variant = "lot-outline-review";
    render(<ProposalOutlineMap {...gateProps} selectedIndex={1} />);
    const copy = await screen.findByTestId("proposal-outline-map-instructions");
    await Promise.resolve();
    // Reverting the gate (always showing the interactive copy) reddens here: a
    // selection would surface "click the map to move it" with no map to click.
    expect(copy).not.toHaveTextContent("click the map to move it");
    expect(copy).toHaveTextContent("Add proposed outline points by keyboard");
  });

  it("updates the copy when an initially interactive surface is REMOVED (exercises the MutationObserver)", async () => {
    // The leaf can transition from drawable to a typed fallback AFTER first paint
    // (e.g. a post-construction map "error" → lot-outline-render-error) WITHOUT
    // re-rendering this wrapper. The wrapper effect keys on [bbl] only, so it does
    // NOT re-run on such a transition — ONLY the MutationObserver catches the
    // subtree childList change and re-syncs the copy. Dropping the observer (keeping
    // just the one-time initial sync) leaves the stale click-to-place copy in place
    // and reddens this test.
    lotMock.variant = "interactive";
    const { rerender } = render(<ProposalOutlineMap {...gateProps} selectedIndex={null} />);
    await waitFor(() =>
      expect(screen.getByTestId("proposal-outline-map-instructions")).toHaveTextContent(
        "Click the lot map to place",
      ),
    );
    // The interactive container (the observed signal) is present at first.
    expect(screen.queryByLabelText(INTERACTIVE_MAP_LABEL)).not.toBeNull();

    // Same bbl → the wrapper effect does not re-run; the interactive container is
    // removed and replaced by a typed fallback surface, a subtree change only the
    // observer can see.
    lotMock.variant = "lot-outline-render-error";
    rerender(<ProposalOutlineMap {...gateProps} selectedIndex={null} />);

    await waitFor(() =>
      expect(screen.getByTestId("proposal-outline-map-instructions")).toHaveTextContent(
        "Add proposed outline points by keyboard",
      ),
    );
    // The observed signal is gone and the stale map-gesture copy did not survive.
    expect(screen.queryByLabelText(INTERACTIVE_MAP_LABEL)).toBeNull();
    expect(screen.getByTestId("proposal-outline-map-instructions")).not.toHaveTextContent(
      "Click the lot map to place",
    );
  });
});

// ---------------------------------------------------------------------------
// Task M5-T071 (DB-047(e)) — the status announces the FINITE point count only
// (what the overlay draws), never not-yet-typed keyboard rows.
// ---------------------------------------------------------------------------
describe("finitePointCount / status — announces only drawn (finite) points (DB-047(e))", () => {
  it("finitePointCount counts only points whose ordinates are both finite", () => {
    expect(
      finitePointCount([
        { lng: -73.99, lat: 40.7 },
        { lng: Number.NaN, lat: Number.NaN },
        { lng: 1, lat: Number.POSITIVE_INFINITY },
      ]),
    ).toBe(1);
  });

  it("the status counts finite points, not raw rows (a not-yet-typed row is silent)", async () => {
    render(
      <ProposalOutlineMap
        bbl="1000010010"
        points={[
          { lng: -73.99, lat: 40.7 },
          { lng: Number.NaN, lat: Number.NaN },
        ]}
        selectedIndex={null}
        onPlace={vi.fn()}
        onSelect={vi.fn()}
        onMoveSelected={vi.fn()}
      />,
    );
    await waitFor(() =>
      expect(screen.getByTestId("proposal-outline-map-status")).toHaveTextContent("1 point drawn"),
    );
    expect(screen.getByTestId("proposal-outline-map-status")).not.toHaveTextContent("2 points drawn");
  });
});
