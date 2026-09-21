import { afterEach, describe, expect, it, vi } from "vitest";
import { act, cleanup, render, screen } from "@testing-library/react";
import { ProposalOutlineMap, drawnOverlayData } from "../ProposalOutlineMap";

/**
 * Task M5-T066 (D-082-R001). The interaction wrapper composes the accepted
 * LotOutlineMap with its additive click props. Real MapLibre pointer geometry
 * proves in the Playwright e2e; here we pin the PURE overlay builder and the
 * wrapper's click-routing contract (place vs. move vs. select) with LotOutlineMap
 * mocked (no WebGL in jsdom).
 */

// Capture the props ProposalOutlineMap passes down so a test can invoke the
// click callbacks exactly as the map runtime would.
interface CapturedMapProps {
  onOutlineMapClick: (lngLat: { lng: number; lat: number }) => void;
  onDrawnVertexClick: (index: number) => void;
  drawnOverlay: unknown;
}
let lastMapProps: CapturedMapProps | null = null;

vi.mock("@/components/address/LotOutlineMap", () => ({
  LotOutlineMap: (props: CapturedMapProps) => {
    lastMapProps = props;
    return <div data-testid="mock-lot-map" />;
  },
}));

afterEach(() => {
  cleanup();
  lastMapProps = null;
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
