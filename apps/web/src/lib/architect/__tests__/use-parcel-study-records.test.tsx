import { act, cleanup, renderHook, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { fetchPropertyProfile, type LookupOutcome } from "@/lib/api";
import { fetchLotGeometry, type LotOutlineOutcome } from "@/lib/lot-geometry-api";
import { baseProfile } from "@/test-support/fixtures";
import { useParcelStudyRecords } from "../use-parcel-study-records";

vi.mock("@/lib/api", () => ({ fetchPropertyProfile: vi.fn() }));
vi.mock("@/lib/lot-geometry-api", () => ({ fetchLotGeometry: vi.fn() }));

const A = "3022640032";
const B = "3022640033";
const C = "3022640034";
const profileFetch = vi.mocked(fetchPropertyProfile);
const outlineFetch = vi.mocked(fetchLotGeometry);

function profile(bbl: string): LookupOutcome {
  const value = baseProfile();
  value.identity.bbl = bbl;
  return { kind: "profile", profile: value, correlationId: "profile-test" };
}

function outline(bbl: string): LotOutlineOutcome {
  return {
    kind: "document", correlationId: "outline-test",
    view: {
      bbl, outcome: "no_outline", outcomeToken: "no_outline", geometry: null,
      geometryUnusable: false, featureCount: 0, reviewRequired: true,
      noOutlineReason: "No source outline", condoClassification: { classification: "unknown", note: null },
      accuracyNote: "Display only", attribution: "Test fixture", disclaimer: "Not a survey",
      notes: [], source: { sourceId: null, datasetVersion: null, retrievedAt: null },
    },
  };
}

function deferred<T>() {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>(complete => { resolve = complete; });
  return { promise, resolve };
}

beforeEach(() => {
  vi.resetAllMocks();
  profileFetch.mockImplementation(async bbl => profile(bbl));
  outlineFetch.mockImplementation(async bbl => outline(bbl));
});
afterEach(cleanup);

describe("useParcelStudyRecords: independent city-record reads", () => {
  it("rejects wrong-BBL profiles and outlines without exposing their values", async () => {
    profileFetch.mockResolvedValue(profile(B));
    outlineFetch.mockResolvedValue(outline(B));
    const { result } = renderHook(() => useParcelStudyRecords([A]));
    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.records[0].profileOutcome).toMatchObject({
      kind: "validation_failure", problems: [expect.stringContaining("identity mismatch")],
    });
    expect(result.current.records[0].outlineOutcome).toMatchObject({ kind: "error", state: "result_mismatch" });
    expect(JSON.stringify(result.current.records)).not.toContain('"kind":"profile"');
    expect(JSON.stringify(result.current.records)).not.toContain('"kind":"document"');
  });

  it("does not hold a successful outline or another parcel behind a profile failure", async () => {
    const delayed = deferred<LookupOutcome>();
    profileFetch.mockImplementation(bbl => bbl === A ? delayed.promise : Promise.resolve(profile(bbl)));
    const { result } = renderHook(() => useParcelStudyRecords([A, B]));
    await waitFor(() => expect(result.current.records[1].loading).toBe(false));
    expect(result.current.records[0]).toMatchObject({ bbl: A, profileOutcome: null, outlineOutcome: { kind: "document" }, loading: true });
    await act(async () => delayed.resolve({ kind: "no_match", bbl: A, message: "Not found", correlationId: null }));
    expect(result.current.loading).toBe(false);
    expect(result.current.records[0].outlineOutcome?.kind).toBe("document");
    expect(result.current.records[1].profileOutcome?.kind).toBe("profile");
  });

  it("clears every old result in the first render for a new scope and ignores late responses", async () => {
    const oldOutline = deferred<LotOutlineOutcome>();
    outlineFetch.mockImplementation(bbl => bbl === A ? oldOutline.promise : Promise.resolve(outline(bbl)));
    const frames: Array<{ bbl: string; profileKind: string | undefined }[]> = [];
    const { result, rerender } = renderHook(({ bbls }) => {
      const state = useParcelStudyRecords(bbls);
      frames.push(state.records.map(record => ({ bbl: record.bbl, profileKind: record.profileOutcome?.kind })));
      return state;
    }, { initialProps: { bbls: [A] } });
    await waitFor(() => expect(result.current.records[0].profileOutcome?.kind).toBe("profile"));
    const firstNewFrame = frames.length;
    rerender({ bbls: [B] });
    expect(frames[firstNewFrame]).toEqual([{ bbl: B, profileKind: undefined }]);
    await waitFor(() => expect(result.current.loading).toBe(false));
    await act(async () => oldOutline.resolve(outline(A)));
    expect(result.current.records.map(record => record.bbl)).toEqual([B]);
    expect(profileFetch.mock.calls[0][1]?.signal?.aborted).toBe(true);
  });

  it("treats a return to an earlier scope as a fresh generation", async () => {
    const freshA = deferred<LookupOutcome>();
    let callsForA = 0;
    profileFetch.mockImplementation(bbl => {
      if (bbl === A && ++callsForA > 1) return freshA.promise;
      return Promise.resolve(profile(bbl));
    });
    const { result, rerender } = renderHook(({ bbls }) => useParcelStudyRecords(bbls), { initialProps: { bbls: [A] } });
    await waitFor(() => expect(result.current.loading).toBe(false));
    rerender({ bbls: [B] });
    await waitFor(() => expect(result.current.loading).toBe(false));
    rerender({ bbls: [A] });
    expect(result.current.records[0].profileOutcome).toBeNull();
    await act(async () => freshA.resolve(profile(A)));
    await waitFor(() => expect(result.current.loading).toBe(false));
  });

  it("retry clears old values immediately and prevents an earlier request from refilling them", async () => {
    const oldProfile = deferred<LookupOutcome>();
    const newProfile = deferred<LookupOutcome>();
    profileFetch.mockReturnValueOnce(oldProfile.promise).mockReturnValueOnce(newProfile.promise);
    const { result } = renderHook(() => useParcelStudyRecords([A]));
    await waitFor(() => expect(result.current.records[0].outlineOutcome?.kind).toBe("document"));
    act(() => result.current.retry());
    expect(result.current.records[0].profileOutcome).toBeNull();
    await act(async () => oldProfile.resolve(profile(A)));
    expect(result.current.records[0].profileOutcome).toBeNull();
    await act(async () => newProfile.resolve({ kind: "network_error", message: "New attempt failed" }));
    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.records[0].profileOutcome?.kind).toBe("network_error");
  });

  it("bounds concurrent work to three parcel workers and aborts on unmount", async () => {
    const profiles = new Map<string, ReturnType<typeof deferred<LookupOutcome>>>();
    const outlines = new Map<string, ReturnType<typeof deferred<LotOutlineOutcome>>>();
    profileFetch.mockImplementation(bbl => {
      const pending = deferred<LookupOutcome>(); profiles.set(bbl, pending); return pending.promise;
    });
    outlineFetch.mockImplementation(bbl => {
      const pending = deferred<LotOutlineOutcome>(); outlines.set(bbl, pending); return pending.promise;
    });
    const { unmount } = renderHook(() => useParcelStudyRecords([A, B, C, "3022640035"]));
    expect(profileFetch).toHaveBeenCalledTimes(3);
    expect(outlineFetch).toHaveBeenCalledTimes(3);
    await act(async () => {
      profiles.get(A)!.resolve(profile(A));
      outlines.get(A)!.resolve(outline(A));
    });
    expect(profileFetch).toHaveBeenCalledTimes(4);
    expect(outlineFetch).toHaveBeenCalledTimes(4);
    unmount();
    expect(profileFetch.mock.calls.every(([, options]) => options?.signal?.aborted)).toBe(true);
  });

  it("deduplicates a parcel set and does not refetch just because its order changes", async () => {
    const { result, rerender } = renderHook(({ bbls }) => useParcelStudyRecords(bbls), { initialProps: { bbls: [B, A, A] } });
    await waitFor(() => expect(result.current.loading).toBe(false));
    rerender({ bbls: [A, B] });
    expect(result.current.records.map(record => record.bbl)).toEqual([A, B]);
    expect(profileFetch).toHaveBeenCalledTimes(2);
    expect(outlineFetch).toHaveBeenCalledTimes(2);
  });

  it("turns an unexpected rejection into a retryable outcome while preserving the other channel", async () => {
    profileFetch.mockRejectedValue(new Error("Unexpected transport failure"));
    const { result } = renderHook(() => useParcelStudyRecords([A]));
    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.records[0]).toMatchObject({ profileOutcome: { kind: "network_error" }, outlineOutcome: { kind: "document" } });
  });
});

const BASES = ["3022640032", "3022640033"];
const BILLING = "3022647515";
const OTHER_BILLING = "3022647516";

function missing(bbl: string): LotOutlineOutcome {
  return { kind: "document", correlationId: null, view: {
    bbl, outcome: "no_outline", outcomeToken: "no_outline", geometry: null,
    geometryUnusable: false, featureCount: 0, reviewRequired: false,
    noOutlineReason: "no_feature_for_bbl", condoClassification: { classification: "unknown", note: null },
    accuracyNote: "Approximate", attribution: "NYC DCP", disclaimer: "Display only", notes: [],
    source: { sourceId: "nyc-dcp-mappluto", datasetVersion: "26v2", retrievedAt: null },
  } };
}

describe("parcel study context requests", () => {
  beforeEach(() => { vi.mocked(fetchLotGeometry).mockImplementation(async bbl => missing(bbl)); });

  it("fetches billing geometry separately without adding billing land or a billing profile request", async () => {
    const { result } = renderHook(() => useParcelStudyRecords(BASES, BILLING));
    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.records.map(record => record.bbl)).toEqual(BASES);
    expect(vi.mocked(fetchPropertyProfile).mock.calls.map(([bbl]) => bbl)).toEqual(BASES);
    expect(vi.mocked(fetchLotGeometry).mock.calls.map(([bbl]) => bbl).sort()).toEqual([...BASES, BILLING]);
    for (const bbl of BASES) expect(outlineFetch).toHaveBeenCalledWith(bbl,
      expect.objectContaining({ source: "tax-map", signal: expect.any(AbortSignal) }));
    expect(outlineFetch.mock.calls.find(([bbl]) => bbl === BILLING)?.[1]?.source).toBeUndefined();
    expect(result.current.contextOutline).toEqual({ bbl: BILLING, outcome: missing(BILLING), loading: false });
  });

  it("rejects foreign billing identity without discarding base records", async () => {
    vi.mocked(fetchLotGeometry).mockImplementation(async bbl => missing(bbl === BILLING ? OTHER_BILLING : bbl));
    const { result } = renderHook(() => useParcelStudyRecords(BASES, BILLING));
    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.contextOutline?.outcome).toMatchObject({ kind: "error", state: "result_mismatch" });
    expect(result.current.records.every(record => record.outlineOutcome?.kind === "document")).toBe(true);
  });

  it("turns a rejected billing request into retryable context failure without discarding base records", async () => {
    vi.mocked(fetchLotGeometry).mockImplementation(async bbl => {
      if (bbl === BILLING) throw new Error("Network unavailable");
      return missing(bbl);
    });
    const { result } = renderHook(() => useParcelStudyRecords(BASES, BILLING));
    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.contextOutline?.outcome?.kind).toBe("network_error");
    expect(result.current.records).toHaveLength(2);
    vi.mocked(fetchLotGeometry).mockImplementation(async bbl => missing(bbl));
    act(() => result.current.retry());
    expect(result.current.contextOutline?.outcome).toBeNull();
    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.contextOutline?.outcome?.kind).toBe("document");
  });

  it("aborts stale context on retry and A → B → A identity switches, ignoring late results", async () => {
    const pending: Array<{ bbl: string; signal?: AbortSignal; resolve: (value: LotOutlineOutcome) => void }> = [];
    vi.mocked(fetchLotGeometry).mockImplementation((bbl, options) => {
      if (BASES.includes(bbl)) return Promise.resolve(missing(bbl));
      return new Promise(resolve => pending.push({ bbl, signal: options?.signal, resolve }));
    });
    const { result, rerender, unmount } = renderHook(({ billing }) => useParcelStudyRecords(BASES, billing), { initialProps: { billing: BILLING } });
    await waitFor(() => expect(pending).toHaveLength(1));
    act(() => result.current.retry());
    await waitFor(() => expect(pending).toHaveLength(2));
    expect(pending[0].signal?.aborted).toBe(true);
    rerender({ billing: OTHER_BILLING });
    await waitFor(() => expect(pending).toHaveLength(3));
    rerender({ billing: BILLING });
    await waitFor(() => expect(pending).toHaveLength(4));
    expect(result.current.contextOutline).toEqual({ bbl: BILLING, outcome: null, loading: true });
    await act(async () => { for (const stale of pending.slice(0, 3)) stale.resolve(missing(stale.bbl)); });
    expect(result.current.contextOutline?.outcome).toBeNull();
    expect(pending.slice(0, 3).every(item => item.signal?.aborted)).toBe(true);
    await act(async () => pending[3].resolve(missing(BILLING)));
    expect(result.current.contextOutline?.outcome).toEqual(missing(BILLING));
    expect(result.current.loading).toBe(false);
    unmount();
    expect(pending[3].signal?.aborted).toBe(true);
  });
});
